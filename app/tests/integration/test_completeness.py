"""ADR-001 §3.5, §8 'Kompletność'; PRD AC-11 (explicit denominators); cross-check with profile.md §8-9."""
import pytest

from map_qa.matching.pairs import build_pairs
from map_qa.normalize.completeness import compute_completeness
from map_qa.sources import connect
from map_qa.sources.files import FilesSource


@pytest.fixture(scope="module")
def rows(data_dir):
    con = connect(data_dir / "data")
    manifest = FilesSource(data_dir).load(con)
    build_pairs(con)
    out = compute_completeness(con)
    linked = con.execute("SELECT count(DISTINCT osm_way_id), count(DISTINCT overture_id) FROM pairs").fetchone()
    con.close()
    return {(r.source, r.attribute, r.population): r for r in out}, manifest, linked


def test_all_attributes_and_populations_present(rows):
    by, _, _ = rows
    osm_attrs = {"maxspeed*", "surface", "lit", "lanes", "sidewalk*"}
    assert {a for (s, a, p) in by if s == "osm"} == osm_attrs
    assert {a for (s, a, p) in by if s == "overture"} == {"speed_limits", "road_surface"}
    assert {p for (_, _, p) in by} == {"all", "linked"}


def test_denominators(rows):
    by, manifest, (linked_osm, linked_ov) = rows
    for (source, attr, pop), r in by.items():
        if pop == "all":
            expected = manifest.table("osm_roads" if source == "osm" else "overture_segments").rows
        else:
            expected = linked_osm if source == "osm" else linked_ov
            assert r.total <= 561
        assert r.total == expected
        assert 0 <= r.with_value <= r.total
        assert r.pct == pytest.approx(100.0 * r.with_value / r.total)


def test_values_match_profile(rows):
    by, _, _ = rows
    assert by[("overture", "speed_limits", "all")].with_value == 12847  # profile §8.3
    assert by[("osm", "lit", "all")].with_value == 14534 + 1014 + 27 + 13 + 1  # every non-null lit value
    assert by[("osm", "surface", "all")].with_value == 99768 - 60202  # profile: 60 202 NULL surface
