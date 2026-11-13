"""ADR-003 §5.9 'Porównanie z mapą po odczycie'; PRD §4.2 step 9, §7, §11, AC-08.

Comparison table only: prediction next to raw map values, never a verdict. Missing map tags are
'brak wartości', never 0 or 'none'. Unknown / abstain readings are never compared as values.
"""
from map_qa.core.models import MapCompareRow
from map_qa.photo_reading.escalator import PhotoReading
from map_qa.photo_reading.map_compare import map_comparison


def street_row(**overrides):
    row = {
        "osm_surface_raw": "asphalt",
        "osm_surface_class": "paved",
        "overture_surface_raw": "paved",
        "overture_surface_class": "paved",
        "osm_lit_raw": "yes",
        "osm_lit_class": "yes",
    }
    row.update(overrides)
    return row


def sign_row(**overrides):
    row = {
        "maxspeed": "20",
        "maxspeed_forward": None,
        "maxspeed_backward": None,
        "maxspeed_conditional": None,
        "mapillary_value": "regulatory--maximum-speed-limit-20--g1",
    }
    row.update(overrides)
    return row


def one(reading, row):
    rows = map_comparison([reading], {reading.photo_id: row})
    assert len(rows) == 1
    return rows[0]


def surface(answer="paved", decision="answered", photo_id="p1"):
    return PhotoReading(photo_id, "photo", "surface", decision, answer=answer)


def lighting(answer="yes", decision="answered", photo_id="p1"):
    return PhotoReading(photo_id, "photo", "street_lighting_visible", decision, answer=answer)


def speed(answer="20", decision="answered_tier2", photo_id="s1"):
    return PhotoReading(photo_id, "sign_crop", "speed_limit_value", decision, answer=answer)


# ---------------------------------------------------------------- real T43 readings
def test_real_street_photo_readings_produce_rows_except_junction():
    readings = [
        PhotoReading("p1", "photo", "surface", "answered", answer="paved"),
        PhotoReading("p1", "photo", "junction_visible", "answered", answer="no"),
        PhotoReading("p1", "photo", "street_lighting_visible", "answered", answer="no"),
    ]
    rows = map_comparison(readings, {"p1": street_row(osm_lit_raw="no", osm_lit_class="no")})
    assert [r.question for r in rows] == ["surface", "street_lighting_visible"]
    assert all(isinstance(r, MapCompareRow) for r in rows)
    assert rows[0].prediction == "paved"
    assert rows[1].prediction == "no"
    assert rows[1].map_values == "OSM lit=no (no)"


def test_real_sign_crop_reading_answered_tier2_is_compared():
    row = one(speed("20", "answered_tier2"), sign_row())
    assert row.photo_id == "s1"
    assert row.question == "speed_limit_value"
    assert row.prediction == "20"
    assert row.decision == "answered_tier2"
    assert row.note == "OSM maxspeed: zgodne; Mapillary: zgodne"


# ---------------------------------------------------------------- junction produces no row
def test_junction_visible_produces_no_row():
    r = PhotoReading("p1", "photo", "junction_visible", "answered", answer="yes")
    assert map_comparison([r], {"p1": street_row()}) == []


# ---------------------------------------------------------------- prediction rule
def test_prediction_is_answer_for_answered_and_answered_tier2():
    assert one(surface("paved", "answered"), street_row()).prediction == "paved"
    assert one(surface("paved", "answered_tier2"), street_row()).prediction == "paved"


def test_prediction_is_none_for_unknown_answer_even_when_answered():
    row = one(surface("unknown", "answered"), street_row())
    assert row.prediction is None
    assert row.note == "nie porównano: brak odpowiedzi modelu (answered)"


def test_prediction_is_none_for_non_answer_decisions_and_note_uses_decision():
    for decision in ["abstain", "model_unavailable", "not_run_budget_or_error"]:
        row = one(surface(None, decision), street_row())
        assert row.prediction is None
        assert row.decision == decision
        assert row.note == f"nie porównano: brak odpowiedzi modelu ({decision})"


