"""One prepared image for all models (ADR-003 §3.2, D-34). Bytes/base64 are never logged."""
from __future__ import annotations

import hashlib
import io
from dataclasses import dataclass
from pathlib import Path

from PIL import Image, ImageOps

MIN_SIDE, MAX_SIDE = 256, 1568
MIN_PIXELS, MAX_PIXELS = 78_400, 2_458_624
JPEG_QUALITY = 92


class ImageOutOfBounds(ValueError):
    pass


@dataclass(frozen=True)
class PreparedImage:
    data: bytes
    sha256: str
    size: tuple[int, int]
    original_size: tuple[int, int]


def prepare_bytes(raw: bytes) -> PreparedImage:
    with Image.open(io.BytesIO(raw)) as src:
        original = src.size
        img = ImageOps.exif_transpose(src).convert("RGB")
    w, h = img.size
    scale = 1.0
    if min(w, h) < MIN_SIDE or w * h < MIN_PIXELS:
        # Upscale until BOTH the 256 px short side and the 78 400 px minimum hold (ADR-003 §3.2, 2026-11-12).
        scale = max(MIN_SIDE / min(w, h), (MIN_PIXELS / (w * h)) ** 0.5) * 1.0005
    elif max(w, h) > MAX_SIDE:
        scale = MAX_SIDE / max(w, h)
    if scale != 1.0:
        w, h = round(w * scale), round(h * scale)
        if not (MIN_PIXELS <= w * h <= MAX_PIXELS):
            raise ImageOutOfBounds(f"{w}x{h}")
        img = img.resize((w, h), Image.Resampling.LANCZOS)
    if not (MIN_PIXELS <= w * h <= MAX_PIXELS):
        raise ImageOutOfBounds(f"{w}x{h}")
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=JPEG_QUALITY)  # no exif= argument: metadata (incl. GPS) dropped
    data = buf.getvalue()
    return PreparedImage(data=data, sha256=hashlib.sha256(data).hexdigest(), size=(w, h), original_size=original)


def prepare_file(path: Path, cache_dir: Path | None = None) -> PreparedImage:
    """Reads the input read-only; the prepared JPEG is stored in the work-dir cache (ADR-003 §3.2 step 4)."""
    prepared = prepare_bytes(Path(path).read_bytes())
    if cache_dir is not None:
        cache_dir.mkdir(parents=True, exist_ok=True)
        target = cache_dir / f"{prepared.sha256}.jpg"
        if not target.exists():
            target.write_bytes(prepared.data)
    return prepared
