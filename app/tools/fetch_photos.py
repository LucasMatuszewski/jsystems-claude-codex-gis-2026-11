"""Fetch report thumbnails (PRD AC-27): reuses the course script `download_photos.py` (same hash checks and
resizing) but skips per-photo HTTP errors instead of stopping at the first one.

Usage (repo root):
    uv run --python 3.12 --with pillow==12.0.0 python -I app/tools/fetch_photos.py course-materials/exercise-data/map-qa

Writes only to <data_dir>/data/photos/ (git-ignored); never overwrites a file; prints counts and error classes.
Verified 2026-11-13: 558 of 561 photos available, 3 Panoramax photos return HTTP 404 at the source.
"""
import csv
import importlib.util
import sys
import time
from collections import Counter
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

BASE = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("dl", BASE / "download_photos.py")
dl = importlib.util.module_from_spec(spec)
spec.loader.exec_module(dl)

out = BASE / "data" / "photos"
out.mkdir(parents=True, exist_ok=True)
rows = list(csv.DictReader(open(BASE / "photos.csv", encoding="utf-8-sig", newline="")))
counts, errors = Counter(), Counter()
for row in rows:
    target = dl.target_path(out, row["filename"])
    if dl.verified(target, row["sha256"]):
        counts["existing"] += 1
        continue
    if target.exists():
        counts["mismatch_existing"] += 1
        continue
    bundled = dl.target_path(BASE / "offline", row["filename"])
    if dl.verified(bundled, row["sha256"]):
        target.write_bytes(bundled.read_bytes())
        counts["offline"] += 1
        continue
    try:
        req = Request(dl.source_url(row["url"]), headers={"User-Agent": "JSystems-map-QA-course/2026; public educational dataset"})
        with urlopen(req, timeout=45) as resp:
            raw = resp.read(40 * 1024 * 1024 + 1)
    except HTTPError as exc:
        errors[f"{row['source']} HTTP {exc.code}"] += 1
        continue
    except (URLError, TimeoutError, OSError) as exc:
        errors[f"{row['source']} {type(exc).__name__}"] += 1
        continue
    if dl.digest(raw) != row["source_sha256"]:
        errors[f"{row['source']} source hash changed"] += 1
        continue
    content = raw if row["source"] == "Mapillary" else dl.prepare_image(raw)
    if dl.digest(content) != row["sha256"]:
        errors[f"{row['source']} hash after resize"] += 1
        continue
    target.write_bytes(content)
    counts["downloaded"] += 1
    time.sleep(0.1)
print(dict(counts), dict(errors))
