"""Download OSM charging stations as GeoJSON and CSV (all tags preserved)."""
import json
import time
from urllib.parse import urlencode

from download_common import fetch_json, parser, report, write_csv, write_json


def to_features(elements):
    features = []
    for element in elements:
        point = element if 'lon' in element else element.get('center')
        if point is None:
            raise ValueError(f"No coordinates for {element['type']}/{element['id']}")
        identity = f"{element['type']}/{element['id']}"
        features.append({'type': 'Feature', 'id': identity,
                         'geometry': {'type': 'Point', 'coordinates': [point['lon'], point['lat']]},
                         'properties': {'osm_type': element['type'], 'osm_id': element['id'],
                                        'tags': element.get('tags', {})}})
    return features


def write_osm(out, features):
    write_json(out / 'osm_chargers.geojson', {'type': 'FeatureCollection', 'features': features})
    rows = [{'osm_type': f['properties']['osm_type'], 'osm_id': f['properties']['osm_id'],
             'longitude': f['geometry']['coordinates'][0], 'latitude': f['geometry']['coordinates'][1],
             'tags': json.dumps(f['properties']['tags'], ensure_ascii=False)} for f in features]
    write_csv(out / 'osm_chargers.csv', rows, ['osm_type', 'osm_id', 'longitude', 'latitude', 'tags'])


def main():
    cli = parser('OSM charging stations: GeoJSON + CSV', bbox=True)
    cli.add_argument('--endpoint', default='https://overpass-api.de/api/interpreter')
    args = cli.parse_args()
    started = time.perf_counter()
    west, south, east, north = args.bbox
    query = (f'[out:json][timeout:60];nwr["amenity"="charging_station"]'
             f'({south},{west},{north},{east});out center tags;')
    response = fetch_json(args.endpoint, data=urlencode({'data': query}).encode(), timeout=args.timeout)
    if 'remark' in response:
        raise RuntimeError(f"Overpass returned an incomplete result: {response['remark']}")
    features = to_features(response['elements'])
    args.out.mkdir(parents=True, exist_ok=True)
    write_osm(args.out, features)
    report(args.out, 'osm', started, {'chargers': len(features)},
           [args.out / 'osm_chargers.geojson', args.out / 'osm_chargers.csv'],
           bbox=args.bbox, endpoint=args.endpoint, query=query)


if __name__ == '__main__':
    main()
