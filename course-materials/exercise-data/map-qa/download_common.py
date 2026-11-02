"""Small, cross-platform public-data downloader utilities (stdlib)."""
import argparse
import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

USER_AGENT = 'JSystemsGISCourse/1.0 (educational public-data sample; https://github.com/LucasMatuszewski/jsystems-claude-codex-gis-2026-11)'


def bbox(value):
    try:
        west, south, east, north = map(float, value.split(','))
    except ValueError as exc:
        raise argparse.ArgumentTypeError('Expected west,south,east,north') from exc
    if not (-180 <= west < east <= 180 and -90 <= south < north <= 90):
        raise argparse.ArgumentTypeError('Invalid WGS84 bbox')
    return west, south, east, north


def parser(description):
    cli = argparse.ArgumentParser(description=description)
    cli.add_argument('--out', type=Path, default=Path(__file__).resolve().parent / 'data')
    cli.add_argument('--timeout', type=float, default=25)
    return cli


def fetch(url, *, timeout=25, data=None):
    for attempt in range(3):
        try:
            with urlopen(Request(url, data=data, headers={'User-Agent': USER_AGENT}), timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            if isinstance(exc, HTTPError) and exc.code not in (429, 500, 502, 503, 504):
                raise
            if attempt == 2:
                raise
            wait = min(10, 2 ** attempt)
            if isinstance(exc, HTTPError):
                try:
                    wait = min(30, float(exc.headers.get('Retry-After', wait)))
                except ValueError:
                    pass
            print(f'HTTP attempt {attempt + 1} failed ({type(exc).__name__}); retry in {wait}s', flush=True)
            time.sleep(wait)
    raise AssertionError('unreachable')


def fetch_json(url, **kwargs):
    payload = json.loads(fetch(url, **kwargs))
    if isinstance(payload, dict) and 'error' in payload:
        raise RuntimeError(f'API error: {payload["error"]}')
    return payload


def write_json(path, payload):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def write_csv(path, rows, fields):
    with path.open('w', encoding='utf-8-sig', newline='') as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def report(out, name, started, counts, paths, **metadata):
    result = {'accessed_at': datetime.now(timezone.utc).isoformat(),
              'seconds': round(time.perf_counter() - started, 3), 'counts': counts,
              'bytes': {str(path.relative_to(out)): path.stat().st_size for path in paths}, **metadata}
    write_json(out / f'{name}_run.json', result)
    print(json.dumps(result, ensure_ascii=False, indent=2), flush=True)
    return result
