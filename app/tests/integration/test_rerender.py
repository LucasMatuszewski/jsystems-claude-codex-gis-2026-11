"""ADR-004 §3.1, §8 'Re-render': report.md identical byte-for-byte except the render date."""
import io

from map_qa.report.model import ReportModel
from map_qa.report.render import write_outputs
from map_qa.report.rerender import rerender


def test_rerender_identical_except_render_date(tmp_path, fixtures_dir, data_dir):
    model = ReportModel.model_validate_json((fixtures_dir / "report_model_min.json").read_text(encoding="utf-8"))
    first = tmp_path / "first"
    write_outputs(model, first, data_dir=data_dir, render_date="2026-11-01", extra_results={"pairs": []})
    original_md = (first / "report.md").read_text(encoding="utf-8")
    original_html = (first / "report.html").read_text(encoding="utf-8")

    second = tmp_path / "second"
    out = io.StringIO()
    code = rerender(first / "results.json", second, out=out, render_date="2030-01-02")
    assert code == 0
    new_md = (second / "report.md").read_text(encoding="utf-8")
    assert new_md != original_md
    assert new_md.replace("2030-01-02", "2026-11-01") == original_md
    assert (second / "report.html").read_text(encoding="utf-8").replace("2030-01-02", "2026-11-01") == original_html
    assert "report.md" in out.getvalue()


def test_rerender_default_output_is_results_dir(tmp_path, fixtures_dir, data_dir):
    model = ReportModel.model_validate_json((fixtures_dir / "report_model_min.json").read_text(encoding="utf-8"))
    write_outputs(model, tmp_path, data_dir=data_dir, render_date="2026-11-01", extra_results={})
    before = (tmp_path / "results.json").read_bytes()
    assert rerender(tmp_path / "results.json", None, out=io.StringIO(), render_date="2026-11-01") == 0
    assert (tmp_path / "results.json").read_bytes() == before  # source of truth untouched


def test_missing_or_invalid_results_is_config_error(tmp_path):
    import pytest

    from map_qa.core.errors import ConfigError
    with pytest.raises(ConfigError):
        rerender(tmp_path / "nope.json", None, out=io.StringIO())
    bad = tmp_path / "bad.json"
    bad.write_text("{}", encoding="utf-8")
    with pytest.raises(ConfigError):
        rerender(bad, None, out=io.StringIO())


def test_rerender_real_run_results(tmp_path, fixtures_dir):
    """results.json captured from a real `map-qa run` on files (2026-11-12, T22 state)."""
    src = fixtures_dir / "results_real_run.json"
    a, b = tmp_path / "a", tmp_path / "b"
    assert rerender(src, a, out=io.StringIO(), render_date="2030-01-02") == 0
    assert rerender(src, b, out=io.StringIO(), render_date="2030-03-04") == 0
    md_a = (a / "report.md").read_text(encoding="utf-8")
    assert md_a == (b / "report.md").read_text(encoding="utf-8").replace("2030-03-04", "2030-01-02")
    assert "Źródło danych: pliki lokalne" in md_a and "| `speed` | `agree` | zgodne | 391 |" in md_a
