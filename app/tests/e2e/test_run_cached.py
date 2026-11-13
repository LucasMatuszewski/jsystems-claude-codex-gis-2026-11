"""E2E with REAL OpenRouter endpoints (no mocks; ADR-000 §10 user rule): `map-qa run --model-reading --yes`
on an empty cache, then the same run again from cache (0 new requests, identical predictions).

PRD AC-12..AC-20, AC-22, AC-24, AC-26; ADR-003 TAC-003-01, TAC-003-02, TAC-003-04.
"""
import json
import os
import re
import shutil
import subprocess

import pytest

from tests.conftest import DATA_DIR, REPO_ROOT, cli_env

pytestmark = [pytest.mark.real_api, pytest.mark.slow]
if not os.environ.get("OPENROUTER_API_KEY"):
    pytest.skip("missing_capture: OPENROUTER_API_KEY not set (real endpoints required)", allow_module_level=True)


def run(config, out):
    return subprocess.run(["uv", "run", "--project", "app", "map-qa", "run", "--config", str(config),
                           "--model-reading", "--yes", "--output-dir", str(out)],
                          cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", env=cli_env(),
                          timeout=900)


@pytest.fixture(scope="module")
def runs(tmp_path_factory):
    base = tmp_path_factory.mktemp("model_run")
    work = base / "work"
    shutil.copytree(DATA_DIR / "data" / ".duckdb_extensions", work / ".duckdb_extensions")
    config = base / "cfg.toml"
    config.write_text(f'data_dir = "{DATA_DIR.as_posix()}"\nwork_dir = "{work.as_posix()}"\n', encoding="utf-8")
    first = run(config, base / "out1")
    second = run(config, base / "out2")
    return base, work, first, second


def load(out, name):
    return json.loads((out / name).read_text(encoding="utf-8"))


def readings(out):
    return [(r["photo_id"], r["question"], r["decision"], r["answer"], r["tier"])
            for r in load(out, "results.json")["report"]["model"]["readings"]]


def test_first_run_real_calls_within_limits(runs):
    base, work, first, _ = runs
    assert first.returncode == 0, first.stderr
    man = load(base / "out1", "run_manifest.json")
    assert 0 < man["model_requests"] <= 100 and man["model_cost_usd"] < 1.0  # AC-13
    model = load(base / "out1", "results.json")["report"]["model"]
    assert model["run"] is True and model["requests_this_run"] == man["model_requests"]
    entries = [json.loads(x) for x in (work / "ledger.jsonl").read_text(encoding="utf-8").splitlines()]
    assert sum(1 for e in entries if e["run_id"] == man["run_id"]) == man["model_requests"]  # TAC-003-02


def test_one_reading_per_image_and_question(runs):
    base, *_ = runs
    sample = load(base / "out1", "sample_manifest.json")
    expected = {(i["photo_id"], q) for i in sample["items"] for q in i["questions"]}
    got = readings(base / "out1")
    assert len(got) == len(expected) and {(p, q) for p, q, *_ in got} == expected  # TAC-003-04
    allowed = {"answered", "answered_tier2", "abstain", "model_unavailable", "not_run_budget_or_error"}
    assert {d for _, _, d, _, _ in got} <= allowed
    assert len(sample["items"]) <= 25
    assert "certain" not in json.dumps(sample)  # ids and paths only


def test_second_run_from_cache_zero_requests_same_predictions(runs):
    base, _, _, second = runs
    assert second.returncode == 0, second.stderr
    assert load(base / "out2", "run_manifest.json")["model_requests"] == 0  # AC-18
    assert readings(base / "out2") == readings(base / "out1")
    md = (base / "out2" / "report.md").read_text(encoding="utf-8")
    assert "W tym uruchomieniu nie wykonano nowych żądań (licznik żądań = 0)." in md


def test_report_sections_and_separation(runs):
    base, *_ = runs
    md = (base / "out1" / "report.md").read_text(encoding="utf-8")
    html = (base / "out1" / "report.html").read_text(encoding="utf-8")
    for text in (md, html):
        assert "Metryki względem etykiet referencyjnych" in text           # labels section
        assert "Predykcje (osobno" in text                                  # predictions section
        assert "Odczyt zdjęcia obok wartości mapy" in text                  # map observations
        assert "Porównanie modeli decyzyjnych na 5 obrazach" in text        # AC-15
        assert "Odczyt modelem nie był uruchomiony" not in text
        assert "Mapillary – metadane pochodne, ODbL 1.0" in text
    model = load(base / "out1", "results.json")["report"]["model"]
    assert len({(r["photo_id"]) for r in model["comparison"]}) == 5
    assert all(r["label_status"] in ("certain", "uncertain", None) for r in model["readings"])  # AC-24 column


def test_no_secrets_and_no_long_base64_anywhere(runs):
    base, work, *_ = runs
    key = os.environ["OPENROUTER_API_KEY"]
    for root in (base / "out1", base / "out2", work / "cache", work):
        for p in root.rglob("*"):
            if p.is_file() and p.suffix in (".json", ".jsonl", ".md", ".html"):
                text = p.read_text(encoding="utf-8")
                assert key not in text, p
                assert not re.search(r"[A-Za-z0-9+/]{65,}={0,2}", re.sub(r"https?://\S+", "", text)), p
