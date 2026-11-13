"""Executive summary data and static SVG charts (PRD §13 AC-31).

Deterministic: every number and sentence is derived from the ReportModel (no LLM call). Charts are inline SVG
with native <title> tooltips and a table view next to each chart; colors are CSS roles defined in the template
(categorical slots 1-3 and one sequential hue, validated reference palette), so dark mode swaps in one place.
"""
from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from html import escape

from map_qa.report.model import ATTRIBUTE_LABELS, CANDIDATE_STATUSES, STATUS_LABELS, ReportModel

ROW_H, GAP, LABEL_W, CHART_W, VALUE_W = 22, 8, 290, 360, 110
_ACC = re.compile(r"([0-9.]+)% \((\d+)/(\d+)\)")


@dataclass
class Bar:
    label: str
    value: float          # bar length in chart units
    text: str             # direct label
    series: int = 1       # categorical slot (1-3) or 0 = sequential hue
    tooltip: str = ""


@dataclass
class Chart:
    title: str
    unit_max: float
    bars: list[Bar]
    legend: list[tuple[int, str]] = field(default_factory=list)
    table_head: list[str] = field(default_factory=list)
    table_rows: list[list[str]] = field(default_factory=list)
    caption: str = ""

    def svg(self) -> str:
        """Horizontal bars from a shared zero baseline; one axis; direct labels in text ink."""
        h = len(self.bars) * (ROW_H + GAP) + GAP
        w = LABEL_W + CHART_W + VALUE_W
        out = [f'<svg viewBox="0 0 {w} {h}" width="100%" role="img" aria-label="{escape(self.title)}" '
               f'xmlns="http://www.w3.org/2000/svg">',
               f'<line class="axis" x1="{LABEL_W}" y1="0" x2="{LABEL_W}" y2="{h}"/>']
        for i, b in enumerate(self.bars):
            y = GAP + i * (ROW_H + GAP)
            length = 0 if self.unit_max <= 0 else max(0.0, b.value) / self.unit_max * CHART_W
            cls = f"s{b.series}" if b.series else "seq"
            out.append(f'<g><title>{escape(b.tooltip or b.label + ": " + b.text)}</title>'
                       f'<text class="lbl" x="{LABEL_W - 8}" y="{y + ROW_H * 0.7:.1f}" text-anchor="end">'
                       f'{escape(b.label)}</text>'
                       f'<rect class="{cls}" x="{LABEL_W}" y="{y}" width="{length:.1f}" height="{ROW_H}" rx="4"/>'
                       f'<text class="val" x="{LABEL_W + length + 6:.1f}" y="{y + ROW_H * 0.7:.1f}">'
                       f'{escape(b.text)}</text></g>')
        out.append("</svg>")
        return "".join(out)


def _pct(num: int, den: int) -> str:
    return "–" if den == 0 else f"{100.0 * num / den:.1f}%"


def _acc(text: str) -> tuple[float, int, int] | None:
    m = _ACC.match(text or "")
    return (float(m.group(1)), int(m.group(2)), int(m.group(3))) if m else None


def status_chart(model: ReportModel, attribute: str) -> Chart:
    rows = [c for c in model.summary.status_counts if c.attribute == attribute]
    pairs = model.summary.pairs
    bars = [Bar(f"{STATUS_LABELS[c.status]} ({c.status})", c.count, f"{c.count} ({_pct(c.count, pairs)})", 0)
            for c in rows]
    return Chart(f"{ATTRIBUTE_LABELS.get(attribute, attribute)}: statusy porównania OSM–Overture (n = {pairs} par)",
                 max([c.count for c in rows] + [1]), bars,
                 table_head=["Status", "Liczba", "% par"],
                 table_rows=[[c.status, (f"{c.attribute}:{c.status}", c.count), _pct(c.count, pairs)]
                             for c in rows])


def completeness_chart(model: ReportModel) -> Chart | None:
    rows = model.summary.completeness
    if not rows:
        return None
    bars = []
    for r in rows:
        series = 1 if r.population == "all" else 2
        pop = "wszystkie drogi" if r.population == "all" else "drogi ze zdjęciem"
        bars.append(Bar(f"{r.source} {r.attribute}", r.pct, f"{r.pct:.1f}%", series,
                        f"{r.source} {r.attribute}, {pop}: {r.with_value}/{r.total} ({r.pct:.1f}%)"))
    return Chart("Kompletność atrybutów (% dróg z wartością)", 100.0, bars,
                 legend=[(1, "wszystkie drogi"), (2, "drogi ze zdjęciem")],
                 table_head=["Źródło", "Atrybut", "Populacja", "Z wartością / mianownik", "%"],
                 table_rows=[[r.source, r.attribute, r.population, f"{r.with_value}/{r.total}", f"{r.pct:.1f}%"]
                             for r in rows])


