"""ADR-003 §8 'Kontrakt Decisions', 'Brak retry', 'Cache': real httpx client, respx replays the T43 captures."""
import json

import httpx
import pytest
import respx

from map_qa.photo_reading.budget import BudgetLedger
from map_qa.photo_reading.cache import DecisionCache
from map_qa.photo_reading.clients import OpenRouterClient, response_cost
from map_qa.photo_reading.escalator import Escalator, Settings
from map_qa.photo_reading.image import prepare_file
from tests.conftest import FIXTURES

DEC = "https://openrouter.ai/api/alpha/decisions"
CHAT = "https://openrouter.ai/api/v1/chat/completions"
CROP = "mapillary_1931009810597411"


def capture(name):
    doc = json.loads((FIXTURES / "captures" / f"{name}.json").read_text(encoding="utf-8"))
    return httpx.Response(doc["status"], json=doc["response_body"])


@pytest.fixture()
def image(data_dir):
    return prepare_file(data_dir / "signs" / "crops" / f"{CROP}.jpg")


def escalator(tmp_path, run_id="r1"):
    s = Settings("openai/gpt-6-luna-decisions", "typesafe/jev-1.14", "openai/gpt-6-luna", 0.80, 0.80, "high",
                 "qs-v1", 0.002, 0.004, 0.002)
    ledger = BudgetLedger(tmp_path / "ledger.jsonl", run_id, 100, 1.0)
    client = OpenRouterClient({"OPENROUTER_API_KEY": "sk-test"}, timeout_s=40)
    return Escalator(s, DecisionCache(tmp_path / "cache"), ledger, client), ledger, client


def test_real_flow_tier1_then_tier2(tmp_path, image):
    with respx.mock() as router:
        dec = router.post(DEC).mock(return_value=capture("decisions-luna-sign_crop-200"))
        chat = router.post(CHAT).mock(return_value=capture("chat-tier2-sign_crop-200"))
        e, ledger, client = escalator(tmp_path)
        r = e.read(CROP, "sign_crop", image, ["speed_limit_value"])[0]
        assert dec.call_count == 1 and chat.call_count == 1
        sent = json.loads(dec.calls[0].request.content)
        assert len(sent["state"]) == 2 and CROP not in dec.calls[0].request.content.decode()
        # AC-12 on the requests actually sent in the escalation flow (T51 review): values from this crop's
        # record in signs.csv / labels.csv / nearest_osm.csv must not appear in either tier's payload.
        for call in (dec.calls[0], chat.calls[0]):
            body = call.request.content.decode()
            for leak in (CROP, "1931009810597411", "jswk", "regulatory--maximum-speed-limit", "19.866218",
                         "50.064759", ".jpg", "\"certain\"", "187014751", "Wf9MDNQijUaEd5olsYVknw"):
                assert leak not in body, leak
    assert (r.decision, r.answer, r.tier) == ("answered_tier2", "20", 2)
    assert ledger.entries_for_run() == 2 == client.posts  # TAC-003-02
    expected = sum(response_cost(json.loads((FIXTURES / "captures" / f"{n}.json").read_text(encoding="utf-8"))
                                 ["response_body"]) for n in ("decisions-luna-sign_crop-200", "chat-tier2-sign_crop-200"))
    assert expected > 0 and ledger.spent_usd == pytest.approx(expected)  # BYOK upstream cost, not usage.cost=0


def test_second_run_zero_posts(tmp_path, image):
    with respx.mock() as router:
        router.post(DEC).mock(return_value=capture("decisions-luna-sign_crop-200"))
        router.post(CHAT).mock(return_value=capture("chat-tier2-sign_crop-200"))
        first = escalator(tmp_path)[0].read(CROP, "sign_crop", image, ["speed_limit_value"])
    with respx.mock(assert_all_called=False) as router:
        dec, chat = router.post(DEC), router.post(CHAT)
        e, ledger, client = escalator(tmp_path, run_id="r2")
        second = e.read(CROP, "sign_crop", image, ["speed_limit_value"])
        assert dec.call_count == 0 and chat.call_count == 0 and client.posts == 0
    assert [(r.decision, r.answer) for r in first] == [(r.decision, r.answer) for r in second]


@pytest.mark.parametrize("status", [400, 429, 500, 524, 529])
def test_error_no_retry(tmp_path, image, status):
    body = json.loads((FIXTURES / "captures" / "decisions-error-400.json").read_text(encoding="utf-8"))
    with respx.mock() as router:
        dec = router.post(DEC).mock(side_effect=[httpx.Response(status, json=body["response_body"]),
                                                 httpx.Response(200, json={})])
        e, ledger, _ = escalator(tmp_path)
        r = e.read(CROP, "sign_crop", image, ["speed_limit_value"])[0]
        again = e.read("other", "sign_crop", image, ["speed_limit_value"])[0]
        assert dec.call_count == 1  # exactly one request, no retry, breaker open
    assert r.decision == "model_unavailable" and r.reason == f"http_{status}"
    assert again.decision == "not_run_budget_or_error"


def test_timeout_no_retry(tmp_path, image):
    with respx.mock() as router:
        dec = router.post(DEC).mock(side_effect=httpx.ReadTimeout("t"))
        e, ledger, _ = escalator(tmp_path)
        r = e.read(CROP, "sign_crop", image, ["speed_limit_value"])[0]
        assert dec.call_count == 1
    assert r.decision == "model_unavailable" and r.reason == "timeout" and ledger.is_open
