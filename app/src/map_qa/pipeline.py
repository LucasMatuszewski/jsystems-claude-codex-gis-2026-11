"""Pipeline orchestration: source -> pairs -> comparisons -> (photo reading) -> report (ADR-000 §3-§6)."""
from __future__ import annotations

import json
import secrets
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import UTC, datetime
from importlib import metadata
from pathlib import Path
from typing import Any, Callable, TextIO

import duckdb

from map_qa.core.config import RunConfig
from map_qa.core.enums import ATTRIBUTES
from map_qa.core.errors import InputChanged
from map_qa.core.models import FileHash, InputManifest
from map_qa.core.paths import sha256_file
from map_qa.matching.compare import compare
from map_qa.matching.pairs import build_pairs
from map_qa.report.model import (
    CANDIDATE_STATUSES, AttrCell, Candidate, CompletenessRow, FileRow, Header, ModelSection, QueueItem,
    ReportModel, RoadRow, SourceCompareRow, Summary, TableRow, Thumb, build_status_counts,
)
from map_qa.report.render import write_outputs
from map_qa.sources import connect

SOURCE_LABELS = {"files": "pliki lokalne", "databricks": "Databricks (workspace.map_qa)"}
VERSION_PACKAGES = ("map-qa", "duckdb", "pyarrow", "httpx", "Jinja2", "pydantic", "Pillow")


@dataclass
class RunContext:
    cfg: RunConfig
    env: dict[str, str]
    out: TextIO
    err: TextIO
    ask: Callable[[str], str] = input
    run_id: str = field(default_factory=lambda: datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ") + "-"
                        + secrets.token_hex(3))
    started: datetime = field(default_factory=lambda: datetime.now(UTC))


def package_versions() -> dict[str, str]:
    out = {}
    for name in VERSION_PACKAGES:
        try:
            out[name.lower()] = metadata.version(name)
        except metadata.PackageNotFoundError:
            out[name.lower()] = "?"
    return out


def make_source(cfg: RunConfig, env: dict[str, str], source: str | None = None):
    name = source or cfg.source
    if name == "files":
        from map_qa.sources.files import FilesSource
        return FilesSource(cfg.data_dir)
    from map_qa.sources.databricks import DatabricksSource
    return DatabricksSource(cfg.data_dir, cfg.work_dir, env=env, timeout_s=cfg.timeout_s)


# ---------------------------------------------------------------- report model building

def _fetch(con: duckdb.DuckDBPyConnection, sql: str, params: list | None = None) -> list[dict[str, Any]]:
    cur = con.execute(sql, params or [])
    names = [d[0] for d in cur.description]
    return [dict(zip(names, row)) for row in cur.fetchall()]


def _raw_osm(rules_json: str, context_json: str) -> list[str]:
    rules = json.loads(rules_json or "[]")
    out = []
    for r in rules:
        if r.get("tag_key"):
            item = f"{r['tag_key']}={r['raw']}"
        elif "class" in r:  # surface value
            item = f"surface={r['raw']}"
        else:
            item = str(r.get("raw"))
        if item not in out:
            out.append(item)
    for k, v in json.loads(context_json or "{}").items():
        out.append(f"{k}={v}")
    return out


def _drop_nulls(value: Any) -> Any:
    if isinstance(value, dict):
        return {k: _drop_nulls(v) for k, v in value.items() if v not in (None, [], {})}
    if isinstance(value, list):
        return [_drop_nulls(v) for v in value]
    return value


def _raw_overture(rules_json: str) -> list[str]:
    """Raw Overture rule for display without empty fields (full raw stays in results.json)."""
    out: list[str] = []
    for r in json.loads(rules_json or "[]"):
        try:
            raw = json.dumps(_drop_nulls(json.loads(r.get("raw"))), ensure_ascii=False, sort_keys=True)
        except (TypeError, ValueError):
            raw = str(r.get("raw"))
        if raw not in out:
            out.append(raw)
    return out


