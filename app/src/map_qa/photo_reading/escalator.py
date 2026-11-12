"""Escalator: tier 1 (Decisions) -> tier 2 (Chat) -> abstain / model_unavailable (ADR-003 §4.2, §5, D-33).

Cache before budget; every attempt counted; no retry; the first error opens the circuit breaker.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from map_qa.core.capture import scrub
from map_qa.core.enums import Decision
from map_qa.photo_reading.budget import BudgetLedger
from map_qa.photo_reading.cache import DecisionCache, tier1_key, tier2_key
from map_qa.photo_reading.clients import CHAT_PATH, DECISIONS_PATH, ApiResult, response_cost
from map_qa.photo_reading.image import PreparedImage
from map_qa.photo_reading.payload import chat_payload, decisions_payload
from map_qa.photo_reading.validate import InvalidResponse, validate_chat, validate_decisions

ACCEPT = {"high": {"high"}, "medium": {"high", "medium"}, "low": {"high", "medium", "low"}}


@dataclass(frozen=True)
class Settings:
    tier1_model: str
    compare_model: str
    tier2_model: str
    t1_threshold: float
    t1_threshold_compare: float
    tier2_accept: str
    qs_version: str
    reserve_tier1: float
    reserve_tier2: float
    reserve_compare: float


@dataclass
class PhotoReading:
    photo_id: str
    kind: str
    question_id: str
    decision: str
    model: str | None = None
    tier: int | None = None
    answer: str | None = None
    probability: float | None = None
    probabilities: dict[str, float] | None = None
    certainty: str | None = None
    tier1_answer: str | None = None
    tier1_probability: float | None = None
    reason: str | None = None
    image_sha256: str | None = None
    request_ids: list[str] = field(default_factory=list)
    from_cache: bool = False


@dataclass
class CallRecord:
    model: str
    tier: str
    questions: list[str]
    cost_usd: float
    cached: bool
    outcome: str


def _error_reason(result: ApiResult) -> str:
    if result.error_kind == "http":
        return f"http_{result.status}"
    return result.error_kind or "error"


class Escalator:
    def __init__(self, settings: Settings, cache: DecisionCache, ledger: BudgetLedger, client) -> None:
        self.s, self.cache, self.ledger, self.client = settings, cache, ledger, client
        self.calls: list[CallRecord] = []
        self.cache_hits = 0

    # ------------------------------------------------------------------ helpers
    def _post(self, path: str, payload: dict, model: str, tier: str, reserve: float, qids: list[str]):
        """Returns (result, None) or (None, refusal_reason). Settles the ledger."""
        res = self.ledger.reserve(model, tier, reserve)
        if res is None:
            return None, self.ledger.refusal_reason
        result = self.client.post(path, payload)
        cost = response_cost(result.body) if result.ok else None
        outcome = "ok" if result.ok else ("timeout" if result.error_kind == "timeout" else "error")
        return (result, res, cost, outcome), None

    def _tier1(self, model: str, tier: str, reserve: float, kind: str, image: PreparedImage, qids: list[str]):
        """Returns (answers | None, request_id, failure_decision, reason, from_cache)."""
        key = tier1_key(image.sha256, model, self.s.qs_version, tier, qids)
        entry = self.cache.get(key)
        if entry is not None:
            self.cache_hits += 1
            self.calls.append(CallRecord(model, tier, qids, 0.0, True, "cache"))
            return validate_decisions(entry["body"], qids), entry["body"].get("id"), None, None, True
        posted, refusal = self._post(DECISIONS_PATH, decisions_payload(model, kind, image, qids), model, tier,
                                     reserve, qids)
        if posted is None:
            return None, None, Decision.NOT_RUN, refusal, False
        result, res, cost, outcome = posted
        if not result.ok:
            self.ledger.settle(res, status_code=result.status, cost_usd=None, outcome=outcome)
            self.calls.append(CallRecord(model, tier, qids, res.amount, False, outcome))
            return None, None, Decision.MODEL_UNAVAILABLE, _error_reason(result), False
        try:
            answers = validate_decisions(result.body, qids)
        except InvalidResponse:
            self.ledger.settle(res, status_code=result.status, cost_usd=None, outcome="invalid_response")
            self.calls.append(CallRecord(model, tier, qids, res.amount, False, "invalid_response"))
            return None, None, Decision.MODEL_UNAVAILABLE, "invalid_response", False
        actual = self.ledger.settle(res, status_code=result.status, cost_usd=cost, outcome="ok")
        self.calls.append(CallRecord(model, tier, qids, actual, False, "ok"))
        self.cache.put(key, {"body": scrub(result.body), "model": result.body.get("model"), "cost_usd": actual,
                             "elapsed_ms": result.elapsed_ms})
        return answers, result.body.get("id"), None, None, False

    # ------------------------------------------------------------------ public
    def read(self, photo_id: str, kind: str, image: PreparedImage, qids: list[str]) -> list[PhotoReading]:
        s = self.s
        answers, req_id, fail, reason, cached = self._tier1(s.tier1_model, "tier1", s.reserve_tier1, kind, image,
                                                            qids)
        if answers is None:
            return [PhotoReading(photo_id, kind, q, str(fail), model=s.tier1_model, tier=1, reason=reason,
                                 image_sha256=image.sha256) for q in qids]
        readings: dict[str, PhotoReading] = {}
        uncertain = []
        for q in qids:
            a = answers[q]
            r = PhotoReading(photo_id, kind, q, "", model=s.tier1_model, tier=1, answer=a.choice,
                             probability=a.pmax, probabilities=a.probabilities, tier1_answer=a.choice,
                             tier1_probability=a.pmax, image_sha256=image.sha256,
                             request_ids=[req_id] if req_id else [], from_cache=cached)
            if a.choice != "unknown" and a.pmax >= s.t1_threshold:
                r.decision = str(Decision.ANSWERED)
            else:
                uncertain.append(q)
            readings[q] = r
        if uncertain:
            self._tier2(kind, image, uncertain, readings)
        return [readings[q] for q in qids]

    def _tier2(self, kind: str, image: PreparedImage, uncertain: list[str], readings: dict[str, PhotoReading]) -> None:
        s = self.s
        t2: dict[str, dict] = {}
        missing = []
        for q in uncertain:
            entry = self.cache.get(tier2_key(image.sha256, s.tier2_model, s.qs_version, q))
            if entry is None:
                missing.append(q)
            else:
                t2[q] = {**entry, "from_cache": True}
        if len(t2):
            self.cache_hits += 1
            self.calls.append(CallRecord(s.tier2_model, "tier2", sorted(t2), 0.0, True, "cache"))
        if missing:
            posted, refusal = self._post(CHAT_PATH, chat_payload(s.tier2_model, kind, image, missing),
                                         s.tier2_model, "tier2", s.reserve_tier2, missing)
            if posted is None:
                for q in missing:
                    self._fail(readings[q], Decision.NOT_RUN, refusal)
            else:
                result, res, cost, outcome = posted
                if not result.ok:
                    self.ledger.settle(res, status_code=result.status, cost_usd=None, outcome=outcome)
                    self.calls.append(CallRecord(s.tier2_model, "tier2", missing, res.amount, False, outcome))
                    for q in missing:
                        self._fail(readings[q], Decision.MODEL_UNAVAILABLE, _error_reason(result))
                else:
                    try:
                        parsed = validate_chat(result.body, missing)
                    except InvalidResponse:
                        self.ledger.settle(res, status_code=result.status, cost_usd=None, outcome="invalid_response")
                        self.calls.append(CallRecord(s.tier2_model, "tier2", missing, res.amount, False,
                                                     "invalid_response"))
                        for q in missing:
                            self._fail(readings[q], Decision.MODEL_UNAVAILABLE, "invalid_response")
                        parsed = None
                    if parsed is not None:
                        actual = self.ledger.settle(res, status_code=result.status, cost_usd=cost, outcome="ok")
                        self.calls.append(CallRecord(s.tier2_model, "tier2", missing, actual, False, "ok"))
                        body = scrub(result.body)
                        for q in missing:
                            entry = {"answer": parsed[q].answer, "certainty": parsed[q].certainty,
                                     "model": result.body.get("model"), "response_id": result.body.get("id"),
                                     "cost_usd": actual, "questions_in_request": missing, "body": body}
                            self.cache.put(tier2_key(image.sha256, s.tier2_model, s.qs_version, q), entry)
                            t2[q] = entry
        accepted = ACCEPT[s.tier2_accept]
        for q, entry in t2.items():
            r = readings[q]
            r.model, r.tier, r.answer, r.certainty = s.tier2_model, 2, entry["answer"], entry["certainty"]
            r.probability = None
            if entry.get("response_id"):
                r.request_ids.append(entry["response_id"])
            r.from_cache = r.from_cache and bool(entry.get("from_cache"))
            if entry["answer"] != "unknown" and entry["certainty"] in accepted:
                r.decision = str(Decision.ANSWERED_TIER2)
            else:
                r.decision = str(Decision.ABSTAIN)
                r.reason = "tier2_unknown" if entry["answer"] == "unknown" else f"tier2_certainty_{entry['certainty']}"

    @staticmethod
    def _fail(r: PhotoReading, decision: Decision, reason: str | None) -> None:
        r.decision, r.reason = str(decision), reason

    def read_compare(self, photo_id: str, kind: str, image: PreparedImage, qids: list[str]) -> list[PhotoReading]:
        """Comparison model: same image and questions, tier 1 only, no escalation (ADR-003 §5.9)."""
        s = self.s
        answers, req_id, fail, reason, cached = self._tier1(s.compare_model, "compare", s.reserve_compare, kind,
                                                            image, qids)
        if answers is None:
            return [PhotoReading(photo_id, kind, q, str(fail), model=s.compare_model, tier=1, reason=reason,
                                 image_sha256=image.sha256) for q in qids]
        out = []
        for q in qids:
            a = answers[q]
            ok = a.choice != "unknown" and a.pmax >= s.t1_threshold_compare
            out.append(PhotoReading(photo_id, kind, q, str(Decision.ANSWERED if ok else Decision.ABSTAIN),
                                    model=s.compare_model, tier=1, answer=a.choice, probability=a.pmax,
                                    probabilities=a.probabilities, tier1_answer=a.choice, tier1_probability=a.pmax,
                                    reason=None if ok else "below_threshold_compare", image_sha256=image.sha256,
                                    request_ids=[req_id] if req_id else [], from_cache=cached))
        return out

    def pending_calls(self, image: PreparedImage, kind: str, qids: list[str], compare: bool = False) -> dict[str, int]:
        """New calls this image would need (listed before confirmation; PRD §4.4)."""
        s = self.s
        out = {"tier1": 0, "tier2": 0}
        entry = self.cache.get(tier1_key(image.sha256, s.tier1_model, s.qs_version, "tier1", qids))
        if entry is None:
            out["tier1"], out["tier2"] = 1, 1  # tier 2 need is unknown before tier 1; counted conservatively
        else:
            answers = validate_decisions(entry["body"], qids)
            unc = [q for q, a in answers.items() if a.choice == "unknown" or a.pmax < s.t1_threshold]
            if any(self.cache.get(tier2_key(image.sha256, s.tier2_model, s.qs_version, q)) is None for q in unc):
                out["tier2"] = 1
        if compare:
            out["compare"] = int(self.cache.get(tier1_key(image.sha256, s.compare_model, s.qs_version, "compare",
                                                          qids)) is None)
        return out
