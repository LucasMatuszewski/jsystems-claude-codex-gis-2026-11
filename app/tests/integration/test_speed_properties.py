"""Property tests on the full snapshot (ADR-001 §3.3, TAC-001-01, TAC-001-02)."""
import json
from collections import Counter

import pytest

from map_qa.core.enums import SpeedKind
from map_qa.normalize.speed import limit_type, osm_rules, overture_rules
from map_qa.sources import connect
from map_qa.sources.files import FilesSource


@pytest.fixture(scope="module")
def con(data_dir):
    c = connect(data_dir / "data")
    FilesSource(data_dir).load(c)
    yield c
    c.close()


def test_osm_limit_type_counts_and_no_lost_keys(con):
    counts: Counter = Counter()
    for (tags_json,) in con.execute("SELECT tags FROM osm_roads").fetchall():
        tags = json.loads(tags_json) if tags_json else {}
        parsed = osm_rules(tags)
        # TAC-001-01: every maxspeed* key is either a rule's tag_key or a context tag.
        seen = {r.tag_key for r in parsed.rules} | set(parsed.context_tags)
        assert seen == {k for k in tags if "maxspeed" in k}
        lt = limit_type(parsed)
        if lt:
            counts[lt] += 1
    # ADR-001 §3.3, measured 2026-11-12: 1453 ways = 1452 implicit_only + 1 type_without_value.
    assert counts == {"implicit_only": 1452, "type_without_value": 1}


def test_overture_rule_count_at_least_elements(con):
    for (limits,) in con.execute("SELECT speed_limits FROM overture_segments WHERE len(speed_limits) > 0").fetchall():
        rules = overture_rules(limits)
        assert len(rules) >= len(limits)  # TAC-001-02
        assert all(r.raw for r in rules)


def test_real_nearest_osm_rows(con):
    """ADR-001 §8 'Prawdziwe wiersze': rows from signs/nearest_osm.csv joined with signs.csv by photo_id.
    Columns there are maxspeed / maxspeed_forward / maxspeed_backward / maxspeed_conditional."""
    rows = con.execute("""
        SELECT n.photo_id, n.maxspeed, n.maxspeed_forward, n.maxspeed_backward, n.maxspeed_conditional
        FROM signs_nearest_osm n JOIN signs s USING (photo_id) ORDER BY n.photo_id""").fetchall()
    seen: dict[str, str] = {}
    for pid, ms, fw, bw, cond in rows:
        tags = {k: v for k, v in {"maxspeed": ms, "maxspeed:forward": fw, "maxspeed:backward": bw,
                                  "maxspeed:conditional": cond}.items() if v}
        parsed = osm_rules(tags)
        kinds = {r.kind for r in parsed.rules}
        if not tags:
            assert parsed.rules == []
            seen.setdefault("missing", pid)
        if ms and ms.strip().isdigit():
            assert any(r.tag_key == "maxspeed" and r.value_kmh == float(ms) for r in parsed.rules)
            seen.setdefault("numeric", pid)
        if fw or bw:
            assert {r.direction for r in parsed.rules if r.tag_key != "maxspeed"} <= {"forward", "backward"}
            seen.setdefault("directional", pid)
        if cond:
            assert any(r.condition_raw for r in parsed.rules)
            seen.setdefault("conditional", pid)
        if SpeedKind.IMPLICIT in kinds:
            seen.setdefault("implicit", pid)
        if ms and ";" in ms:
            seen.setdefault("multi", pid)
    absent = {"missing", "numeric", "directional", "conditional", "implicit", "multi"} - set(seen)
    # The test reports absent case types instead of inventing rows (ADR-001 §8).
    print("nearest_osm case types present:", sorted(seen), "absent:", sorted(absent))
    assert {"missing", "numeric"} <= set(seen)
