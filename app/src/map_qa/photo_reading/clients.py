"""Raw httpx POST to OpenRouter (ADR-000 D-03; ADR-003 §5.1-5.4): 40 s timeout, no retries, no redirects.

The API key is read from OPENROUTER_API_KEY and only placed into the Authorization header here.
Responses are returned as data; no exception escapes (the escalator maps errors to model_unavailable).
"""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import httpx

BASE_URL = "https://openrouter.ai"
DECISIONS_PATH = "/api/alpha/decisions"
CHAT_PATH = "/api/v1/chat/completions"


@dataclass
class ApiResult:
    status: int | None
    body: Any = None
    headers: dict[str, str] = field(default_factory=dict)
    elapsed_ms: float = 0.0
    error_kind: str | None = None  # None | http | timeout | network | invalid_json | missing_key
    error_detail: str | None = None

    @property
    def ok(self) -> bool:
        return self.error_kind is None and self.status == 200


def response_cost(body: Any) -> float | None:
    """Conservative cost of one call: max(usage.cost, usage.cost_details.upstream_inference_cost).
    With BYOK keys OpenRouter reports usage.cost = 0 and the provider charge in cost_details (T43 captures)."""
    if not isinstance(body, dict):
        return None
    usage = body.get("usage") or {}
    values = [usage.get("cost"), (usage.get("cost_details") or {}).get("upstream_inference_cost")]
    nums = [float(v) for v in values if isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0]
    return max(nums) if nums else None


class OpenRouterClient:
    def __init__(self, env: dict[str, str], timeout_s: float = 40.0, transport: httpx.BaseTransport | None = None,
                 base_url: str = BASE_URL) -> None:
        self._key = env.get("OPENROUTER_API_KEY") or ""
        self.base_url = base_url
        self._client = httpx.Client(timeout=httpx.Timeout(timeout_s), follow_redirects=False,
                                    transport=transport or httpx.HTTPTransport(retries=0))
        self.posts = 0  # actual POSTs sent (TAC-003-02)

    def close(self) -> None:
        self._client.close()

    def post(self, path: str, payload: dict[str, Any]) -> ApiResult:
        if not self._key:
            return ApiResult(None, error_kind="missing_key", error_detail="Brak zmiennej OPENROUTER_API_KEY.")
        headers = {"Authorization": f"Bearer {self._key}", "Content-Type": "application/json"}
        t0 = time.monotonic()
        self.posts += 1
        try:
            resp = self._client.post(self.base_url + path, json=payload, headers=headers)
        except httpx.TimeoutException:
            return ApiResult(None, elapsed_ms=(time.monotonic() - t0) * 1000, error_kind="timeout",
                             error_detail="przekroczono limit czasu")
        except httpx.HTTPError as exc:
            return ApiResult(None, elapsed_ms=(time.monotonic() - t0) * 1000, error_kind="network",
                             error_detail=type(exc).__name__)
        elapsed = (time.monotonic() - t0) * 1000
        try:
            body = resp.json()
        except ValueError:
            body = {"raw_text": resp.text[:4000]}
            if resp.status_code == 200:
                return ApiResult(resp.status_code, body, dict(resp.headers), elapsed, "invalid_json")
        kind = None if resp.status_code == 200 else "http"
        detail = None
        if kind and isinstance(body, dict):
            err = body.get("error")
            detail = (err.get("message") if isinstance(err, dict) else str(err or ""))[:300] or None
        return ApiResult(resp.status_code, body, dict(resp.headers), elapsed, kind, detail)
