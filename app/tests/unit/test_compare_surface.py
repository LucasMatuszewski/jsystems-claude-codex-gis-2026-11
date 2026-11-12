"""ADR-001 §3.4: surface statuses follow rules 1-6 of §3.3 on classes."""
from map_qa.matching.compare import compare_surface


def rs(*vals, between=None):
    return [{"value": v, "between": between} for v in vals]


def test_ambiguous_first():
    assert compare_surface("ambiguous", "asphalt", "ov", rs("paved")).status == "ambiguous_link"


def test_missing_osm_before_missing_overture():
    assert compare_surface("ok", None, None, None).status == "missing_osm"


def test_missing_overture():
    r = compare_surface("ok", "asphalt", None, None)
    assert (r.status, r.reason) == ("missing_overture", "no_overture_candidate")
    assert compare_surface("ok", "asphalt", "ov", []).status == "missing_overture"


def test_agree_disagree_on_classes_not_strings():
    assert compare_surface("ok", "asphalt", "ov", rs("paving_stones")).status == "agree"
    r = compare_surface("ok", "asphalt", "ov", rs("gravel"))
    assert r.status == "disagree" and (r.osm_value, r.overture_value) == ("paved", "unpaved")


def test_not_comparable_cases():
    assert compare_surface("ok", "xyz", "ov", rs("paved")).reason == "osm:unknown_value"
    assert compare_surface("ok", "asphalt", "ov", rs("unknown")).reason == "overture:unknown_value"
    r = compare_surface("ok", "asphalt", "ov", rs("paved", between=[0, 0.3]))
    assert (r.status, r.reason) == ("not_comparable", "overture:partial_between")
    assert r.overture_rules[0]["raw"] == "paved"
