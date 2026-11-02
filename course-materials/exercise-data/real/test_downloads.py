"""Offline contracts for validation and data preservation; no network mocks."""
import argparse
import csv
import json
from pathlib import Path
import tempfile
import unittest
import zipfile

from download_common import parse_bbox
from download_osm_chargers import to_features, write_osm
from download_gtfs import extract_feed
from download_gios_air import latest_available, measurement_error_status


class DownloadContracts(unittest.TestCase):
    def test_bbox_order_and_finite_ranges(self):
        self.assertEqual(parse_bbox('19.25,51.65,19.65,51.9'), (19.25, 51.65, 19.65, 51.9))
        for value in ('1,2,3', '20,52,19,51', '-181,0,1,2', '0,-91,1,2',
                      'nan,0,1,2', '0,0,inf,2'):
            with self.subTest(value=value), self.assertRaises(argparse.ArgumentTypeError):
                parse_bbox(value)

    def test_osm_preserves_tags_and_uses_lon_lat_and_element_identity(self):
        # Constructed geometry/tag cases, not a mocked API response.
        elements = [{'type': 'node', 'id': 1, 'lon': 19.4, 'lat': 51.7,
                     'tags': {'name': 'Łódź', 'access': 'customers', 'socket:type2': '2'}},
                    {'type': 'way', 'id': 1, 'center': {'lon': 19.5, 'lat': 51.8},
                     'tags': {'operator': 'Sieć'}}]
        features = to_features(elements)
        self.assertEqual(features[0]['geometry']['coordinates'], [19.4, 51.7])
        self.assertEqual(features[0]['properties']['tags'], elements[0]['tags'])
        self.assertNotEqual(features[0]['id'], features[1]['id'])
        with tempfile.TemporaryDirectory() as folder:
            write_osm(Path(folder), features)
            with (Path(folder) / 'osm_chargers.csv').open(encoding='utf-8-sig') as handle:
                rows = list(csv.DictReader(handle))
            self.assertEqual(json.loads(rows[0]['tags']), elements[0]['tags'])
            self.assertEqual(len(json.loads((Path(folder) / 'osm_chargers.geojson').read_text())['features']), 2)

    def test_osm_empty_result_is_valid(self):
        with tempfile.TemporaryDirectory() as folder:
            write_osm(Path(folder), [])
            self.assertEqual(json.loads((Path(folder) / 'osm_chargers.geojson').read_text())['features'], [])

    def test_latest_measurement_does_not_turn_null_into_zero(self):
        values = [{'Data': '2026-11-02 01:00:00', 'Wartość': None},
                  {'Data': '2026-11-02 00:00:00', 'Wartość': 0.0},
                  {'Data': '2026-11-01 23:00:00', 'Wartość': 7.0}]
        self.assertEqual(latest_available(values)['Wartość'], 0.0)
        self.assertIsNone(latest_available([values[0]]))
        self.assertIsNone(latest_available([]))

    def test_only_documented_manual_sensor_error_is_treated_as_no_live_data(self):
        self.assertEqual(measurement_error_status({'error_code': 'API-ERR-100003'}),
                         'manual_sensor_unavailable')
        with self.assertRaises(ValueError):
            measurement_error_status({'error_code': 'unknown'})

    def test_zip_rejects_traversal_and_accepts_flat_gtfs(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name in ('../outside.txt', '/outside.txt', '..\\outside.txt'):
                archive = root / 'bad.zip'
                with zipfile.ZipFile(archive, 'w') as z:
                    z.writestr(name, 'unsafe')
                with self.subTest(name=name), self.assertRaises(ValueError):
                    extract_feed(archive, root / 'bad')
            archive = root / 'good.zip'
            with zipfile.ZipFile(archive, 'w') as z:
                z.writestr('stops.txt', 'stop_id,stop_lat,stop_lon\n001,51.7,19.4\n')
            extract_feed(archive, root / 'good')
            self.assertTrue((root / 'good/stops.txt').is_file())


if __name__ == '__main__':
    unittest.main()
