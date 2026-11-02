"""GIOS v1: all stations and latest available values for selected stations."""
import json
import time
from urllib.error import HTTPError
from urllib.parse import urlencode

from download_common import fetch_json, parser, report, write_csv, write_json

BASE = 'https://api.gios.gov.pl/pjp-api/v1/rest/'
STATIONS = 'Lista stacji pomiarowych'
SENSORS = 'Lista stanowisk pomiarowych dla podanej stacji'
VALUES = 'Lista danych pomiarowych'


def pages(endpoint, key, timeout):
    rows = []
    page = 0
    while True:
        response = fetch_json(BASE + endpoint + '?' + urlencode({'page': page, 'size': 500}), timeout=timeout)
        rows.extend(response[key])
        page += 1
        if page >= response['totalPages']:
            return rows
        time.sleep(0.2)


def latest_available(values):
    available = [v for v in values if v['Wartość'] is not None]
    return max(available, key=lambda v: v['Data']) if available else None


def measurement_error_status(error):
    # The API explicitly identifies manual sensors. All other errors remain failures.
    if error.get('error_code') == 'API-ERR-100003':
        return 'manual_sensor_unavailable'
    raise ValueError(f"Unexpected GIOS error: {error}")


def main():
    cli = parser('GIOS stations and latest measurements (v1 JSON-LD)')
    cli.add_argument('--stations', type=int, nargs='+', default=[295, 296, 10058], help='Station IDs (default: Lodz)')
    cli.add_argument('--sensors-per-station', type=int, default=2)
    args = cli.parse_args()
    if args.sensors_per_station < 1:
        cli.error('--sensors-per-station must be positive')
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    stations = pages('station/findAll', STATIONS, args.timeout)
    ids = {r['Identyfikator stacji'] for r in stations}
    if missing := set(args.stations) - ids:
        cli.error(f'Unknown stations: {sorted(missing)}')
    write_json(args.out / 'gios_stations.json', stations)
    normalized = [{'station_id': s['Identyfikator stacji'], 'name': s['Nazwa stacji'],
                   'latitude': float(s['WGS84 φ N']), 'longitude': float(s['WGS84 λ E']),
                   'city': s['Nazwa miasta']} for s in stations]
    write_csv(args.out / 'gios_stations.csv', normalized,
              ['station_id', 'name', 'latitude', 'longitude', 'city'])
    raw, latest = [], []
    for station in dict.fromkeys(args.stations):
        sensors = pages(f'station/sensors/{station}', SENSORS, args.timeout)
        # These pollutant codes support automatic measurements. Some stations
        # still have no recent values: report that explicitly, never substitute 0.
        candidates = [s for s in sensors if s['Wskaźnik - kod'] in {'PM10', 'PM2.5', 'NO2', 'O3', 'SO2', 'CO'}]
        for sensor in candidates[:args.sensors_per_station]:
            sensor_id = sensor['Identyfikator stanowiska']
            time.sleep(0.25)
            status, error = None, None
            try:
                values = pages(f'data/getData/{sensor_id}', VALUES, args.timeout)
            except HTTPError as exc:
                if exc.code != 400:
                    raise
                error = json.loads(exc.read())
                status = measurement_error_status(error)
                values = []
            raw.append({'station_id': station, 'sensor': sensor, 'values': values, 'error': error})
            value = latest_available(values)
            latest.append({'station_id': station, 'sensor_id': sensor_id,
                           'pollutant': sensor['Wskaźnik - kod'], 'unit': 'µg/m³',
                           'measured_at_local': value['Data'] if value else '',
                           'value': value['Wartość'] if value else '',
                           'status': status or ('available' if value else 'no_recent_value')})
    write_json(args.out / 'gios_measurements.json', raw)
    write_csv(args.out / 'gios_latest.csv', latest,
              ['station_id', 'sensor_id', 'pollutant', 'unit', 'measured_at_local', 'value', 'status'])
    report(args.out, 'gios', started,
           {'stations': len(stations), 'sensors': len(latest),
            'measurements': sum(len(s['values']) for s in raw),
            'latest_non_null': sum(row['status'] == 'available' for row in latest),
            'manual_sensors': sum(row['status'] == 'manual_sensor_unavailable' for row in latest)},
           [args.out / f'gios_{name}' for name in ['stations.json', 'stations.csv', 'measurements.json', 'latest.csv']],
           station_ids=args.stations, api=BASE)


if __name__ == '__main__':
    main()
