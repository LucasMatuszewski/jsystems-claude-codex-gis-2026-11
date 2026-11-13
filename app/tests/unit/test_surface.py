"""ADR-001 §3.4, §8 'Nawierzchnia'."""
import pytest

from map_qa.core.enums import SurfaceClass
from map_qa.normalize.surface import comparable_surface, osm_surface_value, overture_surface_values


@pytest.mark.parametrize("raw,cls", [("asphalt", "paved"), ("gravel", "unpaved"), ("grass_paver", "unpaved"),
                                     ("xyz", "unknown_value"), ("Asphalt", "paved"), ("paving_Stones", "paved"),
                                     ("concrete:plates", "paved"), ("sett", "paved"), ("ground", "unpaved"),
                                     ("utwardzona", "unknown_value")])
def test_osm_classes(raw, cls):
    v = osm_surface_value(raw)
    assert v.cls == cls and v.raw == raw and v.source == "osm"


def test_osm_missing():
    assert osm_surface_value(None).cls == SurfaceClass.MISSING
    assert osm_surface_value("  ").cls == SurfaceClass.MISSING


@pytest.mark.parametrize("raw,cls", [("paved", "paved"), ("paving_stones", "paved"), ("metal", "paved"),
                                     ("unpaved", "unpaved"), ("gravel", "unpaved"), ("dirt", "unpaved"),
                                     ("unknown", "unknown_value")])
def test_overture_classes(raw, cls):
    assert overture_surface_values([{"value": raw, "between": None}])[0].cls == cls


def test_overture_empty():
    assert overture_surface_values([]) == [] and overture_surface_values(None) == []


def test_comparable_single_whole():
    assert comparable_surface(overture_surface_values([{"value": "paved", "between": None}])) == ("paved", None)
    assert comparable_surface(overture_surface_values([{"value": "paved", "between": [0, 1]}])) == ("paved", None)


def test_partial_between_not_comparable():
    vals = overture_surface_values([{"value": "paved", "between": [0, 0.5]}, {"value": "gravel", "between": [0.5, 1]}])
    assert comparable_surface(vals) == (None, "partial_between")
    assert vals[0].between == (0.0, 0.5)


def test_unknown_value_not_comparable():
    assert comparable_surface(overture_surface_values([{"value": "unknown", "between": None}])) == (
        None, "unknown_value")
