"""DecisionCache (ADR-003 §5.6): checked before the budget; a hit costs nothing. Errors are never cached."""
from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


def _h(*parts: str) -> str:
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def tier1_key(image_sha256: str, model: str, qs_version: str, tier: str, question_ids: list[str]) -> str:
    return _h(image_sha256, model, qs_version, tier, ",".join(sorted(question_ids)))


def tier2_key(image_sha256: str, model: str, qs_version: str, question_id: str) -> str:
    return _h(image_sha256, model, qs_version, "tier2", question_id)


class DecisionCache:
    def __init__(self, cache_dir: Path) -> None:
        self.dir = Path(cache_dir) / "decisions"

    def get(self, key: str) -> dict[str, Any] | None:
        path = self.dir / f"{key}.json"
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def put(self, key: str, entry: dict[str, Any]) -> None:
        """entry: response body, returned model, cost, elapsed (no base64, no request headers)."""
        self.dir.mkdir(parents=True, exist_ok=True)
        doc = {"captured_at": datetime.now(UTC).isoformat(timespec="seconds"), **entry}
        (self.dir / f"{key}.json").write_text(json.dumps(doc, ensure_ascii=False, indent=1), encoding="utf-8",
                                              newline="\n")
