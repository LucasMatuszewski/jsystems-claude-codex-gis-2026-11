"""Manual review items (PRD §14 AC-33, ADR-005 D-54).

Pure functions: PhotoReadings + labels (already obtained through Evaluator) -> JSON-ready review items.
"""
from __future__ import annotations

import random
from typing import Any

from map_qa.photo_reading.questions import QUESTIONS

REASONS = ("models_disagree", "escalated", "label_disagree", "near_threshold", "control")
ANSWERED = {"answered", "answered_tier2"}
NEAR = 0.10


def _probs(probabilities: dict[str, float] | None) -> list[list[Any]] | None:
    if not probabilities:
        return None
    return [[k, v] for k, v in sorted(probabilities.items(), key=lambda kv: (-kv[1], kv[0]))]


def _question(qid: str) -> dict[str, Any]:
    q = QUESTIONS[qid]
    return {"id": qid, "text": q["instructions"],
            "options": [{"value": k, "definition": v} for k, v in q["criteria"].items()]}


def _rows(r, c, label, tier1_model: str | None) -> list[dict[str, Any]]:
    rows = [{"role": "tier1", "model": tier1_model or (r.model if r.tier == 1 else None), "answer": r.tier1_answer,
             "probabilities": _probs(r.probabilities), "certainty": None,
             "decision": "answered" if r.decision == "answered" else "escalated"}]
    if r.tier == 2:
        rows.append({"role": "tier2", "model": r.model, "answer": r.answer if r.certainty else None,
                     "probabilities": None, "certainty": r.certainty, "decision": r.decision, "reason": r.reason})
    if c is not None:
        rows.append({"role": "compare", "model": c.model, "answer": c.answer, "probabilities": _probs(c.probabilities),
                     "certainty": None, "decision": c.decision, "reason": c.reason})
    rows.append({"role": "final", "model": None, "answer": r.answer if r.decision in ANSWERED else None,
                 "probabilities": None, "certainty": None, "decision": r.decision, "reason": r.reason})
    value, status = label if label else (None, None)
    rows.append({"role": "reference_label", "model": None, "answer": value, "status": status, "probabilities": None,
                 "certainty": None, "decision": None})
    return rows


def _reasons(r, c, label, t1_threshold: float) -> list[str]:
    out = []
    t2_answer = r.answer if r.tier == 2 and r.certainty else None
    if (t2_answer is not None and t2_answer != r.tier1_answer) or (
            c is not None and c.answer is not None and c.answer != r.tier1_answer):
        out.append("models_disagree")
    if r.tier == 2 or r.decision == "abstain":
        out.append("escalated")
    if label and label[1] == "certain" and label[0] is not None and r.decision in ANSWERED and r.answer != label[0]:
        out.append("label_disagree")
    if r.tier1_probability is not None and abs(r.tier1_probability - t1_threshold) <= NEAR + 1e-9:
        out.append("near_threshold")
    return out or ["control"]


def build_items(readings, compare_readings, labels: dict, *, t1_threshold: float, max_items: int = 100,
                seed: int = 42, tier1_model: str | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Returns (items in review order, stats). A reading without any tier-1 answer cannot be reviewed."""
    cmp = {(c.photo_id, c.question_id): c for c in compare_readings}
    groups: dict[str, list[dict[str, Any]]] = {k: [] for k in REASONS}
    not_reviewable = []
    for r in readings:
        key = (r.photo_id, r.question_id)
        item_id = f"{r.photo_id}|{r.question_id}"
        if r.tier1_answer is None:
            not_reviewable.append({"item_id": item_id, "decision": r.decision, "reason": r.reason})
            continue
        c, label = cmp.get(key), labels.get(key)
        reasons = _reasons(r, c, label, t1_threshold)
        groups[reasons[0]].append({"item_id": item_id, "photo_id": r.photo_id, "kind": r.kind,
                                   "question_id": r.question_id, "image_sha256": r.image_sha256,
                                   "question": _question(r.question_id), "reasons": reasons,
                                   "rows": _rows(r, c, label, tier1_model)})
    random.Random(seed).shuffle(groups["control"])
    ordered = [it for k in REASONS for it in groups[k]]
    selected = ordered[:max_items]
    stats = {"reviewable": len(ordered), "selected": len(selected), "cut_by_cap": len(ordered) - len(selected),
             "not_reviewable": not_reviewable,
             "by_reason": {k: sum(1 for it in selected if it["reasons"][0] == k) for k in REASONS}}
    return selected, stats