def build_report_model(con: duckdb.DuckDBPyConnection, ctx: RunContext, manifest: InputManifest,
                       attributes: tuple[str, ...], completeness: list[CompletenessRow],
                       source_comparison: list[SourceCompareRow], other_source_label: str | None,
                       model_section: ModelSection, readings_by_photo: dict[str, list] | None = None,
                       shows_mapillary: bool = False) -> ReportModel:
    cfg = ctx.cfg
    links = _fetch(con, "SELECT * FROM links ORDER BY photo_id")
    pairs = [r for r in links if r["link_status"] != "no_candidate"]
    comps = _fetch(con, "SELECT * FROM comparisons ORDER BY photo_id, attribute")
    photos = {r["photo_id"]: r for r in _fetch(
        con, "SELECT photo_id, source, source_url, author, license, width, height FROM photos")}

    header = Header(
        run_id=ctx.run_id, run_date=ctx.started.isoformat(timespec="seconds"), source=manifest.source,
        source_label=SOURCE_LABELS.get(manifest.source, manifest.source), snapshots=manifest.snapshots,
        files=[FileRow(name=f.name, sha256=f.sha256, expected_match=f.expected_match) for f in manifest.files],
        tables=[TableRow(name=t.name, rows=t.rows, statement_id=t.statement_id) for t in manifest.tables],
        config={k: v for k, v in cfg.public_dict().items()
                if k in ("source", "output_dir", "model_reading", "max_images", "max_requests", "max_cost_usd",
                         "tier1_model", "compare_model", "tier2_model", "t1_threshold", "t1_threshold_compare",
                         "tier2_accept", "timeout_s", "question_set_version", "seed")},
        warnings=list(manifest.warnings), source_comparison=source_comparison,
        other_source_label=other_source_label)

    status_counts = build_status_counts([(c["attribute"], c["status"]) for c in comps], attributes)
    by_road: dict[int, dict[str, Counter]] = defaultdict(lambda: defaultdict(Counter))
    photos_per_road: Counter = Counter()
    for p in pairs:
        photos_per_road[p["osm_way_id"]] += 1
    for c in comps:
        by_road[c["osm_way_id"]][c["attribute"]][c["status"]] += 1
    roads = [RoadRow(osm_way_id=w, photos=n, statuses={a: dict(sorted(s.items())) for a, s in by_road[w].items()})
             for w, n in sorted(photos_per_road.items(), key=lambda kv: (-kv[1], kv[0])) if n > 1]
    summary = Summary(
        photos=len(links), pairs=len(pairs),
        no_candidate=sum(1 for r in links if r["link_status"] == "no_candidate"),
        link_status=dict(sorted(Counter(r["link_status"] for r in links).items())),
        status_counts=status_counts, roads_total=len(photos_per_road), roads=roads, completeness=completeness)

    comps_by_photo: dict[str, list[dict]] = defaultdict(list)
    for c in comps:
        comps_by_photo[c["photo_id"]].append(c)
    candidates, queue = [], []
    for p in pairs:
        cells = [AttrCell(attribute=c["attribute"], status=c["status"], reason=c["reason"],
                          osm_value=c["osm_value"], overture_value=c["overture_value"],
                          osm_raw=_raw_osm(c["osm_rules"], c["context_tags"]),
                          overture_raw=_raw_overture(c["overture_rules"]))
                 for c in comps_by_photo[p["photo_id"]]]
        if not any(cell.status in CANDIDATE_STATUSES for cell in cells):
            continue
        ph = photos.get(p["photo_id"], {})
        candidates.append(Candidate(
            photo_id=p["photo_id"], osm_way_id=p["osm_way_id"], overture_id=p["overture_id"],
            distance_m=p["distance_m"], distance_m_recomputed=p["distance_m_recomputed"],
            link_status=p["link_status"], candidate_flags=list(p["candidate_flags"] or []),
            flags=list(p["flags"] or []), reasons=list(p["reasons"] or []),
            thumb=Thumb(photo_id=p["photo_id"], kind="photo", source_url=ph.get("source_url"),
                        author=ph.get("author"), source=ph.get("source"), license=ph.get("license"),
                        width=ph.get("width"), height=ph.get("height")),
            attributes=cells, readings=(readings_by_photo or {}).get(p["photo_id"], [])))
        if p["link_status"] == "ambiguous":
            queue.append(QueueItem(kind="ambiguous_link", photo_id=p["photo_id"], subject=", ".join(attributes),
                                   reason=", ".join(p["reasons"] or [])))
    for r in model_section.readings:
        if r.decision in ("abstain", "model_unavailable"):
            queue.append(QueueItem(kind=r.decision, photo_id=r.photo_id, subject=r.question, reason=r.reason))
    return ReportModel(header=header, summary=summary, candidates=candidates, manual_queue=queue,
                       model=model_section, shows_mapillary_derived=shows_mapillary)


