"""Review page safety (PRD §14 AC-38, ADR-005 D-52; ADR-003 TAC-003-01)."""
from __future__ import annotations

import json
import re

from map_qa.review.export import render_page

EVIL = "</script><script>alert(1)</script> & <b>"


def data():
    return {"schema": "map-qa-review-data/1", "export_id": "abc", "exported_at": "2026-11-13T00:00:00Z",
            "question_set_version": "qs-v1", "thresholds": {"t1_threshold": 0.8, "t1_threshold_compare": 0.8, "tier2_accept": "high"}, "models": {},
            "images": {"s1": {"src": "images/s1.jpg", "attribution": {"author": EVIL}}},
            "items": [{"item_id": "p|surface", "comment": EVIL}], "stats": {}}


def test_data_is_embedded_escaped_and_round_trips():
    html = render_page(data())
    assert "<script>alert(1)" not in html and "<b>" not in html
    m = re.search(r'<script type="application/json" id="review-data">(.*?)</script>', html, re.S)
    assert m and json.loads(m.group(1))["images"]["s1"]["attribution"]["author"] == EVIL


def test_single_inline_script_no_external_resources():
    html = render_page(data())
    assert html.count("<script") == 2  # data block + inline app
    assert not re.search(r'<script[^>]+src=', html)
    assert not re.search(r'(src|href)="https?:', html)
    assert "fetch(" not in html and "XMLHttpRequest" not in html
    assert '<html lang="pl">' in html


def test_no_base64_blobs():
    assert not re.search(r"[A-Za-z0-9+/]{65,}={0,2}", render_page(data()))
