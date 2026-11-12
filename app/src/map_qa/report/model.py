"""ReportModel: built once, rendered by both templates (ADR-004 §4, ADR-000 D-04).

All counters are computed here, never in templates (AC-23).
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from map_qa.core.enums import ComparisonStatus
from map_qa.core.models import CompletenessRow  # noqa: F401 (re-export)

STATUS_ORDER = [s.value for s in ComparisonStatus]
CANDIDATE_STATUSES = ["disagree", "missing_osm", "missing_overture", "not_comparable", "ambiguous_link"]
ATTRIBUTE_LABELS = {"speed": "Ograniczenie prędkości", "surface": "Nawierzchnia"}
STATUS_LABELS = {
    "agree": "zgodne",
    "disagree": "rozbieżne",
    "missing_osm": "brak w OSM",
    "missing_overture": "brak w Overture",
    "not_comparable": "nieporównywalne",
    "ambiguous_link": "niepewne połączenie",
}
DECISION_LABELS = {
    "answered": "odpowiedź tier 1",
    "answered_tier2": "odpowiedź tier 2",
    "abstain": "abstencja (kolejka ręczna)",
    "model_unavailable": "model niedostępny",
    "not_run_budget_or_error": "nie uruchomiono (limit lub błąd)",
}
DISCLAIMER = ("Odczyt zdjęcia jest predykcją modelu, a nie weryfikacją terenową. "
              "Rozbieżność źródeł nie oznacza automatycznie błędu mapy.")
NOT_RUN = "Odczyt modelem nie był uruchomiony"


class FileRow(BaseModel):
    name: str
    sha256: str
    expected_match: str | None = None


class TableRow(BaseModel):
    name: str
    rows: int
    statement_id: str | None = None


class SourceCompareRow(BaseModel):
    table: str
    selected_rows: int | None
    other_rows: int | None
    keys_only_selected: int | None = None
    keys_only_other: int | None = None
    equal: bool


class Header(BaseModel):
    run_id: str
    run_date: str
    source: str
    source_label: str
    snapshots: dict[str, str]
    files: list[FileRow] = Field(default_factory=list)
    tables: list[TableRow] = Field(default_factory=list)
    config: dict[str, Any] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)
    source_comparison: list[SourceCompareRow] = Field(default_factory=list)
    other_source_label: str | None = None


class StatusCount(BaseModel):
    attribute: str
    status: str
    count: int


class RoadRow(BaseModel):
    osm_way_id: int
    photos: int
    statuses: dict[str, dict[str, int]]


class Thumb(BaseModel):
    photo_id: str
    kind: str = "photo"  # photo / sign_crop
    source_url: str | None = None
    author: str | None = None
    source: str | None = None
    license: str | None = None
    src: str | None = None  # set by the renderer after copying: thumbs/<photo_id>.jpg
    width: int | None = None
    height: int | None = None


class AttrCell(BaseModel):
    attribute: str
    status: str
    reason: str | None = None
    osm_value: str | None = None
    overture_value: str | None = None
    osm_raw: list[str] = Field(default_factory=list)
    overture_raw: list[str] = Field(default_factory=list)


class ReadingCell(BaseModel):
    question: str
    decision: str
    answer: str | None = None
    tier: int | None = None
    probability: float | None = None
    certainty: str | None = None


class Candidate(BaseModel):
    photo_id: str
    osm_way_id: int | None
    overture_id: str | None
    distance_m: float | None
    distance_m_recomputed: float | None
    link_status: str
    candidate_flags: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    reasons: list[str] = Field(default_factory=list)
    thumb: Thumb
    attributes: list[AttrCell]
    readings: list[ReadingCell] = Field(default_factory=list)


class QueueItem(BaseModel):
    kind: str  # ambiguous_link / abstain / model_unavailable
    photo_id: str
    subject: str
    reason: str | None = None


class ModelCounter(BaseModel):
    model: str
    tier: str
    question: str
    requests: int
    cost_usd: float
    cache_hits: int = 0


class DecisionCount(BaseModel):
    question: str
    decision: str
    count: int


class ReadingRow(BaseModel):
    photo_id: str
    kind: str
    question: str
    decision: str
    answer: str | None = None
    tier: int | None = None
    model: str | None = None
    probability: float | None = None
    certainty: str | None = None
    tier1_answer: str | None = None
    tier1_probability: float | None = None
    reason: str | None = None


class EvalRow(BaseModel):
    question: str
    model: str
    tier: str
    evaluated: int
    correct: int
    answered: int
    abstained: int
    unavailable: int
    not_run: int
    uncertain_excluded: int
    accuracy_all: str
    coverage: str
    selective_accuracy: str


class CompareRow(BaseModel):
    photo_id: str
    question: str
    luna_answer: str | None
    luna_p: float | None
    jev_answer: str | None
    jev_p: float | None
    same: bool | None
    p_diff: float | None


class MapCompareRow(BaseModel):
    photo_id: str
    question: str
    prediction: str | None
    decision: str
    map_values: str
    note: str | None = None


class ModelSection(BaseModel):
    run: bool = False
    not_run_reason: str = NOT_RUN
    question_set_version: str | None = None
    thresholds: dict[str, Any] = Field(default_factory=dict)
    sample: dict[str, int] = Field(default_factory=dict)
    requests_this_run: int = 0
    cost_this_run_usd: float = 0.0
    ledger_total_requests: int = 0
    ledger_total_cost_usd: float = 0.0
    cache_hits: int = 0
    max_requests: int | None = None
    max_cost_usd: float | None = None
    stopped_reason: str | None = None
    counters: list[ModelCounter] = Field(default_factory=list)
    decisions: list[DecisionCount] = Field(default_factory=list)
    readings: list[ReadingRow] = Field(default_factory=list)
    evaluation: list[EvalRow] = Field(default_factory=list)
    comparison: list[CompareRow] = Field(default_factory=list)
    comparison_summary: dict[str, Any] = Field(default_factory=dict)
    map_comparison: list[MapCompareRow] = Field(default_factory=list)


class Summary(BaseModel):
    photos: int
    pairs: int
    no_candidate: int
    link_status: dict[str, int]
    status_counts: list[StatusCount]
    roads_total: int = 0
    roads: list[RoadRow] = Field(default_factory=list)
    completeness: list[CompletenessRow] = Field(default_factory=list)


class ReportModel(BaseModel):
    header: Header
    summary: Summary
    candidates: list[Candidate] = Field(default_factory=list)
    manual_queue: list[QueueItem] = Field(default_factory=list)
    model: ModelSection = Field(default_factory=ModelSection)
    shows_mapillary_derived: bool = False

    # ---- derived views (computed in Python, not in templates) ----
    def counter(self, attribute: str, status: str) -> int:
        for c in self.summary.status_counts:
            if c.attribute == attribute and c.status == status:
                return c.count
        return 0

    def attributes(self) -> list[str]:
        seen: list[str] = []
        for c in self.summary.status_counts:
            if c.attribute not in seen:
                seen.append(c.attribute)
        return seen

    def candidate_groups(self) -> list[dict[str, Any]]:
        groups = []
        for attr in self.attributes():
            for status in CANDIDATE_STATUSES:
                items = [c for c in self.candidates
                         if any(a.attribute == attr and a.status == status for a in c.attributes)]
                groups.append({"attribute": attr, "status": status, "count": self.counter(attr, status),
                               "rows": items, "label": f"{ATTRIBUTE_LABELS.get(attr, attr)}: "
                                                        f"{STATUS_LABELS.get(status, status)}"})
        return groups


def build_status_counts(rows: list[tuple[str, str]], attributes: tuple[str, ...]) -> list[StatusCount]:
    """rows: (attribute, status) per comparison; every status appears, zero included (AC-26)."""
    counts = {(a, s): 0 for a in attributes for s in STATUS_ORDER}
    for attr, status in rows:
        counts[(attr, status)] += 1
    return [StatusCount(attribute=a, status=s, count=counts[(a, s)]) for a in attributes for s in STATUS_ORDER]
