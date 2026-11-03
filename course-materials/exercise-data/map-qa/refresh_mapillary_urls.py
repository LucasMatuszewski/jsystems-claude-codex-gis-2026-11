# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Odświeża adresy miniatur Mapillary; zachowuje identyfikatory i przypięte hashe."""
import argparse
import csv
import json
import os
from pathlib import Path
import time
from urllib.parse import urlencode
from urllib.request import Request, urlopen

BASE = Path(__file__).resolve().parent


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=BASE / "photos.csv")
    parser.add_argument("--out", type=Path, default=BASE / "data" / "photos-refreshed.csv")
    parser.add_argument("--limit", type=int, default=None, help="Maksymalna liczba adresów Mapillary do odświeżenia")
    args = parser.parse_args()
    token = os.environ.get("MAPILLARY_TOKEN")
    if not token:
        parser.error("Brak zmiennej MAPILLARY_TOKEN; nie wklejaj jej do polecenia ani pliku")
    if args.out.exists():
        parser.error("Plik docelowy już istnieje; wybierz nowy --out")
    if args.limit is not None and args.limit < 1:
        parser.error("--limit musi być dodatni")
    with args.manifest.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        fields = reader.fieldnames
        rows = list(reader)
    updated = 0
    for row in rows:
        if row["source"] != "Mapillary" or (args.limit is not None and updated >= args.limit):
            continue
        image_id = row["photo_id"].removeprefix("mapillary_")
        if not image_id.isdigit():
            raise ValueError("Niepoprawny identyfikator obrazu Mapillary")
        request = Request("https://graph.mapillary.com/" + image_id + "?" + urlencode({"fields": "thumb_1024_url"}), headers={"Authorization": "OAuth " + token})
        with urlopen(request, timeout=45) as response:
            row["url"] = json.load(response)["thumb_1024_url"]
        updated += 1
        time.sleep(0.2)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("x", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    print(f"Odświeżone adresy: {updated}. Hashe pozostały bez zmian.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        # Graph URLs and exceptions may contain authentication details.
        print(f"Odświeżanie przerwane: {type(exc).__name__}")
        raise SystemExit(2)
