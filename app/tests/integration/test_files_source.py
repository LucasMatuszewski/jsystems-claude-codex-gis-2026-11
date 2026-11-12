import json
import shutil

import duckdb
import pytest

from map_qa.core.errors import SchemaMismatch
from map_qa.core.paths import sha256_bytes, sha256_file
from map_qa.sources import connect
from map_qa.sources.files import FilesSource, check_schema, describe

EXPECTED_ROWS = {"osm_roads": 99768, "overture_segments": 85405, "photos": 561, "photo_road_links": 561}


@pytest.fixture(scope="module")
def loaded(data_dir):
    con = connect(data_dir / "data")
    manifest = FilesSource(data_dir).load(con)
    yield con, manifest
    con.close()


def test_views_and_row_counts(loaded):
    con, manifest = loaded
    for name, rows in EXPECTED_ROWS.items():
        assert con.execute(f"SELECT count(*) FROM {name}").fetchone()[0] == rows
        assert manifest.table(name).rows == rows
    assert con.execute("SELECT count(*) FROM signs").fetchone()[0] == 119
    assert con.execute("SELECT count(*) FROM signs_nearest_osm").fetchone()[0] == 119


def test_no_label_views_registered(loaded):
    con, _ = loaded
    names = {r[0] for r in con.execute("SELECT view_name FROM duckdb_views() WHERE NOT internal").fetchall()}
    assert not any("label" in n for n in names)


def test_describe_matches_expected_schema(loaded, fixtures_dir):
    con, _ = loaded
    expected = json.loads((fixtures_dir / "schema_expected.json").read_text(encoding="utf-8"))
    for table in EXPECTED_ROWS:
        assert [list(c) for c in describe(con, table)] == expected[table], table


def test_manifest_hashes_and_snapshots(loaded, data_dir):
    _, manifest = loaded
    assert manifest.source == "files"
    assert manifest.snapshots == {"osm_extract_date": "2026-11-01", "overture_release": "2026-10-21.0"}
    sources = json.loads((data_dir / "sources.json").read_text(encoding="utf-8"))["files"]
    by_name = {f.name: f for f in manifest.files}
    for fname in ("osm_roads.parquet", "overture_segments.parquet"):
        assert by_name[fname].sha256 == sources[fname]["sha256"]
        assert by_name[fname].expected_match == "exact"
    for fname in ("photos.csv", "photo_road_links.csv"):
        entry = by_name[fname]
        assert entry.sha256 == sha256_file(data_dir / fname)  # raw bytes as read (AC-04)
        assert entry.expected_sha256 == sources[fname]["sha256"] and entry.matches_expected is True
    assert by_name["signs/signs.csv"].expected_sha256 is None
    assert manifest.warnings == []


def test_all_eight_sources_json_files_match(data_dir):
    sources = json.loads((data_dir / "sources.json").read_text(encoding="utf-8"))["files"]
    assert len(sources) == 8
    for fname, meta in sources.items():
        raw = (data_dir / fname).read_bytes()
        # Exact, or equal after CRLF->LF (Git autocrlf checkout of text files on Windows).
        assert meta["sha256"] in {sha256_bytes(raw), sha256_bytes(raw.replace(b"\r\n", b"\n"))}, fname


def test_signs_nearest_osm_keeps_raw_maxspeed_text(loaded):
    con, _ = loaded
    types = dict((c, t) for c, t in describe(con, "signs_nearest_osm"))
    assert types["maxspeed"] == "VARCHAR"


def test_removed_column_raises_schema_mismatch(tmp_path, data_dir):
    # Copy of the links file without one column -> SchemaMismatch (exit 4).
    work = tmp_path / "data"
    shutil.copytree(data_dir, work, ignore=shutil.ignore_patterns("data", "offline", "signs", "*.parquet", "*.gz", "*.geojson"))
    for f in ("osm_roads.parquet", "overture_segments.parquet"):
        (work / f).write_bytes(b"")  # placeholders are never read in this test
    src = (data_dir / "photo_road_links.csv").read_text(encoding="utf-8").splitlines()
    cut = [",".join(line.split(",")[:-1]) for line in src]
    (work / "photo_road_links.csv").write_text("\n".join(cut) + "\n", encoding="utf-8")
    con = duckdb.connect()
    con.execute(f"CREATE VIEW photo_road_links AS SELECT * FROM read_csv('{(work / 'photo_road_links.csv').as_posix()}')")
    with pytest.raises(SchemaMismatch) as exc:
        check_schema(con, "photo_road_links")
    assert exc.value.exit_code == 4 and exc.value.column == "candidate_flags"