# ---------------------------------------------------------------- input tracking (AC-04)

def add_read_files(manifest: InputManifest, data_dir: Path, paths: list[Path]) -> None:
    known = {f.name for f in manifest.files}
    for p in paths:
        try:
            rel = Path(p).resolve().relative_to(Path(data_dir).resolve()).as_posix()
        except ValueError:
            continue
        if rel not in known:
            manifest.files.append(FileHash(name=rel, sha256=sha256_file(p), bytes=Path(p).stat().st_size))
            known.add(rel)


def verify_inputs_unchanged(manifest: InputManifest, base: Path) -> None:
    for f in manifest.files:
        path = Path(base) / f.name
        if path.is_file() and sha256_file(path) != f.sha256:
            raise InputChanged(f.name)


# ---------------------------------------------------------------- main run

def run(ctx: RunContext) -> int:
    cfg = ctx.cfg
    con = connect(cfg.work_dir)
    try:
        source = make_source(cfg, ctx.env)
        manifest = source.load(con)  # MissingCredential / SourceUnavailable / SchemaMismatch raise before output
        source_comparison: list[SourceCompareRow] = []
        other_label = None
        if cfg.compare_sources:
            from map_qa.sources.compare import compare_sources
            other = "databricks" if cfg.source == "files" else "files"
            source_comparison = compare_sources(con, make_source(cfg, ctx.env, other), cfg.work_dir)
            other_label = SOURCE_LABELS[other]
            for row in source_comparison:
                if not row.equal:
                    manifest.warnings.append(f"Różnica między źródłami w tabeli {row.table}.")
        build_pairs(con)
        attributes = ATTRIBUTES
        compare(con, attributes)
        completeness = completeness_rows(con)

        model_section = ModelSection(max_requests=cfg.max_requests, max_cost_usd=cfg.max_cost_usd)
        readings_by_photo: dict[str, list] = {}
        extra_files: list[Path] = []
        shows_mapillary = False
        sample_manifest = None
        if cfg.model_reading:
            from map_qa.photo_reading.runner import run_photo_reading
            outcome = run_photo_reading(con, ctx)
            model_section = outcome.section
            readings_by_photo = outcome.readings_by_photo
            extra_files = outcome.files_read
            shows_mapillary = outcome.shows_mapillary
            sample_manifest = outcome.sample_manifest

        add_read_files(manifest, cfg.data_dir, extra_files)
        model = build_report_model(con, ctx, manifest, attributes, completeness, source_comparison, other_label,
                                   model_section, readings_by_photo, shows_mapillary)
        extra = {"pairs": _jsonable(_fetch(con, "SELECT * FROM pairs ORDER BY photo_id")),
                 "no_candidate_photos": _jsonable(_fetch(
                     con, "SELECT * FROM links WHERE link_status = 'no_candidate' ORDER BY photo_id")),
                 "comparisons": _jsonable(_fetch(con, "SELECT * FROM comparisons ORDER BY photo_id, attribute"))}
        out_dir = Path(cfg.output_dir)
        thumbs_read = write_outputs(model, out_dir, cfg.data_dir, render_date=ctx.started.date().isoformat(),
                                    extra_results=extra)
        add_read_files(manifest, cfg.data_dir, thumbs_read)
        if sample_manifest is not None:
            (out_dir / "sample_manifest.json").write_text(json.dumps(sample_manifest, ensure_ascii=False, indent=1),
                                                         encoding="utf-8", newline="\n")
        run_manifest = {
            "run_id": ctx.run_id, "run_date": ctx.started.isoformat(timespec="seconds"),
            "config": cfg.public_dict(), "input_manifest": manifest.model_dump(mode="json"),
            "versions": package_versions(),
            "thresholds": {"t1_threshold": cfg.t1_threshold, "t1_threshold_compare": cfg.t1_threshold_compare,
                           "tier2_accept": cfg.tier2_accept},
            "model_requests": model_section.requests_this_run, "model_cost_usd": model_section.cost_this_run_usd,
        }
        (out_dir / "run_manifest.json").write_text(json.dumps(run_manifest, ensure_ascii=False, indent=1),
                                                   encoding="utf-8", newline="\n")
        if manifest.source == "files":
            verify_inputs_unchanged(manifest, cfg.data_dir)
        else:
            verify_inputs_unchanged(InputManifest(source="x", files=[f for f in manifest.files
                                                                     if not f.name.startswith("databricks/")]),
                                    cfg.data_dir)
        print_summary(ctx, model, out_dir)
        return 0
    finally:
        con.close()


