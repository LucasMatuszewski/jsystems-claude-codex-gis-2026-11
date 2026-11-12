"""Status enums (PRD AC-06, ADR-002 §3.4, ADR-003 §4.2)."""
from __future__ import annotations

from enum import StrEnum


class ComparisonStatus(StrEnum):
    AGREE = "agree"
    DISAGREE = "disagree"
    MISSING_OSM = "missing_osm"
    MISSING_OVERTURE = "missing_overture"
    NOT_COMPARABLE = "not_comparable"
    AMBIGUOUS_LINK = "ambiguous_link"


class LinkStatus(StrEnum):
    OK = "ok"
    AMBIGUOUS = "ambiguous"
    NO_CANDIDATE = "no_candidate"


class Decision(StrEnum):
    ANSWERED = "answered"
    ANSWERED_TIER2 = "answered_tier2"
    ABSTAIN = "abstain"
    MODEL_UNAVAILABLE = "model_unavailable"
    NOT_RUN = "not_run_budget_or_error"


class SpeedKind(StrEnum):
    NUMERIC = "numeric"
    IMPLICIT = "implicit"
    NONE = "none"
    SIGNALS = "signals"
    WALK = "walk"
    VARIABLE = "variable"
    UNPARSEABLE = "unparseable"


class SurfaceClass(StrEnum):
    PAVED = "paved"
    UNPAVED = "unpaved"
    UNKNOWN_VALUE = "unknown_value"
    MISSING = "missing"


class LitClass(StrEnum):
    YES = "yes"
    NO = "no"
    YES_CONDITIONAL = "yes_conditional"
    UNKNOWN_VALUE = "unknown_value"
    MISSING = "missing"


ATTRIBUTES = ("speed", "surface")
