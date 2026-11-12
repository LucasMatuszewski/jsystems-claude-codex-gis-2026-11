"""FilesSource: local GeoParquet/CSV snapshot (ADR-001 §3.2)."""
from __future__ import annotations

import json
from importlib import resources
from pathlib import Path

import duckdb

from map_qa.core.errors import SourceUnavailable
from map_qa.core.models import FileHash, InputManifest, TableInfo
from map_qa.core.paths import sha256_bytes, sha256_file
from map_qa.sources import MAP_VIEWS, sql_literal
from map_qa.sources.schema import check_schema, describe

__all__ = ["FilesSource", "check_schema", "describe", "read_sources_json", "snapshots_from"]

FILES = {
    "osm_roads": "osm_roads.parquet",
    "overture_segments": "overture_segments.parquet",
    "photos": "photos.csv",
    "photo_road_links": "photo_road_links.csv",
    "signs": "signs/signs.csv",
    "signs_nearest_osm": "signs/nearest_osm.csv",
}
LOCAL_ONLY_VIEWS = ("signs", "signs_nearest_osm")


def read_sources_json(data_dir: Path) -> dict:
    return json.loads((Path(data_dir) / "sources.json").read_text(encoding="utf-8"))


def snapshots_from(sources: dict) -> dict[str, str]:
    return {
        "osm_extract_date": str(sources["osm"]["extract_date"])[:10],
        "overture_release": str(sources["overture"]["release"]),
    }


TEXT_SUFFIXES = {".csv", ".json", ".geojson", ".md", ".txt", ".sql"}


def hash_file(data_dir: Path, rel: str, expected: dict) -> FileHash:
    path = Path(data_dir) / rel
    fh = FileHash(name=rel, sha256=sha256_file(path), bytes=path.stat().st_size,
                  expected_sha256=(expected.get(rel) or {}).get("sha256"))
    if fh.expected_sha256 and fh.expected_sha256 != fh.sha256 and path.suffix.lower() in TEXT_SUFFIXES:
        fh.sha256_lf = sha256_bytes(path.read_bytes().replace(b"\r\n", b"\n"))
    return fh


def register_views(con: duckdb.DuckDBPyConnection, data_dir: Path, views: tuple[str, ...]) -> None:
    sql = resources.files("map_qa.sql").joinpath("views_files.sql").read_text(encoding="utf-8")
    params = {k: sql_literal((Path(data_dir) / v).resolve().as_posix()) for k, v in FILES.items()}
    for stmt in sql.format(**params).split(";"):
        body = "\n".join(line for line in stmt.splitlines() if not line.strip().startswith("--")).strip()
        if not body:
            continue
        view = body.split(" VIEW ", 1)[1].split()[0]
        if view in views:
            con.execute(body)


def hash_warnings(files: list[FileHash]) -> list[str]:
    return [f"Hash pliku {fh.name} różni się od sources.json (dane mogły zostać świadomie odświeżone)."
            for fh in files if fh.matches_expected is False]


class FilesSource:
    name = "files"

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)

    def load(self, con: duckdb.DuckDBPyConnection) -> InputManifest:
        missing = [rel for rel in ("sources.json", *FILES.values()) if not (self.data_dir / rel).is_file()]
        if missing:
            raise SourceUnavailable(f"Brak pliku wejściowego {missing[0]} w katalogu {self.data_dir}.")
        sources = read_sources_json(self.data_dir)
        expected = sources.get("files", {})
        register_views(con, self.data_dir, tuple(FILES))
        for view in MAP_VIEWS:
            check_schema(con, view)
        manifest = InputManifest(source=self.name, snapshots=snapshots_from(sources))
        manifest.files.append(hash_file(self.data_dir, "sources.json", expected))
        for view, rel in FILES.items():
            fh = hash_file(self.data_dir, rel, expected)
            manifest.files.append(fh)
            rows = con.execute(f"SELECT count(*) FROM {view}").fetchone()[0]
            manifest.tables.append(TableInfo(name=view, rows=rows, path=rel, sha256=fh.sha256))
        manifest.warnings.extend(hash_warnings(manifest.files))
        return manifest
