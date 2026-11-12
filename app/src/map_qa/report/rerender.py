"""`map-qa report --from results.json`: re-render without network (ADR-004 §3.1)."""
from __future__ import annotations

import json
import shutil
from datetime import date
from pathlib import Path
from typing import TextIO

from pydantic import ValidationError

from map_qa.core.errors import ConfigError
from map_qa.report.model import ReportModel
from map_qa.report.render import render_html, render_markdown


def rerender(results_path: str | Path, output_dir: str | Path | None, out: TextIO,
             render_date: str | None = None) -> int:
    src = Path(results_path)
    try:
        doc = json.loads(src.read_text(encoding="utf-8"))
        model = ReportModel.model_validate(doc["report"])
    except FileNotFoundError:
        raise ConfigError(f"Nie znaleziono pliku wyników: {src}.") from None
    except (json.JSONDecodeError, KeyError, TypeError, ValidationError):
        raise ConfigError(f"Plik {src} nie jest poprawnym plikiem results.json map-qa.") from None
    dest = Path(output_dir) if output_dir else src.parent
    dest.mkdir(parents=True, exist_ok=True)
    if dest.resolve() != src.parent.resolve():
        for c in model.candidates:  # keep relative thumbnails working in the new location
            if c.thumb.src and (src.parent / c.thumb.src).is_file():
                (dest / "thumbs").mkdir(exist_ok=True)
                shutil.copyfile(src.parent / c.thumb.src, dest / c.thumb.src)
    when = render_date or date.today().isoformat()
    (dest / "report.md").write_text(render_markdown(model, when), encoding="utf-8", newline="\n")
    (dest / "report.html").write_text(render_html(model, when), encoding="utf-8", newline="\n")
    out.write(f"Zapisano: {dest / 'report.md'}\nZapisano: {dest / 'report.html'}\nKod wyjścia: 0\n")
    return 0
