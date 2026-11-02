"""Shared HTTP, CLI and metrics helpers for the public-data exercises."""
import argparse
import csv
from datetime import datetime, timezone
import json
import math
from pathlib import Path
import time
import urllib.error
import urllib.request

DATA_DIR = Path(__file__).resolve().parent / 'data'
DEFAULT_BBOX = (19.25, 51.65, 19.65, 51.90)  # west, south, east, north
USER_AGENT = 'JSystems-GIS-Course/1.0 (+https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11)'


def parse_bbox(value):
    try:
        west, south, east, north = map(float, value.split(','))
        if (not all(math.isfinite(x) for x in (west, south, east, north))
                or not -180 <= west < east <= 180 or not -90 <= south < north <= 90):
            raise ValueError
        return west, south, east, north
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError('bbox: west,south,east,north in WGS84') from None


def parser(description, *, bbox=False):
    result = argparse.ArgumentParser(description=description)
    result.add_argument('--out', type=Path, default=DATA_DIR, help='Output directory')
    result.add_argument('--timeout', type=float, default=90, help='HTTP timeout in seconds')
    if bbox:
        result.add_argument('--bbox', type=parse_bbox, default=DEFAULT_BBOX,
                            help='west,south,east,north (default: Lodz)')
    return result


def fetch(url, *, data=None, timeout=90, attempts=3):
    """Retry transient HTTP/network errors; do not retry permanent 4xx errors."""
    for attempt in range(attempts):
        try:
            request = urllib.request.Request(url, data=data, headers={'User-Agent': USER_AGENT})
            with urllib.request.urlopen(request, timeout=timeout) as response:
                return response.read()
        except (urllib.error.URLError, TimeoutError, ConnectionError) as error:
            if isinstance(error, urllib.error.HTTPError) and error.code not in (408, 429, 500, 502, 503, 504):
                raise
            if attempt == attempts - 1:
                raise
            retry_after = error.headers.get('Retry-After', '') if isinstance(error, urllib.error.HTTPError) else ''
            delay = min(60, int(retry_after)) if retry_after.isdigit() else 2 ** (attempt + 1)
            print(f'Retry {attempt + 1}/{attempts - 1} in {delay}s: {error}', flush=True)
            time.sleep(delay)


def fetch_json(url, **kwargs):
    return json.loads(fetch(url, **kwargs))


def write_json(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def report(out, name, started, counts, files, **details):
    result = {'downloaded_at_utc': datetime.now(timezone.utc).isoformat(),
              'seconds': round(time.perf_counter() - started, 2), 'rows': counts,
              'files_bytes': {str(p.relative_to(out)): p.stat().st_size for p in files}, **details}
    write_json(out / f'{name}_run.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
