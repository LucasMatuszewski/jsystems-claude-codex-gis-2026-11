"""ADR-003 §5.6 cache keys and storage; AC-18."""
from map_qa.photo_reading.cache import DecisionCache, tier1_key, tier2_key


def test_tier1_key_ignores_question_order_and_depends_on_everything_else():
    k = tier1_key("img", "model", "qs-v1", "tier1", ["b", "a"])
    assert k == tier1_key("img", "model", "qs-v1", "tier1", ["a", "b"])
    assert k != tier1_key("img2", "model", "qs-v1", "tier1", ["a", "b"])
    assert k != tier1_key("img", "other", "qs-v1", "tier1", ["a", "b"])
    assert k != tier1_key("img", "model", "qs-v2", "tier1", ["a", "b"])  # version change -> miss
    assert k != tier1_key("img", "model", "qs-v1", "compare", ["a", "b"])
    assert len(k) == 64


def test_tier2_key_per_question():
    assert tier2_key("img", "m", "qs-v1", "surface") != tier2_key("img", "m", "qs-v1", "junction_visible")


def test_put_get_roundtrip_without_base64(tmp_path):
    c = DecisionCache(tmp_path)
    key = tier1_key("img", "m", "qs-v1", "tier1", ["surface"])
    assert c.get(key) is None
    c.put(key, {"body": {"answers": {}}, "model": "m", "cost_usd": 0.001, "elapsed_ms": 10})
    got = c.get(key)
    assert got["body"] == {"answers": {}} and "captured_at" in got
    assert (tmp_path / "decisions" / f"{key}.json").is_file()
