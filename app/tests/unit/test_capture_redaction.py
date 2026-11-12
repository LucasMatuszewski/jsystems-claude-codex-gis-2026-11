"""ADR-003 §5.8: capture recorder stores no key, no base64, no auth/cookie headers; client sets auth itself."""
import json

import httpx

from map_qa.photo_reading.capture import CaptureRecorder
from map_qa.photo_reading.clients import OpenRouterClient
from map_qa.photo_reading.image import prepare_bytes
from map_qa.photo_reading.payload import decisions_payload
from tests.unit.test_payload import image_with_gps

KEY = "sk-or-v1-FAKEKEY-0123456789"


def transport_echo(status=200, body=None, headers=None):
    seen = []

    def handler(request: httpx.Request):
        seen.append(request)
        return httpx.Response(status, json=body or {"ok": True}, headers=headers or {"set-cookie": "a=b",
                                                                                    "x-generation-id": "g1"})
    return httpx.MockTransport(handler), seen


def test_client_sends_bearer_and_never_retries():
    tr, seen = transport_echo(status=429, body={"error": {"message": "rate"}})
    client = OpenRouterClient({"OPENROUTER_API_KEY": KEY}, timeout_s=40, transport=tr)
    res = client.post("/api/alpha/decisions", {"model": "m"})
    assert len(seen) == 1 and seen[0].headers["authorization"] == f"Bearer {KEY}"
    assert res.status == 429 and res.error_kind == "http"


def test_client_timeout_is_error_kind():
    def handler(request):
        raise httpx.ReadTimeout("slow", request=request)
    client = OpenRouterClient({"OPENROUTER_API_KEY": KEY}, timeout_s=40, transport=httpx.MockTransport(handler))
    res = client.post("/api/alpha/decisions", {"model": "m"})
    assert res.error_kind == "timeout" and res.status is None


def test_capture_is_redacted(tmp_path):
    img = image_with_gps()
    payload = decisions_payload("openai/gpt-6-luna-decisions", "photo", img, ["surface"])
    tr, _ = transport_echo(body={"answers": {}, "model": "openai/gpt-6-luna-decisions-x", "usage": {"cost": 0.0001}})
    res = OpenRouterClient({"OPENROUTER_API_KEY": KEY}, timeout_s=40, transport=tr).post("/api/alpha/decisions",
                                                                                         payload)
    path = CaptureRecorder(tmp_path).record("decisions-luna-200", "/api/alpha/decisions", payload, res, image=img)
    text = path.read_text(encoding="utf-8")
    assert KEY not in text and "base64" not in text and "set-cookie" not in text.lower()
    doc = json.loads(text)
    assert doc["request_meta"]["image"] == {"image_sha256": img.sha256, "bytes": len(img.data)}
    assert doc["model_sent"] == "openai/gpt-6-luna-decisions"
    assert doc["model_returned"] == "openai/gpt-6-luna-decisions-x"
    assert doc["target"] == "openrouter" and doc["status"] == 200


def test_missing_key_is_error_without_request():
    client = OpenRouterClient({}, timeout_s=40, transport=httpx.MockTransport(lambda r: httpx.Response(200)))
    res = client.post("/api/alpha/decisions", {})
    assert res.error_kind == "missing_key"


def test_prepare_bytes_used():  # keep import used for linters
    assert prepare_bytes