def test_non_answer_decision_is_not_compared_even_if_answer_present():
    row = one(surface("paved", "abstain"), street_row())
    assert row.prediction is None
    assert row.note == "nie porównano: brak odpowiedzi modelu (abstain)"


# ---------------------------------------------------------------- surface
def test_surface_map_values_show_raw_and_class():
    row = one(surface("paved"), street_row())
    assert row.map_values == "OSM surface=asphalt (paved); Overture=paved (paved)"


def test_surface_note_compares_each_source_separately():
    row = one(surface("paved"), street_row(overture_surface_raw="gravel", overture_surface_class="unpaved"))
    assert row.note == "OSM: zgodne; Overture: różne"


def test_surface_note_both_different():
    row = one(surface("unpaved"), street_row())
    assert row.note == "OSM: różne; Overture: różne"


def test_surface_missing_vs_not_comparable_are_distinct():
    """AC-08 / user story 2: a missing value and an unrecognised/non-reducible value are reported differently
    (changed after the T51 review; the earlier expectation merged both into 'brak wartości')."""
    expected = {("unknown_value", "paved"): "OSM: nieporównywalne (unknown_value); Overture: zgodne",
                ("missing", "paved"): "OSM: brak wartości; Overture: zgodne",
                ("paved", None): "OSM: zgodne; Overture: brak wartości",
                ("paved", "not_comparable"): "OSM: zgodne; Overture: nieporównywalne (not_comparable)"}
    for (osm_class, ov_class), note in expected.items():
        row = one(surface("paved"), street_row(osm_surface_class=osm_class, overture_surface_class=ov_class))
        assert row.note == note


def test_surface_missing_keys_are_brak_wartosci_and_map_values_dash():
    row = one(surface("paved"), {})
    assert row.note == "OSM: brak wartości; Overture: brak wartości"
    assert row.map_values == "OSM surface=– (–); Overture=– (–)"


def test_missing_map_row_for_photo_is_treated_as_missing_not_zero():
    rows = map_comparison([surface("paved")], {})
    assert rows[0].note == "OSM: brak wartości; Overture: brak wartości"


# ---------------------------------------------------------------- street lighting
def test_lighting_yes_matches_yes_and_yes_conditional():
    assert one(lighting("yes"), street_row(osm_lit_raw="yes", osm_lit_class="yes")).note == "OSM: zgodne"
    row = one(lighting("yes"), street_row(osm_lit_raw="yes_conditional", osm_lit_class="yes_conditional"))
    assert row.note == "OSM: zgodne"
    assert row.map_values == "OSM lit=yes_conditional (yes_conditional)"


def test_lighting_no_matches_no_and_mismatch_is_roznie():
    assert one(lighting("no"), street_row(osm_lit_raw="no", osm_lit_class="no")).note == "OSM: zgodne"
    assert one(lighting("no"), street_row(osm_lit_raw="yes", osm_lit_class="yes")).note == "OSM: różne"
    assert one(lighting("yes"), street_row(osm_lit_raw="no", osm_lit_class="no")).note == "OSM: różne"


def test_lighting_missing_vs_unknown_value():
    """AC-08: missing `lit` and an unrecognised value (e.g. `disused`) are distinct (T51 review)."""
    for cls in ["missing", None]:
        row = one(lighting("yes"), street_row(osm_lit_raw=None, osm_lit_class=cls))
        assert row.note == "OSM: brak wartości"
    row = one(lighting("yes"), street_row(osm_lit_raw="disused", osm_lit_class="unknown_value"))
    assert row.note == "OSM: nieporównywalne (unknown_value)"


def test_lighting_missing_key_is_not_treated_as_no():
    row = one(lighting("no"), {})
    assert row.note == "OSM: brak wartości"
    assert row.map_values == "OSM lit=– (–)"


