"""`map-qa review export` (PRD §14, ADR-005 D-51…D-55).

Rebuilds the run's sample, reads every answer from the decision cache only (no model request is possible),
and writes a static review page with the exact prepared images the models received.
"""
from __future__ import annotations

import csv
import hashlib
import json
import shutil
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, TextIO

from jinja2 import Environment, PackageLoader, StrictUndefined, select_autoescape
from markupsafe import Markup

from map_qa.photo_reading.budget import BudgetLedger
from map_qa.photo_reading.cache import DecisionCache, tier2_key
from map_qa.photo_reading.escalator import Escalator, Settings
from map_qa.photo_reading.evaluator import Evaluator
from map_qa.photo_reading.image import ImageOutOfBounds, prepare_file
from map_qa.photo_reading.payload import chat_payload, decisions_payload, describe_request
from map_qa.photo_reading.sample import plan_sample
from map_qa.review.items import build_items

SCHEMA = "map-qa-review-data/1"


class _NoNetwork:
    """The export must never call a model; a cache miss is refused by the zero-budget ledger first."""

    def post(self, path, payload):  # pragma: no cover - guarded by the ledger
        raise RuntimeError("map-qa review export never sends model requests")


def _safe_json(data: Any) -> str:
    text = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    return text.replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def render_page(data: dict[str, Any]) -> str:
    env = Environment(loader=PackageLoader("map_qa", "templates"), autoescape=select_autoescape(["html", "j2"]),
                      undefined=StrictUndefined, keep_trailing_newline=True)
    return env.get_template("review.html.j2").render(d=data, data_json=Markup(_safe_json(data)))


def _read_csv(path: Path) -> dict[str, dict[str, str]]:
    if not path.is_file():
        return {}
    with open(path, encoding="utf-8", newline="") as fh:
        return {row["photo_id"]: row for row in csv.DictReader(fh)}


def _https(url: str | None) -> str | None:
    return url if url and url.startswith("https://") else None


def _attribution(kind: str, row: dict[str, str] | None) -> dict[str, Any]:
    row = row or {}
    author = row.get("creator") if kind == "sign_crop" else row.get("author")
    return {"author": author or None, "source": row.get("source") or None, "license": row.get("license") or "CC-BY-SA-4.0",
            "source_url": _https(row.get("source_url"))}


def _context(data_dir: Path, pid: str, row: dict[str, str] | None, review_dir: Path) -> dict[str, Any] | None:
    """Full source photo of a sign crop with the crop box in percent (shown to the human only)."""
    src = data_dir / "signs" / "photos" / f"{pid}.jpg"
    if not src.is_file() or not row:
        return None
    try:
        x1, y1, x2, y2 = json.loads(row.get("crop_bbox_px") or "")
        w, h = float(row["source_width"]), float(row["source_height"])
    except (ValueError, KeyError, TypeError):
        return None
    (review_dir / "context").mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, review_dir / "context" / f"{pid}.jpg")
    return {"src": f"context/{pid}.jpg",
            "box_pct": [round(100 * x1 / w, 2), round(100 * y1 / h, 2), round(100 * (x2 - x1) / w, 2),
                        round(100 * (y2 - y1) / h, 2)]}


def _settings(cfg) -> Settings:
    return Settings(cfg.tier1_model, cfg.compare_model, cfg.tier2_model, cfg.t1_threshold, cfg.t1_threshold_compare,
                    cfg.tier2_accept, cfg.question_set_version, cfg.reserve_usd_tier1, cfg.reserve_usd_tier2,
                    cfg.reserve_usd_compare)


def _tier2_requests(cache: DecisionCache, cfg, kind: str, img, readings) -> list[dict[str, Any]]:
    sets: list[tuple[str, ...]] = []
    for r in readings:
        if r.tier != 2:
            continue
        entry = cache.get(tier2_key(img.sha256, cfg.tier2_model, cfg.question_set_version, r.question_id))
        qs = tuple((entry or {}).get("questions_in_request") or [r.question_id])
        if qs not in sets:
            sets.append(qs)
    return [{"questions": list(qs), "body": describe_request(chat_payload(cfg.tier2_model, kind, img, list(qs)),
                                                                None)["body"]} for qs in sets]


