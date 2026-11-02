# /// script
# requires-python = ">=3.12"
# dependencies = ["pillow==12.0.0"]
# ///
"""Download a small attributed Commons/Panoramax sample, or render offline fixtures.

Commons category membership is a weak label, not a verified speed reading.
Panoramax points are camera positions, not traffic-sign locations.
"""
import csv
from datetime import datetime, timezone
import hashlib
import html
import json
import re
import time
from pathlib import Path, PureWindowsPath
from urllib.parse import urlencode

from download_common import bbox, fetch, fetch_json, parser, report, write_csv, write_json

FIELDS = ['image_id', 'filename', 'source_url', 'download_url', 'creator', 'license',
          'license_url', 'longitude', 'latitude', 'captured_at', 'category_speed_hint',
          'observed_speed', 'label_status', 'sha256', 'view_azimuth', 'annotations_json']


def plain(value):
    return html.unescape(re.sub('<[^>]+>', '', value)).strip()


def commons(args):
    rows, raw, seen = [], [], set()
    # Cycle classes so that truncation does not yield only 30 km/h photos.
    buckets = []
    for speed in (30, 50, 70, 90):
        params = {'action': 'query', 'format': 'json', 'generator': 'categorymembers',
                  'gcmtitle': f'Category:{speed} km/h speed limit road signs in Poland',
                  'gcmtype': 'file', 'gcmlimit': 50, 'prop': 'imageinfo|coordinates',
                  'iiprop': 'url|extmetadata|mime', 'iiurlwidth': 640, 'coprimary': 'all'}
        url = 'https://commons.wikimedia.org/w/api.php?' + urlencode(params)
        payload = fetch_json(url, timeout=args.timeout)
        raw.append({'query_url': url, 'category_speed': speed, 'response': payload})
        candidates = []
        for page in payload.get('query', {}).get('pages', {}).values():
            info = page.get('imageinfo', [{}])[0]
            meta = info.get('extmetadata', {})
            license_name = meta.get('LicenseShortName', {}).get('value', '')
            if info.get('mime') != 'image/jpeg' or license_name not in ('CC0', 'CC BY 4.0', 'CC BY-SA 4.0'):
                continue
            if args.cc0_only and license_name != 'CC0':
                continue
            candidates.append((speed, page, info, meta))
        buckets.append(candidates)
    for index in range(50):
        for bucket in buckets:
            if index >= len(bucket):
                continue
            speed, page, info, meta = bucket[index]
            identity = str(page['pageid'])
            if identity in seen:
                continue
            seen.add(identity)
            url = info.get('thumburl', info['url'])
            filename = f'commons_{identity}.jpg'
            content = fetch(url, timeout=args.timeout)
            if not content.startswith(b'\xff\xd8'):
                raise RuntimeError(f'Expected JPEG: {identity}')
            (args.out / filename).write_bytes(content)
            point = page.get('coordinates', [{}])[0]
            rows.append(dict.fromkeys(FIELDS, ''))
            rows[-1].update(image_id=identity, filename=filename, source_url=info['descriptionurl'],
                            download_url=url, creator=plain(meta.get('Artist', {}).get('value', '')),
                            license=meta['LicenseShortName']['value'],
                            license_url=meta.get('LicenseUrl', {}).get('value', 'https://creativecommons.org/publicdomain/zero/1.0/' if meta['LicenseShortName']['value'] == 'CC0' else ''),
                            longitude=point.get('lon', ''), latitude=point.get('lat', ''),
                            captured_at=plain(meta.get('DateTimeOriginal', {}).get('value', '')),
                            category_speed_hint=speed, label_status='category_hint_UNVERIFIED',
                            sha256=hashlib.sha256(content).hexdigest())
            print(f'Downloaded {filename} ({len(content)} B)', flush=True)
            time.sleep(0.1)
            if len(rows) >= args.limit:
                write_json(args.out / 'commons_metadata.json', raw)
                return rows
    write_json(args.out / 'commons_metadata.json', raw)
    return rows


