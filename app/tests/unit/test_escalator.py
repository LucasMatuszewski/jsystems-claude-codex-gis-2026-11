"""ADR-003 §4.2, §5.2-5.4, §5.7, §8; PRD AC-16, AC-17, AC-18, AC-20.

Fake client bodies are taken from the REAL captures (T43). Variants are derived from them (ADR-003 §8
'Walidacja odpowiedzi' allows a capture body with a removed option etc.).
"""
import copy
import json

import pytest

from map_qa.photo_reading.budget import BudgetLedger
from map_qa.photo_reading.cache import DecisionCache
from map_qa.photo_reading.clients import CHAT_PATH, DECISIONS_PATH, ApiResult
from map_qa.photo_reading.escalator import Escalator, Settings
from map_qa.photo_reading.image import prepare_bytes
from map_qa.photo_reading.validate import InvalidResponse, validate_chat, validate_decisions
from tests.conftest import FIXTURES
from tests.unit.test_image import jpeg

PHOTO_QS = ["surface", "junction_visible", "street_lighting_visible"]


def cap(name):
    return json.loads((FIXTURES / "captures" / f"{name}.json").read_text(encoding="utf-8"))["response_body"]


def chat_body(answers: dict) -> dict:
    body = copy.deepcopy(cap("chat-tier2-photo-200"))
    body["choices"][0]["message"]["content"] = json.dumps(answers)
    return body


class FakeClient:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def post(self, path, payload):
        self.calls.append((path, payload))
        r = self.responses.pop(0)
        return r if isinstance(r, ApiResult) else ApiResult(200, r, {}, 10.0)

    def close(self):
        pass


def make(tmp_path, responses, t1=0.80, accept="high", max_requests=100, run_id="r"):
    client = FakeClient(responses)
    settings = Settings(tier1_model="openai/gpt-6-luna-decisions", compare_model="typesafe/jev-1.14",
                        tier2_model="openai/gpt-6-luna", t1_threshold=t1, t1_threshold_compare=0.80,
                        tier2_accept=accept, qs_version="qs-v1", reserve_tier1=0.002, reserve_tier2=0.004,
                        reserve_compare=0.002)
    ledger = BudgetLedger(tmp_path / "ledger.jsonl", run_id=run_id, max_requests=max_requests, max_cost_usd=1.0)
    return Escalator(settings, DecisionCache(tmp_path / "cache"), ledger, client), client, ledger


IMG = prepare_bytes(jpeg(800, 600))
IMG2 = prepare_bytes(jpeg(640, 480))


def by_q(readings):
    return {r.question_id: r for r in readings}


def test_confident_tier1_all_answered(tmp_path):
    e, client, _ = make(tmp_path, [cap("decisions-luna-photo-200")])
    rs = by_q(e.read("p1", "photo", IMG, PHOTO_QS))
    assert [c[0] for c in client.calls] == [DECISIONS_PATH]
    assert {q: (r.decision, r.answer, r.tier) for q, r in rs.items()} == {
        "surface": ("answered", "paved", 1), "junction_visible": ("answered", "no", 1),
        "street_lighting_visible": ("answered", "no", 1)}
    assert rs["street_lighting_visible"].probability == pytest.approx(0.95)


def test_threshold_boundary(tmp_path):
    # 0.95 < 0.96 -> lighting escalates; 0.99 stays
    body = chat_body({"street_lighting_visible": {"answer": "yes", "certainty": "high"}})
    e, client, _ = make(tmp_path, [cap("decisions-luna-photo-200"), body], t1=0.96)
    rs = by_q(e.read("p1", "photo", IMG, PHOTO_QS))
    assert [c[0] for c in client.calls] == [DECISIONS_PATH, CHAT_PATH]
    sent = client.calls[1][1]["response_format"]["json_schema"]["schema"]["required"]
    assert sent == ["street_lighting_visible"]  # only uncertain questions go to tier 2
    assert "0.95" not in json.dumps(client.calls[1][1])  # no tier-1 answer/probabilities (no anchoring)
    assert rs["street_lighting_visible"].decision == "answered_tier2"
    assert rs["street_lighting_visible"].tier1_answer == "no" and rs["junction_visible"].decision == "answered"


