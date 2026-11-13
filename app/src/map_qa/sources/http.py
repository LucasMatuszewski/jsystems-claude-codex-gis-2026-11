"""Shared httpx client policy (ADR-000 D-03): 40 s timeouts, no retries, no redirects."""
from __future__ import annotations

import httpx


def make_client(timeout_s: float = 40.0) -> httpx.Client:
    # httpx.HTTPTransport(retries=0) is the default; set explicitly so no hidden retry exists.
    return httpx.Client(timeout=httpx.Timeout(timeout_s), transport=httpx.HTTPTransport(retries=0),
                        follow_redirects=False)
