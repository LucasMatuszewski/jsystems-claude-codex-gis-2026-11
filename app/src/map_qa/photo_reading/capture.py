"""CaptureRecorder (ADR-003 §5.8): safe capture of a real OpenRouter exchange."""
from __future__ import annotations

from pathlib import Path
from typing import Any

import httpx

from map_qa.core.capture import build_capture, write_capture
from map_qa.photo_reading.clients import ApiResult
from map_qa.photo_reading.image import PreparedImage
from map_qa.photo_reading.payload import describe_request


class CaptureRecorder:
    def __init__(self, captures_dir: Path) -> None:
        self.dir = Path(captures_dir)

    def record(self, name: str, endpoint: str, payload: dict[str, Any], result: ApiResult,
               image: PreparedImage | None = None) -> Path:
        body = result.body if result.body is not None else {"error_kind": result.error_kind,
                                                            "error_detail": result.error_detail}
        returned = body.get("model") if isinstance(body, dict) else None
        doc = build_capture(target="openrouter", endpoint=endpoint, method="POST", status=result.status or 0,
                            response_headers=result.headers, response_body=body, elapsed_ms=result.elapsed_ms,
                            request_meta=describe_request(payload, image),
                            client_version=f"httpx {httpx.__version__}; OpenRouter API",
                            model_sent=payload.get("model"), model_returned=returned)
        return write_capture(doc, self.dir / f"{name}.json")
