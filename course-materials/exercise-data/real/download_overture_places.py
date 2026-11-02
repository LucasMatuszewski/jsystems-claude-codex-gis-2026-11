"""Extract the latest Overture Places GeoParquet for a bbox using DuckDB."""
import re
import time

from download_common import fetch_json, parser, report

CATALOG = 'https://stac.overturemaps.org/catalog.json'
EV_CATEGORIES = ['electric_vehicle_charging_station', 'ev_charging_station', 'charging_station']


def main():
    import duckdb

    cli = parser('Overture Places -> GeoParquet (anonymous public S3)', bbox=True)
    cli.add_argument('--release', help='Release ID; default: latest from official STAC catalog')
    cli.add_argument('--ev-only', action='store_true', help='Filter known EV charging categories')
    args = cli.parse_args()
    started = time.perf_counter()
    release = args.release or fetch_json(CATALOG, timeout=args.timeout)['latest']
    if not re.fullmatch(r'\d{4}-\d{2}-\d{2}\.\d+', release):
        cli.error('Release must have format YYYY-MM-DD.N')
    args.out.mkdir(parents=True, exist_ok=True)
    source = f's3://overturemaps-us-west-2/release/{release}/theme=places/type=place/*'
    filename = 'overture_ev_places.parquet' if args.ev_only else 'overture_places.parquet'
    output = args.out / filename
    print(f'Release {release}; bbox {args.bbox}; querying public S3...', flush=True)
    with duckdb.connect() as con:
        # Local extension cache avoids relying on a writable user home on course VMs.
        extensions = args.out.resolve() / '.duckdb_extensions'
        con.execute('SET extension_directory = ?', [str(extensions)])
        for extension in ('httpfs', 'spatial'):
            con.execute(f'INSTALL {extension}; LOAD {extension}')
        con.execute("SET s3_region='us-west-2'; SET threads=4; SET memory_limit='2GB'")
        con.execute('SET http_timeout = ?', [max(1, int(args.timeout))])
        con.execute('SET http_retries=3')
        west, south, east, north = args.bbox
        sql = '''SELECT * FROM read_parquet(?, hive_partitioning=true)
                 WHERE bbox.xmin >= ? AND bbox.ymin >= ? AND bbox.xmax <= ? AND bbox.ymax <= ?'''
        parameters = [source, west, south, east, north]
        if args.ev_only:
            # Overture schema 2.0 replaced categories with taxonomy. Support pinned older releases too.
            columns = {row[0] for row in con.execute('DESCRIBE SELECT * FROM read_parquet(?)', [source]).fetchall()}
            if 'taxonomy' in columns:
                sql += ' AND (taxonomy.primary IN (SELECT unnest(?)) OR list_has_any(taxonomy.alternates, ?))'
            elif 'categories' in columns:
                sql += ' AND (categories.primary IN (SELECT unnest(?)) OR list_has_any(categories.alternate, ?))'
            else:
                raise ValueError('Unsupported Overture category schema; inspect the selected release')
            parameters += [EV_CATEGORIES, EV_CATEGORIES]
        con.execute('CREATE TEMP TABLE places AS ' + sql, parameters)
        count = con.execute('SELECT count(*) FROM places').fetchone()[0]
        con.table('places').write_parquet(str(output), compression='zstd')
    report(args.out, 'overture_ev' if args.ev_only else 'overture', started,
           {'places': count}, [output], release=release, bbox=args.bbox, source=source,
           ev_categories=EV_CATEGORIES if args.ev_only else None, duckdb_version=duckdb.__version__)


if __name__ == '__main__':
    main()
