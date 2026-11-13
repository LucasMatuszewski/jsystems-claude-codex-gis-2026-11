"""PayloadBuilder (ADR-003 §5.1, §5.4): allowlist — only neutral question text and the prepared image.

The functions take no photo record at all, so IDs, labels, map attributes, coordinates or author names
cannot reach the request (PRD AC-12).
"""
from __future__ import annotations

import base64
from typing import Any

from map_qa.photo_reading.image import PreparedImage
from map_qa.photo_reading.questions import QUESTIONS, STATE_TEXT, options

CERTAINTY = ["high", "medium", "low"]


def _data_url(image: PreparedImage) -> str:
    return "data:image/jpeg;base64," + base64.b64encode(image.data).decode("ascii")


def decisions_payload(model: str, kind: str, image: PreparedImage, question_ids: list[str]) -> dict[str, Any]:
    return {
        "model": model,
        "state": [STATE_TEXT[kind], {"type": "image_url", "image_url": {"url": _data_url(image)}}],
        "questions": {qid: {"type": "choice", "instructions": QUESTIONS[qid]["instructions"],
                            "criteria": dict(QUESTIONS[qid]["criteria"])} for qid in question_ids},
    }


def chat_schema(question_ids: list[str]) -> dict[str, Any]:
    return {
        "type": "object",
        "properties": {qid: {"type": "object",
                             "properties": {"answer": {"type": "string", "enum": options(qid)},
                                            "certainty": {"type": "string", "enum": CERTAINTY}},
                             "required": ["answer", "certainty"], "additionalProperties": False}
                       for qid in question_ids},
        "required": list(question_ids),
        "additionalProperties": False,
    }


def chat_prompt(kind: str, question_ids: list[str]) -> str:
    lines = [STATE_TEXT[kind], "", "Answer each question about the image by choosing exactly one option.",
             "For each answer also rate your certainty as high, medium or low.", ""]
    for qid in question_ids:
        lines.append(f"Question `{qid}`: {QUESTIONS[qid]['instructions']}")
        for opt, definition in QUESTIONS[qid]["criteria"].items():
            lines.append(f"- {opt}: {definition}")
        lines.append("")
    lines.append("Reply only with JSON that matches the provided schema.")
    return "\n".join(lines)


def chat_payload(model: str, kind: str, image: PreparedImage, question_ids: list[str]) -> dict[str, Any]:
    """Tier 2: same image, the uncertain questions only; tier-1 answers are NOT sent (no anchoring)."""
    return {
        "model": model,
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": chat_prompt(kind, question_ids)},
            {"type": "image_url", "image_url": {"url": _data_url(image)}},
        ]}],
        "reasoning": {"effort": "medium"},
        "response_format": {"type": "json_schema",
                            "json_schema": {"name": "photo_reading", "strict": True,
                                            "schema": chat_schema(question_ids)}},
    }


def describe_request(payload: dict[str, Any], image: PreparedImage | None) -> dict[str, Any]:
    """Request description for captures: the image is replaced by its hash and size."""
    def strip(v: Any) -> Any:
        if isinstance(v, dict):
            if v.get("type") == "image_url":
                return {"type": "image_url", "image_url": "<image>"}
            return {k: strip(x) for k, x in v.items()}
        if isinstance(v, list):
            return [strip(x) for x in v]
        return v
    meta = {"body": strip(payload)}
    if image is not None:
        meta["image"] = {"image_sha256": image.sha256, "bytes": len(image.data)}
    return meta
