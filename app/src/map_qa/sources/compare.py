"""--compare-sources: row counts and key sets of both sources (ADR-001 §3.2, PRD §4.3 step 4)."""
from __future__ import annotations

from pathlib import Path

import duckdb

from map_qa.core.models import SourceCompareRow
from map_qa.sources import MAP_VIEWS, connect

KEYS = {"osm_roads": "osm_id", "overture_segments": "id", "photos": "photo_id", "photo_road_links": "photo_id"}


def _keys(con: duckdb.DuckDBPyConnection, table: str) -> set:
    return {r[0] for r in con.execute(f"SELECT {KEYS[table]} FROM {table}").fetchall()}


def compare_sources(con: duckdb.DuckDBPyConnection, other_source, work_dir: Path) -> list[SourceCompareRow]:
    """Loads `other_source` into a separate in-memory DuckDB; `con` (selected source) is not modified."""
    other = connect(work_dir)
    try:
        other_source.load(other)
        rows = []
        for table in MAP_VIEWS:
            a, b = _keys(con, table), _keys(other, table)
            na = con.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            nb = other.execute(f"SELECT count(*) FROM {table}").fetchone()[0]
            only_a, only_b = len(a - b), len(b - a)
            rows.append(SourceCompareRow(table=table, selected_rows=na, other_rows=nb, keys_only_selected=only_a,
                                         keys_only_other=only_b, equal=(na == nb and only_a == 0 and only_b == 0)))
        return rows
    finally:
        other.close()
