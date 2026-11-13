"""Speed-limit normalization for OSM maxspeed* tags and Overture speed_limits (ADR-001 §3.3).

Pure functions on dicts; no I/O. Every rule keeps its raw value (D-13).
"""
from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from typing import Any

from map_qa.core.enums import SpeedKind

MPH = 1.609344
KNOT = 1.852
DIRECTIONS = {"forward", "backward"}
VEHICLES = {"hgv", "bus", "trailer", "goods", "motorcar", "motorcycle", "coach", "caravan", "psv",
            "agricultural", "moped", "bicycle", "vehicle", "motor_vehicle", "hazmat", "tourist_bus"}
# maxspeed*-containing keys that never create a rule (ADR-001 §3.3 table): context only.
TYPE_KEYS = ("maxspeed:type", "source:maxspeed", "maxspeed:source", "zone:maxspeed")
CONTEXT_PREFIXES = TYPE_KEYS + ("maxspeed:variable", "check_date:maxspeed", "source:maxspeed:", "note:maxspeed")
_NUM = re.compile(r"^(\d+(?:[.,]\d+)?)\s*(mph|km/h|kmh|kph|knots)?$", re.IGNORECASE)
_IMPLICIT = re.compile(r"^[A-Za-z]{2}:\S+$")
_COND = re.compile(r"^\s*(?P<value>[^@]+?)\s*@\s*\((?P<cond>.*)\)\s*$")


@dataclass(frozen=True)
class SpeedRule:
    source: str
    kind: SpeedKind
    value_kmh: float | None
    unit_raw: str | None
    direction: str
    condition_raw: str | None
    between: tuple[float, float] | None
    raw: str
    tag_key: str | None = None

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["kind"] = str(self.kind)
        d["between"] = list(self.between) if self.between else None
        return d


@dataclass
class OsmSpeed:
    rules: list[SpeedRule] = field(default_factory=list)
    context_tags: dict[str, str] = field(default_factory=dict)


def _is_context_key(key: str) -> bool:
    if key in TYPE_KEYS or key == "maxspeed:variable" or key == "check_date:maxspeed":
        return True
    if any(key.startswith(p + ":") for p in TYPE_KEYS):  # e.g. source:maxspeed:forward
        return True
    return key.startswith("source:maxspeed") or key.startswith("check_date:maxspeed") or key.startswith(
        "note:maxspeed") or key.startswith("maxspeed:variable")


def _parse_value(text: str) -> tuple[SpeedKind, float | None, str | None]:
    v = text.strip()
    m = _NUM.match(v)
    if m:
        num = float(m.group(1).replace(",", "."))
        unit = (m.group(2) or "km/h").lower()
        if unit == "mph":
            return SpeedKind.NUMERIC, round(num * MPH, 2), "mph"
        if unit == "knots":
            return SpeedKind.NUMERIC, round(num * KNOT, 2), "knots"
        return SpeedKind.NUMERIC, num, "km/h"
    low = v.lower()
    if low == "none":
        return SpeedKind.NONE, None, None
    if low == "signals":
        return SpeedKind.SIGNALS, None, None
    if low == "walk":
        return SpeedKind.WALK, None, None
    if low == "variable":
        return SpeedKind.VARIABLE, None, None
    if _IMPLICIT.match(v):
        return SpeedKind.IMPLICIT, None, None
    return SpeedKind.UNPARSEABLE, None, None


def _split_top_level(text: str, sep: str = ";") -> list[str]:
    """Split on sep outside parentheses."""
    parts, depth, cur = [], 0, []
    for ch in text:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        if ch == sep and depth == 0:
            parts.append("".join(cur))
            cur = []
        else:
            cur.append(ch)
    parts.append("".join(cur))
    return [p for p in (s.strip() for s in parts) if p]


def osm_rules(tags: dict[str, Any] | None) -> OsmSpeed:
    """All rules from keys `maxspeed` / `maxspeed:*`; context keys go to context_tags."""
    out = OsmSpeed()
    for key in sorted((tags or {}).keys()):
        if "maxspeed" not in key:
            continue
        raw_val = tags[key]
        if raw_val is None:
            continue
        raw = str(raw_val)
        if _is_context_key(key) or not (key == "maxspeed" or key.startswith("maxspeed:")):
            out.context_tags[key] = raw
            continue
        parts = key.split(":")[1:]
        direction = "both"
        conditional = lanes = False
        qualifiers: list[str] = []
        for p in parts:
            if p in DIRECTIONS:
                direction = p
            elif p == "conditional":
                conditional = True
            elif p == "lanes":
                lanes = True
            elif p == "both_ways":
                direction = "both"
            else:
                qualifiers.append(f"vehicle={p}" if p in VEHICLES else f"qualifier={p}")
        base_cond = ";".join(qualifiers) or None

        def add(text: str, cond: str | None, raw_text: str) -> None:
            kind, val, unit = _parse_value(text)
            out.rules.append(SpeedRule("osm", kind, val, unit if kind == SpeedKind.NUMERIC else None,
                                       direction, cond, None, raw_text, key))

        if conditional:
            for chunk in _split_top_level(raw):
                m = _COND.match(chunk)
                if m:
                    cond = m.group("cond").strip()
                    add(m.group("value"), ";".join(x for x in (base_cond, cond) if x), chunk)
                else:
                    out.rules.append(SpeedRule("osm", SpeedKind.UNPARSEABLE, None, None, direction,
                                               base_cond or "unparsed_condition", None, chunk, key))
        elif lanes:
            for i, lane_val in enumerate(raw.split("|"), start=1):
                cond = ";".join(x for x in (base_cond, f"lane={i}") if x)
                add(lane_val, cond, raw)
        else:
            for chunk in [c for c in raw.split(";") if c.strip()] or [raw]:
                add(chunk, base_cond, raw if ";" not in raw else chunk.strip())
    return out