def panoramax(args):
    url = args.endpoint.rstrip('/') + '/search?' + urlencode({'bbox': ','.join(map(str, args.bbox)), 'limit': args.limit})
    payload = fetch_json(url, timeout=args.timeout)
    write_json(args.out / 'panoramax_items.geojson', payload)
    rows = []
    for item in payload.get('features', [])[:args.limit]:
        properties = item['properties']
        license_name = properties.get('license', '')
        if license_name not in ('CC-BY-SA-4.0', 'CC-BY-4.0', 'CC0-1.0'):
            raise RuntimeError(f'Unreviewed image license {license_name!r}; choose another item')
        asset = item['assets'][args.resolution]['href']
        content = fetch(asset, timeout=args.timeout)
        if not content.startswith(b'\xff\xd8'):
            raise RuntimeError(f'Expected JPEG: {item["id"]}')
        filename = f'panoramax_{item["id"]}.jpg'
        (args.out / filename).write_bytes(content)
        links = {link['rel']: link['href'] for link in item['links']}
        point = item['geometry']['coordinates']
        row = dict.fromkeys(FIELDS, '')
        row.update(image_id=item['id'], filename=filename, source_url=links['self'], download_url=asset,
                   creator=', '.join(p['name'] for p in item.get('providers', []) if 'producer' in p.get('roles', [])),
                   license=license_name, license_url=links.get('license', ''),
                   longitude=point[0], latitude=point[1], captured_at=properties.get('datetime', ''),
                   label_status='unlabelled_camera_position', sha256=hashlib.sha256(content).hexdigest(),
                   view_azimuth=properties.get('view:azimuth', ''),
                   annotations_json=json.dumps({'annotations': properties.get('annotations', []),
                                                'semantics': properties.get('semantics', [])}, ensure_ascii=False))
        rows.append(row)
        print(f'Downloaded {filename} ({len(content)} B)', flush=True)
        time.sleep(0.1)
    return rows


