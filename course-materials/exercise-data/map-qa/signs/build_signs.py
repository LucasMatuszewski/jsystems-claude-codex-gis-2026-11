# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow==12.0.0"]
# ///
"""Odtwarza prawdziwe zdjęcia i wycinki Mapillary z przypiętego manifestu.

Weryfikacja offline: uv run --python 3.12 build_signs.py --verify-only
Pobieranie brakujących plików: ten sam skrypt bez --verify-only, z MAPILLARY_TOKEN.
Współrzędne crop_bbox_px odnoszą się do miniatury źródłowej, przed skalowaniem.
Nie odtwarza etykiet przez ponowne wywołanie modeli ani nie aktualizuje OSM.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import time
from urllib.parse import urlencode, urlparse
from urllib.request import Request, urlopen

from PIL import Image

BASE = Path(__file__).resolve().parent
IMAGE_ID = re.compile(r"mapillary_[0-9]+\Z")
VALUES = {str(n) for n in (5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80, 90, 100, 110, 120, 130, 140)} | {"none", "unreadable"}


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def valid_hash(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Niepoprawny SHA-256 w manifeście")
    return value


def image_path(base: Path, folder: str, photo_id: str) -> Path:
    if folder not in ("photos", "crops") or not IMAGE_ID.fullmatch(photo_id):
        raise ValueError("Niepoprawny identyfikator lub katalog zdjęcia")
    directory = base / folder
    target = directory / f"{photo_id}.jpg"
    if directory.is_symlink() or target.is_symlink():
        raise ValueError("Katalog lub plik zdjęcia jest dowiązaniem")
    return target


def verified(path: Path, expected: str) -> bool:
    valid_hash(expected)
    return path.is_file() and digest(path.read_bytes()) == expected


def prepare_images(raw: bytes, bbox: list[int]) -> tuple[bytes, bytes]:
    image = Image.open(io.BytesIO(raw)).convert("RGB")
    if (len(bbox) != 4 or any(type(v) is not int for v in bbox)
            or not (0 <= bbox[0] < bbox[2] <= image.width and 0 <= bbox[1] < bbox[3] <= image.height)):
        raise ValueError("Niepoprawny crop_bbox_px względem zdjęcia źródłowego")
    crop = image.crop(tuple(bbox))
    image.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    frame_buffer, crop_buffer = io.BytesIO(), io.BytesIO()
    image.save(frame_buffer, "JPEG", quality=82, optimize=False)
    crop.save(crop_buffer, "JPEG", quality=92, optimize=False)
    return frame_buffer.getvalue(), crop_buffer.getvalue()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def validate_manifest(base: Path) -> list[dict[str, str]]:
    rows = read_csv(base / "signs.csv")
    ids = [row["photo_id"] for row in rows]
    if not ids or len(ids) != len(set(ids)):
        raise ValueError("Pusty manifest lub powtórzone photo_id")
    for row in rows:
        for folder in ("photos", "crops"):
            image_path(base, folder, row["photo_id"])
        for key in ("sha256", "crop_sha256", "source_sha256"):
            valid_hash(row[key])
        bbox = json.loads(row["crop_bbox_px"])
        if len(bbox) != 4 or any(type(x) is not int for x in bbox):
            raise ValueError("Niepoprawny crop_bbox_px")
        if not (-180 <= float(row["longitude"]) <= 180 and -90 <= float(row["latitude"]) <= 90):
            raise ValueError("Niepoprawne współrzędne geograficzne")
    for filename in ("labels.csv", "nearest_osm.csv"):
        related = read_csv(base / filename)
        related_ids = [r["photo_id"] for r in related]
        if len(related_ids) != len(set(related_ids)) or set(related_ids) != set(ids):
            raise ValueError(f"Niespójne identyfikatory w {filename}")
        if filename == "labels.csv":
            for label in related:
                if label["sign_value"] not in VALUES or label["status"] not in ("certain", "uncertain"):
                    raise ValueError("Niepoprawna etykieta lub status")
    return rows


def download(photo_id: str, token: str, timeout: float) -> bytes:
    image_id = photo_id.removeprefix("mapillary_")
    request = Request(
        f"https://graph.mapillary.com/{image_id}?" + urlencode({"fields": "thumb_2048_url"}),
        headers={"Authorization": "OAuth " + token, "User-Agent": "JSystems-map-QA-course/2026"},
    )
    with urlopen(request, timeout=timeout) as response:
        metadata = json.load(response)
    url = metadata["thumb_2048_url"]
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Niepoprawny adres miniatury")
    with urlopen(Request(url), timeout=timeout) as response:
        raw = response.read(25 * 1024 * 1024 + 1)
    if len(raw) > 25 * 1024 * 1024:
        raise ValueError("Zbyt duży obraz źródłowy")
    return raw


def atomic_write(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".part")
    temporary = Path(name)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(content)
        temporary.replace(path)
    finally:
        temporary.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify-only", action="store_true")
    parser.add_argument("--out", type=Path, default=BASE)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--timeout", type=float, default=35)
    args = parser.parse_args()
    if args.timeout <= 0 or (args.limit is not None and args.limit < 1):
        parser.error("Timeout i limit muszą być dodatnie")
    rows = validate_manifest(BASE)
    if args.limit is not None:
        rows = rows[:args.limit]
    checked = downloaded = missing = 0
    for row in rows:
        paths = [image_path(args.out, folder, row["photo_id"]) for folder in ("photos", "crops")]
        hashes = [row["sha256"], row["crop_sha256"]]
        matches = [verified(path, sha) for path, sha in zip(paths, hashes)]
        if any(path.exists() and not match for path, match in zip(paths, matches)):
            raise ValueError(f"Niezgodny hash istniejącego pliku: {row['photo_id']}")
        if not all(matches):
            if args.verify_only:
                missing += 1
                continue
            token = os.environ.get("MAPILLARY_TOKEN")
            if not token:
                raise ValueError("Brak zmiennej MAPILLARY_TOKEN")
            # One attempt per request. A failure terminates the run, without retries.
            raw = download(row["photo_id"], token, args.timeout)
            if digest(raw) != row["source_sha256"]:
                raise ValueError(f"Zmieniło się źródło: {row['photo_id']}")
            contents = prepare_images(raw, json.loads(row["crop_bbox_px"]))
            if any(digest(content) != sha for content, sha in zip(contents, hashes)):
                raise ValueError("Niezgodna transformacja: zachowaj Pillow 12.0.0 i wersję libjpeg")
            for path, content, match in zip(paths, contents, matches):
                if not match:
                    atomic_write(path, content)
            downloaded += 1
            time.sleep(0.25)
        for path in paths:
            if path.stat().st_size > 2_000_000:
                raise ValueError(f"Plik przekracza 2 MB: {path.name}")
        with Image.open(paths[0]) as im:
            if max(im.size) > 1600:
                raise ValueError("Pełny kadr przekracza 1600 px")
        checked += 1
    total = sum(p.stat().st_size for p in args.out.rglob("*") if p.is_file())
    if total >= 35_000_000:
        raise ValueError("Katalog przekracza limit 35 MB")
    print(f"checked={checked} downloaded={downloaded} missing={missing} bytes={total}")
    return 1 if missing else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as exc:
        # Never print signed URLs, request headers, API response bodies or tokens.
        print(f"Weryfikacja/pobieranie przerwane: {type(exc).__name__}. Sprawdź manifest, hashe i połączenie.", file=sys.stderr)
        raise SystemExit(2)
