"""OSM `lit` classes (ADR-001 §3.4). Compared only with the photo reading, never with Overture."""
from __future__ import annotations

from map_qa.core.enums import LitClass

CONDITIONAL = {"automatic", "24/7", "sunset-sunrise", "limited", "interval"}


def lit_class(raw: str | None) -> str:
    if raw is None or not str(raw).strip():
        return str(LitClass.MISSING)
    v = str(raw).strip().lower()
    if v == "yes":
        return str(LitClass.YES)
    if v == "no":
        return str(LitClass.NO)
    if v in CONDITIONAL:
        return str(LitClass.YES_CONDITIONAL)
    # e.g. `disused`: not evidence of working lighting nor of its absence (decision 2026-11-12, ADR-001 §3.4)
    return str(LitClass.UNKNOWN_VALUE)
