"""E2E: `map-qa review export` on the real cache of the last model run (PRD §14 AC-32, AC-33, AC-38).

No model request is possible here: the export uses only cached answers (ADR-005 D-51).
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path

import pytest

from tests.conftest import DATA_DIR, REPO_ROOT, cli_env

CACHE = DATA_DIR / "data" / "cache" / "decisions"
LEDGER = DATA_DIR / "data" / "ledger.jsonl"
if not CACHE.is_dir() or not any(CACHE.iterdir()):
    pytest.skip("missing_capture: no cached model answers; run `map-qa run --model-reading` first",
                allow_module_level=True)


def _sha(p: Path) -> str | None:
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None


@pytest.fixture(scope="module")
def export(tmp_path_factory):
    out = tmp_path_factory.mktemp("review_out")
    before = _sha(LEDGER)
    proc = subprocess.run(["uv", "run", "--project", "app", "map-qa", "review", "export", "--output-dir", str(out)],
                          cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
                          env=cli_env(OPENROUTER_API_KEY=""), timeout=600)
    return out, proc, before


def page_data(out: Path) -> dict:
    html = (out / "review" / "review.html").read_text(encoding="utf-8")
    m = re.search(r'<script type="application/json" id="review-data">(.*?)</script>', html, re.S)
    return json.loads(m.group(1))


def test_export_succeeds_without_key_and_without_requests(export):
    out, proc, before = export
    assert proc.returncode == 0, proc.stderr
    assert _sha(LEDGER) == before  # nothing written to the real ledger
    assert "review.html" in proc.stdout


def test_items_cover_the_sample_with_existing_images(export):
    out, _, _ = export
    d = page_data(out)
    assert d["schema"] == "map-qa-review-data/1" and d["question_set_version"] == "qs-v1"
    assert 0 < len(d["items"]) <= 100
    assert d["stats"]["selected"] == len(d["items"])
    for it in d["items"]:
        img = d["images"][it["image_sha256"]]
        assert (out / "review" / img["src"]).is_file()
        assert img["prepared_size"][0] >= 1 and img["original_size"][0] >= 1
        assert img["attribution"]["license"]
        assert img["requests"]["tier1"]["state"][1]["image_url"] == "<image>"
        roles = [r["role"] for r in it["rows"]]
        assert roles[0] == "tier1" and roles[-2:] == ["final", "reference_label"]
    crops = [d["images"][it["image_sha256"]] for it in d["items"] if it["kind"] == "sign_crop"]
    assert crops and any(c.get("context") for c in crops)
    for c in crops:
        if c.get("context"):
            assert (out / "review" / c["context"]["src"]).is_file()


def test_review_outputs_contain_no_base64(export):
    out, _, _ = export
    for p in (out / "review").rglob("*"):
        if p.suffix in (".html", ".json"):
            assert not re.search(r"[A-Za-z0-9+/]{65,}={0,2}", p.read_text(encoding="utf-8")), p
