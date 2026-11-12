"""ADR-003 §5.5, D-33, §8 'Limit żądań', 'Limit kosztu'; PRD AC-13 (no API shape asserted here)."""
import json

import pytest

from map_qa.photo_reading.budget import BudgetLedger


def ledger(tmp_path, **kw):
    args = {"run_id": "r1", "max_requests": 100, "max_cost_usd": 1.0, "clock": lambda: 1000.0}
    args.update(kw)
    return BudgetLedger(tmp_path / "ledger.jsonl", **args)


def test_request_limit_three_of_five(tmp_path):
    b = ledger(tmp_path, max_requests=3)
    granted = []
    for _ in range(5):
        r = b.reserve("m", "tier1", 0.02)
        if r:
            granted.append(r)
            b.settle(r, status_code=200, cost_usd=0.001, outcome="ok")
    assert len(granted) == 3 and b.requests_used == 3
    assert b.refusal_reason == "max_requests"


def test_cost_limit_with_reservation(tmp_path):
    b = ledger(tmp_path, max_cost_usd=0.05)
    r1, r2 = b.reserve("m", "tier1", 0.02), b.reserve("m", "tier1", 0.02)
    assert r1 and r2 and b.reserve("m", "tier1", 0.02) is None  # 0.02+0.02 open +0.02 > 0.05
    assert b.refusal_reason == "max_cost_usd"


def test_zero_cost_releases_reservation(tmp_path):
    b = ledger(tmp_path, max_cost_usd=0.05)
    for _ in range(5):
        r = b.reserve("m", "tier1", 0.02)
        b.settle(r, status_code=200, cost_usd=0.0, outcome="ok")
    assert b.spent_usd == 0.0 and b.requests_used == 5


def test_missing_cost_charges_full_reservation(tmp_path):
    b = ledger(tmp_path)
    r = b.reserve("m", "tier2", 0.04)
    b.settle(r, status_code=200, cost_usd=None, outcome="ok")
    assert b.spent_usd == pytest.approx(0.04)


def test_error_opens_breaker_and_charges_reservation(tmp_path):
    b = ledger(tmp_path)
    r = b.reserve("m", "tier1", 0.02)
    b.settle(r, status_code=429, cost_usd=None, outcome="error")
    assert b.is_open and b.spent_usd == pytest.approx(0.02)
    assert b.reserve("m", "tier1", 0.02) is None and b.refusal_reason == "circuit_open"


def test_error_in_second_request_scenario(tmp_path):
    """ADR-003 §8: error in 2nd request -> 1 success, 1 unavailable, 3 not_run (5 items, limit 3)."""
    b = ledger(tmp_path, max_requests=3)
    outcomes = []
    for i in range(5):
        r = b.reserve("m", "tier1", 0.02)
        if r is None:
            outcomes.append("not_run")
            continue
        if i == 1:
            b.settle(r, status_code=500, cost_usd=None, outcome="error")
            outcomes.append("unavailable")
        else:
            b.settle(r, status_code=200, cost_usd=0.001, outcome="ok")
            outcomes.append("ok")
    assert outcomes == ["ok", "unavailable", "not_run", "not_run", "not_run"]


def test_ledger_is_append_only_per_run_with_history(tmp_path):
    b = ledger(tmp_path)
    r = b.reserve("m", "tier1", 0.02)
    b.settle(r, status_code=200, cost_usd=0.003, outcome="ok")
    b2 = ledger(tmp_path, run_id="r2")
    assert b2.requests_used == 0  # limits are per run
    r = b2.reserve("m", "tier1", 0.02)
    b2.settle(r, status_code=200, cost_usd=0.002, outcome="ok")
    lines = [json.loads(x) for x in (tmp_path / "ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    assert [e["run_id"] for e in lines] == ["r1", "r2"]
    assert set(lines[0]) >= {"run_id", "ts", "model", "tier", "reserved_usd", "actual_usd", "status_code", "outcome"}
    assert b2.history_totals() == (2, pytest.approx(0.005))
    assert b2.entries_for_run() == 1


def test_resume_same_run_id_counts_existing_entries(tmp_path):
    b = ledger(tmp_path, max_requests=2)
    for _ in range(2):
        b.settle(b.reserve("m", "tier1", 0.02), status_code=200, cost_usd=0.001, outcome="ok")
    again = ledger(tmp_path, max_requests=2)
    assert again.requests_used == 2 and again.reserve("m", "tier1", 0.02) is None