def accuracy_chart(model: ReportModel) -> Chart | None:
    rows = [e for e in model.model.evaluation if e.tier == "tier 1" or e.tier.startswith("końcowa")
            or "porównanie" in e.tier]
    if not rows:
        return None
    bars, table = [], []
    for e in rows:
        parsed = _acc(e.accuracy_all)
        series = 1 if e.tier == "tier 1" else (2 if e.tier.startswith("końcowa") else 3)
        view = {1: "tier 1 (Luna Decisions)", 2: "końcowa: tier 1 + tier 2", 3: "Jev 1.14 (5 obrazów)"}[series]
        short = {1: "tier 1", 2: "końcowa", 3: "Jev"}[series]
        value = parsed[0] if parsed else 0.0
        text = f"{parsed[0]:.0f}% ({parsed[1]}/{parsed[2]})" if parsed else "brak ocen"
        bars.append(Bar(f"{e.question} · {short}", value, text, series,
                        f"{e.question}, {view}: accuracy {e.accuracy_all}; pokrycie {e.coverage}; "
                        f"po abstencji {e.selective_accuracy}"))
        table.append([e.question, view, e.accuracy_all, e.coverage, e.selective_accuracy, str(e.uncertain_excluded)])
    return Chart("Zgodność odczytu z etykietami AI (accuracy, abstencja = błąd)", 100.0, bars,
                 legend=[(1, "tier 1 (Luna Decisions)"), (2, "końcowa: tier 1 + tier 2"), (3, "Jev 1.14 (5 obrazów)")],
                 table_head=["Pytanie", "Wariant", "Accuracy", "Pokrycie", "Accuracy po abstencji",
                             "Wykluczone uncertain"], table_rows=table)


def insights(model: ReportModel) -> list[str]:
    s = model.summary
    out = []
    reasons: dict[str, Counter] = {"speed": Counter(), "surface": Counter()}
    for c in model.candidates:
        for a in c.attributes:
            if a.status == "not_comparable" and a.attribute in reasons:
                reasons[a.attribute][a.reason or "?"] += 1
    for attr in model.attributes():
        cnt = {c.status: c.count for c in s.status_counts if c.attribute == attr}
        top = reasons.get(attr, Counter()).most_common(1)
        why = f"; najczęstszy powód nieporównywalności: {top[0][0]} ({top[0][1]})" if top else ""
        out.append(f"{ATTRIBUTE_LABELS.get(attr, attr)}: {cnt.get('agree', 0)} z {s.pairs} par "
                   f"({_pct(cnt.get('agree', 0), s.pairs)}) ma zgodne wartości OSM i Overture, "
                   f"{cnt.get('disagree', 0)} rozbieżnych, {cnt.get('missing_osm', 0) + cnt.get('missing_overture', 0)} "
                   f"z brakującą wartością, {cnt.get('not_comparable', 0)} nieporównywalnych{why}.")
    amb = s.link_status.get("ambiguous", 0)
    out.append(f"{amb} z {s.photos} zdjęć ({_pct(amb, s.photos)}) ma niepewne połączenie z drogą i czeka na ręczny "
               f"przegląd; {s.no_candidate} zdjęć nie ma kandydata w promieniu 25 m.")
    linked = [r for r in s.completeness if r.population == "linked"]
    if linked:
        low = min(linked, key=lambda r: r.pct)
        out.append(f"Najsłabiej uzupełniony atrybut na drogach ze zdjęciami: {low.source} {low.attribute} "
                   f"({low.with_value}/{low.total}, {low.pct:.1f}%).")
    if model.model.run:
        dec = Counter()
        for d in model.model.decisions:
            dec[d.decision] += d.count
        total = sum(dec.values())
        out.append(f"Odczyt zdjęć: {total} pytań; {dec['answered']} rozstrzygnął tier 1, {dec['answered_tier2']} "
                   f"tier 2, {dec['abstain']} trafiło do kolejki ręcznej (abstain), "
                   f"{dec['model_unavailable']} błędów API, {dec['not_run_budget_or_error']} nieuruchomionych.")
        finals = [(e, _acc(e.accuracy_all)) for e in model.model.evaluation if e.tier.startswith("końcowa")]
        finals = [(e, a) for e, a in finals if a and a[2] > 0]
        if finals:
            best = max(finals, key=lambda x: x[1][0])
            worst = min(finals, key=lambda x: x[1][0])
            out.append(f"Najwyższa zgodność z etykietami AI: {best[0].question} ({best[0].accuracy_all}); "
                       f"najniższa: {worst[0].question} ({worst[0].accuracy_all}). Próbka jest mała, więc to "
                       f"wskazówka, a nie pomiar jakości.")
        if model.model.comparison_summary:
            cs = model.model.comparison_summary
            out.append(f"Luna Decisions i Jev 1.14 na tych samych 5 obrazach: zgodne odpowiedzi "
                       f"{cs.get('Zgodne odpowiedzi', '–')}, średnia różnica max(p) {cs.get('Średnia |Δ max(p)|', '–')}.")
        out.append(f"Koszt wszystkich odpowiedzi modeli w raporcie: {model.model.answers_cost_usd:.4f} USD "
                   f"(nowe żądania w tym uruchomieniu: {model.model.requests_this_run}, "
                   f"{model.model.cost_this_run_usd:.4f} USD).")
    return out


def kpis(model: ReportModel) -> list[tuple[str, str, str]]:
    s = model.summary
    agree = sum(c.count for c in s.status_counts if c.attribute == "speed" and c.status == "agree")
    cand = len(model.candidates)
    out = [("pairs", str(s.pairs), "par zdjęcie–droga"),
           ("speed_agree", _pct(agree, s.pairs), "zgodnych limitów prędkości"),
           ("candidates", str(cand), "par do przeglądu"),
           ("queue", str(len(model.manual_queue)), "pozycji w kolejce ręcznej")]
    if model.model.run:
        out.append(("cost", f"{model.model.answers_cost_usd:.4f} USD", "koszt odpowiedzi modeli"))
    return out


def summary_context(model: ReportModel) -> dict:
    charts = [status_chart(model, a) for a in model.attributes()]
    for extra in (completeness_chart(model), accuracy_chart(model)):
        if extra is not None:
            charts.append(extra)
    return {"kpis": kpis(model), "insights": insights(model), "charts": charts,
            "candidate_statuses": CANDIDATE_STATUSES}
