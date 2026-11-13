"""ADR-002 §5 invariants and TAC-002-02 on the real snapshot (speed)."""
import pytest

from map_qa.core.enums import ComparisonStatus
from map_qa.matching.compare import compare
from map_qa.matching.pairs import build_pairs
from map_qa.sources import connect
from map_qa.sources.files import FilesSource


@pytest.fixture(scope="module")
def con(data_dir):
    c = connect(data_dir / "data")
    FilesSource(data_dir).load(c)
    build_pairs(c)
    compare(c, attributes=("speed",))
    yield c
    c.close()


def test_one_speed_status_per_pair(con):
    n_pairs = con.execute("SELECT count(*) FROM pairs").fetchone()[0]
    n_cmp = con.execute("SELECT count(*) FROM comparisons WHERE attribute = 'speed'").fetchone()[0]
    distinct = con.execute("SELECT count(DISTINCT photo_id) FROM comparisons WHERE attribute = 'speed'").fetchone()[0]
    assert n_cmp == n_pairs == distinct == 558


def test_statuses_from_allowed_set(con):
    allowed = {s.value for s in ComparisonStatus}
    got = {r[0] for r in con.execute("SELECT DISTINCT status FROM comparisons").fetchall()}
    assert got <= allowed


def test_ambiguous_never_agree_or_disagree(con):
    bad = con.execute("""SELECT count(*) FROM comparisons c JOIN pairs p USING (photo_id)
                         WHERE p.link_status = 'ambiguous' AND c.status IN ('agree', 'disagree')""").fetchone()[0]
    assert bad == 0
    amb = con.execute("""SELECT count(*) FROM comparisons c JOIN pairs p USING (photo_id)
                         WHERE p.link_status = 'ambiguous' AND c.status <> 'ambiguous_link'""").fetchone()[0]
    assert amb == 0


def test_agree_disagree_only_with_both_values(con):
    bad = con.execute("""SELECT count(*) FROM comparisons WHERE status IN ('agree', 'disagree')
                         AND (osm_value IS NULL OR overture_value IS NULL)""").fetchone()[0]
    assert bad == 0
