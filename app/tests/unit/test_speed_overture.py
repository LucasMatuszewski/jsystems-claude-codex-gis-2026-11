"""ADR-001 §3.3 / §8: Overture speed_limits parsing."""
import json

from map_qa.core.enums import SpeedKind
from map_qa.normalize.speed import comparable_value, overture_rules


def el(value=50, unit="km/h", when=None, between=None, variable=None, min_speed=None):
    return {"min_speed": min_speed, "max_speed": None if value is None else {"value": value, "unit": unit},
            "is_max_speed_variable": variable, "when": when, "between": between}


def test_simple_rule():
    rules = overture_rules([el()])
    assert len(rules) == 1
    r = rules[0]
    assert (r.source, r.kind, r.value_kmh, r.direction, r.condition_raw, r.between) == (
        "overture", SpeedKind.NUMERIC, 50.0, "both", None, None)
    assert json.loads(r.raw)["max_speed"] == {"value": 50, "unit": "km/h"}
    assert comparable_value(rules) == (50.0, None)


def test_empty_or_null_means_no_rules():
    assert overture_rules([]) == [] and overture_rules(None) == []


def test_heading_and_partial_between():
    rules = overture_rules([el(when={"heading": "forward", "during": None, "using": None, "recognized": None,
                                      "mode": None, "vehicle": None}, between=[0, 0.4])])
    r = rules[0]
    assert r.direction == "forward" and r.between == (0.0, 0.4) and r.condition_raw is None
    assert comparable_value(rules)[0] is None


def test_between_full_segment_is_whole():
    rules = overture_rules([el(between=[0, 1])])
    assert comparable_value(rules) == (50.0, None)


def test_mode_is_condition_sorted_json():
    rules = overture_rules([el(value=50), el(value=40, when={"mode": ["hgv", "bus"], "heading": None})])
    cond = [r for r in rules if r.condition_raw]
    assert json.loads(cond[0].condition_raw) == {"mode": ["hgv", "bus"]}
    assert comparable_value(rules) == (50.0, None)


def test_during_condition():
    r = overture_rules([el(when={"during": "Mo-Fr06:00-18:00"})])[0]
    assert json.loads(r.condition_raw) == {"during": "Mo-Fr06:00-18:00"}


def test_variable_gives_variable_rule():
    rules = overture_rules([el(variable=True)])
    kinds = sorted(r.kind for r in rules)
    assert SpeedKind.VARIABLE in kinds
    assert comparable_value(rules)[0] is None


def test_mph_conversion():
    assert overture_rules([el(value=30, unit="mph")])[0].value_kmh == 48.28


def test_min_speed_only_is_not_lost():
    rules = overture_rules([el(value=None, min_speed={"value": 30, "unit": "km/h"})])
    assert len(rules) >= 1 and rules[0].kind == SpeedKind.UNPARSEABLE


def test_directional_equal_values_comparable():
    rules = overture_rules([el(value=50, when={"heading": "forward"}), el(value=50, when={"heading": "backward"})])
    assert comparable_value(rules) == (50.0, None)
