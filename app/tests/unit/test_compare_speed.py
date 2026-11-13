"""ADR-001 §3.3 ordered status rules 1-6 for `speed` (PRD AC-06, AC-07, AC-08, AC-10)."""
import pytest

from map_qa.matching.compare import compare_speed


def el(value, when=None, between=None):
    return {"max_speed": {"value": value, "unit": "km/h"}, "min_speed": None, "is_max_speed_variable": None,
            "when": when, "between": between}


def status(link="ok", tags=None, overture_id="ov1", limits=None):
    return compare_speed(link, tags or {}, overture_id, limits)


def test_rule1_ambiguous_link_wins_over_everything():
    r = status(link="ambiguous", tags={"maxspeed": "50"}, limits=[el(50)])
    assert r.status == "ambiguous_link"


def test_rule2_missing_osm_even_without_overture():
    r = status(tags={}, overture_id=None, limits=None)
    assert r.status == "missing_osm"


def test_missing_tag_never_disagree_or_zero():
    r = status(tags={"highway": "residential"}, limits=[el(50)])
    assert r.status == "missing_osm" and r.osm_value is None


def test_rule3_no_overture_candidate():
    r = status(tags={"maxspeed": "50"}, overture_id=None)
    assert (r.status, r.reason) == ("missing_overture", "no_overture_candidate")


def test_rule3_overture_without_rules():
    r = status(tags={"maxspeed": "50"}, limits=[])
    assert (r.status, r.reason) == ("missing_overture", "no_overture_rules")


def test_rule4_implicit_only_not_comparable_not_missing():
    r = status(tags={"source:maxspeed": "PL:urban"}, limits=[el(50)])
    assert (r.status, r.reason) == ("not_comparable", "osm:implicit_only")


def test_rule4_type_without_value():
    r = status(tags={"maxspeed:type": "sign"}, limits=[el(50)])
    assert (r.status, r.reason) == ("not_comparable", "osm:type_without_value")


def test_rule4_conditional_only_overture():
    r = status(tags={"maxspeed": "50"}, limits=[el(30, when={"during": "Mo-Fr06:00-18:00"})])
    assert (r.status, r.reason) == ("not_comparable", "overture:only_conditional")
    assert len(r.overture_rules) == 1  # raw rule still shown (AC-07)


def test_rule4_partial_between():
    r = status(tags={"maxspeed": "50"}, limits=[el(50, between=[0, 0.4])])
    assert (r.status, r.reason) == ("not_comparable", "overture:partial_between")


def test_rule4_directional_osm():
    r = status(tags={"maxspeed:forward": "50", "maxspeed:backward": "70"}, limits=[el(50)])
    assert (r.status, r.reason) == ("not_comparable", "osm:directional_differs")


def test_rule5_agree_and_conditionals_do_not_block():
    r = status(tags={"maxspeed": "50", "maxspeed:hgv": "40", "maxspeed:conditional": "30 @ (22:00-06:00)"},
               limits=[el(50), el(40, when={"mode": ["hgv", "bus"]})])
    assert r.status == "agree" and r.osm_value == 50.0 and r.overture_value == 50.0
    assert len(r.osm_rules) == 3 and len(r.overture_rules) == 2  # all raw rules kept


def test_rule5_tolerance():
    assert status(tags={"maxspeed": "30 mph"}, limits=[el(48)]).status == "agree"  # 48.28 vs 48 -> |d|<0.5


def test_rule6_disagree():
    r = status(tags={"maxspeed": "50"}, limits=[el(70)])
    assert r.status == "disagree" and r.reason == "delta_kmh=20"


@pytest.mark.parametrize("tags", [{"maxspeed": "none"}, {"maxspeed": "PL:urban"}, {"maxspeed": "walk"}])
def test_non_numeric_osm_values_not_comparable(tags):
    assert status(tags=tags, limits=[el(50)]).status == "not_comparable"
