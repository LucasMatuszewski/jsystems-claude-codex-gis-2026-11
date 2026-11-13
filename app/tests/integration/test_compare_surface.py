"""ADR-002 §5 invariant with both attributes: count(comparisons) = 2 x count(pairs)."""
from map_qa.matching.compare import compare
from map_qa.matching.pairs import build_pairs
from map_qa.sources import connect
from map_qa.sources.files import FilesSource


def test_two_statuses_per_pair(data_dir):
    con = connect(data_dir / "data")
    FilesSource(data_dir).load(con)
    build_pairs(con)
    compare(con)
    n_pairs = con.execute("SELECT count(*) FROM pairs").fetchone()[0]
    assert con.execute("SELECT count(*) FROM comparisons").fetchone()[0] == 2 * n_pairs
    per = con.execute("SELECT attribute, count(*) FROM comparisons GROUP BY 1 ORDER BY 1").fetchall()
    assert per == [("speed", n_pairs), ("surface", n_pairs)]
    dup = con.execute("SELECT count(*) FROM (SELECT photo_id, attribute FROM comparisons GROUP BY ALL"
                      " HAVING count(*) > 1)").fetchone()[0]
    assert dup == 0
    con.close()