def limit_type(parsed: OsmSpeed) -> str | None:
    """`implicit_only` / `type_without_value` when no numeric rule but a type key has a value (§3.3)."""
    if any(r.kind == SpeedKind.NUMERIC for r in parsed.rules):
        return None
    values: list[str] = []
    for key, val in parsed.context_tags.items():
        if any(key == t or key.startswith(t + ":") for t in TYPE_KEYS) and str(val).strip():
            values.extend(v.strip().lower() for v in str(val).split(";") if v.strip())
    if not values:
        return None
    if any(re.match(r"^[a-z]{2}:", v) or re.match(r"^zone\d+$", v) for v in values):
        return "implicit_only"
    return "type_without_value"


def _num(v: Any) -> float | None:
    return None if v is None else float(v)


def overture_rules(speed_limits: list[dict[str, Any]] | None) -> list[SpeedRule]:
    """One or two rules per speed_limits element (ADR-001 §3.3, TAC-001-02)."""
    rules: list[SpeedRule] = []
    for element in speed_limits or []:
        raw = json.dumps(element, sort_keys=True, ensure_ascii=False, default=str)
        when = element.get("when") or {}
        direction = when.get("heading") if when.get("heading") in DIRECTIONS else "both"
        cond_fields = {k: v for k, v in sorted(when.items()) if k != "heading" and v not in (None, [], "")}
        condition = json.dumps(cond_fields, sort_keys=True, ensure_ascii=False, default=str) if cond_fields else None
        btw = element.get("between")
        between = (float(btw[0]), float(btw[1])) if btw else None
        max_speed = element.get("max_speed") or None
        produced = False
        if max_speed and max_speed.get("value") is not None:
            unit = (max_speed.get("unit") or "km/h")
            value = _num(max_speed["value"])
            if unit.lower() == "mph":
                value = round(value * MPH, 2)
            rules.append(SpeedRule("overture", SpeedKind.NUMERIC, value, unit, direction, condition, between, raw))
            produced = True
        if element.get("is_max_speed_variable"):
            rules.append(SpeedRule("overture", SpeedKind.VARIABLE, None, None, direction, condition, between, raw))
            produced = True
        if not produced:
            rules.append(SpeedRule("overture", SpeedKind.UNPARSEABLE, None, None, direction, condition, between, raw))
    return rules


def _whole_segment(r: SpeedRule) -> bool:
    return r.between is None or (r.between[0] <= 0.0 and r.between[1] >= 1.0)


def comparable_value(rules: list[SpeedRule]) -> tuple[float | None, str | None]:
    """Comparable value: exactly one distinct unconditional numeric value covering the whole segment
    and both directions (ADR-001 §3.3). Returns (value, None) or (None, reason)."""
    if not rules:
        return None, "no_rules"
    uncond = [r for r in rules if r.condition_raw is None]
    if not uncond:
        return None, "only_conditional"
    for r in uncond:
        if r.kind == SpeedKind.UNPARSEABLE:
            return None, "unparseable"
        if r.kind != SpeedKind.NUMERIC:
            return None, str(r.kind)
    if any(not _whole_segment(r) for r in uncond):
        return None, "partial_between"
    by_dir: dict[str, set[float]] = {"both": set(), "forward": set(), "backward": set()}
    for r in uncond:
        by_dir[r.direction].add(r.value_kmh)
    if any(len(v) > 1 for v in by_dir.values()):
        return None, "multiple_values"
    if not by_dir["both"]:
        if not by_dir["forward"] or not by_dir["backward"]:
            return None, "direction_partial"
        if by_dir["forward"] != by_dir["backward"]:
            return None, "directional_differs"
    values = by_dir["both"] | by_dir["forward"] | by_dir["backward"]
    if len(values) != 1:
        return None, "directional_differs"
    return next(iter(values)), None
