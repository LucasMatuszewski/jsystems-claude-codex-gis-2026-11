"""ADR-001 §3.3 / §8: OSM maxspeed* parsing, comparable value and limit type."""
import pytest

from map_qa.core.enums import SpeedKind
from map_qa.normalize.speed import comparable_value, limit_type, osm_rules


def one(rules):
    assert len(rules) == 1, rules
    return rules[0]


def test_numeric_both_directions():
    r = one(osm_rules({"maxspeed": "50"}).rules)
    assert (r.kind, r.value_kmh, r.direction, r.tag_key, r.raw, r.condition_raw) == (
        SpeedKind.NUMERIC, 50.0, "both", "maxspeed", "50", None)
    assert r.source == "osm" and r.unit_raw == "km/h"


def test_numeric_with_spaces():
    assert one(osm_rules({"maxspeed": " 50 "}).rules).value_kmh == 50.0


@pytest.mark.parametrize("raw", ["30 mph", "30mph"])
def test_mph_converted_and_unit_kept(raw):
    r = one(osm_rules({"maxspeed": raw}).rules)
    assert r.value_kmh == 48.28 and r.unit_raw == "mph" and r.raw == raw


@pytest.mark.parametrize("raw", ["PL:urban", "PL:zone30", "PL:rural", "PL:living_street"])
def test_implicit_has_no_value(raw):
    r = one(osm_rules({"maxspeed": raw}).rules)
    assert r.kind == SpeedKind.IMPLICIT and r.value_kmh is None


@pytest.mark.parametrize("raw,kind", [("none", SpeedKind.NONE), ("signals", SpeedKind.SIGNALS),
                                      ("walk", SpeedKind.WALK), ("fast-ish", SpeedKind.UNPARSEABLE)])
def test_special_values(raw, kind):
    r = one(osm_rules({"maxspeed": raw}).rules)
    assert r.kind == kind and r.value_kmh is None and r.raw == raw


def test_multiple_values_give_two_rules_and_no_comparable_value():
    p = osm_rules({"maxspeed": "50;70"})
    assert [r.value_kmh for r in p.rules] == [50.0, 70.0]
    assert {r.tag_key for r in p.rules} == {"maxspeed"}
    assert comparable_value(p.rules) == (None, "multiple_values")


def test_directional_different_not_comparable():
    p = osm_rules({"maxspeed:forward": "50", "maxspeed:backward": "70"})
    assert {(r.direction, r.value_kmh) for r in p.rules} == {("forward", 50.0), ("backward", 70.0)}
    assert comparable_value(p.rules) == (None, "directional_differs")


def test_directional_equal_is_comparable():
    p = osm_rules({"maxspeed:forward": "50", "maxspeed:backward": "50"})
    assert comparable_value(p.rules) == (50.0, None)


def test_single_direction_only_not_comparable():
    p = osm_rules({"maxspeed:forward": "50"})
    assert comparable_value(p.rules)[0] is None


def test_conditional_kept_and_comparable_from_unconditional():
    p = osm_rules({"maxspeed": "50", "maxspeed:conditional": "30 @ (Mo-Fr 07:00-17:00)"})
    cond = [r for r in p.rules if r.condition_raw]
    assert len(cond) == 1 and cond[0].value_kmh == 30.0 and cond[0].condition_raw == "Mo-Fr 07:00-17:00"
    assert cond[0].raw == "30 @ (Mo-Fr 07:00-17:00)" and cond[0].tag_key == "maxspeed:conditional"
    assert comparable_value(p.rules) == (50.0, None)


def test_several_conditions_split_on_semicolon():
    p = osm_rules({"maxspeed:conditional": "30 @ (Mo-Fr 07:00-17:00); 40 @ (Sa,Su)"})
    assert [(r.value_kmh, r.condition_raw) for r in p.rules] == [(30.0, "Mo-Fr 07:00-17:00"), (40.0, "Sa,Su")]
    assert comparable_value(p.rules) == (None, "only_conditional")