def completeness_rows(con: duckdb.DuckDBPyConnection) -> list[CompletenessRow]:
    try:
        from map_qa.normalize.completeness import compute_completeness
    except ImportError:
        return []
    return compute_completeness(con)


def _jsonable(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for r in rows:
        d = {}
        for k, v in r.items():
            if isinstance(v, str) and k in ("osm_rules", "overture_rules", "context_tags"):
                d[k] = json.loads(v)
            elif isinstance(v, (list, tuple)):
                d[k] = list(v)
            else:
                d[k] = v
        out.append(d)
    return out


def print_summary(ctx: RunContext, model: ReportModel, out_dir: Path) -> None:
    w = ctx.out.write
    s = model.summary
    w(f"Źródło danych: {model.header.source_label}\n")
    w(f"Zdjęcia: {s.photos}, pary: {s.pairs}, bez kandydata: {s.no_candidate}\n")
    for attr in model.attributes():
        parts = ", ".join(f"{c.status} {c.count}" for c in s.status_counts if c.attribute == attr)
        w(f"{attr}: {parts}\n")
    if model.model.run:
        w(f"Odczyt modelem: żądania {model.model.requests_this_run}, koszt {model.model.cost_this_run_usd:.4f} USD,"
          f" z cache {model.model.cache_hits}\n")
    else:
        w(f"{model.model.not_run_reason}.\n")
    for name in ("report.md", "report.html", "results.json", "run_manifest.json"):
        w(f"Zapisano: {out_dir / name}\n")
    if (out_dir / "sample_manifest.json").exists() and model.model.run:
        w(f"Zapisano: {out_dir / 'sample_manifest.json'}\n")
    w("Kod wyjścia: 0\n")


# ---------------------------------------------------------------- capture (ADR-004 §3.1, ADR-003 §5.8)

DEFAULT_CAPTURES_DIR = Path("app/tests/fixtures/captures")


def confirm(prompt: str, yes: bool, ask: Callable[[str], str], out: TextIO) -> bool:
    if yes:
        return True
    out.write(prompt)
    out.flush()
    try:
        return ask("Potwierdzić? [y/N] ").strip().lower() in ("y", "yes", "t", "tak")
    except EOFError:
        return False


def run_capture(cfg: RunConfig, env: dict[str, str], *, kind: str, yes: bool, image: str | None, name: str | None,
                captures_dir: str | None, out: TextIO, ask: Callable[[str], str]) -> int:
    target_dir = Path(captures_dir) if captures_dir else DEFAULT_CAPTURES_DIR
    if kind == "databricks":
        from map_qa.sources.databricks import record_capture, required_env
        required_env(env)  # exit 3 before asking when a variable is missing
        if not confirm("Jedno rzeczywiste zapytanie SELECT (photos LIMIT 5) do Databricks.\n", yes, ask, out):
            out.write("Anulowano: nie wysłano żadnego żądania.\n")
            return 0
        record_capture(env, target_dir, name=name or "databricks-photos-limit5", out=out, timeout_s=cfg.timeout_s)
        return 0
    from map_qa.photo_reading.capture_cli import run_model_capture
    return run_model_capture(cfg, env, kind=kind, yes=yes, image=image, name=name, captures_dir=target_dir, out=out,
                             ask=ask)
