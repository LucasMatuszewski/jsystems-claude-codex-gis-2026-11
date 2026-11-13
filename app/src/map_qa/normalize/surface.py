"""Surface classes for OSM `surface` and Overture `road_surface` (ADR-001 §3.4). Raw values are kept."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from map_qa.core.enums import SurfaceClass

OSM_PAVED = {"asphalt", "concrete", "concrete:plates", "concrete:lanes", "paved", "paving_stones", "sett",
             "unhewn_cobblestone", "cobblestone", "bricks", "metal", "wood", "chipseal"}
OSM_UNPAVED = {"unpaved", "compacted", "fine_gravel", "gravel", "pebblestone", "ground", "dirt", "earth", "grass",
               "grass_paver", "mud", "sand", "rock", "woodchips"}
OVERTURE_PAVED = {"paved", "paving_stones", "metal"}
OVERTURE_UNPAVED = {"unpaved", "gravel", "dirt"}


@dataclass(frozen=True)
class SurfaceValue:
    source: str
    cls: SurfaceClass
    raw: str | None
    between: tuple[float, float] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"source": self.source, "class": str(self.cls), "raw": self.raw,
                "between": list(self.between) if self.between else None}


def _classify(raw: str, paved: set[str], unpaved: set[str]) -> SurfaceClass:
    key = raw.strip().lower()
    if key in paved:
        return SurfaceClass.PAVED
    if key in unpaved:
        return SurfaceClass.UNPAVED
    return SurfaceClass.UNKNOWN_VALUE


def osm_surface_value(raw: str | None) -> SurfaceValue:
    if raw is None or not str(raw).strip():
        return SurfaceValue("osm", SurfaceClass.MISSING, raw)
    return SurfaceValue("osm", _classify(str(raw), OSM_PAVED, OSM_UNPAVED), str(raw))


def overture_surface_values(road_surface: list[dict[str, Any]] | None) -> list[SurfaceValue]:
    out = []
    for el in road_surface or []:
        raw = el.get("value")
        btw = el.get("between")
        between = (float(btw[0]), float(btw[1])) if btw else None
        cls = SurfaceClass.UNKNOWN_VALUE if raw is None else _classify(str(raw), OVERTURE_PAVED, OVERTURE_UNPAVED)
        out.append(SurfaceValue("overture", cls, raw, between))
    return out


def comparable_surface(values: list[SurfaceValue]) -> tuple[str | None, str | None]:
    """One class for the whole segment, or (None, reason)."""
    if not values:
        return None, "no_values"
    if any(v.between is not None and not (v.between[0] <= 0 and v.between[1] >= 1) for v in values):
        return None, "partial_between"
    if any(v.cls == SurfaceClass.UNKNOWN_VALUE for v in values):
        return None, "unknown_value"
    classes = {str(v.cls) for v in values}
    if len(classes) > 1:
        return None, "multiple_values"
    return classes.pop(), None
