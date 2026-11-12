"""Evaluator: the ONLY component that opens reference_labels.csv and signs/labels.csv (ADR-003 §3, TAC-003-03).

It exposes sampling strata (ids only) to the SamplePlanner and computes metrics (§5.9). Label values never
leave this module except as evaluation results.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

from map_qa.core.models import CompareRow, EvalRow

STREET_QUESTIONS = ("surface", "junction_visible", "street_lighting_visible")


@dataclass(frozen=True)
class Label:
    value: str | None
    status: str  # certain / uncertain


class Evaluator:
    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self._street: dict[tuple[str, str], Label] | None = None
        self._signs: dict[str, Label] | None = None
        self.files_read: list[Path] = []

    # ---- label loading (read-only)
    def _load(self) -> None:
        if self._street is not None:
            return
        street: dict[tuple[str, str], Label] = {}
        path = self.data_dir / "reference_labels.csv"
        with open(path, encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                value = (row.get("label") or "").strip() or None
                street[(row["photo_id"], row["question"])] = Label(value, (row.get("status") or "").strip())
        signs: dict[str, Label] = {}
        spath = self.data_dir / "signs" / "labels.csv"
        with open(spath, encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                value = (row.get("sign_value") or "").strip() or None
                signs[row["photo_id"]] = Label(value, (row.get("status") or "").strip())
        self._street, self._signs = street, signs
        self.files_read = [path, spath]

    # ---- strata for the planner: ids only, no values
    def street_candidates(self) -> list[str]:
        """photo_ids with a `certain` label for at least one street question."""
        self._load()
        return sorted({pid for (pid, q), lab in self._street.items()
                       if q in STREET_QUESTIONS and lab.status == "certain"})

    def sign_strata(self) -> dict[str, str]:
        """photo_id -> 'positive' (certain numeric B-33) / 'negative' (certain none/unreadable)."""
        self._load()
        out = {}
        for pid, lab in self._signs.items():
            if lab.status != "certain" or lab.value is None:
                continue
            out[pid] = "positive" if lab.value.isdigit() else "negative"
        return out

    # ---- labels for evaluation (used only inside this module)
    def label(self, photo_id: str, question: str) -> Label | None:
        self._load()
        if question == "speed_limit_value":
            return self._signs.get(photo_id) or self._street.get((photo_id, question))
        return self._street.get((photo_id, question))

    def label_columns(self, readings) -> dict[tuple[str, str], tuple[str | None, str | None]]:
        """(photo_id, question) -> (label value, status) for the report's separate label column (AC-24)."""
        out = {}
        for r in readings:
            lab = self.label(r.photo_id, r.question_id)
            out[(r.photo_id, r.question_id)] = (lab.value, lab.status) if lab else (None, None)
        return out


# ---------------------------------------------------------------- metrics (ADR-003 §5.9)

ANSWERED = {"answered", "answered_tier2"}


def _ratio(num: int, den: int) -> str:
    return "nieokreślone" if den == 0 else f"{100.0 * num / den:.1f}% ({num}/{den})"


def _row(question: str, model: str, tier: str, items, evaluator: "Evaluator"):
    """items: (photo_id, question, decision, answer) after the tier view is applied."""
    c = dict(evaluated=0, correct=0, answered=0, abstained=0, unavailable=0, not_run=0, uncertain_excluded=0)
    correct_answered = 0
    for pid, q, decision, answer in items:
        lab = evaluator.label(pid, q)
        if lab is None or lab.status != "certain" or lab.value is None:
            c["uncertain_excluded"] += 1  # empty/uncertain labels are never turned into no/none
            continue
        c["evaluated"] += 1
        if decision in ANSWERED:
            c["answered"] += 1
            if answer == lab.value:
                c["correct"] += 1
                correct_answered += 1
        elif decision == "abstain":
            c["abstained"] += 1
        elif decision == "model_unavailable":
            c["unavailable"] += 1
        else:
            c["not_run"] += 1
    return EvalRow(question=question, model=model, tier=tier, **c,
                   accuracy_all=_ratio(c["correct"], c["evaluated"]),
                   coverage=_ratio(c["answered"], c["evaluated"]),
                   selective_accuracy=_ratio(correct_answered, c["answered"]))


def evaluate(readings, evaluator: "Evaluator", compare_readings=()) -> list:
    """Per question: tier-1 view, tier-2 view, final view, and the comparison model (tier 1)."""
    rows = []
    questions = list(dict.fromkeys(r.question_id for r in readings))
    t1_model = next((r.model for r in readings if r.tier == 1 and r.model), "tier1")
    t2_model = next((r.model for r in readings if r.tier == 2 and r.model), "gpt-6-luna")
    for q in questions:
        rs = [r for r in readings if r.question_id == q]
        tier1 = [(r.photo_id, q, "answered" if r.decision == "answered" else
                  ("abstain" if r.tier == 2 or r.decision == "abstain" else r.decision), r.tier1_answer) for r in rs]
        rows.append(_row(q, t1_model, "tier 1", tier1, evaluator))
        esc = [(r.photo_id, q, r.decision, r.answer) for r in rs if r.tier == 2]
        rows.append(_row(q, t2_model, "tier 2 (tylko eskalowane)", esc, evaluator))
        final = [(r.photo_id, q, r.decision, r.answer) for r in rs]
        rows.append(_row(q, f"{t1_model} → {t2_model.split('/')[-1]}", "końcowa (tier 1 + tier 2)", final, evaluator))
        cmp = [(r.photo_id, q, r.decision, r.answer) for r in compare_readings if r.question_id == q]
        if cmp:
            rows.append(_row(q, compare_readings[0].model, "tier 1 (porównanie, 5 obrazów)", cmp, evaluator))
    return rows


def compare_models(primary, compare):
    """Luna vs Jev on the same images and questions, tier 1 without escalation (AC-15)."""
    idx = {(r.photo_id, r.question_id): r for r in primary}
    table = []
    for c in compare:
        p = idx.get((c.photo_id, c.question_id))
        if p is None:
            continue
        pa, pp = p.tier1_answer, p.tier1_probability
        same = None if pa is None or c.answer is None else pa == c.answer
        diff = None if pp is None or c.probability is None else abs(pp - c.probability)
        table.append(CompareRow(photo_id=c.photo_id, question=c.question_id, luna_answer=pa, luna_p=pp,
                                jev_answer=c.answer, jev_p=c.probability, same=same, p_diff=diff))
    both = [r for r in table if r.same is not None]
    diffs = [r.p_diff for r in table if r.p_diff is not None]
    summary = {"Pary obraz–pytanie": len(table),
               "Zgodne odpowiedzi": f"{sum(1 for r in both if r.same)}/{len(both)}",
               "Średnia |Δ max(p)|": f"{sum(diffs) / len(diffs):.3f}" if diffs else "–",
               "Uwaga": "prawdopodobieństwa różnych modeli nie są wprost porównywalne; mała próbka, bez wniosków o kalibracji"}
    return table, summary
