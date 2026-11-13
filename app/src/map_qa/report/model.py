"""ReportModel: built once, rendered by both templates (ADR-004 §4, ADR-000 D-04).

All counters are computed here, never in templates (AC-23).
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field

from map_qa.core.enums import ComparisonStatus
from map_qa.core.models import (  # noqa: F401 (re-export)
    CompareRow, CompletenessRow, EvalRow, MapCompareRow, SourceCompareRow,
)

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
    label: str | None = None          # reference label (Evaluator), shown in its own column (AC-24)
    label_status: str | None = None


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
    answers_cost_usd: float = 0.0  # all answers used, incl. original cost of cached ones (AC-30)
    answers_cost_by_model: dict[str, float] = Field(default_factory=dict)
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


# ---- PRD §13 (2026-11-13): glossary (AC-28) and label provenance (AC-29), shared by all templates
LABEL_PROVENANCE = (
    "Etykiety referencyjne przygotowały agenty AI: zdjęcia ulic oznaczył Codex, a wycinki znaków to zgodny odczyt "
    "dwóch modeli (Codex i GLM-5.3-Flash). Etykiety nie zostały zweryfikowane przez człowieka, więc accuracy "
    "oznacza zgodność z roboczą referencją AI, a nie poprawność terenową.")
GLOSSARY = [
    ("Tier 1", "model decyzyjny (openai/gpt-6-luna-decisions) zwraca zamkniętą odpowiedź z prawdopodobieństwem "
               "każdej opcji; odpowiedź z max(p) ≥ progu T1 jest przyjmowana (`answered`)."),
    ("Tier 2", "ogólny LLM (openai/gpt-6-luna, rozumowanie medium) dostaje ten sam obraz i tylko pytania, przy których "
               "tier 1 był niepewny albo odpowiedział `unknown`; sam ocenia pewność (high/medium/low). Przyjmowane jest "
               "tylko `high` (`answered_tier2`)."),
    ("Model porównawczy", "typesafe/jev-1.14 odpowiada na te same pytania dla 5 obrazów, tylko na poziomie tier 1, "
                          "żeby porównać dwa modele decyzyjne."),
    ("abstain", "żaden poziom nie dał pewnej odpowiedzi; pozycja trafia do kolejki ręcznej."),
    ("model_unavailable", "błąd API, timeout albo niepoprawna odpowiedź; nigdy nie jest zamieniany na odpowiedź. "
                          "Po pierwszym błędzie kolejne płatne wywołania są wstrzymane."),
    ("not_run_budget_or_error", "pytanie nie zostało wysłane, bo skończył się limit żądań lub kosztu albo wcześniej "
                                "wystąpił błąd."),
    ("agree / disagree", "OSM i Overture mają po jednej bezwarunkowej wartości dla całego odcinka; są zgodne "
                         "lub różne. Zgodność oznacza zgodność snapshotów (Overture w 99% pochodzi z OSM)."),
    ("missing_osm / missing_overture", "brak tagu lub reguły po danej stronie; brak nigdy nie jest liczony jako 0."),
    ("not_comparable", "wartości nie da się uczciwie porównać: reguła warunkowa, kierunkowa, dotyczy części odcinka "
                       "(`between`), limit tylko typem (np. PL:urban) albo nieznana wartość."),
    ("ambiguous_link", "połączenie zdjęcia z drogą jest niepewne (np. kilku podobnych kandydatów); para trafia do "
                       "kolejki ręcznej i nie dostaje agree/disagree."),
]
