"""Capture documents (ADR-003 §5.8 schema, shared by OpenRouter and Databricks; ADR-000 TAC-05).

Pure functions: no network. Secrets never enter a capture: request headers are not stored, response headers
drop authorization/cookies, base64 images are replaced by their hash, presigned URL query strings are redacted.
"""
from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

REQUIRED_FIELDS = ("captured_at", "target", "endpoint", "method", "model_sent", "model_returned", "client_version",
                   "request_meta", "status", "response_headers", "response_body", "elapsed_ms")
DROP_HEADERS = {"set-cookie", "authorization", "cookie", "proxy-authorization", "x-databricks-org-id"}
DATA_URL = re.compile(r"data:image/[a-z]+;base64,[A-Za-z0-9+/=]+")
REDACTED = "<redacted-presigned-query>"


def mask_host(host: str) -> str:
    """https://dbc-1234.cloud.databricks.com -> *.cloud.databricks.com"""
    netloc = urlsplit(host if "://" in host else f"https://{host}").hostname or host
    parts = netloc.split(".")
    return "*." + ".".join(parts[1:]) if len(parts) > 2 else netloc


def safe_headers(headers: dict[str, str]) -> dict[str, str]:
    return {k.lower(): v for k, v in headers.items() if k.lower() not in DROP_HEADERS}


def redact_presigned(url: str) -> str:
    parts = urlsplit(url)
    if not parts.query:
        return url
    return urlunsplit((parts.scheme, parts.netloc, parts.path, REDACTED, ""))


def scrub(value: Any) -> Any:
    """Replace data URLs by hash, redact presigned query strings, recursively."""
    if isinstance(value, dict):
        out = {}
        for k, v in value.items():
            if k == "external_link" and isinstance(v, str):
                out[k] = redact_presigned(v)
            elif k == "http_headers" and isinstance(v, dict):
                out[k] = {hk: "<redacted>" for hk in v}
            else:
                out[k] = scrub(v)
        return out
    if isinstance(value, list):
        return [scrub(v) for v in value]
    if isinstance(value, str) and DATA_URL.search(value):
        return DATA_URL.sub(lambda m: f"<image sha256={hashlib.sha256(m.group(0).encode()).hexdigest()}>", value)
    return value


def build_capture(*, target: str, endpoint: str, method: str, status: int, response_headers: dict[str, str],
                  response_body: Any, elapsed_ms: float, request_meta: dict[str, Any], client_version: str,
                  model_sent: str | None = None, model_returned: str | None = None,
                  body_file: str | None = None, body_sha256: str | None = None) -> dict[str, Any]:
    doc = {
        "captured_at": datetime.now(UTC).isoformat(timespec="seconds"),
        "target": target, "endpoint": endpoint, "method": method,
        "model_sent": model_sent, "model_returned": model_returned, "client_version": client_version,
        "request_meta": scrub(request_meta), "status": status, "response_headers": safe_headers(response_headers),
        "response_body": scrub(response_body), "elapsed_ms": round(elapsed_ms, 1),
    }
    if body_file:
        doc["body_file"] = body_file
        doc["body_sha256"] = body_sha256
    return doc


def write_capture(doc: dict[str, Any], path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, ensure_ascii=False, indent=1) + "\n", encoding="utf-8", newline="\n")
    return path
