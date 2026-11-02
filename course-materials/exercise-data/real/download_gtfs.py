"""Download the official Lodz static GTFS, extract it and load stops in DuckDB."""
from pathlib import PurePosixPath
import shutil
import time
import zipfile

from download_common import fetch, parser, report

DEFAULT_URL = 'https://otwarte.miasto.lodz.pl/wp-content/uploads/2025/06/GTFS.zip'


def extract_feed(archive, destination):
    # GTFS consists of flat text files. Validate every entry before writing any.
    with zipfile.ZipFile(archive) as source:
        for entry in source.infolist():
            path = PurePosixPath(entry.filename.replace('\\', '/'))
            if path.is_absolute() or len(path.parts) != 1 or ':' in entry.filename or entry.is_dir():
                raise ValueError(f'Unsafe or non-flat GTFS ZIP entry: {entry.filename}')
        if sum(entry.file_size for entry in source.infolist()) > 1024 ** 3:
            raise ValueError('GTFS archive exceeds 1 GiB uncompressed')
        if 'stops.txt' not in source.namelist():
            raise ValueError('GTFS archive is missing stops.txt')
        # Extract into a fresh sibling folder, then swap it in, so files from an
        # older feed never mix with the new one.
        destination.parent.mkdir(parents=True, exist_ok=True)
        staging = destination.with_name(destination.name + '.new')
        shutil.rmtree(staging, ignore_errors=True)
        staging.mkdir()
        for entry in source.infolist():
            with source.open(entry) as src, (staging / entry.filename).open('wb') as dst:
                shutil.copyfileobj(src, dst)
    shutil.rmtree(destination, ignore_errors=True)
    staging.rename(destination)


def main():
    import duckdb

    cli = parser('Official Lodz GTFS static feed -> DuckDB stops')
    cli.add_argument('--url', default=DEFAULT_URL, help='Public GTFS ZIP URL')
    args = cli.parse_args()
    started = time.perf_counter()
    args.out.mkdir(parents=True, exist_ok=True)
    archive = args.out / 'gtfs.zip'
    archive.write_bytes(fetch(args.url, timeout=args.timeout))
    folder = args.out / 'gtfs'
    extract_feed(archive, folder)
    database = args.out / 'gtfs.duckdb'
    with duckdb.connect(str(database)) as con:
        # Keep identifiers as strings: leading zeros are meaningful in GTFS.
        con.execute('CREATE OR REPLACE TABLE stops AS SELECT * FROM read_csv(?, all_varchar=true)',
                    [str(folder / 'stops.txt')])
        count = con.execute('SELECT count(*) FROM stops').fetchone()[0]
        invalid = con.execute('''SELECT count(*) FROM stops WHERE
            try_cast(stop_lat AS DOUBLE) IS NULL OR try_cast(stop_lon AS DOUBLE) IS NULL
            OR NOT (try_cast(stop_lat AS DOUBLE) BETWEEN -90 AND 90)
            OR NOT (try_cast(stop_lon AS DOUBLE) BETWEEN -180 AND 180)''').fetchone()[0]
    files = [archive, database, *sorted(folder.iterdir())]
    report(args.out, 'gtfs', started, {'stops': count, 'invalid_coordinates': invalid}, files, url=args.url)


if __name__ == '__main__':
    main()
