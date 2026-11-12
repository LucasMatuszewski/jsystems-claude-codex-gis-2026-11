"""AC-23: counters in MD = HTML = results.json; per-attribute status sums = pairs; AC-26 zeros."""
import json
import re

from map_qa.report.model import ReportModel
from map_qa.report.render import write_outputs


def md_counters(md: str) -> dict[str, int]:
    # rows like: | speed | agree | zgodne | 12 |   (marker column `counter` key in first two cells)
    out = {}
    for attr, status, value in re.findall(r"^\| `(\w+)` \| `(\w+)` \| [^|]+ \| (\d+) \|$", md, re.MULTILINE):
        out[f"{attr}:{status}"] = int(value)
    return out


def html_counters(html: str) -> dict[str, int]:
    return {k: int(v) for k, v in re.findall(r'data-counter="([\w:]+)">(\d+)<', html)}


def test_counters_identical_everywhere(tmp_path, fixtures_dir, data_dir):
    model = ReportModel.model_validate_json((fixtures_dir / "report_model_min.json").read_text(encoding="utf-8"))
    out = tmp_path / "o"
    write_outputs(model, out, data_dir=data_dir, render_date="2026-11-12", extra_results={})
    md = (out / "report.md").read_text(encoding="utf-8")
    html = (out / "report.html").read_text(encoding="utf-8")
    js = json.loads((out / "results.json").read_text(encoding="utf-8"))["report"]
    from_json = {f"{c['attribute']}:{c['status']}": c["count"] for c in js["summary"]["status_counts"]}
    m, h = md_counters(md), html_counters(html)
    assert m and m == from_json
    assert {k: v for k, v in h.items() if k in from_json} == from_json
    for attr in ("speed", "surface"):
        total = sum(v for k, v in from_json.items() if k.startswith(attr + ":"))
        assert total == js["summary"]["pairs"]
    # AC-26: zero is a valid result and is shown as 0
    assert any(v == 0 for v in from_json.values())