def test_low_tier1_on_sign_crop_goes_to_tier2_real_flow(tmp_path):
    e, client, _ = make(tmp_path, [cap("decisions-luna-sign_crop-200"), cap("chat-tier2-sign_crop-200")])
    r = e.read("s1", "sign_crop", IMG, ["speed_limit_value"])[0]
    assert (r.decision, r.answer, r.tier, r.certainty) == ("answered_tier2", "20", 2, "high")
    assert r.tier1_probability == pytest.approx(0.38)


@pytest.mark.parametrize("certainty,answer,expected", [("medium", "yes", "abstain"), ("low", "yes", "abstain"),
                                                         ("high", "unknown", "abstain")])
def test_tier2_not_high_or_unknown_is_abstain(tmp_path, certainty, answer, expected):
    body = chat_body({"street_lighting_visible": {"answer": answer, "certainty": certainty}})
    e, _, _ = make(tmp_path, [cap("decisions-luna-photo-200"), body], t1=0.96)
    assert by_q(e.read("p1", "photo", IMG, PHOTO_QS))["street_lighting_visible"].decision == expected


def test_tier2_accept_medium_config(tmp_path):
    body = chat_body({"street_lighting_visible": {"answer": "yes", "certainty": "medium"}})
    e, _, _ = make(tmp_path, [cap("decisions-luna-photo-200"), body], t1=0.96, accept="medium")
    assert by_q(e.read("p1", "photo", IMG, PHOTO_QS))["street_lighting_visible"].decision == "answered_tier2"


def test_unknown_with_high_probability_escalates(tmp_path):
    t1 = copy.deepcopy(cap("decisions-luna-photo-200"))
    t1["answers"]["surface"] = {"type": "choice", "choice": "unknown",
                                "probabilities": {"paved": 0.03, "unpaved": 0.02, "unknown": 0.95}, "confidence": 0.9}
    body = chat_body({"surface": {"answer": "paved", "certainty": "high"}})
    e, client, _ = make(tmp_path, [t1, body])
    assert by_q(e.read("p1", "photo", IMG, PHOTO_QS))["surface"].decision == "answered_tier2"


def test_none_and_unreadable_are_answers(tmp_path):
    for value in ("none", "unreadable"):
        body = copy.deepcopy(cap("decisions-luna-sign_crop-200"))
        probs = {k: 0.0 for k in body["answers"]["speed_limit_value"]["probabilities"]}
        probs[value] = 0.85
        probs["20"] = 0.15
        body["answers"]["speed_limit_value"].update(choice=value, probabilities=probs)
        e, client, _ = make(tmp_path / value, [body])
        r = e.read("s", "sign_crop", IMG, ["speed_limit_value"])[0]
        assert (r.decision, r.answer) == ("answered", value) and len(client.calls) == 1


def test_http_429_is_unavailable_no_retry_and_breaker(tmp_path):
    err = ApiResult(429, cap("decisions-error-400"), {}, 5.0, "http", "rate")
    e, client, ledger = make(tmp_path, [err])
    rs = e.read("p1", "photo", IMG, PHOTO_QS)
    assert {r.decision for r in rs} == {"model_unavailable"} and len(client.calls) == 1
    assert ledger.is_open
    nxt = e.read("p2", "photo", IMG2, PHOTO_QS)
    assert {r.decision for r in nxt} == {"not_run_budget_or_error"} and len(client.calls) == 1


@pytest.mark.parametrize("kind", ["timeout", "network"])
def test_timeout_and_network_unavailable(tmp_path, kind):
    e, client, ledger = make(tmp_path, [ApiResult(None, None, {}, 40000.0, kind)])
    assert {r.decision for r in e.read("p1", "photo", IMG, PHOTO_QS)} == {"model_unavailable"}
    assert ledger.is_open and ledger.spent_usd == pytest.approx(0.002)


def test_invalid_response_is_unavailable(tmp_path):
    body = copy.deepcopy(cap("decisions-luna-photo-200"))
    del body["answers"]["junction_visible"]
    e, _, ledger = make(tmp_path, [body])
    rs = by_q(e.read("p1", "photo", IMG, PHOTO_QS))
    assert rs["surface"].decision == "model_unavailable" and rs["surface"].reason == "invalid_response"
    assert ledger.is_open


def test_tier2_error_marks_only_escalated_questions(tmp_path):
    e, client, _ = make(tmp_path, [cap("decisions-luna-photo-200"),
                                   ApiResult(500, {"error": {"message": "x"}}, {}, 5.0, "http")], t1=0.96)
    rs = by_q(e.read("p1", "photo", IMG, PHOTO_QS))
    assert rs["street_lighting_visible"].decision == "model_unavailable"
    assert rs["surface"].decision == "answered"