def synthetic(args):
    from PIL import Image, ImageDraw, ImageFont
    rows, roads = [], []
    # Pillow's embedded default font makes this independent of Windows font paths.
    font = ImageFont.load_default(size=120)
    for index in range(args.limit):
        speed = (30, 50, 70, 90, None)[index % 5]
        image = Image.new('RGB', (512, 512), (204, 218, 228))
        draw = ImageDraw.Draw(image)
        draw.rectangle((0, 370, 512, 512), fill=(80, 83, 85))
        if speed:
            shift = (index % 3 - 1) * 10
            draw.rectangle((245 + shift, 260, 265 + shift, 470), fill=(140, 140, 140))
            draw.ellipse((80 + shift, 55, 430 + shift, 405), fill='white', outline=(200, 20, 30), width=30)
            draw.text((255 + shift, 225), str(speed), font=font, fill='black', anchor='mm')
        else:
            draw.rectangle((180, 150, 330, 340), fill=(30, 100, 190))
        filename = f'synthetic_{index:03}.png'
        path = args.out / filename
        image.save(path)
        row = dict.fromkeys(FIELDS, '')
        row.update(image_id=f'synthetic_{index:03}', filename=filename, creator='Edukey course fixture generator',
                   license='CC0-1.0', license_url='https://creativecommons.org/publicdomain/zero/1.0/',
                   observed_speed=str(speed) if speed else 'none', label_status='synthetic_ground_truth',
                   sha256=hashlib.sha256(path.read_bytes()).hexdigest())
        lon, lat = 19.44 + (index % 5) * 0.003, 51.77 + (index // 5) * 0.003
        row.update(longitude=lon, latitude=lat, label_status='synthetic_ground_truth')
        rows.append(row)
        mapped = speed if index % 2 == 0 and speed else (50 if speed != 50 else 30)
        roads.append({'type': 'Feature', 'id': f'synthetic/{index}',
                      'geometry': {'type': 'LineString', 'coordinates': [[lon - 0.0005, lat], [lon + 0.0005, lat]]},
                      'properties': {'osm_id': index + 1, 'maxspeed': str(mapped), 'highway': 'residential',
                                     'oneway': 'no', 'source': 'synthetic_fixture_not_OSM'}})
    write_json(args.out / 'synthetic_roads.geojson', {'type': 'FeatureCollection', 'features': roads})
    return rows


def pinned(args):
    with args.manifest.open(encoding='utf-8-sig', newline='') as stream:
        rows = list(csv.DictReader(stream))[:args.limit]
    for row in rows:
        filename = row['filename']
        if Path(filename).name != filename or PureWindowsPath(filename).name != filename:
            raise ValueError('Manifest filename must be a flat basename')
        if row['license'] not in ('CC0', 'CC BY 4.0', 'CC BY-SA 4.0', 'CC-BY-SA-4.0', 'CC-BY-4.0', 'CC0-1.0'):
            raise ValueError('Manifest license is not in the reviewed allowlist')
        content = fetch(row['download_url'], timeout=args.timeout)
        if hashlib.sha256(content).hexdigest() != row['sha256']:
            raise ValueError(f'Image changed: {filename}; re-review before reusing its label')
        (args.out / filename).write_bytes(content)
        print(f'Downloaded and hash-verified {filename}', flush=True)
        time.sleep(0.1)
    return rows


def main():
    cli = parser(__doc__)
    cli.add_argument('--source', choices=['commons', 'panoramax', 'synthetic'], default='commons')
    cli.add_argument('--limit', type=int, default=24)
    cli.add_argument('--cc0-only', action='store_true')
    cli.add_argument('--manifest', type=Path, help='Pinned labels CSV: re-download exact URLs and verify image SHA-256')
    cli.add_argument('--bbox', type=bbox, default=bbox('19.35,51.72,19.52,51.82'))
    cli.add_argument('--endpoint', default='https://api.panoramax.xyz/api')
    cli.add_argument('--resolution', choices=['thumb', 'sd'], default='thumb')
    args = cli.parse_args()
    if not 1 <= args.limit <= 50:
        cli.error('--limit must be 1..50')
    args.out.mkdir(parents=True, exist_ok=True)
    started = time.perf_counter()
    rows = pinned(args) if args.manifest else {'commons': commons, 'panoramax': panoramax, 'synthetic': synthetic}[args.source](args)
    if not rows:
        raise RuntimeError('No eligible images returned; no sample was produced')
    write_csv(args.out / 'labels.csv', rows, FIELDS)
    attribution = [f'Image sample provenance, accessed {datetime.now(timezone.utc).date().isoformat()}. Keep this file and labels.csv with redistributed images.',
                   'Commons categories are label hints only. Panoramax coordinates are camera locations.',
                   'Synthetic fixtures are original generated drawings dedicated to CC0-1.0; their coordinates and road attributes are invented fixture values, not OSM observations.']
    for row in rows:
        attribution.append(f'{row["filename"]}: {row["creator"]}; {row["source_url"]}; {row["license"]} {row["license_url"]}; downloaded derivative, unmodified.')
    (args.out / 'ATTRIBUTION.txt').write_text('\n'.join(attribution) + '\n', encoding='utf-8')
    paths = [args.out / row['filename'] for row in rows] + [args.out / 'labels.csv', args.out / 'ATTRIBUTION.txt']
    report(args.out, args.source + '_images', started, {'images': len(rows), 'geolocated': sum(row['longitude'] != '' for row in rows),
           'verified_labels': sum(row['label_status'] in ('synthetic_ground_truth', 'visual_review') for row in rows)}, paths,
           source=args.source, bbox=args.bbox if args.source == 'panoramax' else None)


if __name__ == '__main__':
    main()
