"""Data sources: register fixed DuckDB views and build the InputManifest (ADR-001 §3.2)."""
from __future__ import annotations

from pathlib import Path

import duckdb

from map_qa.core.paths import duckdb_extension_dir

MAP_VIEWS = ("osm_roads", "overture_segments", "photos", "photo_road_links")


def connect(work_dir: Path) -> duckdb.DuckDBPyConnection:
    """In-memory DuckDB with the spatial extension from the ignored work dir (ADR-000 §2)."""
    ext = duckdb_extension_dir(Path(work_dir))
    ext.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(config={"extension_directory": str(ext)})
    con.execute("INSTALL spatial")  # no network when already installed
    con.execute("LOAD spatial")
    return con


def sql_literal(text: str) -> str:
    return "'" + str(text).replace("'", "''") + "'"
