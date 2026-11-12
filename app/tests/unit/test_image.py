"""ADR-003 §3.2, §8 'Przygotowanie obrazu', D-34."""
import io

import pytest
from PIL import Image

from map_qa.photo_reading.image import ImageOutOfBounds, prepare_bytes


def jpeg(w, h, exif_orientation=None, fmt="JPEG"):
    img = Image.new("RGB", (w, h), (120, 30, 30))
    buf = io.BytesIO()
    if exif_orientation:
        exif = Image.Exif()
        exif[0x0112] = exif_orientation
        exif[0x8825] = {2: (50.0, 3.0, 0.0)}  # GPS IFD
        img.save(buf, fmt, exif=exif.tobytes())
    else:
        img.save(buf, fmt)
    return buf.getvalue()


def size_of(data):
    return Image.open(io.BytesIO(data)).size


def test_small_crop_upscaled_to_256_short_side_and_min_pixels():
    p = prepare_bytes(jpeg(120, 140))
    w, h = size_of(p.data)
    assert min(w, h) >= 256 and w * h >= 78_400 and p.original_size == (120, 140)
    assert abs(w / h - 120 / 140) < 0.01  # aspect ratio kept


def test_elongated_crop_only_needs_256_short_side():
    assert min(size_of(prepare_bytes(jpeg(100, 400)).data)) == 256


def test_large_photo_downscaled_to_1568_long_side():
    p = prepare_bytes(jpeg(4000, 3000))
    assert max(size_of(p.data)) == 1568 and size_of(p.data) == (1568, 1176)


def test_exif_rotation_applied_and_metadata_removed():
    p = prepare_bytes(jpeg(400, 300, exif_orientation=6, fmt="PNG"))  # 90° rotation -> 300x400
    assert size_of(p.data) == (300, 400)
    out = Image.open(io.BytesIO(p.data))
    assert out.format == "JPEG" and not out.getexif()


def test_sha256_of_prepared_bytes_is_stable():
    a, b = prepare_bytes(jpeg(800, 600)), prepare_bytes(jpeg(800, 600))
    assert a.sha256 == b.sha256 and len(a.sha256) == 64


def test_out_of_bounds_rejected():
    with pytest.raises(ImageOutOfBounds):
        prepare_bytes(jpeg(4000, 40))  # extreme aspect: 256 short side -> 25600 long side -> too many pixels


def test_all_real_sign_crops_and_offline_photos_are_accepted(data_dir):
    from map_qa.photo_reading.image import prepare_file
    paths = list((data_dir / "signs" / "crops").glob("*.jpg")) + list((data_dir / "offline").glob("*.jpg"))
    assert len(paths) == 159
    for path in paths:
        w, h = prepare_file(path).size
        assert min(w, h) >= 256 and 78_400 <= w * h <= 2_458_624, path.name
