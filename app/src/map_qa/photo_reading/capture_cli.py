"""`map-qa capture --kind {decisions-luna, decisions-jev, chat-tier2}` (ADR-004 §3.1, §3.3; ADR-003 §5.8).

Prints cost and limit, asks y/N (or --yes), sends exactly ONE real request within the budget and writes a
safe capture. Mocks in tests are derived only from these captures.
"""
from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path
from typing import Callable, TextIO

from map_qa.core.config import RunConfig
from map_qa.core.errors import ConfigError, MissingCredential
from map_qa.photo_reading.budget import BudgetLedger
from map_qa.photo_reading.capture import CaptureRecorder
from map_qa.photo_reading.clients import CHAT_PATH, DECISIONS_PATH, OpenRouterClient, response_cost
from map_qa.photo_reading.evaluator import Evaluator
from map_qa.photo_reading.image import prepare_file
from map_qa.photo_reading.payload import chat_payload, decisions_payload
from map_qa.photo_reading.questions import questions_for
from map_qa.photo_reading.sample import photo_path, plan_sample


def _ask_yes(prompt: str, yes: bool, ask: Callable[[str], str], out: TextIO) -> bool:
    out.write(prompt)
    if yes:
        return True
    try:
        return ask("Potwierdzić? [y/N] ").strip().lower() in ("y", "yes", "t", "tak")
    except EOFError:
        return False


def resolve_image(cfg: RunConfig, image: str | None, default_kind: str = "photo") -> tuple[str, str, Path]:
    data_dir = Path(cfg.data_dir)
    if image:
        p = photo_path(data_dir, image, Path.is_file)
        if p is not None:
            return image, "photo", p
        crop = data_dir / "signs" / "crops" / f"{image}.jpg"
        if crop.is_file():
            return image, "sign_crop", crop
        raise ConfigError(f"Nie znaleziono pliku obrazu dla {image}.")
    manifest = plan_sample(data_dir, Evaluator(data_dir), seed=cfg.seed, max_images=cfg.max_images)
    item = next(i for i in manifest["items"] if i["kind"] == default_kind)
    return item["photo_id"], item["kind"], data_dir / item["path"]


def run_model_capture(cfg: RunConfig, env: dict[str, str], *, kind: str, yes: bool, image: str | None,
                      name: str | None, captures_dir: Path, out: TextIO, ask: Callable[[str], str],
                      client_factory: Callable[[], object] | None = None) -> int:
    if not env.get("OPENROUTER_API_KEY"):
        raise MissingCredential("OPENROUTER_API_KEY")
    model, tier, reserve, path = {
        "decisions-luna": (cfg.tier1_model, "tier1", cfg.reserve_usd_tier1, DECISIONS_PATH),
        "decisions-jev": (cfg.compare_model, "compare", cfg.reserve_usd_compare, DECISIONS_PATH),
        "chat-tier2": (cfg.tier2_model, "tier2", cfg.reserve_usd_tier2, CHAT_PATH),
    }[kind]
    photo_id, img_kind, img_path = resolve_image(cfg, image)
    qids = questions_for(img_kind)
    prompt = (f"Capture {kind}: 1 żądanie do {model}, obraz typu {img_kind}, pytania: {', '.join(qids)}.\n"
              f"Rezerwacja kosztu: {reserve:.2f} USD; limit kosztu: {cfg.max_cost_usd:.2f} USD; limit żądań: 1.\n")
    if not _ask_yes(prompt, yes, ask, out):
        out.write("Anulowano: nie wysłano żadnego żądania.\n")
        return 0
    prepared = prepare_file(img_path, Path(cfg.work_dir) / "cache" / "images")
    payload = (chat_payload if kind == "chat-tier2" else decisions_payload)(model, img_kind, prepared, qids)
    ledger = BudgetLedger(Path(cfg.work_dir) / "ledger.jsonl",
                          run_id="capture-" + datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ"),
                          max_requests=1, max_cost_usd=cfg.max_cost_usd)
    res = ledger.reserve(model, tier, reserve)
    if res is None:
        out.write(f"Limit budżetu nie pozwala na wywołanie ({ledger.refusal_reason}).\n")
        return 0
    client = client_factory() if client_factory else OpenRouterClient(env, timeout_s=cfg.timeout_s)
    try:
        result = client.post(path, payload)
    finally:
        client.close()
    cost = response_cost(result.body)
    ledger.settle(res, status_code=result.status, cost_usd=cost, outcome="ok" if result.ok else "error")
    status = result.status if result.status is not None else result.error_kind
    capture_name = name or f"{kind}-{img_kind}-{status}"
    saved = CaptureRecorder(captures_dir).record(capture_name, path, payload, result, image=prepared)
    out.write(f"Zapisano capture: {saved} (status {status}, {result.elapsed_ms:.0f} ms, koszt {cost})\n")
    return 0