def build_review_data(cfg, *, max_items: int, review_dir: Path) -> dict[str, Any]:
    data_dir, work_dir = Path(cfg.data_dir), Path(cfg.work_dir)
    evaluator = Evaluator(data_dir)
    sample = plan_sample(data_dir, evaluator, seed=cfg.seed, max_images=cfg.max_images)
    photos, signs = _read_csv(data_dir / "photos.csv"), _read_csv(data_dir / "signs" / "signs.csv")
    cache = DecisionCache(work_dir / "cache")
    for sub in ("images", "context"):
        shutil.rmtree(review_dir / sub, ignore_errors=True)
    (review_dir / "images").mkdir(parents=True, exist_ok=True)

    readings, compare, images, out_of_bounds = [], [], {}, []
    with tempfile.TemporaryDirectory() as tmp:
        ledger = BudgetLedger(Path(tmp) / "ledger.jsonl", "review-export", 0, 0.0)
        esc = Escalator(_settings(cfg), cache, ledger, _NoNetwork())
        for item in sample["items"]:
            pid, kind, qids = item["photo_id"], item["kind"], item["questions"]
            try:
                img = prepare_file(data_dir / item["path"], work_dir / "cache" / "images")
            except ImageOutOfBounds:
                out_of_bounds.append(pid)
                continue
            rs = esc.read(pid, kind, img, qids)
            cs = esc.read_compare(pid, kind, img, qids) if item["compare"] else []
            readings.extend(rs)
            compare.extend(c for c in cs if c.tier1_answer is not None)
            shutil.copyfile(work_dir / "cache" / "images" / f"{img.sha256}.jpg", review_dir / "images" / f"{pid}.jpg")
            row = (signs if kind == "sign_crop" else photos).get(pid)
            requests: dict[str, Any] = {"tier1": describe_request(decisions_payload(cfg.tier1_model, kind, img, qids),
                                                                  None)["body"]}
            if item["compare"]:
                requests["compare"] = describe_request(decisions_payload(cfg.compare_model, kind, img, qids),
                                                       None)["body"]
            requests["tier2"] = _tier2_requests(cache, cfg, kind, img, rs)
            images[img.sha256] = {
                "photo_id": pid, "kind": kind, "src": f"images/{pid}.jpg",
                "prepared_size": list(img.size), "original_size": list(img.original_size),
                "upscale": round(max(img.size) / max(img.original_size), 2),
                "attribution": _attribution(kind, row), "requests": requests,
                "context": _context(data_dir, pid, row, review_dir) if kind == "sign_crop" else None,
            }
        if ledger.requests_used:  # pragma: no cover - defensive: the export must stay free
            raise RuntimeError("review export attempted a model request")

    labels = evaluator.label_columns(readings)
    items, stats = build_items(readings, compare, labels, t1_threshold=cfg.t1_threshold, max_items=max_items,
                               seed=cfg.seed, tier1_model=cfg.tier1_model)
    stats["image_out_of_bounds"] = out_of_bounds
    used = {it["image_sha256"] for it in items}
    for sha in [s for s in images if s not in used]:
        (review_dir / images[sha]["src"]).unlink(missing_ok=True)
        if images[sha]["context"]:
            (review_dir / images[sha]["context"]["src"]).unlink(missing_ok=True)
        del images[sha]
    thresholds = {"t1_threshold": cfg.t1_threshold, "t1_threshold_compare": cfg.t1_threshold_compare,
                  "tier2_accept": cfg.tier2_accept}
    ident = json.dumps([[it["item_id"], it["image_sha256"]] for it in items] + [cfg.question_set_version, thresholds],
                       sort_keys=True)
    return {"schema": SCHEMA, "export_id": hashlib.sha256(ident.encode()).hexdigest()[:12],
            "exported_at": datetime.now(UTC).isoformat(timespec="seconds"),
            "question_set_version": cfg.question_set_version, "thresholds": thresholds,
            "models": {"tier1": cfg.tier1_model, "compare": cfg.compare_model, "tier2": cfg.tier2_model},
            "images": images, "items": items, "stats": stats}


def export_review(cfg, *, max_items: int = 100, out: TextIO) -> int:
    review_dir = Path(cfg.output_dir) / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    data = build_review_data(cfg, max_items=max_items, review_dir=review_dir)
    page = review_dir / "review.html"
    page.write_text(render_page(data), encoding="utf-8", newline="\n")
    s = data["stats"]
    reasons = ", ".join(f"{k} {v}" for k, v in s["by_reason"].items())
    out.write(f"Pozycje do oceny: {s['selected']} z {s['reviewable']} ({reasons}).\n")
    if s["cut_by_cap"]:
        out.write(f"Pominięte przez limit --max-items: {s['cut_by_cap']}.\n")
    if s["not_reviewable"] or s["image_out_of_bounds"]:
        out.write(f"Bez odpowiedzi w cache (nie do oceny): {len(s['not_reviewable'])}; "
                  f"obraz poza zakresem: {len(s['image_out_of_bounds'])}.\n")
    out.write("Żądania do modeli: 0 (tylko cache).\n")
    out.write(f"Strona przeglądu: {page}\n")
    return 0