# ---------------------------------------------------------------- speed limit
def test_speed_none_and_unreadable_notes():
    assert one(speed("none"), sign_row()).note == "odczyt: brak znaku B-33 w wycinku"
    assert one(speed("unreadable"), sign_row()).note == "odczyt: wartość nieczytelna"


def test_speed_none_and_unreadable_have_prediction_none_for_numeric_only_compare():
    # 'none' and 'unreadable' are readings, not numeric values: they are reported as such
    row = one(speed("none"), sign_row())
    assert row.prediction == "none"


def test_speed_numeric_compares_osm_and_mapillary():
    assert one(speed("20"), sign_row()).note == "OSM maxspeed: zgodne; Mapillary: zgodne"
    assert one(speed("30"), sign_row()).note == "OSM maxspeed: różne; Mapillary: różne"


def test_speed_osm_and_mapillary_compared_independently():
    row = one(speed("20"), sign_row(maxspeed="50", mapillary_value="regulatory--maximum-speed-limit-20--g1"))
    assert row.note == "OSM maxspeed: różne; Mapillary: zgodne"


def test_speed_osm_maxspeed_exact_string_after_strip():
    assert one(speed("20"), sign_row(maxspeed=" 20 ")).note == "OSM maxspeed: zgodne; Mapillary: zgodne"
    # exact equality: '50' is not '50 mph' or '50;60'
    assert one(speed("50"), sign_row(maxspeed="50 mph")).note == "OSM maxspeed: różne; Mapillary: różne"


def test_speed_missing_osm_maxspeed_is_brak_wartosci_not_zero():
    row = one(speed("20"), sign_row(maxspeed=None, mapillary_value="regulatory--maximum-speed-limit-20--g1"))
    assert row.note == "OSM maxspeed: brak wartości; Mapillary: zgodne"


def test_speed_missing_mapillary_is_brak_wartosci():
    row = one(speed("20"), sign_row(mapillary_value=None))
    assert row.note == "OSM maxspeed: zgodne; Mapillary: brak wartości"


def test_speed_mapillary_without_number_is_brak_wartosci():
    row = one(speed("20"), sign_row(mapillary_value="regulatory--no-parking--g1"))
    assert row.note == "OSM maxspeed: zgodne; Mapillary: brak wartości"


def test_speed_map_values_show_raw_tags_with_dash_for_missing():
    row = one(speed("20"), sign_row(maxspeed="50", maxspeed_conditional="30 @ (Mo-Fr 07:00-09:00)"))
    assert row.map_values == (
        "OSM maxspeed=50; maxspeed:forward=–; maxspeed:backward=–; "
        "maxspeed:conditional=30 @ (Mo-Fr 07:00-09:00); Mapillary=20"
    )


def test_speed_map_values_mapillary_missing_shows_dash():
    row = one(speed("20"), sign_row(mapillary_value=None))
    assert row.map_values.endswith("Mapillary=–")


def test_speed_abstain_is_not_compared():
    row = one(speed(None, "abstain"), sign_row())
    assert row.prediction is None
    assert row.note == "nie porównano: brak odpowiedzi modelu (abstain)"


# ---------------------------------------------------------------- ordering and shape
def test_output_order_matches_input_order_across_photos():
    readings = [
        surface("paved", photo_id="p2"),
        speed("20", photo_id="s1"),
        lighting("no", photo_id="p1"),
    ]
    rows = map_comparison(
        readings,
        {"p1": street_row(), "p2": street_row(), "s1": sign_row()},
    )
    assert [(r.photo_id, r.question) for r in rows] == [
        ("p2", "surface"),
        ("s1", "speed_limit_value"),
        ("p1", "street_lighting_visible"),
    ]


def test_row_carries_decision_and_question_fields():
    row = one(surface("paved", "answered_tier2"), street_row())
    assert row.decision == "answered_tier2"
    assert row.question == "surface"
    assert row.photo_id == "p1"
