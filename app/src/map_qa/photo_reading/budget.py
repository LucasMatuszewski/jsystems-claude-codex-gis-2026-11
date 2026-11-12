"""BudgetLedger: limits checked BEFORE each call, append-only ledger, circuit breaker (ADR-003 §5.5, D-33)."""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Callable


@dataclass
class Reservation:
    model: str
    tier: str
    amount: float
    settled: bool = False


class BudgetLedger:
    def __init__(self, path: Path, run_id: str, max_requests: int, max_cost_usd: float,
                 clock: Callable[[], float] = time.time) -> None:
        self.path, self.run_id = Path(path), run_id
        self.max_requests, self.max_cost_usd, self.clock = max_requests, max_cost_usd, clock
        self.requests_used = 0
        self.spent_usd = 0.0
        self.reserved_open = 0.0
        self.is_open = False
        self.open_reason: str | None = None
        self.refusal_reason: str | None = None
        for e in self._entries():  # limits are per run_id (also when a run is resumed)
            if e.get("run_id") == run_id:
                self.requests_used += 1
                self.spent_usd += float(e.get("actual_usd") or 0)

    def _entries(self) -> list[dict]:
        if not self.path.exists():
            return []
        return [json.loads(line) for line in self.path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def reserve(self, model: str, tier: str, amount: float) -> Reservation | None:
        if self.is_open:
            self.refusal_reason = "circuit_open"
            return None
        if self.requests_used + 1 > self.max_requests:
            self.refusal_reason = "max_requests"
            return None
        if self.spent_usd + self.reserved_open + amount > self.max_cost_usd + 1e-12:
            self.refusal_reason = "max_cost_usd"
            return None
        self.requests_used += 1  # every attempt counts, including failures (AC-13)
        self.reserved_open += amount
        return Reservation(model, tier, amount)

    def settle(self, res: Reservation, *, status_code: int | None, cost_usd: float | None, outcome: str) -> float:
        if res.settled:
            raise RuntimeError("reservation already settled")
        res.settled = True
        self.reserved_open = max(0.0, self.reserved_open - res.amount)
        ok = outcome == "ok"
        actual = float(cost_usd) if (ok and isinstance(cost_usd, (int, float)) and cost_usd >= 0) else res.amount
        self.spent_usd += actual
        entry = {"run_id": self.run_id, "ts": self.clock(), "model": res.model, "tier": res.tier,
                 "reserved_usd": res.amount, "actual_usd": actual, "status_code": status_code, "outcome": outcome}
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.path, "a", encoding="utf-8", newline="\n") as fh:
            fh.write(json.dumps(entry) + "\n")
        if not ok:
            self.open_breaker(outcome)
        return actual

    def open_breaker(self, reason: str) -> None:
        self.is_open = True
        self.open_reason = self.open_reason or reason

    def entries_for_run(self) -> int:
        return sum(1 for e in self._entries() if e.get("run_id") == self.run_id)

    def run_cost(self) -> float:
        return sum(float(e.get("actual_usd") or 0) for e in self._entries() if e.get("run_id") == self.run_id)

    def history_totals(self) -> tuple[int, float]:
        entries = self._entries()
        return len(entries), sum(float(e.get("actual_usd") or 0) for e in entries)
