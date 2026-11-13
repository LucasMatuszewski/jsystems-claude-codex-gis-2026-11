"""Manual review items (PRD §14 AC-33, ADR-005 D-54): one item per image–question, priority order, cap."""
from __future__ import annotations

from map_qa.photo_reading.escalator import PhotoReading
from map_qa.review.items import build_items

T1 = 0.80


def tier1(pid, q, answer, p, probs=None, kind="photo", sha="s1"):
    probs = probs or {answer: p, "other": round(1 - p, 4)}
    return PhotoReading(pid, kind, q, "answered", model="luna", tier=1, answer=answer, probability=p,
                        probabilities=probs, tier1_answer=answer, tier1_probability=p, image_sha256=sha)


def tier2(pid, q, t1_answer, t1_p, answer, certainty, decision="answered_tier2", sha="s1"):
    r = tier1(pid, q, t1_answer, t1_p, sha=sha)
    r.decision, r.model, r.tier, r.answer, r.certainty, r.probability = decision, "gpt", 2, answer, certainty, None
    return r


def labels_for(readings, value=None, status="certain"):
    return {(r.photo_id, r.question_id): (value if value is not None else r.answer, status) for r in readings}


def ids(items):
    return [i["item_id"] for i in items]


def test_one_item_per_reading_with_model_rows():
    r = tier2("p1", "street_lighting_visible", "yes", 0.75, "no", "high")
    c = tier1("p1", "street_lighting_visible", "no", 0.9)
    c.model = "jev"
    items, stats = build_items([r], [c], {("p1", "street_lighting_visible"): ("yes", "certain")}, t1_threshold=T1,
                               tier1_model="luna")
    assert len(items) == 1 and stats["reviewable"] == 1
    it = items[0]
    assert it["item_id"] == "p1|street_lighting_visible" and it["image_sha256"] == "s1"
    rows = {row["role"]: row for row in it["rows"]}
    assert rows["tier1"]["model"] == "luna"  # escalated reading: tier-1 model still named
    assert rows["tier1"]["answer"] == "yes" and rows["tier1"]["probabilities"][0] == ["yes", 0.75]
    assert rows["tier2"]["answer"] == "no" and rows["tier2"]["certainty"] == "high"
    assert rows["compare"]["answer"] == "no" and rows["compare"]["model"] == "jev"
    assert rows["final"]["answer"] == "no" and rows["final"]["decision"] == "answered_tier2"
    assert rows["reference_label"]["answer"] == "yes" and rows["reference_label"]["status"] == "certain"
    assert [o["value"] for o in it["question"]["options"]] == ["yes", "no", "unknown"]
    assert set(it["reasons"]) == {"models_disagree", "escalated", "label_disagree", "near_threshold"}


def test_probabilities_sorted_descending():
    r = tier1("p1", "surface", "paved", 0.7, probs={"unknown": 0.1, "paved": 0.7, "unpaved": 0.2})
    items, _ = build_items([r], [], labels_for([r]), t1_threshold=T1)
    assert items[0]["rows"][0]["probabilities"] == [["paved", 0.7], ["unpaved", 0.2], ["unknown", 0.1]]


def test_rows_absent_when_model_not_asked():
    r = tier1("p1", "surface", "paved", 1.0)
    items, _ = build_items([r], [], {}, t1_threshold=T1)
    roles = [row["role"] for row in items[0]["rows"]]
    assert roles == ["tier1", "final", "reference_label"]
    assert items[0]["rows"][-1]["answer"] is None  # no label: shown as missing, never as "no"


def test_priority_order_and_seeded_control():
    disagree = tier2("a", "surface", "paved", 0.6, "unpaved", "high")
    abstain = tier2("b", "surface", "unknown", 0.9, "unknown", "low", decision="abstain")
    label = tier1("c", "surface", "paved", 0.99)
    near = tier1("d", "surface", "paved", 0.85)
    controls = [tier1(f"z{i}", "surface", "paved", 0.99) for i in range(6)]
    readings = controls[:3] + [near, label, abstain, disagree] + controls[3:]
    labels = labels_for(readings)
    labels[("c", "surface")] = ("unpaved", "certain")
    items, _ = build_items(readings, [], labels, t1_threshold=T1, seed=42)
    assert ids(items)[:4] == ["a|surface", "b|surface", "c|surface", "d|surface"]
    assert sorted(ids(items)[4:]) == sorted(f"z{i}|surface" for i in range(6))
    again, _ = build_items(readings, [], labels, t1_threshold=T1, seed=42)
    assert ids(again) == ids(items)
    assert items[-1]["reasons"] == ["control"]


def test_uncertain_label_is_not_a_label_disagreement():
    r = tier1("c", "surface", "paved", 0.99)
    items, _ = build_items([r], [], {("c", "surface"): ("unpaved", "uncertain")}, t1_threshold=T1)
    assert items[0]["reasons"] == ["control"]


def test_cap_keeps_highest_priority():
    readings = [tier1(f"z{i}", "surface", "paved", 0.99) for i in range(5)]
    readings.append(tier2("a", "surface", "paved", 0.6, "unpaved", "high"))
    items, stats = build_items(readings, [], labels_for(readings), t1_threshold=T1, max_items=3)
    assert len(items) == 3 and items[0]["item_id"] == "a|surface"
    assert stats["selected"] == 3 and stats["reviewable"] == 6 and stats["cut_by_cap"] == 3


def test_not_run_reading_is_not_reviewable():
    r = PhotoReading("x", "photo", "surface", "not_run_budget_or_error", model="luna", tier=1, reason="max_requests",
                     image_sha256="s9")
    ok = tier1("p1", "surface", "paved", 0.99)
    items, stats = build_items([r, ok], [], {}, t1_threshold=T1)
    assert ids(items) == ["p1|surface"]
    assert stats["not_reviewable"] == [{"item_id": "x|surface", "decision": "not_run_budget_or_error",
                                        "reason": "max_requests"}]


def test_sign_question_has_all_speed_options():
    r = tier1("s", "speed_limit_value", "50", 0.95, kind="sign_crop")
    items, _ = build_items([r], [], {}, t1_threshold=T1)
    values = [o["value"] for o in items[0]["question"]["options"]]
    assert values[0] == "5" and values[-2:] == ["none", "unreadable"] and len(values) == 19
