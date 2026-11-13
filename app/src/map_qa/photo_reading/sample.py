"""SamplePlanner (ADR-003 §3.1, PRD AC-14/AC-15): deterministic 15 street photos + 10 sign crops.

The manifest holds only IDs, kinds, paths, sequences and question IDs (no label values).
"""
from __future__ import annotations

import csv
import random
from collections import Counter
from pathlib import Path
from typing import Callable

from map_qa.photo_reading.evaluator import Evaluator
from map_qa.photo_reading.questions import QUESTION_SET_VERSION, questions_for

N_PHOTOS, N_POSITIVE, N_NEGATIVE = 15, 6, 4
MAX_PER_SEQUENCE = 2
N_COMPARE_PHOTOS, N_COMPARE_CROPS = 3, 2


def _read_csv(path: Path, key: str, cols: tuple[str, ...]) -> dict[str, dict]:
    with open(path, encoding="utf-8", newline="") as fh:
        return {r[key]: {c: r.get(c) for c in cols} for r in csv.DictReader(fh)}


def photo_path(data_dir: Path, photo_id: str, exists: Callable[[Path], bool]) -> Path | None:
    """Image source: data/photos/ (after download_photos.py) or offline/ (ADR-003 §3.1)."""
    for p in (data_dir / "data" / "photos" / f"{photo_id}.jpg", data_dir / "offline" / f"{photo_id}.jpg"):
        if exists(p):
            return p
    return None


def _pick(ids: list[str], seq_of: dict[str, str], n: int, rng: random.Random, path_of: Callable[[str], Path | None],
          per_seq: Counter, counters: Counter) -> list[tuple[str, Path]]:
    order = sorted(ids)
    rng.shuffle(order)
    chosen: list[tuple[str, Path]] = []
    for pid in order:
        if len(chosen) >= n:
            break
        seq = seq_of.get(pid) or f"_none_{pid}"
        if per_seq[seq] >= MAX_PER_SEQUENCE:
            continue
        path = path_of(pid)
        if path is None:
            counters["image_missing"] += 1  # replaced by the next draw
            continue
        per_seq[seq] += 1
        chosen.append((pid, path))
    return chosen


def plan_sample(data_dir: Path, evaluator: Evaluator, seed: int = 42, max_images: int = 25,
                exists: Callable[[Path], bool] = Path.is_file) -> dict:
    data_dir = Path(data_dir)
    rng = random.Random(seed)
    counters: Counter = Counter()
    photos = _read_csv(data_dir / "photos.csv", "photo_id", ("source", "sequence"))
    signs = _read_csv(data_dir / "signs" / "signs.csv", "photo_id", ("sequence",))

    street_ids = [pid for pid in evaluator.street_candidates() if (photos.get(pid) or {}).get("source") == "Panoramax"]
    strata = evaluator.sign_strata()
    positives = [pid for pid, s in strata.items() if s == "positive"]
    negatives = [pid for pid, s in strata.items() if s == "negative"]

    n_photos = min(N_PHOTOS, max_images)
    n_signs_total = max(0, max_images - n_photos)
    n_pos = min(N_POSITIVE, n_signs_total)
    n_neg = min(N_NEGATIVE, n_signs_total - n_pos)

    street = _pick(street_ids, {k: v["sequence"] for k, v in photos.items()}, n_photos, rng,
                   lambda pid: photo_path(data_dir, pid, exists), Counter(), counters)

    def crop_path(pid: str) -> Path | None:
        p = data_dir / "signs" / "crops" / f"{pid}.jpg"
        return p if exists(p) else None

    sign_seq = {k: v["sequence"] for k, v in signs.items()}
    per_seq: Counter = Counter()
    crops = _pick(positives, sign_seq, n_pos, rng, crop_path, per_seq, counters)
    crops += _pick(negatives, sign_seq, n_neg, rng, crop_path, per_seq, counters)
    # Stable order inside kinds: draw order (positives first) is shuffled once more so the comparison subset
    # (first 2 crops) is not always positive.
    rng.shuffle(crops)

    items = []
    for i, (pid, path) in enumerate(street):
        items.append({"photo_id": pid, "kind": "photo", "path": path.relative_to(data_dir).as_posix(),
                      "sequence": photos[pid]["sequence"], "questions": questions_for("photo"),
                      "compare": i < N_COMPARE_PHOTOS})
    for i, (pid, path) in enumerate(crops):
        items.append({"photo_id": pid, "kind": "sign_crop", "path": path.relative_to(data_dir).as_posix(),
                      "sequence": sign_seq.get(pid), "questions": questions_for("sign_crop"),
                      "compare": i < N_COMPARE_CROPS})
    return {"seed": seed, "question_set_version": QUESTION_SET_VERSION, "max_images": max_images,
            "items": items, "counters": {"image_missing": counters["image_missing"],
                                         "photos": len(street), "sign_crops": len(crops)}}
