"""ADR-003 §3.1, §8 'Próbka'; PRD AC-14, AC-15 (labels only through the Evaluator API)."""
import zlib
from collections import Counter

import pytest

from map_qa.photo_reading.evaluator import Evaluator
from map_qa.photo_reading.sample import plan_sample


@pytest.fixture(scope="module")
def manifest(data_dir):
    return plan_sample(data_dir, Evaluator(data_dir), seed=42, max_images=25)


def test_sizes_and_kinds(manifest):
    kinds = Counter(i["kind"] for i in manifest["items"])
    assert kinds == {"photo": 15, "sign_crop": 10}
    assert len(manifest["items"]) <= 25


def test_questions_per_kind(manifest):
    for item in manifest["items"]:
        if item["kind"] == "photo":
            assert item["questions"] == ["surface", "junction_visible", "street_lighting_visible"]
        else:
            assert item["questions"] == ["speed_limit_value"]


def test_max_two_per_sequence(manifest):
    for kind in ("photo", "sign_crop"):
        seqs = Counter(i["sequence"] for i in manifest["items"] if i["kind"] == kind)
        assert max(seqs.values()) <= 2


def test_deterministic(data_dir, manifest):
    again = plan_sample(data_dir, Evaluator(data_dir), seed=42, max_images=25)
    assert again == manifest
    other = plan_sample(data_dir, Evaluator(data_dir), seed=7, max_images=25)
    assert [i["photo_id"] for i in other["items"]] != [i["photo_id"] for i in manifest["items"]]


def test_manifest_has_only_ids_and_paths(manifest):
    allowed = {"photo_id", "kind", "path", "sequence", "questions", "compare"}
    for item in manifest["items"]:
        assert set(item) <= allowed
    text = repr(manifest)
    for leak in ("certain", "paved", "label", "mapillary_value", "negative_type"):
        assert leak not in text


def test_files_exist_and_comparison_subset(manifest, data_dir):
    for item in manifest["items"]:
        assert (data_dir / item["path"]).is_file()
    cmp = [i for i in manifest["items"] if i["compare"]]
    assert [i["kind"] for i in cmp] == ["photo"] * 3 + ["sign_crop"] * 2
    assert cmp == [i for i in manifest["items"] if i["kind"] == "photo"][:3] + \
        [i for i in manifest["items"] if i["kind"] == "sign_crop"][:2]


def test_six_positive_four_negative_signs(manifest, data_dir):
    strata = Evaluator(data_dir).sign_strata()
    got = Counter(strata[i["photo_id"]] for i in manifest["items"] if i["kind"] == "sign_crop")
    assert got == {"positive": 6, "negative": 4}


def test_missing_image_is_replaced_and_counted(data_dir, tmp_path):
    m = plan_sample(data_dir, Evaluator(data_dir), seed=42, max_images=25,
                    exists=lambda p: p.is_file() and ("offline" not in str(p) or zlib.crc32(str(p).encode()) % 3 != 0))
    assert sum(1 for i in m["items"] if i["kind"] == "photo") == 15
    assert m["counters"]["image_missing"] > 0


def test_max_images_caps_total(data_dir):
    m = plan_sample(data_dir, Evaluator(data_dir), seed=42, max_images=10)
    assert len(m["items"]) <= 10
