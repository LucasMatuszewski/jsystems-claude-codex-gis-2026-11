"""Response validation (ADR-003 §5.2, §5.4). Shapes follow the real captures from T43."""
from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any

from map_qa.photo_reading.payload import CERTAINTY
from map_qa.photo_reading.questions import options


class InvalidResponse(ValueError):
    pass


@dataclass(frozen=True)
class T1Answer:
    choice: str
    probabilities: dict[str, float]
    confidence: float | None

    @property
    def pmax(self) -> float:
        return max(self.probabilities.values())


@dataclass(frozen=True)
class T2Answer:
    answer: str
    certainty: str


def _num(v: Any) -> bool:
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def validate_decisions(body: Any, question_ids: list[str]) -> dict[str, T1Answer]:
    if not isinstance(body, dict) or not isinstance(body.get("answers"), dict):
        raise InvalidResponse("brak answers")
    usage = body.get("usage")
    if isinstance(usage, dict) and "cost" in usage and not (_num(usage["cost"]) and usage["cost"] >= 0):
        raise InvalidResponse("usage.cost")
    out = {}
    for qid in question_ids:
        a = body["answers"].get(qid)
        if not isinstance(a, dict) or a.get("type") != "choice":
            raise InvalidResponse(f"{qid}: brak odpowiedzi typu choice")
        opts = options(qid)
        if a.get("choice") not in opts:
            raise InvalidResponse(f"{qid}: choice spoza opcji")
        probs = a.get("probabilities")
        if not isinstance(probs, dict) or set(probs) != set(opts):
            raise InvalidResponse(f"{qid}: probabilities nie zawiera wszystkich opcji")
        if not all(_num(p) and 0 <= p <= 1 for p in probs.values()):
            raise InvalidResponse(f"{qid}: prawdopodobieństwo poza [0,1]")
        if not 0.99 <= sum(probs.values()) <= 1.01:
            raise InvalidResponse(f"{qid}: suma prawdopodobieństw")
        conf = a.get("confidence")
        out[qid] = T1Answer(a["choice"], {k: float(v) for k, v in probs.items()},
                            float(conf) if _num(conf) else None)
    return out


def validate_chat(body: Any, question_ids: list[str]) -> dict[str, T2Answer]:
    try:
        content = body["choices"][0]["message"]["content"]
        data = json.loads(content)
    except (KeyError, IndexError, TypeError, ValueError):
        raise InvalidResponse("brak treści JSON") from None
    if not isinstance(data, dict) or set(data) != set(question_ids):
        raise InvalidResponse("klucze niezgodne ze schematem")
    out = {}
    for qid in question_ids:
        item = data[qid]
        if not isinstance(item, dict) or set(item) != {"answer", "certainty"}:
            raise InvalidResponse(f"{qid}: niezgodne pola")
        if item["answer"] not in options(qid) or item["certainty"] not in CERTAINTY:
            raise InvalidResponse(f"{qid}: wartość spoza enum")
        out[qid] = T2Answer(item["answer"], item["certainty"])
    return out
