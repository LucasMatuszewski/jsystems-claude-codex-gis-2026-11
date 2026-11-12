"""Photo reading integrated into `map-qa run --model-reading` (PRD §4.2, §9.1; ADR-003 §3-§5; ADR-004 §3.3).

Pipeline layer: composes photo_reading components and builds the report's model section.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import duckdb

from map_qa.core.errors import MissingCredential
from map_qa.normalize.lit import lit_class
from map_qa.normalize.speed import comparable_value, osm_rules
from map_qa.normalize.surface import comparable_surface, osm_surface_value, overture_surface_values
from map_qa.photo_reading.budget import BudgetLedger
from map_qa.photo_reading.cache import DecisionCache
from map_qa.photo_reading.clients import OpenRouterClient
from map_qa.photo_reading.escalator import Escalator, PhotoReading, Settings
from map_qa.photo_reading.evaluator import Evaluator, compare_models, evaluate
from map_qa.photo_reading.image import ImageOutOfBounds, prepare_file
from map_qa.photo_reading.map_compare import map_comparison
from map_qa.photo_reading.questions import QUESTION_SET_VERSION
from map_qa.photo_reading.sample import plan_sample
from map_qa.report.model import (
    NOT_RUN, DecisionCount, ModelCounter, ModelSection, ReadingCell, ReadingRow,
)

DECISIONS = ["answered", "answered_tier2", "abstain", "model_unavailable", "not_run_budget_or_error"]


@dataclass
class ReadingOutcome:
    section: ModelSection
    readings_by_photo: dict[str, list[ReadingCell]] = field(default_factory=dict)
    files_read: list[Path] = field(default_factory=list)
    shows_mapillary: bool = False
    sample_manifest: dict | None = None


class _LazyClient:
    """Creates the HTTP client only when a real call is needed (cache-only runs need no key)."""

    def __init__(self, env: dict[str, str], timeout_s: float) -> None:
        self.env, self.timeout_s, self._c = env, timeout_s, None

    def post(self, path, payload):
        if self._c is None:
            self._c = OpenRouterClient(self.env, timeout_s=self.timeout_s)
        return self._c.post(path, payload)

    def close(self):
        if self._c is not None:
            self._c.close()


def _settings(cfg) -> Settings:
    return Settings(cfg.tier1_model, cfg.compare_model, cfg.tier2_model, cfg.t1_threshold, cfg.t1_threshold_compare,
                    cfg.tier2_accept, cfg.question_set_version, cfg.reserve_usd_tier1, cfg.reserve_usd_tier2,
                    cfg.reserve_usd_compare)


def _map_rows(con: duckdb.DuckDBPyConnection, items: list[dict]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    photo_ids = [i["photo_id"] for i in items if i["kind"] == "photo"]
    crop_ids = [i["photo_id"] for i in items if i["kind"] == "sign_crop"]
    if photo_ids:
        cur = con.execute("""SELECT l.photo_id, o.surface, o.lit, s.road_surface, l.overture_id, l.link_status
                             FROM links l LEFT JOIN osm_roads o ON o.osm_id = l.osm_way_id
                             LEFT JOIN overture_segments s ON s.id = l.overture_id
                             WHERE l.photo_id IN (SELECT unnest(?))""", [photo_ids])
        for pid, surface, lit, road_surface, ov_id, link_status in cur.fetchall():
            ov = overture_surface_values(road_surface) if ov_id else []
            ov_cls, _ = comparable_surface(ov) if ov else (None, None)
            if ov and ov_cls is None:
                ov_cls = "not_comparable"  # partial `between`, several classes or unknown value
            rows[pid] = {"osm_surface_raw": surface, "osm_surface_class": str(osm_surface_value(surface).cls),
                         "overture_surface_raw": ", ".join(str(v.raw) for v in ov) or None,
                         "overture_surface_class": ov_cls, "osm_lit_raw": lit, "osm_lit_class": lit_class(lit),
                         "link_status": link_status}
    if crop_ids:
        cur = con.execute("""SELECT s.photo_id, n.maxspeed, n.maxspeed_forward, n.maxspeed_backward,
                                    n.maxspeed_conditional, s.mapillary_value
                             FROM signs s LEFT JOIN signs_nearest_osm n USING (photo_id)
                             WHERE s.photo_id IN (SELECT unnest(?))""", [crop_ids])
        for pid, ms, fw, bw, cond, mv in cur.fetchall():
            tags = {k: v for k, v in {"maxspeed": ms, "maxspeed:forward": fw, "maxspeed:backward": bw,
                                      "maxspeed:conditional": cond}.items() if v}
            value, reason = comparable_value(osm_rules(tags).rules)
            rows[pid] = {"maxspeed": ms, "maxspeed_forward": fw, "maxspeed_backward": bw,
                         "maxspeed_conditional": cond, "mapillary_value": mv,
                         "osm_speed_value": value, "osm_speed_reason": reason}
    return rows


def _counters(calls) -> list[ModelCounter]:
    agg: dict[tuple[str, str, str], list[float]] = defaultdict(lambda: [0, 0.0, 0])
    for c in calls:
        share = c.cost_usd / max(1, len(c.questions))
        for q in c.questions:
            a = agg[(c.model, c.tier, q)]
            if c.cached:
                a[2] += 1
            else:
                a[0] += 1
                a[1] += share
    return [ModelCounter(model=m, tier=t, question=q, requests=int(v[0]), cost_usd=round(v[1], 8),
                         cache_hits=int(v[2])) for (m, t, q), v in sorted(agg.items())]


def run_photo_reading(con: duckdb.DuckDBPyConnection, ctx) -> ReadingOutcome:
    cfg = ctx.cfg
    data_dir, work_dir = Path(cfg.data_dir), Path(cfg.work_dir)
    evaluator = Evaluator(data_dir)
    sample = plan_sample(data_dir, evaluator, seed=cfg.seed, max_images=cfg.max_images)
    items = sample["items"]
    files_read = list(evaluator.files_read)
    prepared: dict[str, Any] = {}
    out_of_bounds = []
    for item in items:
        path = data_dir / item["path"]
        files_read.append(path)
        try:
            prepared[item["photo_id"]] = prepare_file(path, work_dir / "cache" / "images")
        except ImageOutOfBounds:
            out_of_bounds.append(item["photo_id"])
    sample["counters"]["image_out_of_bounds"] = len(out_of_bounds)

    ledger = BudgetLedger(work_dir / "ledger.jsonl", ctx.run_id, cfg.max_requests, cfg.max_cost_usd)
    client = _LazyClient(ctx.env, cfg.timeout_s)
    esc = Escalator(_settings(cfg), DecisionCache(work_dir / "cache"), ledger, client)

    # Calls needed beyond the cache (PRD §4.4); confirmation only when something must be paid for.
    pending = Counter()
    for item in items:
        img = prepared.get(item["photo_id"])
        if img is not None:
            pending.update(esc.pending_calls(img, item["kind"], item["questions"], compare=item["compare"]))
    new_calls = sum(pending.values())
    section = ModelSection(run=True, question_set_version=QUESTION_SET_VERSION,
                           thresholds={"t1_threshold": cfg.t1_threshold,
                                       "t1_threshold_compare": cfg.t1_threshold_compare,
                                       "tier2_accept": cfg.tier2_accept},
                           max_requests=cfg.max_requests, max_cost_usd=cfg.max_cost_usd)
    w = ctx.out.write
    if new_calls:
        if not ctx.env.get("OPENROUTER_API_KEY"):
            raise MissingCredential("OPENROUTER_API_KEY")
        n_q = sum(len(i["questions"]) for i in items)
        w(f"Próbka: {len(items)} obrazów ({sample['counters']['photos']} zdjęć, "
          f"{sample['counters']['sign_crops']} wycinków), {n_q} pytań; seed {cfg.seed}.\n"
          f"Przewidywane nowe żądania (maks.): tier 1 {pending['tier1']}, tier 2 {pending['tier2']}, "
          f"porównanie {pending['compare']}; limit żądań {cfg.max_requests}, limit kosztu {cfg.max_cost_usd:.2f} USD.\n"
          f"Modele: {cfg.tier1_model} / {cfg.tier2_model} / {cfg.compare_model}; "
          f"progi: T1={cfg.t1_threshold}, T1 porównanie={cfg.t1_threshold_compare}, tier 2={cfg.tier2_accept}.\n")
        w("Manifest próbki (PRD §4.2 krok 2):\n")
        for n, item in enumerate(items, start=1):
            mark = " [porównanie]" if item["compare"] else ""
            w(f"  {n:2d}. {item['photo_id']} ({item['kind']}): {', '.join(item['questions'])}{mark}\n")
            img = prepared.get(item["photo_id"])
            need = esc.new_call_questions(img, item["questions"]) if img is not None else None
            if need and need["tier2"] and not need["tier1"]:
                w(f"      wymaga nowych wywołań tier 2: {', '.join(need['tier2'])}\n")
        confirmed = bool(cfg.yes)
        if not confirmed:
            try:
                confirmed = ctx.ask("Potwierdzić płatne wywołania? [y/N] ").strip().lower() in ("y", "yes", "t", "tak")
            except EOFError:
                confirmed = False
        if not confirmed:
            w("Odmowa: raport bez odczytu modelem.\n")
            return ReadingOutcome(ModelSection(run=False, not_run_reason=f"{NOT_RUN} (odmowa potwierdzenia)",
                                               max_requests=cfg.max_requests, max_cost_usd=cfg.max_cost_usd),
                                  files_read=files_read, sample_manifest=sample)
    readings: list[PhotoReading] = []
    compare_readings: list[PhotoReading] = []
    try:
        for idx, item in enumerate(items, start=1):
            img = prepared.get(item["photo_id"])
            if img is None:
                rs = [PhotoReading(item["photo_id"], item["kind"], q, "not_run_budget_or_error",
                                   reason="image_out_of_bounds") for q in item["questions"]]
            else:
                rs = esc.read(item["photo_id"], item["kind"], img, item["questions"])
                if item["compare"]:
                    compare_readings.extend(esc.read_compare(item["photo_id"], item["kind"], img,
                                                             item["questions"]))
            for r in rs:  # progress: index, question, tier, status (never bytes or keys)
                w(f"[{idx}/{len(items)}] {r.question_id}: tier {r.tier or '–'}, {r.decision}\n")
            readings.extend(rs)
    finally:
        client.close()

    labels = evaluator.label_columns(readings)
    section.sample = {"obrazy": len(items), "zdjęcia ulic": sample["counters"]["photos"],
                      "wycinki znaków": sample["counters"]["sign_crops"],
                      "brak pliku (zastąpione)": sample["counters"]["image_missing"],
                      "obraz poza zakresem": len(out_of_bounds), "podzbiór porównawczy": sum(i["compare"] for i in items)}
    section.readings = [ReadingRow(photo_id=r.photo_id, kind=r.kind, question=r.question_id, decision=r.decision,
                                   answer=r.answer if r.decision in ("answered", "answered_tier2") else None,
                                   tier=r.tier, model=r.model, probability=r.tier1_probability,
                                   certainty=r.certainty, tier1_answer=r.tier1_answer,
                                   tier1_probability=r.tier1_probability, reason=r.reason,
                                   label=labels[(r.photo_id, r.question_id)][0],
                                   label_status=labels[(r.photo_id, r.question_id)][1]) for r in readings]
    decisions = Counter((r.question_id, r.decision) for r in readings)
    section.decisions = [DecisionCount(question=q, decision=d, count=decisions[(q, d)])
                         for q in dict.fromkeys(r.question_id for r in readings) for d in DECISIONS]
    section.counters = _counters(esc.calls)
    section.cache_hits = esc.cache_hits
    section.requests_this_run = ledger.entries_for_run()
    section.cost_this_run_usd = round(ledger.run_cost(), 8)
    section.ledger_total_requests, total_cost = ledger.history_totals()
    section.ledger_total_cost_usd = round(total_cost, 8)
    if ledger.is_open:
        section.stopped_reason = f"pierwszy błąd API ({ledger.open_reason}); pozostałe pozycje nie zostały uruchomione"
    elif any(r.decision == "not_run_budget_or_error" and r.reason in ("max_requests", "max_cost_usd")
             for r in readings):
        section.stopped_reason = "osiągnięto limit budżetu"
    section.evaluation = evaluate(readings, evaluator, compare_readings)
    section.comparison, section.comparison_summary = compare_models(readings, compare_readings)
    section.map_comparison = map_comparison(readings, _map_rows(con, items))

    by_photo: dict[str, list[ReadingCell]] = defaultdict(list)
    for r in readings:
        by_photo[r.photo_id].append(ReadingCell(question=r.question_id, decision=r.decision,
                                                answer=r.answer if r.decision in ("answered", "answered_tier2")
                                                else None, tier=r.tier, probability=r.tier1_probability,
                                                certainty=r.certainty))
    return ReadingOutcome(section, dict(by_photo), files_read,
                          shows_mapillary=any(i["kind"] == "sign_crop" for i in items), sample_manifest=sample)
