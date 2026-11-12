"""Command-line entry point (ADR-004 §3.1, D-41: argparse)."""
from __future__ import annotations

import argparse
import sys


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="map-qa",
        description="Porównanie atrybutów dróg OSM i Overture ze zdjęciami ulic (Kraków).",
    )
    sub = parser.add_subparsers(dest="command", metavar="{run,report,capture}")
    sub.add_parser("run", help="Pełny pipeline i raport")
    sub.add_parser("report", help="Ponowne renderowanie raportu z results.json")
    sub.add_parser("capture", help="Jedno rzeczywiste żądanie API i zapis capture")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command is None:
        parser.print_help()
        return 2
    return 0


def main_entry() -> None:
    sys.exit(main(sys.argv[1:]))
