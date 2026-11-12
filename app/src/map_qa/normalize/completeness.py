"""Completeness table (ADR-001 §3.5, PRD AC-11)."""
from __future__ import annotations

from importlib import resources

import duckdb

from map_qa.core.models import CompletenessRow

ATTRIBUTE_ORDER = {("osm", "maxspeed*"): 0, ("osm", "surface"): 1, ("osm", "lit"): 2, ("osm", "lanes"): 3,
                   ("osm", "sidewalk*"): 4, ("overture", "speed_limits"): 5, ("overture", "road_surface"): 6}


def compute_completeness(con: duckdb.DuckDBPyConnection) -> list[CompletenessRow]:
    sql = resources.files("map_qa.sql").joinpath("completeness.sql").read_text(encoding="utf-8")
    rows = [CompletenessRow(source=s, attribute=a, population=p, with_value=w, total=t, pct=float(pct))
            for s, a, p, w, t, pct in con.execute(sql).fetchall()]
    return sorted(rows, key=lambda r: (ATTRIBUTE_ORDER.get((r.source, r.attribute), 99), r.population))
