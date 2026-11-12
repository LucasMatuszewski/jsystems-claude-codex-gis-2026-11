"""Photo-road pairs and link_status (ADR-002 §3.2-§3.4, §4-§5)."""
from __future__ import annotations

from importlib import resources

import duckdb
import pyarrow as pa

from map_qa.core.enums import LinkStatus

DISTANCE_TOLERANCE_M = 0.5  # AC-09
MAX_RADIUS_M = 25.0
RESTRICTED = {"private", "no", "destination"}
# Informational candidate flags carried to `flags` (ADR-002 §3.4 "Rzeczywiste flagi").
INFO_FLAGS = ("camera_against_way_direction", "poor_heading_alignment", "boundary_crossing", "missing_heading")


def angle_diff(a: float | None, b: float | None) -> float | None:
    """Directed difference on the circle, 0-180 (ADR-002 §3.3)."""
    if a is None or b is None:
        return None
    d = abs(float(a) - float(b)) % 360.0
    return min(d, 360.0 - d)


def undirected_diff(a: float | None, b: float | None) -> float | None:
    """Difference against an undirected line, 0-90."""
    d = angle_diff(a, b)
    return None if d is None else min(d, 180.0 - d)


def link_rank(distance_m: float, bearing_diff: float | None) -> float:
    """Source ranking rule from sources.json: distance + bearing_diff/9; missing heading adds 5 m."""
    return distance_m + (5.0 if bearing_diff is None else bearing_diff / 9.0)


def pick_candidate(cands: list[dict]) -> tuple[dict, bool]:
    """Characterization of the input ranking: min rank, ties by distance then osm_id;
    an alternative within 2 m of the best rank marks ambiguity."""
    ranked = sorted(cands, key=lambda c: (round(link_rank(c["distance_m"], c["bearing_diff"]), 9),
                                          c["distance_m"], c["osm_id"]))
    best = ranked[0]
    best_rank = link_rank(best["distance_m"], best["bearing_diff"])
    ambiguous = any(link_rank(c["distance_m"], c["bearing_diff"]) - best_rank < 2.0 for c in ranked[1:])
    return best, ambiguous


def _flags_and_status(row: dict) -> tuple[list[str], list[str], str]:
    cflags = [f.strip() for f in row["candidate_flags_raw"].split(";") if f.strip()]
    flags: list[str] = [f for f in INFO_FLAGS if f in cflags]
    reasons: list[str] = []
    panorama = bool(row["is_panorama"]) or "panorama_heading_ambiguous" in cflags
    if panorama:
        flags.append("panorama")
    if row["same_position_time_n"] and row["same_position_time_n"] > 1:
        flags.append("suspect_position")  # placeholder-looking metadata (profile §6)
    if row["osm_way_id"] is None:
        return cflags, flags, [], str(LinkStatus.NO_CANDIDATE)
    if "ambiguous_candidates" in cflags:
        reasons.append("ambiguous_candidates")
    if row["distance_m"] is not None and row["distance_m"] > MAX_RADIUS_M:
        reasons.append("distance_over_25m")
    rec = row["distance_m_recomputed"]
    if rec is not None and row["distance_m"] is not None and abs(rec - row["distance_m"]) > DISTANCE_TOLERANCE_M:
        flags.append("distance_mismatch")
        reasons.append("distance_mismatch")
    if panorama and row["heading"] is None:
        reasons.append("panorama_without_heading")
    if (row["highway"] == "service" or "service_way" in cflags
            or (row["access"] or "") in RESTRICTED or (row["motor_vehicle"] or "") in RESTRICTED):
        flags.append("service_or_restricted")
    if ((row["bridge"] not in (None, "no")) or (row["tunnel"] not in (None, "no"))
            or (row["layer"] not in (None, "0")) or (row["overture_level_rules_n"] or 0) > 0):
        flags.append("grade_separated")
    if "overture_spatial_only" in cflags or row["match_method"] == "spatial_fallback":
        flags.append("overture_spatial_fallback")
    status = LinkStatus.AMBIGUOUS if reasons else LinkStatus.OK
    return cflags, flags, reasons, str(status)


LINK_COLUMNS = ["photo_id", "osm_way_id", "overture_id", "distance_m", "distance_m_recomputed", "bearing_diff",
                "directed_bearing_diff", "heading", "is_panorama", "match_method", "osm_candidate_count",
                "highway", "candidate_flags", "flags", "reasons", "link_status"]


def build_pairs(con: duckdb.DuckDBPyConnection) -> None:
    """Creates tables `links` (all photos, incl. no_candidate) and `pairs` (link_status in ok/ambiguous)."""
    con.execute(resources.files("map_qa.sql").joinpath("pairs.sql").read_text(encoding="utf-8"))
    cur = con.execute("SELECT * FROM link_base ORDER BY photo_id")
    names = [d[0] for d in cur.description]
    records = []
    for values in cur.fetchall():
        row = dict(zip(names, values))
        cflags, flags, reasons, status = _flags_and_status(row)
        rec = {k: row.get(k) for k in LINK_COLUMNS if k in row}
        rec.update(candidate_flags=cflags, flags=flags, reasons=reasons, link_status=status)
        records.append(rec)
    schema = pa.schema([
        ("photo_id", pa.string()), ("osm_way_id", pa.int64()), ("overture_id", pa.string()),
        ("distance_m", pa.float64()), ("distance_m_recomputed", pa.float64()), ("bearing_diff", pa.float64()),
        ("directed_bearing_diff", pa.float64()), ("heading", pa.float64()), ("is_panorama", pa.bool_()),
        ("match_method", pa.string()), ("osm_candidate_count", pa.int64()), ("highway", pa.string()),
        ("candidate_flags", pa.list_(pa.string())), ("flags", pa.list_(pa.string())),
        ("reasons", pa.list_(pa.string())), ("link_status", pa.string()),
    ])
    links_arrow = pa.Table.from_pylist(records, schema=schema)  # noqa: F841 (referenced by DuckDB below)
    con.execute("CREATE OR REPLACE TABLE links AS SELECT * FROM links_arrow")
    con.execute("CREATE OR REPLACE VIEW pairs AS SELECT * FROM links WHERE link_status <> 'no_candidate'")
