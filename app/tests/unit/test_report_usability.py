"""PRD §13 (2026-11-13): AC-27 thumbnail links, AC-28 glossary, AC-29 label provenance, AC-30 costs,
AC-31 executive summary."""
import json
import re

import pytest

from map_qa.photo_reading.budget import BudgetLedger
from map_qa.photo_reading.cache import DecisionCache
from map_qa.report.model import EvalRow, ModelSection, ReportModel
from map_qa.report.render import render_html, render_markdown, render_summary, write_outputs
from tests.unit.test_escalator import IMG, PHOTO_QS, cap, make

PROVENANCE = "nie zostały zweryfikowane przez człowieka"


@pytest.fixture()
def model(fixtures_dir) -> ReportModel:
    return ReportModel.model_validate_json((fixtures_dir / "report_model_min.json").read_text(encoding="utf-8"))


def with_model_run(model: ReportModel) -> ReportModel:
    m = model.model_copy(deep=True)
    m.model = ModelSection(run=True, question_set_version="qs-v1", requests_this_run=0, cost_this_run_usd=0.0,
                           answers_cost_usd=0.0123, answers_cost_by_model={"openai/gpt-6-luna-decisions": 0.01,
                                                                           "openai/gpt-6-luna": 0.0023},
                           cache_hits=12, max_requests=100, max_cost_usd=1.0,
                           evaluation=[EvalRow(question="surface", model="openai/gpt-6-luna-decisions", tier="tier 1",
                                               evaluated=10, correct=9, answered=10, abstained=0, unavailable=0,
                                               not_run=0, uncertain_excluded=1, accuracy_all="90.0% (9/10)",
                                               coverage="100.0% (10/10)", selective_accuracy="90.0% (9/10)")])
    return m


def test_glossary_in_both_reports(model):
    for text in (render_markdown(model, "2026-11-13"), render_html(model, "2026-11-13")):
        assert "Słowniczek" in text
        for term in ("Tier 1", "Tier 2", "abstain", "model_unavailable", "not_run_budget_or_error",
                     "not_comparable", "ambiguous_link"):
            assert term in text, term


def test_label_provenance_next_to_metrics(model):
    m = with_model_run(model)
    for text in (render_markdown(m, "2026-11-13"), render_html(m, "2026-11-13")):
        metrics = text.index("Metryki względem etykiet referencyjnych")
        assert PROVENANCE in text[metrics:metrics + 1500]
        assert "GLM-5.3-Flash" in text


def test_total_cost_including_cache(model):
    m = with_model_run(model)
    for text in (render_markdown(m, "2026-11-13"), render_html(m, "2026-11-13")):
        assert "łącznie z odpowiedziami z cache" in text and "0.0123" in text


def test_thumbnail_placeholder_links(model, tmp_path, data_dir):
    m = model.model_copy(deep=True)
    m.candidates[1].thumb.source = "Mapillary"
    m.candidates[1].thumb.source_url = "https://www.mapillary.com/app/?pKey=123"
    write_outputs(m, tmp_path, data_dir=data_dir, render_date="2026-11-13", extra_results={})
    html = (tmp_path / "report.html").read_text(encoding="utf-8")
    assert re.search(r'href="https://www\.mapillary\.com/app/\?pKey=123"[^>]*>zobacz zdjęcie \(Mapillary\)<', html)
    m.candidates[1].thumb.source = "Panoramax"
    m.candidates[1].thumb.source_url = "https://api.panoramax.xyz/api/collections/x/items/y"
    html = render_html(m, "2026-11-13")
    assert "metadane źródła (API Panoramax)" in html


def test_summary_is_static_polish_and_consistent(model, tmp_path, data_dir):
    m = with_model_run(model)
    write_outputs(m, tmp_path, data_dir=data_dir, render_date="2026-11-13", extra_results={})
    html = (tmp_path / "summary.html").read_text(encoding="utf-8")
    assert '<html lang="pl">' in html and "<script" not in html and 'src="http' not in html
    assert html.count("<svg") >= 2 and html.count("<details") >= 2  # charts + table views
    assert "prefers-color-scheme: dark" in html
    assert PROVENANCE in html
    assert f'data-kpi="pairs">{m.summary.pairs}<' in html
    for c in m.summary.status_counts:
        assert f'data-counter="{c.attribute}:{c.status}">{c.count}<' in html  # same counts as report (AC-23)
    assert "Najważniejsze wnioski" in html and "report.html" in html
    assert render_summary(m, "2026-11-13") == html


def test_escalator_tracks_original_cost_of_cached_answers(tmp_path):
    e, _, _ = make(tmp_path, [cap("decisions-luna-photo-200")])
    e.read("p1", "photo", IMG, PHOTO_QS)
    paid = sum(c.original_cost_usd for c in e.calls)
    assert paid > 0
    e2, client2, _ = make(tmp_path, [], run_id="r2")
    e2.read("p1", "photo", IMG, PHOTO_QS)
    assert client2.calls == [] and sum(c.cost_usd for c in e2.calls) == 0
    assert sum(c.original_cost_usd for c in e2.calls) == pytest.approx(paid)
    assert DecisionCache and BudgetLedger and json  # imports used
