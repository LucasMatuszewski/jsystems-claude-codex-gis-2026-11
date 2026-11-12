"""Evaluator: the ONLY component that opens reference_labels.csv and signs/labels.csv (ADR-003 §3, TAC-003-03).

It exposes sampling strata (ids only) to the SamplePlanner and computes metrics (§5.9). Label values never
leave this module except as evaluation results.
"""
from __future__ import annotations

import csv
from dataclasses import dataclass
from pathlib import Path

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
