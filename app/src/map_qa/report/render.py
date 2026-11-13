"""Render ReportModel to report.md, report.html and results.json (ADR-004 §3.4-3.6)."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path
from typing import Any

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape

from map_qa.report.model import (
    ATTRIBUTE_LABELS, DECISION_LABELS, DISCLAIMER, GLOSSARY, LABEL_PROVENANCE, NOT_RUN, STATUS_LABELS, ReportModel,
)

SAFE_ID = re.compile(r"^[A-Za-z0-9_\-]+$")
RESULTS_SCHEMA_VERSION = 1


def md_escape(value: Any) -> str:
    """Markdown cell escaping: | ` < > escaped, newlines -> space (ADR-004 §3.6)."""
    if value is None:
        return ""
    text = str(value)
    text = text.replace("\\", "\\\\").replace("|", "\\|").replace("`", "\\`")
    text = text.replace("<", "&lt;").replace(">", "&gt;")
    return " ".join(text.replace("\r", "\n").split("\n")) if "\n" in text or "\r" in text else text


def safe_url(url: Any) -> str | None:
    """Only https links are allowed (http and javascript: are dropped)."""
    if not isinstance(url, str):
        return None
    u = url.strip()
    return u if u.lower().startswith("https://") else None


def fmt_num(value: Any, digits: int = 2) -> str:
    if value is None:
        return "–"
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def fmt_pct(value: Any) -> str:
    return "–" if value is None else f"{float(value):.1f}%"


def _common(env: Environment) -> Environment:
    env.filters.update(num=fmt_num, pct=fmt_pct, safe_url=safe_url)
    env.globals.update(STATUS_LABELS=STATUS_LABELS, ATTRIBUTE_LABELS=ATTRIBUTE_LABELS,
                       DECISION_LABELS=DECISION_LABELS, DISCLAIMER=DISCLAIMER, NOT_RUN=NOT_RUN,
                       GLOSSARY=GLOSSARY, LABEL_PROVENANCE=LABEL_PROVENANCE)
    return env


def _md_env() -> Environment:
    # finalize escapes every {{ }} output, so untrusted text can never break a table.
    env = Environment(loader=PackageLoader("map_qa", "templates"), autoescape=False, undefined=StrictUndefined,
                      finalize=md_escape, trim_blocks=True, lstrip_blocks=True, keep_trailing_newline=True)
    return _common(env)


def _html_env() -> Environment:
    env = Environment(loader=PackageLoader("map_qa", "templates"), autoescape=select_autoescape(["html", "j2"]),
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    return _common(env)


def render_markdown(model: ReportModel, render_date: str) -> str:
    return _md_env().get_template("report.md.j2").render(m=model, render_date=render_date)


def render_html(model: ReportModel, render_date: str) -> str:
    return _html_env().get_template("report.html.j2").render(m=model, render_date=render_date)


def render_summary(model: ReportModel, render_date: str) -> str:
    """One-page executive summary (PRD §13 AC-31); SVG markup is generated from escaped values only."""
    from map_qa.report.summary import summary_context
    return _html_env().get_template("summary.html.j2").render(m=model, s=summary_context(model),
                                                             render_date=render_date)


def thumbnail_source(data_dir: Path, photo_id: str, kind: str) -> Path | None:
    """ADR-004 §3.5 source order: data/photos, offline, signs/crops (sign crops)."""
    if not SAFE_ID.match(photo_id):
        return None
    candidates = ([data_dir / "signs" / "crops" / f"{photo_id}.jpg"] if kind == "sign_crop" else [
        data_dir / "data" / "photos" / f"{photo_id}.jpg", data_dir / "offline" / f"{photo_id}.jpg"])
    return next((p for p in candidates if p.is_file()), None)


def copy_thumbnails(model: ReportModel, out_dir: Path, data_dir: Path) -> list[Path]:
    """Copies thumbnails to out_dir/thumbs/<photo_id>.jpg; returns the input files read."""
    thumbs_dir = out_dir / "thumbs"
    read: list[Path] = []
    thumbs = [c.thumb for c in model.candidates]
    for thumb in thumbs:
        src = thumbnail_source(data_dir, thumb.photo_id, thumb.kind)
        if src is None:
            thumb.src = None
            continue
        thumbs_dir.mkdir(parents=True, exist_ok=True)
        dest = thumbs_dir / f"{thumb.photo_id}.jpg"
        if not dest.exists() or dest.stat().st_size != src.stat().st_size:
            shutil.copyfile(src, dest)
        thumb.src = f"thumbs/{thumb.photo_id}.jpg"
        if src not in read:
            read.append(src)
    return read


def results_document(model: ReportModel, extra_results: dict[str, Any]) -> dict[str, Any]:
    return {"schema_version": RESULTS_SCHEMA_VERSION, "report": model.model_dump(mode="json"), **extra_results}


def write_outputs(model: ReportModel, out_dir: Path, data_dir: Path, render_date: str,
                  extra_results: dict[str, Any], copy_thumbs: bool = True) -> list[Path]:
    """Writes report.md, report.html, results.json. Returns input files read (thumbnails)."""
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    read = copy_thumbnails(model, out_dir, Path(data_dir)) if copy_thumbs else []
    (out_dir / "report.md").write_text(render_markdown(model, render_date), encoding="utf-8", newline="\n")
    (out_dir / "report.html").write_text(render_html(model, render_date), encoding="utf-8", newline="\n")
    (out_dir / "summary.html").write_text(render_summary(model, render_date), encoding="utf-8", newline="\n")
    (out_dir / "results.json").write_text(
        json.dumps(results_document(model, extra_results), ensure_ascii=False, indent=1), encoding="utf-8",
        newline="\n")
    return read
