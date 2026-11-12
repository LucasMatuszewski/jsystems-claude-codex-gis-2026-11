"""Command-line entry point (ADR-004 §3.1-§3.3, §5; D-41: argparse, testable main(argv) -> int)."""
from __future__ import annotations

import argparse
import io
import os
import sys
from typing import Callable, TextIO

from map_qa.core.config import load_config
from map_qa.core.errors import MapQaError


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="map-qa",
        description="Porównanie atrybutów dróg OSM i Overture ze zdjęciami ulic (Kraków).",
    )
    sub = parser.add_subparsers(dest="command", metavar="{run,report,capture}")

    run = sub.add_parser("run", help="Pełny pipeline i raport")
    run.add_argument("--config", help="Plik TOML (lub MAP_QA_CONFIG)")
    run.add_argument("--source", choices=["files", "databricks"], help="Źródło danych (lub MAP_QA_SOURCE)")
    run.add_argument("--output-dir", help="Katalog wyników (domyślnie reports/map-qa)")
    run.add_argument("--model-reading", action="store_true", default=None, help="Włącz płatny odczyt zdjęć")
    run.add_argument("--yes", action="store_true", default=None, help="Potwierdź płatne wywołania bez pytania")
    run.add_argument("--max-requests", type=int, help="Limit żądań do modeli (domyślnie 100)")
    run.add_argument("--max-cost-usd", type=float, help="Limit kosztu w USD (domyślnie 1.00)")
    run.add_argument("--compare-sources", action="store_true", default=None,
                     help="Porównaj liczności i klucze obu źródeł")
    run.add_argument("--t1-threshold", type=float, help="Próg tier 1 dla modelu głównego")
    run.add_argument("--t1-threshold-compare", type=float, help="Próg tier 1 dla modelu porównawczego")
    run.add_argument("--tier2-accept", choices=["high", "medium", "low"], help="Akceptowana pewność tier 2")

    rep = sub.add_parser("report", help="Ponowne renderowanie raportu z results.json")
    rep.add_argument("--from", dest="from_path", required=True, help="Ścieżka do results.json")
    rep.add_argument("--output-dir", help="Katalog wyników (domyślnie katalog pliku results.json)")

    cap = sub.add_parser("capture", help="Jedno rzeczywiste żądanie API i zapis capture")
    cap.add_argument("--kind", required=True, choices=["decisions-luna", "decisions-jev", "chat-tier2", "databricks"])
    cap.add_argument("--config", help="Plik TOML (lub MAP_QA_CONFIG)")
    cap.add_argument("--yes", action="store_true", default=None, help="Potwierdź bez pytania")
    cap.add_argument("--image", help="photo_id obrazu do capture (domyślnie pierwszy z próbki)")
    cap.add_argument("--name", help="Nazwa pliku capture (bez .json)")
    cap.add_argument("--captures-dir", help="Katalog capture (domyślnie app/tests/fixtures/captures)")
    return parser


RUN_KEYS = {"config": "config", "source": "source", "output_dir": "output_dir", "model_reading": "model_reading",
            "yes": "yes", "max_requests": "max_requests", "max_cost_usd": "max_cost_usd",
            "compare_sources": "compare_sources", "t1_threshold": "t1_threshold",
            "t1_threshold_compare": "t1_threshold_compare", "tier2_accept": "tier2_accept"}


def main(argv: list[str] | None = None, *, env: dict[str, str] | None = None, stdout: TextIO | None = None,
         stderr: TextIO | None = None, ask: Callable[[str], str] | None = None) -> int:
    env = dict(os.environ) if env is None else env
    out = stdout or sys.stdout
    err = stderr or sys.stderr
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help(out)
        return 2
    try:
        if args.command == "run":
            from map_qa.pipeline import RunContext, run
            cli = {k: getattr(args, a) for a, k in RUN_KEYS.items()}
            cfg = load_config(cli, env)
            ctx = RunContext(cfg=cfg, env=env, out=out, err=err, ask=ask or input)
            return run(ctx)
        if args.command == "report":
            from map_qa.report.rerender import rerender
            return rerender(args.from_path, args.output_dir, out=out)
        if args.command == "capture":
            from map_qa.photo_reading.capture_cli import run_capture
            cfg = load_config({"config": args.config}, env)
            return run_capture(cfg, env, kind=args.kind, yes=bool(args.yes), image=args.image, name=args.name,
                               captures_dir=args.captures_dir, out=out, ask=ask or input)
    except MapQaError as exc:
        err.write(f"Błąd: {exc}\n")
        return exc.exit_code
    return 2


def main_entry() -> None:
    for stream in (sys.stdout, sys.stderr):
        if isinstance(stream, io.TextIOWrapper):
            stream.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main(sys.argv[1:]))