def test_none_vs_missing():
    assert one(osm_rules({"maxspeed": "none"}).rules).kind == SpeedKind.NONE
    p = osm_rules({"highway": "residential"})
    assert p.rules == [] and limit_type(p) is None
    assert comparable_value(p.rules) == (None, "no_rules")


def test_implicit_only_from_source_maxspeed():
    p = osm_rules({"source:maxspeed": "PL:urban"})
    assert p.rules == []
    assert p.context_tags == {"source:maxspeed": "PL:urban"}
    assert limit_type(p) == "implicit_only"


def test_multi_value_type_keeps_both_entries():
    p = osm_rules({"source:maxspeed": "PL:zone30;sign"})
    assert p.context_tags["source:maxspeed"] == "PL:zone30;sign"
    assert limit_type(p) == "implicit_only"


@pytest.mark.parametrize("tags,expected", [
    ({"maxspeed:type": "sign"}, "type_without_value"),
    ({"source:maxspeed": "survey"}, "type_without_value"),
    ({"source:maxspeed": "zone30"}, "implicit_only"),
    ({"maxspeed:source": "pl:zone30"}, "implicit_only"),
    ({"zone:maxspeed": "PL:30"}, "implicit_only"),
    ({"source:maxspeed:forward": "PL:urban"}, "implicit_only"),
    ({"source:maxspeed": "PL:urban", "maxspeed": "50"}, None),
    ({"source:maxspeed": "PL:urban", "maxspeed:hgv": "40"}, None),
])
def test_limit_type(tags, expected):
    assert limit_type(osm_rules(tags)) == expected


@pytest.mark.parametrize("key", ["maxspeed:type", "source:maxspeed", "zone:maxspeed", "maxspeed:variable",
                                 "maxspeed:source", "check_date:maxspeed", "source:maxspeed:forward"])
def test_context_keys_do_not_create_rules(key):
    p = osm_rules({key: "PL:urban" if "date" not in key else "2024-01-01"})
    assert p.rules == [] and key in p.context_tags


def test_vehicle_rules_are_conditional():
    p = osm_rules({"maxspeed": "50", "maxspeed:hgv": "40"})
    hgv = [r for r in p.rules if r.tag_key == "maxspeed:hgv"]
    assert hgv[0].value_kmh == 40.0 and hgv[0].condition_raw == "vehicle=hgv"
    assert comparable_value(p.rules) == (50.0, None)


def test_vehicle_with_direction():
    r = one(osm_rules({"maxspeed:bus:forward": "60"}).rules)
    assert r.condition_raw == "vehicle=bus" and r.direction == "forward"


def test_lanes_one_rule_per_lane():
    p = osm_rules({"maxspeed:lanes": "120|120|120|80"})
    assert [(r.value_kmh, r.condition_raw) for r in p.rules] == [
        (120.0, "lane=1"), (120.0, "lane=2"), (120.0, "lane=3"), (80.0, "lane=4")]
    assert comparable_value(p.rules) == (None, "only_conditional")


def test_lanes_do_not_affect_comparable_value():
    p = osm_rules({"maxspeed": "100", "maxspeed:lanes": "120|120|120|80"})
    assert comparable_value(p.rules) == (100.0, None)


def test_implicit_directional_value():
    r = one(osm_rules({"maxspeed:forward": "PL:urban"}).rules)
    assert r.kind == SpeedKind.IMPLICIT and r.direction == "forward"


def test_implicit_main_value_not_comparable():
    assert comparable_value(osm_rules({"maxspeed": "PL:urban"}).rules) == (None, "implicit")


def test_every_maxspeed_key_is_accounted_for():
    tags = {"maxspeed": "50", "maxspeed:forward": "50", "maxspeed:hgv": "40", "maxspeed:type": "sign",
            "maxspeed:conditional": "30 @ (22:00-06:00)", "source:maxspeed": "sign", "name": "x"}
    p = osm_rules(tags)
    seen = {r.tag_key for r in p.rules} | set(p.context_tags)
    assert seen == {k for k in tags if "maxspeed" in k}
