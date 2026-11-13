"""ADR-002 §3.3 and §8: angle differences and ranking tie-break (characterization of sources.json rule)."""
import pytest

from map_qa.matching.pairs import angle_diff, link_rank, pick_candidate, undirected_diff


@pytest.mark.parametrize("a,b,expected", [(359, 1, 2), (1, 359, 2), (0, 180, 180), (90, 270, 180), (0.0, 0.0, 0)])
def test_directed_angle_diff(a, b, expected):
    assert angle_diff(a, b) == pytest.approx(expected)


@pytest.mark.parametrize("a,b,expected", [(359, 1, 2), (0, 180, 0), (90, 270, 0), (10, 100, 90), (10, 120, 70)])
def test_undirected_angle_diff(a, b, expected):
    assert undirected_diff(a, b) == pytest.approx(expected)


def test_missing_heading_is_none_and_zero_is_north():
    assert angle_diff(10, None) is None and undirected_diff(None, 10) is None
    assert angle_diff(0.0, 0.0) == 0  # heading 0.0 is north, not missing


def test_reversed_geometry_keeps_bearing_diff():
    heading, way = 37.0, 120.0
    assert undirected_diff(heading, way) == pytest.approx(undirected_diff(heading, (way + 180) % 360))
    assert angle_diff(heading, way) != pytest.approx(angle_diff(heading, (way + 180) % 360))


def test_rank_rule():
    assert link_rank(4.0, 9.0) == pytest.approx(5.0)
    assert link_rank(4.0, None) == pytest.approx(9.0)  # missing heading adds 5 m


def test_tie_break_distance_then_osm_id():
    cands = [{"osm_id": 7, "distance_m": 3.0, "bearing_diff": 9.0},   # rank 4
             {"osm_id": 5, "distance_m": 2.0, "bearing_diff": 18.0},  # rank 4, smaller distance
             {"osm_id": 3, "distance_m": 2.0, "bearing_diff": 18.0}]  # rank 4, same distance, smaller id
    chosen, ambiguous = pick_candidate(cands)
    assert chosen["osm_id"] == 3 and ambiguous is True


def test_alternative_outside_two_metres_not_ambiguous():
    chosen, ambiguous = pick_candidate([{"osm_id": 1, "distance_m": 1.0, "bearing_diff": 0.0},
                                        {"osm_id": 2, "distance_m": 4.0, "bearing_diff": 0.0}])
    assert chosen["osm_id"] == 1 and ambiguous is False
