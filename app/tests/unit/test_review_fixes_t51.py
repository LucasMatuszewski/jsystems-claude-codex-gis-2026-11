"""Regression tests for the T51 second-review findings (Claude reviewer, 2026-11-12)."""
import io
import json

import pytest

from map_qa.core.errors import InputChanged
from map_qa.core.models import FileHash, InputManifest
from map_qa.photo_reading.budget import BudgetLedger
from map_qa.photo_reading.escalator import PhotoReading
from map_qa.photo_reading.map_compare import map_comparison
from map_qa.pipeline import verify_inputs_unchanged


def speed(answer, decision="answered_tier2"):
    return PhotoReading("s1", "sign_crop", "speed_limit_value", decision, answer=answer)


def test_speed_uses_normalized_comparable_value():
    # maxspeed "50 km/h" normalizes to 50 -> equal to prediction 50 (not a raw-string mismatch)
    rows = {"s1": {"maxspeed": "50 km/h", "osm_speed_value": 50.0, "osm_speed_reason": None,
                   "mapillary_value": "regulatory--maximum-speed-limit-50--g1"}}
    assert map_comparison([speed("50")], rows)[0].note == "OSM: zgodne; Mapillary: zgodne"


def test_speed_directional_only_is_not_comparable_not_missing():
    rows = {"s1": {"maxspeed_forward": "50", "maxspeed_backward": "70", "osm_speed_value": None,
                   "osm_speed_reason": "directional_differs"}}
    note = map_comparison([speed("50")], rows)[0].note
    assert note.startswith("OSM: nieporównywalne (directional_differs)")


def test_speed_without_any_rule_is_missing():
    rows = {"s1": {"osm_speed_value": None, "osm_speed_reason": "no_rules"}}
    assert map_comparison([speed("50")], rows)[0].note.startswith("OSM: brak wartości")


def test_ambiguous_link_is_not_compared():
    rows = {"p1": {"link_status": "ambiguous", "osm_surface_class": "paved", "overture_surface_class": "paved"}}
    r = map_comparison([PhotoReading("p1", "photo", "surface", "answered", answer="paved")], rows)[0]
    assert r.note == "nie porównano: niepewne połączenie (ambiguous_link)" and r.prediction == "paved"


def test_cost_above_reservation_stops_paid_loop(tmp_path):
    b = BudgetLedger(tmp_path / "l.jsonl", "r", max_requests=10, max_cost_usd=1.0)
    res = b.reserve("m", "tier1", 0.002)
    b.settle(res, status_code=200, cost_usd=0.01, outcome="ok")
    assert b.is_open and b.open_reason == "cost_above_reservation"


def test_deleted_input_is_detected(tmp_path):
    f = tmp_path / "a.csv"
    f.write_text("x", encoding="utf-8")
    man = InputManifest(source="files", files=[FileHash(name="a.csv", sha256="0" * 64, bytes=1)])
    f.unlink()
    with pytest.raises(InputChanged):
        verify_inputs_unchanged(man, tmp_path)
