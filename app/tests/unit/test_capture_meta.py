"""ADR-000 TAC-05 meta test: every capture fixture has the ADR-003 §5.8 fields and no secret headers."""
import hashlib
import json
import re

import pytest

from map_qa.core.capture import REQUIRED_FIELDS, build_capture, mask_host, redact_presigned, scrub
from conftest import FIXTURES

CAPTURES = sorted((FIXTURES / "captures").glob("*.json"))


@pytest.mark.parametrize("path", CAPTURES, ids=lambda p: p.name)
def test_capture_has_required_fields_and_no_secrets(path):
    doc = json.loads(path.read_text(encoding="utf-8"))
    for f in REQUIRED_FIELDS:
        assert f in doc, f
    headers = {k.lower() for k in doc["response_headers"]}
    assert "authorization" not in headers and "set-cookie" not in headers
    text = path.read_text(encoding="utf-8")
    assert not re.search(r"data:image/[a-z]+;base64,", text)
    assert "X-Amz-Signature" not in text and "Bearer " not in text
    if doc.get("body_file"):
        body = (path.parent / doc["body_file"]).read_bytes()
        assert hashlib.sha256(body).hexdigest() == doc["body_sha256"]


def test_there_are_captures():
    assert CAPTURES


def test_helpers():
    assert mask_host("https://dbc-12ab.cloud.databricks.com") == "*.cloud.databricks.com"
    assert redact_presigned("https://s.example/x?sig=abc&exp=1") == "https://s.example/x?<redacted-presigned-query>"
    s = scrub({"u": "data:image/jpeg;base64,QUJD", "external_link": "https://a/b?c=d"})
    assert "base64" not in s["u"] and s["external_link"].endswith("<redacted-presigned-query>")
    doc = build_capture(target="openrouter", endpoint="/x", method="POST", status=200,
                        response_headers={"Set-Cookie": "a", "Authorization": "b", "X-Ok": "1"},
                        response_body={}, elapsed_ms=1, request_meta={}, client_version="t")
    assert doc["response_headers"] == {"x-ok": "1"}