def test_budget_limit_three_requests_five_images(tmp_path):
    e, client, _ = make(tmp_path, [cap("decisions-luna-photo-200")] * 5, max_requests=3)
    imgs = [prepare_bytes(jpeg(400 + i * 10, 300)) for i in range(5)]
    decisions = [e.read(f"p{i}", "photo", im, PHOTO_QS)[0].decision for i, im in enumerate(imgs)]
    assert decisions == ["answered"] * 3 + ["not_run_budget_or_error"] * 2 and len(client.calls) == 3


def test_cache_second_run_zero_requests_same_predictions(tmp_path):
    e, client, _ = make(tmp_path, [cap("decisions-luna-sign_crop-200"), cap("chat-tier2-sign_crop-200")])
    first = e.read("s1", "sign_crop", IMG, ["speed_limit_value"])
    e2, client2, ledger2 = make(tmp_path, [], run_id="r2")
    second = e2.read("s1", "sign_crop", IMG, ["speed_limit_value"])
    assert client2.calls == [] and ledger2.requests_used == 0
    assert [(r.decision, r.answer) for r in first] == [(r.decision, r.answer) for r in second]
    assert e2.cache_hits == 2


def test_lower_threshold_reevaluates_from_cache(tmp_path):
    e, _, _ = make(tmp_path, [cap("decisions-luna-sign_crop-200"), cap("chat-tier2-sign_crop-200")])
    e.read("s1", "sign_crop", IMG, ["speed_limit_value"])
    e2, client2, _ = make(tmp_path, [], t1=0.30, run_id="r2")
    r = e2.read("s1", "sign_crop", IMG, ["speed_limit_value"])[0]
    assert client2.calls == [] and (r.decision, r.answer, r.tier) == ("answered", "20", 1)


def test_raising_threshold_lists_new_calls(tmp_path):
    e, _, _ = make(tmp_path, [cap("decisions-luna-photo-200")])
    e.read("p1", "photo", IMG, PHOTO_QS)
    e2, client2, _ = make(tmp_path, [], t1=0.96, run_id="r2")
    assert e2.pending_calls(IMG, "photo", PHOTO_QS) == {"tier1": 0, "tier2": 1}
    assert client2.calls == []


def test_compare_model_tier1_only(tmp_path):
    e, client, _ = make(tmp_path, [cap("decisions-jev-photo-200")])
    rs = by_q(e.read_compare("p1", "photo", IMG, PHOTO_QS))
    assert [c[1]["model"] for c in client.calls] == ["typesafe/jev-1.14"]
    assert rs["junction_visible"].model == "typesafe/jev-1.14" and rs["junction_visible"].tier == 1
    assert all(r.decision in ("answered", "abstain") for r in rs.values())


def test_validate_decisions_rules():
    body = cap("decisions-luna-photo-200")
    assert set(validate_decisions(body, PHOTO_QS)) == set(PHOTO_QS)
    bad = copy.deepcopy(body)
    del bad["answers"]["surface"]["probabilities"]["unknown"]  # removed option
    with pytest.raises(InvalidResponse):
        validate_decisions(bad, PHOTO_QS)
    bad = copy.deepcopy(body)
    bad["answers"]["surface"]["probabilities"] = {"paved": 0.6, "unpaved": 0.2, "unknown": 0.1}  # sum 0.9
    with pytest.raises(InvalidResponse):
        validate_decisions(bad, PHOTO_QS)
    bad = copy.deepcopy(body)
    bad["answers"]["surface"]["choice"] = "cobbles"
    with pytest.raises(InvalidResponse):
        validate_decisions(bad, PHOTO_QS)


def test_validate_chat_rules():
    body = cap("chat-tier2-photo-200")
    assert set(validate_chat(body, PHOTO_QS)) == set(PHOTO_QS)
    with pytest.raises(InvalidResponse):
        validate_chat(chat_body({"surface": {"answer": "gravelish", "certainty": "high"}}), ["surface"])
    broken = copy.deepcopy(body)
    broken["choices"][0]["message"]["content"] = "not json"
    with pytest.raises(InvalidResponse):
        validate_chat(broken, PHOTO_QS)
