"""E2E (no mocks): `map-qa run` on local files (PRD AC-01, AC-04, AC-21, AC-23; ADR-000 TAC-02, TAC-03)."""
import json
import re
import subprocess
import time

import pytest

from conftest import REPO_ROOT, cli_env
from map_qa.core.paths import sha256_file

INPUTS = ["osm_roads.parquet", "overture_segments.parquet", "photos.csv", "photo_road_links.csv",
          "signs/signs.csv", "signs/nearest_osm.csv", "sources.json", "reference_labels.csv", "signs/labels.csv"]


@pytest.fixture(scope="module")
def run_result(tmp_path_factory, data_dir):
    out = tmp_path_factory.mktemp("report")
    before = {f: sha256_file(data_dir / f) for f in INPUTS}
    t0 = time.monotonic()
    proc = subprocess.run(["uv", "run", "--project", "app", "map-qa", "run", "--output-dir", str(out)],
                          cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", env=cli_env(),
                          timeout=300)
    elapsed = time.monotonic() - t0
    after = {f: sha256_file(data_dir / f) for f in INPUTS}
    return proc, out, elapsed, before, after


def test_exit_zero_and_four_files(run_result):
    proc, out, elapsed, *_ = run_result
    assert proc.returncode == 0, proc.stderr
    for name in ("report.md", "report.html", "results.json", "run_manifest.json"):
        assert (out / name).is_file(), name
    assert elapsed < 120  # TAC-02
    assert str(out / "report.md") in proc.stdout and str(out / "report.html") in proc.stdout


def test_header_source_and_snapshots(run_result):
    _, out, *_ = run_result
    for name in ("report.md", "report.html"):
        text = (out / name).read_text(encoding="utf-8")
        assert "Źródło danych: pliki lokalne" in text
        assert "2026-11-01" in text and "2026-10-21.0" in text
        assert "Odczyt modelem nie był uruchomiony" in text


def test_inputs_unchanged(run_result):
    *_, before, after = run_result
    assert before == after  # AC-04


def test_run_manifest_has_hashes_and_no_model_requests(run_result, data_dir):
    _, out, *_ = run_result
    man = json.loads((out / "run_manifest.json").read_text(encoding="utf-8"))
    names = {f["name"]: f for f in man["input_manifest"]["files"]}
    for f in ("osm_roads.parquet", "overture_segments.parquet", "photos.csv", "photo_road_links.csv"):
        assert names[f]["sha256"] == sha256_file(data_dir / f)
    assert man["model_requests"] == 0 and man["config"]["source"] == "files"
    assert "versions" in man and man["versions"]["duckdb"] == "1.5.6"
    thumbs = [n for n in names if n.startswith("offline/") or n.startswith("data/photos/")]
    assert thumbs, "copied thumbnails are listed as read inputs (ADR-001 §3.2)"


def test_counts_consistent_and_stdout_summary(run_result):
    proc, out, *_ = run_result
    res = json.loads((out / "results.json").read_text(encoding="utf-8"))
    summary = res["report"]["summary"]
    assert summary["pairs"] == 558 and summary["photos"] == 561 and summary["no_candidate"] == 3
    for attr in ("speed", "surface"):
        total = sum(c["count"] for c in summary["status_counts"] if c["attribute"] == attr)
        assert total == summary["pairs"]
    assert len(res["pairs"]) == 558
    html = (out / "report.html").read_text(encoding="utf-8")
    md = (out / "report.md").read_text(encoding="utf-8")
    for c in summary["status_counts"]:
        assert f'data-counter="{c["attribute"]}:{c["status"]}">{c["count"]}<' in html
        assert re.search(rf"^\| `{c['attribute']}` \| `{c['status']}` \| [^|]+ \| {c['count']} \|$", md, re.M)
    assert "agree" in proc.stdout and "Kod wyjścia: 0" in proc.stdout


def test_completeness_and_surface_in_report(run_result):
    _, out, *_ = run_result
    res = json.loads((out / "results.json").read_text(encoding="utf-8"))
    comp = res["report"]["summary"]["completeness"]
    assert {(r["source"], r["attribute"]) for r in comp} >= {("osm", "maxspeed*"), ("overture", "road_surface")}
    md = (out / "report.md").read_text(encoding="utf-8")
    assert "| osm | maxspeed* | wszystkie drogi |" in md and "drogi ze zdjęciem" in md
    assert "Nawierzchnia: rozbieżne" in md
    assert len(res["comparisons"]) == 2 * res["report"]["summary"]["pairs"]
