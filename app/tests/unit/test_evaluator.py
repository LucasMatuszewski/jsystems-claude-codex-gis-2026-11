"""ADR-003 §5.9, §8 'Ewaluacja'; PRD AC-15, AC-19, AC-20."""
import pytest

from map_qa.photo_reading.escalator import PhotoReading
from map_qa.photo_reading.evaluator import Evaluator, Label, compare_models, evaluate


class StubEvaluator(Evaluator):
    def __init__(self, labels):
        self.labels = labels

    def label(self, photo_id, question):
        return self.labels.get((photo_id, question))


def R(pid, q, decision, answer=None, tier=1, model="luna", t1=None, p=0.9):
    return PhotoReading(pid, "photo", q, decision, model=model, tier=tier, answer=answer, probability=p,
                        tier1_answer=t1 if t1 is not None else answer, tier1_probability=p)


LABELS = {("a", "surface"): Label("paved", "certain"), ("b", "surface"): Label("unpaved", "certain"),
          ("c", "surface"): Label("paved", "uncertain"), ("d", "surface"): Label(None, "certain"),
          ("e", "surface"): Label("paved", "certain"), ("f", "surface"): Label("paved", "certain")}


def rows(readings, **kw):
    return {r.tier: r for r in evaluate(readings, StubEvaluator(LABELS), **kw) if r.question == "surface"}


def test_metrics_with_explicit_denominators():
    readings = [R("a", "surface", "answered", "paved"),
                R("b", "surface", "answered_tier2", "unpaved", tier=2, model="gpt", t1="paved", p=0.5),
                R("c", "surface", "answered", "paved"),          # uncertain label -> excluded
                R("d", "surface", "answered", "paved"),          # empty label -> excluded, never 'no'
                R("e", "surface", "abstain", "unknown", tier=2, model="gpt", t1="unknown"),
                R("f", "surface", "model_unavailable", None)]
    final = rows(readings)["końcowa (tier 1 + tier 2)"]
    assert (final.evaluated, final.correct, final.answered, final.abstained, final.unavailable,
            final.uncertain_excluded) == (4, 2, 2, 1, 1, 2)
    assert final.accuracy_all == "50.0% (2/4)"       # abstain + unavailable count as wrong
    assert final.coverage == "50.0% (2/4)"
    assert final.selective_accuracy == "100.0% (2/2)"


def test_tier1_view_counts_escalations_as_not_answered():
    readings = [R("a", "surface", "answered", "paved"),
                R("b", "surface", "answered_tier2", "unpaved", tier=2, model="gpt", t1="paved", p=0.5)]
    t1 = rows(readings)["tier 1"]
    assert (t1.evaluated, t1.answered, t1.correct) == (2, 1, 1)


def test_answered_zero_is_undetermined():
    readings = [R("a", "surface", "abstain", "unknown", tier=2, model="gpt")]
    final = rows(readings)["końcowa (tier 1 + tier 2)"]
    assert final.selective_accuracy == "nieokreślone" and final.answered == 0


def test_sign_none_and_unreadable_are_distinct_answers():
    labels = {("s1", "speed_limit_value"): Label("none", "certain"),
              ("s2", "speed_limit_value"): Label("unreadable", "certain")}
    ev = StubEvaluator(labels)
    rs = [PhotoReading("s1", "sign_crop", "speed_limit_value", "answered", model="l", tier=1, answer="unreadable",
                       tier1_answer="unreadable"),
          PhotoReading("s2", "sign_crop", "speed_limit_value", "answered", model="l", tier=1, answer="unreadable",
                       tier1_answer="unreadable")]
    final = [r for r in evaluate(rs, ev) if r.tier.startswith("końcowa")][0]
    assert (final.evaluated, final.correct) == (2, 1)


def test_compare_models_same_images_only():
    luna = [R("a", "surface", "answered", "paved", p=0.9), R("b", "surface", "abstain", "paved", p=0.5),
            R("z", "surface", "answered", "paved", p=0.9)]  # z not in compare subset
    jev = [R("a", "surface", "answered", "paved", model="jev", p=0.8),
           R("b", "surface", "answered", "unpaved", model="jev", p=0.7)]
    table, summary = compare_models(luna, jev)
    assert [(r.photo_id, r.same) for r in table] == [("a", True), ("b", False)]
    assert table[0].p_diff == pytest.approx(0.1)
    assert summary["Zgodne odpowiedzi"] == "1/2"


def test_label_rows_for_report():
    readings = [R("a", "surface", "answered", "paved"), R("c", "surface", "answered", "paved")]
    out = StubEvaluator(LABELS).label_columns(readings)
    assert out[("a", "surface")] == ("paved", "certain") and out[("c", "surface")] == ("paved", "uncertain")
