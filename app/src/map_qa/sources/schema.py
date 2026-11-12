"""Input schema contract (ADR-001 §3.1). Full expected DESCRIBE: tests/fixtures/schema_expected.json."""
from __future__ import annotations

import duckdb

from map_qa.core.errors import SchemaMismatch

# Columns the pipeline relies on, with the expected type ("GEOMETRY*" = any CRS, "LIST" = list of structs).
REQUIRED: dict[str, dict[str, str]] = {
    "osm_roads": {
        "osm_id": "BIGINT", "geometry": "GEOMETRY*", "highway": "VARCHAR", "maxspeed": "VARCHAR",
        "surface": "VARCHAR", "lanes": "VARCHAR", "lit": "VARCHAR", "tags": "VARCHAR", "node_ids": "BIGINT[]",
        "boundary_crossing": "BOOLEAN", "sidewalk": "VARCHAR", "sidewalk:left": "VARCHAR",
        "sidewalk:right": "VARCHAR", "access": "VARCHAR", "motor_vehicle": "VARCHAR", "bridge": "VARCHAR",
        "tunnel": "VARCHAR", "layer": "VARCHAR", "oneway": "VARCHAR",
    },
    "overture_segments": {
        "id": "VARCHAR", "geometry": "GEOMETRY*", "class": "VARCHAR", "subclass": "VARCHAR",
        "speed_limits": "LIST", "road_surface": "LIST", "sources": "LIST", "connectors": "LIST",
        "access_restrictions": "LIST", "level_rules": "LIST", "bbox": "STRUCT", "version": "INTEGER",
    },
    "photos": {
        "photo_id": "VARCHAR", "filename": "VARCHAR", "source": "VARCHAR", "url": "VARCHAR",
        "source_url": "VARCHAR", "longitude": "DOUBLE", "latitude": "DOUBLE", "heading": "DOUBLE",
        "captured_at": "TIMESTAMP WITH TIME ZONE", "sequence": "VARCHAR", "license": "VARCHAR",
        "author": "VARCHAR", "is_panorama": "BOOLEAN",
    },
    "photo_road_links": {
        "photo_id": "VARCHAR", "osm_way_id": "BIGINT", "overture_id": "VARCHAR", "distance_m": "DOUBLE",
        "bearing_diff": "DOUBLE", "directed_bearing_diff": "DOUBLE", "osm_candidate_count": "BIGINT",
        "match_method": "VARCHAR", "candidate_flags": "VARCHAR",
    },
}


def describe(con: duckdb.DuckDBPyConnection, view: str) -> list[tuple[str, str]]:
    return [(r[0], r[1]) for r in con.execute(f"DESCRIBE SELECT * FROM {view}").fetchall()]


def _type_ok(expected: str, actual: str) -> bool:
    if expected == "GEOMETRY*":
        return actual.startswith("GEOMETRY")
    if expected == "LIST":
        return actual.startswith("STRUCT(") and actual.endswith("[]")
    if expected == "STRUCT":
        return actual.startswith("STRUCT(") and not actual.endswith("[]")
    return actual == expected


def check_schema(con: duckdb.DuckDBPyConnection, view: str) -> None:
    actual = dict(describe(con, view))
    for column, expected in REQUIRED[view].items():
        if column not in actual:
            raise SchemaMismatch(view, column, "brak kolumny")
        if not _type_ok(expected, actual[column]):
            raise SchemaMismatch(view, column, f"typ {actual[column]} zamiast {expected}")
