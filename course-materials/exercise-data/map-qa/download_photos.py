# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow==12.0.0"]
# ///
"""Odtwarza przypięte zdjęcia Panoramax. Weryfikuje źródło i wynik, wznawia pobranie."""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import os
from pathlib import Path, PureWindowsPath
import re
import shutil
import sys
import tempfile
import time
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from PIL import Image, ImageOps

BASE = Path(__file__).resolve().parent


def valid_hash(value: str) -> str:
    if not re.fullmatch(r"[0-9a-f]{64}", value):
        raise ValueError("Manifest zawiera niepoprawny SHA-256")
    return value


def target_path(directory: Path, filename: str) -> Path:
    if not filename or Path(filename).name != filename or "\\" in filename or PureWindowsPath(filename).drive or filename in (".", ".."):
        raise ValueError("Nazwa zdjęcia musi być pojedynczą nazwą pliku")
    target = directory / filename
    if target.is_symlink():
        raise ValueError("Plik docelowy jest dowiązaniem")
    return target


def source_url(value: str) -> str:
    parsed = urlparse(value)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("Źródło musi być adresem HTTPS bez danych logowania")
    return value


def digest(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def verified(path: Path, expected: str) -> bool:
    valid_hash(expected)
    return path.is_file() and digest(path.read_bytes()) == expected


def prepare_image(raw: bytes) -> bytes:
    image = ImageOps.exif_transpose(Image.open(io.BytesIO(raw))).convert("RGB")
    image.thumbnail((1024, 1024), Image.Resampling.LANCZOS)
    result = io.BytesIO()
    image.save(result, "JPEG", quality=85, optimize=False)
    return result.getvalue()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=BASE / "photos.csv")
    parser.add_argument("--out", type=Path, default=BASE / "data" / "photos")
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--timeout", type=float, default=45)
    parser.add_argument("--verify-only", action="store_true")
    args = parser.parse_args()
    if args.limit is not None and args.limit < 1:
        parser.error("--limit musi być dodatni")
    if args.timeout <= 0:
        parser.error("--timeout musi być dodatni")
    with args.manifest.open(encoding="utf-8-sig", newline="") as handle:
        rows = list(csv.DictReader(handle))
    if args.limit is not None:
        rows = rows[:args.limit]
    # Validate all paths and hashes before any network request.
    names = [row["filename"] for row in rows]
    if len(names) != len(set(names)):
        raise ValueError("Powtarzająca się nazwa pliku w manifeście")
    for row in rows:
        target_path(args.out, row["filename"])
        valid_hash(row["sha256"])
        valid_hash(row["source_sha256"])
        source_url(row["url"])
    args.out.mkdir(parents=True, exist_ok=True)
    counts = {"existing": 0, "offline": 0, "downloaded": 0, "missing": 0}
    for row in rows:
        target = target_path(args.out, row["filename"])
        if verified(target, row["sha256"]):
            counts["existing"] += 1
            continue
        # A corrupt file fails closed; it is never silently accepted or overwritten.
        if target.exists():
            raise ValueError(f"Niezgodny hash istniejącego pliku: {target.name}")
        bundled = target_path(BASE / "offline", row["filename"])
        if verified(bundled, row["sha256"]):
            if not args.verify_only:
                shutil.copyfile(bundled, target)
            counts["offline"] += 1
            continue
        if args.verify_only:
            counts["missing"] += 1
            continue
        req = Request(source_url(row["url"]), headers={"User-Agent": "JSystems-map-QA-course/2026; public educational dataset"})
        # One attempt. A failed download can be resumed by re-running this command.
        with urlopen(req, timeout=args.timeout) as response:
            raw = response.read(40 * 1024 * 1024 + 1)
        if len(raw) > 40 * 1024 * 1024 or digest(raw) != row["source_sha256"]:
            raise ValueError(f"Źródłowy plik zmienił się: {row['photo_id']}")
        content = raw if row["source"] == "Mapillary" else prepare_image(raw)
        if digest(content) != row["sha256"]:
            raise ValueError(f"Niezgodny hash po przeskalowaniu: {row['photo_id']}; zachowaj Pillow 12.0.0 i sprawdź wersję JPEG")
        # Unique temp file in the target folder: an interrupted run leaves nothing that blocks a retry.
        fd, temp_name = tempfile.mkstemp(dir=target.parent, prefix=target.name + ".", suffix=".part")
        temporary = Path(temp_name)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(content)
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)
        counts["downloaded"] += 1
        print(f"Pobrano {row['photo_id']}", flush=True)
        time.sleep(0.1)
    print(" ".join(f"{key}={value}" for key, value in counts.items()))
    return 1 if counts["missing"] else 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ValueError, OSError) as exc:
        # Do not echo request URLs, authentication headers or response bodies.
        print(f"Pobieranie przerwane: {type(exc).__name__}. Sprawdź połączenie, manifest i hashe; pliki wejściowe pozostają bez zmian.", file=sys.stderr)
        raise SystemExit(2)
