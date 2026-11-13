"""Reading-vs-map comparison table (ADR-003 §5.9 'Porównanie z mapą po odczycie'; PRD §4.2 step 9, §7, §11).

Pure function: puts each photo-reading prediction next to the raw map values. It states agreement or
disagreement per source and never gives a verdict. Missing map tags are 'brak wartości', never 0 or
'none'. Unknown and abstained readings are reported with their decision and never compared as values.
"""
from __future__ import annotations

import re

from map_qa.core.models import MapCompareRow
from map_qa.photo_reading.escalator import PhotoReading

ANSWERED_DECISIONS = {"answered", "answered_tier2"}
MISSING_CLASSES = {None, "missing"}
NOT_COMPARABLE_CLASSES = {"unknown_value", "not_comparable"}
LIGHTING_MATCH = {"yes": {"yes", "yes_conditional"}, "no": {"no"}}
MAPILLARY_SPEED = re.compile(r"maximum-speed-limit-(\d+)")
DASH = "–"
MISSING = "brak wartości"


def _show(value) -> str:
    if value is None or str(value).strip() == "":
        return DASH
    return str(value)


def _prediction(reading: PhotoReading) -> str | None:
    if reading.decision in ANSWERED_DECISIONS and reading.answer not in (None, "unknown"):
        return reading.answer
    return None


def _agreement(prediction: str, map_class) -> str:
    if map_class in MISSING_CLASSES:
        return MISSING
    if map_class in NOT_COMPARABLE_CLASSES:
        return f"nieporównywalne ({map_class})"  # AC-08: not the same as a missing value
    return "zgodne" if prediction == map_class else "różne"


def _mapillary_number(row: dict) -> str | None:
    mapillary = row.get("mapillary_value")
    match = MAPILLARY_SPEED.search(mapillary) if mapillary else None
    return match.group(1) if match else None


# ---------------------------------------------------------------- raw map values (always shown)
def _surface_values(row: dict) -> str:
    return (
        f"OSM surface={_show(row.get('osm_surface_raw'))} ({_show(row.get('osm_surface_class'))}); "
        f"Overture={_show(row.get('overture_surface_raw'))} ({_show(row.get('overture_surface_class'))})"
    )


def _lighting_values(row: dict) -> str:
    return f"OSM lit={_show(row.get('osm_lit_raw'))} ({_show(row.get('osm_lit_class'))})"


def _speed_values(row: dict) -> str:
    return (
        f"OSM maxspeed={_show(row.get('maxspeed'))}; "
        f"maxspeed:forward={_show(row.get('maxspeed_forward'))}; "
        f"maxspeed:backward={_show(row.get('maxspeed_backward'))}; "
        f"maxspeed:conditional={_show(row.get('maxspeed_conditional'))}; "
        f"Mapillary={_show(_mapillary_number(row))}"
    )


# ---------------------------------------------------------------- notes (only for answered readings)
def _surface_note(prediction: str, row: dict) -> str:
    osm = _agreement(prediction, row.get("osm_surface_class"))
    overture = _agreement(prediction, row.get("overture_surface_class"))
    return f"OSM: {osm}; Overture: {overture}"


def _lighting_note(prediction: str, row: dict) -> str:
    lit_class = row.get("osm_lit_class")
    if lit_class in MISSING_CLASSES:
        return f"OSM: {MISSING}"
    if lit_class in NOT_COMPARABLE_CLASSES:
        return f"OSM: nieporównywalne ({lit_class})"
    matches = lit_class in LIGHTING_MATCH.get(prediction, set())
    return f"OSM: {'zgodne' if matches else 'różne'}"


def _speed_note(prediction: str, row: dict) -> str:
    if prediction == "none":
        return "odczyt: brak znaku B-33 w wycinku"
    if prediction == "unreadable":
        return "odczyt: wartość nieczytelna"
    value = prediction.strip()
    if "osm_speed_value" in row:  # normalized comparable value (ADR-001 §3.3), computed by the pipeline
        osm_value, reason = row.get("osm_speed_value"), row.get("osm_speed_reason")
        if osm_value is not None:
            same = value.isdigit() and abs(float(value) - float(osm_value)) < 0.5
            osm_part = f"OSM: {'zgodne' if same else 'różne'}"
        elif reason in (None, "no_rules"):
            osm_part = f"OSM: {MISSING}"
        else:
            osm_part = f"OSM: nieporównywalne ({reason})"
    else:
        osm = (row.get("maxspeed") or "").strip()
        if not osm:
            osm_part = f"OSM maxspeed: {MISSING}"
        else:
            osm_part = f"OSM maxspeed: {'zgodne' if osm == value else 'różne'}"
    mapillary = _mapillary_number(row)
    if mapillary is None:
        map_part = f"Mapillary: {MISSING}"
    else:
        map_part = f"Mapillary: {'zgodne' if mapillary == value else 'różne'}"
    return f"{osm_part}; {map_part}"


_COMPARISONS = {
    "surface": (_surface_values, _surface_note),
    "street_lighting_visible": (_lighting_values, _lighting_note),
    "speed_limit_value": (_speed_values, _speed_note),
}


def map_comparison(readings: list[PhotoReading], map_rows: dict[str, dict]) -> list[MapCompareRow]:
    """One row per reading whose question has a map comparison, in input order.

    `junction_visible` (and any other question without a map comparison) produces no row.
    """
    out: list[MapCompareRow] = []
    for reading in readings:
        comparison = _COMPARISONS.get(reading.question_id)
        if comparison is None:
            continue
        values_of, note_of = comparison
        row = map_rows.get(reading.photo_id) or {}
        prediction = _prediction(reading)
        if prediction is None:
            note = f"nie porównano: brak odpowiedzi modelu ({reading.decision})"
        elif row.get("link_status") == "ambiguous":
            note = "nie porównano: niepewne połączenie (ambiguous_link)"  # AC-10, ADR-002 D-22
        else:
            note = note_of(prediction, row)
        out.append(
            MapCompareRow(
                photo_id=reading.photo_id,
                question=reading.question_id,
                prediction=prediction,
                decision=reading.decision,
                map_values=values_of(row),
                note=note,
            )
        )
    return out
