"""ADR-002 §3–§8: pairs in EPSG:2180, link_status and flags on the real snapshot."""
import random
import statistics

import pytest
from pyproj import Transformer

from map_qa.matching.pairs import build_pairs
from map_qa.sources import connect
from map_qa.sources.files import FilesSource

RYNEK = (19.9372, 50.0617)


@pytest.fixture(scope="module")
def con(data_dir):
    c = connect(data_dir / "data")
    FilesSource(data_dir).load(c)
    build_pairs(c)
    yield c
    c.close()


def test_axis_order_matches_pyproj_always_xy(con):
    x, y = con.execute("SELECT ST_X(g), ST_Y(g) FROM (SELECT ST_Transform(ST_Point(?, ?), 'EPSG:4326', 'EPSG:2180',"
                       " always_xy := true) AS g)", list(RYNEK)).fetchone()
    ox, oy = Transformer.from_crs("EPSG:4326", "EPSG:2180", always_xy=True).transform(*RYNEK)
    assert abs(x - ox) < 0.01 and abs(y - oy) < 0.01
    # Guard: without always_xy DuckDB swaps axes and the point lands far outside Poland's 2180 extent.
    bx, by = con.execute("SELECT ST_X(g), ST_Y(g) FROM (SELECT ST_Transform(ST_Point(?, ?), 'EPSG:4326', 'EPSG:2180')"
                         " AS g)", list(RYNEK)).fetchone()
    assert not (abs(bx - ox) < 1 and abs(by - oy) < 1)


def test_known_100_m_distance(con):
    inv = Transformer.from_crs("EPSG:2180", "EPSG:4326", always_xy=True)
    a = inv.transform(567000.0, 244000.0)
    b = inv.transform(567100.0, 244000.0)
    d = con.execute("SELECT ST_Distance(ST_Transform(ST_Point(?, ?), 'EPSG:4326', 'EPSG:2180', always_xy := true),"
                    " ST_Transform(ST_Point(?, ?), 'EPSG:4326', 'EPSG:2180', always_xy := true))",
                    [*a, *b]).fetchone()[0]
    assert d == pytest.approx(100.0, abs=0.01)


def test_spot_check_three_random_pairs(con):
    rows = con.execute("SELECT photo_id, distance_m, distance_m_recomputed FROM pairs ORDER BY photo_id").fetchall()
    for pid, given, recomputed in random.Random(42).sample(rows, 3):
        assert abs(recomputed - given) <= 0.5, pid  # AC-09


def test_median_delta_small(con):
    deltas = [abs(a - b) for a, b in con.execute("SELECT distance_m, distance_m_recomputed FROM pairs").fetchall()]
    assert statistics.median(deltas) < 0.05  # TAC-002-03


def test_link_statuses(con):
    counts = dict(con.execute("SELECT link_status, count(*) FROM links GROUP BY 1").fetchall())
    assert counts["no_candidate"] == 3
    assert sum(counts.values()) == 561
    assert set(r[0] for r in con.execute("SELECT DISTINCT link_status FROM pairs").fetchall()) <= {"ok", "ambiguous"}
    assert con.execute("SELECT count(*) FROM pairs").fetchone()[0] == 558


def test_ambiguous_candidates_are_ambiguous(con):
    bad = con.execute("SELECT count(*) FROM pairs WHERE list_contains(candidate_flags, 'ambiguous_candidates')"
                      " AND link_status <> 'ambiguous'").fetchone()[0]
    assert bad == 0
    n = con.execute("SELECT count(*) FROM pairs WHERE list_contains(reasons, 'ambiguous_candidates')").fetchone()[0]
    assert n == 65


def test_poor_heading_alignment_is_informational(con):
    rows = con.execute("SELECT link_status, flags, reasons FROM pairs"
                       " WHERE list_contains(candidate_flags, 'poor_heading_alignment')").fetchall()
    assert len(rows) == 27
    for status, flags, reasons in rows:
        assert "poor_heading_alignment" in flags
        assert "poor_heading_alignment" not in reasons


def test_suspect_position_flag(con):
    n = con.execute("SELECT count(*) FROM links WHERE list_contains(flags, 'suspect_position')").fetchone()[0]
    assert n == 3


def test_service_and_spatial_fallback_flags(con):
    svc = con.execute("SELECT count(*) FROM pairs WHERE list_contains(candidate_flags, 'service_way')"
                      " AND NOT list_contains(flags, 'service_or_restricted')").fetchone()[0]
    assert svc == 0
    fb = con.execute("SELECT link_status, flags FROM pairs"
                     " WHERE list_contains(candidate_flags, 'overture_spatial_only')").fetchall()
    assert len(fb) == 1 and "overture_spatial_fallback" in fb[0][1]


def test_panorama_without_heading_is_ambiguous(con):
    rows = con.execute("SELECT link_status, reasons FROM pairs WHERE heading IS NULL AND"
                       " (list_contains(candidate_flags, 'panorama_heading_ambiguous') OR is_panorama)").fetchall()
    for status, reasons in rows:
        assert status == "ambiguous" and "panorama_without_heading" in reasons


def test_heading_zero_is_not_missing(con):
    n = con.execute("SELECT count(*) FROM links WHERE heading = 0.0").fetchone()[0]
    assert n == 23
