# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Download OSM highway ways and mapped sign nodes, preserving topology and all tags."""
import json
from datetime import datetime, timezone
import time
from urllib.parse import urlencode
from download_common import bbox, fetch, fetch_json, parser, report, write_csv, write_json
import xml.etree.ElementTree as ET


def to_features(elements):
    roads, signs = [], []
    for element in elements:
        tags = element.get('tags', {})
        if element['type'] == 'way' and 'highway' in tags:
            coordinates = [[p['lon'], p['lat']] for p in element.get('geometry', [])]
            if len(coordinates) < 2 or len(coordinates) != len(element.get('nodes', [])):
                raise ValueError(f'Incomplete geometry for way/{element["id"]}')
            roads.append({'type': 'Feature', 'id': f'way/{element["id"]}',
                          'geometry': {'type': 'LineString', 'coordinates': coordinates},
                          'properties': {'osm_id': element['id'], 'osm_type': 'way',
                                         'maxspeed': tags.get('maxspeed'), 'highway': tags['highway'],
                                         'oneway': tags.get('oneway'), 'name': tags.get('name'),
                                         'nodes': element['nodes'], 'tags': tags}})
        elif element['type'] == 'node' and 'traffic_sign' in tags:
            signs.append({'type': 'Feature', 'id': f'node/{element["id"]}',
                          'geometry': {'type': 'Point', 'coordinates': [element['lon'], element['lat']]},
                          'properties': {'osm_id': element['id'], 'tags': tags}})
    return roads, signs


def main():
    cli = parser(__doc__)
    cli.add_argument('--bbox', type=bbox, default=bbox('19.435,51.770,19.465,51.790'))
    cli.add_argument('--source', choices=['overpass', 'osm-api'], default='overpass')
    cli.add_argument('--endpoint', default='https://overpass-api.de/api/interpreter')
    args = cli.parse_args()
    west, south, east, north = args.bbox
    if (east - west) * (north - south) > 0.05:
        cli.error('Use a small bbox (area <= 0.05 square degrees)')
    started = time.perf_counter()
    region = f'({south},{west},{north},{east})'
    query = f'[out:json][timeout:60];(way["highway"]{region};node["traffic_sign"]{region};);out body geom;'
    if args.source == 'osm-api':
        if (east - west) * (north - south) > 0.0002:
            cli.error('Main OSM API fallback requires a tiny bbox (area <= 0.0002 square degrees)')
        source_url = 'https://api.openstreetmap.org/api/0.6/map?' + urlencode({'bbox': ','.join(map(str, args.bbox))})
        xml_bytes = fetch(source_url, timeout=args.timeout)
        root = ET.fromstring(xml_bytes)
        nodes = {int(node.attrib['id']): {'lon': float(node.attrib['lon']), 'lat': float(node.attrib['lat'])}
                 for node in root.findall('node')}
        elements = []
        for way in root.findall('way'):
            tags = {tag.attrib['k']: tag.attrib['v'] for tag in way.findall('tag')}
            if 'highway' not in tags:
                continue
            refs = [int(node.attrib['ref']) for node in way.findall('nd')]
            if any(ref not in nodes for ref in refs):
                raise RuntimeError('Incomplete way geometry from main OSM API')
            elements.append({'type': 'way', 'id': int(way.attrib['id']), 'nodes': refs,
                             'geometry': [nodes[ref] for ref in refs], 'tags': tags})
        for node in root.findall('node'):
            tags = {tag.attrib['k']: tag.attrib['v'] for tag in node.findall('tag')}
            if 'traffic_sign' in tags:
                elements.append({'type': 'node', 'id': int(node.attrib['id']),
                                 **nodes[int(node.attrib['id'])], 'tags': tags})
        payload = {'elements': elements, 'osm3s': {'source': source_url, 'generator': root.attrib.get('generator')},
                   'note': 'Converted from main OSM API XML, not an Overpass response'}
    else:
        source_url = args.endpoint
        payload = fetch_json(args.endpoint, data=urlencode({'data': query}).encode(), timeout=args.timeout)
    if 'remark' in payload:
        raise RuntimeError(f'Incomplete Overpass result: {payload["remark"]}')
    roads, signs = to_features(payload['elements'])
    if not roads:
        raise RuntimeError('No road ways returned')
    args.out.mkdir(parents=True, exist_ok=True)
    raw_name = 'overpass_raw.json' if args.source == 'overpass' else 'osm_api_converted.json'
    write_json(args.out / raw_name, payload)
    if args.source == 'osm-api':
        (args.out / 'osm_api_raw.xml').write_bytes(xml_bytes)
    write_json(args.out / 'osm_roads.geojson', {'type': 'FeatureCollection', 'features': roads})
    write_json(args.out / 'osm_signs.geojson', {'type': 'FeatureCollection', 'features': signs})
    rows = [{'osm_id': f['properties']['osm_id'], 'maxspeed': f['properties']['maxspeed'],
             'highway': f['properties']['highway'], 'oneway': f['properties']['oneway'],
             'tags': json.dumps(f['properties']['tags'], ensure_ascii=False)} for f in roads]
    write_csv(args.out / 'osm_roads.csv', rows, ['osm_id', 'maxspeed', 'highway', 'oneway', 'tags'])
    (args.out / 'ATTRIBUTION.txt').write_text(f'© OpenStreetMap contributors, ODbL 1.0.\nhttps://www.openstreetmap.org/copyright\nDownloaded {datetime.now(timezone.utc).date().isoformat()}; retain raw tags and the ODbL notice.\n', encoding='utf-8')
    report(args.out, 'osm_roads', started, {'ways': len(roads), 'with_maxspeed': sum(bool(r['maxspeed']) for r in rows),
           'mapped_sign_nodes': len(signs)}, [args.out / n for n in (raw_name, 'osm_roads.geojson', 'osm_signs.geojson', 'osm_roads.csv')] + ([args.out / 'osm_api_raw.xml'] if args.source == 'osm-api' else []),
           bbox=args.bbox, endpoint=source_url, source=args.source, query=query if args.source == 'overpass' else None, osm_base=payload.get('osm3s', {}))


if __name__ == '__main__':
    main()
