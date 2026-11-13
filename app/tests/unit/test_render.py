"""ADR-004 §3.4-3.6, §8, TAC-004-01/02; PRD AC-22, AC-24, AC-25, AC-26 (fixture model only)."""
import json
import re

import pytest

from map_qa.report.model import ReportModel
from map_qa.report.render import md_escape, render_html, render_markdown, safe_url, write_outputs


@pytest.fixture()
def model(fixtures_dir) -> ReportModel:
    return ReportModel.model_validate_json((fixtures_dir / "report_model_min.json").read_text(encoding="utf-8"))


def test_html_escapes_untrusted_text(model):
    html = render_html(model, render_date="2026-11-12")
    assert "<script>alert(1)</script>" not in html
    assert "&lt;script&gt;" in html
    assert "<script" not in html  # TAC-004-01
    assert 'src="http' not in html


def test_html_is_polish_utf8_static(model):
    html = render_html(model, render_date="2026-11-12")
    assert '<html lang="pl">' in html and '<meta charset="utf-8">' in html
    assert "Źródło danych: pliki lokalne" in html
    assert "Odczyt zdjęcia jest predykcją modelu, a nie weryfikacją terenową." in html
    assert "© OpenStreetMap contributors, ODbL 1.0" in html
    assert "Overture Maps Foundation, ODbL 1.0 (release 2026-10-21.0)" in html


def test_markdown_table_not_broken_by_pipe(model):
    md = render_markdown(model, render_date="2026-11-12")
    assert "Jan \\| Kowalski" in md
    assert "Źródło danych: pliki lokalne" in md


def test_md_escape():
    assert md_escape("a|b`c<d>e\nf") == "a\\|b\\`c&lt;d&gt;e f"


@pytest.mark.parametrize("url,ok", [("https://x.org/a", True), ("http://x.org", False),
                                    ("javascript:alert(1)", False), (None, False), ("JAVASCRIPT:x", False)])
def test_only_https_links(url, ok):
    assert (safe_url(url) is not None) == ok


def test_javascript_link_removed_and_rel_set(model):
    html = render_html(model, render_date="2026-11-12")
    assert "javascript:" not in html.lower()
    for a in re.findall(r"<a [^>]*>", html):
        assert 'rel="noopener noreferrer"' in a


def test_empty_categories_show_brak_kandydatow(model):
    md = render_markdown(model, render_date="2026-11-12")
    html = render_html(model, render_date="2026-11-12")
    assert "Brak kandydatów" in md and "Brak kandydatów" in html


def test_no_model_run_sections(model):
    md = render_markdown(model, render_date="2026-11-12")
    html = render_html(model, render_date="2026-11-12")
    assert md.count("Odczyt modelem nie był uruchomiony") >= 2
    assert html.count("Odczyt modelem nie był uruchomiony") >= 2


def test_thumbnails_copied_or_placeholder(model, tmp_path, data_dir):
    out = tmp_path / "out"
    write_outputs(model, out, data_dir=data_dir, render_date="2026-11-12", extra_results={})
    html = (out / "report.html").read_text(encoding="utf-8")
    srcs = re.findall(r'<img [^>]*src="([^"]+)"', html)
    assert srcs, "fixture has one pair with an offline thumbnail"
    for src in srcs:
        assert re.fullmatch(r"thumbs/[A-Za-z0-9_\-]+\.jpg", src)
        assert (out / src).is_file()  # TAC-004-02
    assert "Miniatura niedostępna" in html
    assert "base64" not in html
    # attribution under the thumbnail (AC-22)
    assert "CC-BY-SA-4.0" in html and "Panoramax" in html
    assert set(p.name for p in out.iterdir()) >= {"report.md", "report.html", "results.json"}
    results = json.loads((out / "results.json").read_text(encoding="utf-8"))
    assert results["report"]["summary"]["pairs"] == model.summary.pairs


def test_sections_are_separate_and_labelled(model):
    md = render_markdown(model, render_date="2026-11-12")
    for heading in ("## 1. Nagłówek", "## 2. Podsumowanie", "## 3. Kandydaci do przeglądu",
                    "## 4. Kolejka ręczna", "## 5. Ewaluacja modelu", "## 6. Ograniczenia i atrybucja"):
        assert heading in md
