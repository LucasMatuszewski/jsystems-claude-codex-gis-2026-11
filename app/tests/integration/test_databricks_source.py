"""ADR-001 §5, D-11, TAC-001-04: DatabricksSource replaying REAL captures (respx; captured 2026-11-12, T30)."""
import json

import httpx
import pytest
import respx

from map_qa.core.errors import SourceUnavailable
from map_qa.sources import connect
from map_qa.sources.databricks import DatabricksSource
from map_qa.sources.schema import describe

HOST = "https://dbc-test.cloud.databricks.com"
ENV = {"DATABRICKS_HOST": HOST, "DATABRICKS_TOKEN": "dapi-FAKE-TOKEN-123", "DATABRICKS_SQL_WAREHOUSE_ID": "wh-fake"}
TABLES = ("osm_roads", "overture_segments", "photos", "photo_road_links")


def load_capture(fixtures_dir, name):
    cap = json.loads((fixtures_dir / "captures" / f"{name}.json").read_text(encoding="utf-8"))
    return cap


def mock_api(router, fixtures_dir, fail_table=None):
    statements = {}
    for t in TABLES:
        cap = load_capture(fixtures_dir, f"databricks-{t}-limit5")
        if t == fail_table:
            cap = load_capture(fixtures_dir, "databricks-missing_table_error_capture-limit5")
        statements[t] = cap
        link = (cap["response_body"].get("result") or {}).get("external_links")
        if link:
            chunk = (fixtures_dir / "captures" / f"databricks-{t}-limit5.chunk0.arrow").read_bytes()
            url = link[0]["external_link"].split("?")[0]
            router.get(url__startswith=url).mock(return_value=httpx.Response(200, content=chunk))
    posts = []

    def on_post(request):
        body = json.loads(request.content)
        posts.append(body)
        assert request.headers["authorization"] == "Bearer dapi-FAKE-TOKEN-123"
        assert body["format"] == "ARROW_STREAM" and body["disposition"] == "EXTERNAL_LINKS"
        table = body["statement"].rsplit(".", 1)[1].split()[0]
        cap = statements[table]
        return httpx.Response(cap["status"], json=cap["response_body"])

    router.post(f"{HOST}/api/2.0/sql/statements").mock(side_effect=on_post)
    return posts


def test_load_materializes_and_registers_views(tmp_path, data_dir, fixtures_dir):
    con = connect(data_dir / "data")
    with respx.mock(assert_all_called=False) as router:
        posts = mock_api(router, fixtures_dir)
        src = DatabricksSource(data_dir, tmp_path / "work", env=ENV, poll_interval=0)
        manifest = src.load(con)
        chunk_calls = [c for c in router.calls if "storage.cloud.databricks.com" in str(c.request.url)]
    assert len(posts) == 4  # TAC-001-04: one POST per table
    assert all("authorization" not in c.request.headers for c in chunk_calls)  # presigned: no token
    for t in TABLES:
        assert con.execute(f"SELECT count(*) FROM {t}").fetchone()[0] == 5
        assert manifest.table(t).rows == 5 and manifest.table(t).statement_id
    types = dict(describe(con, "photos"))
    assert types["captured_at"] == "TIMESTAMP WITH TIME ZONE" and types["bytes"] == "BIGINT"
    assert "_rescued_data" not in dict(describe(con, "osm_roads"))
    assert dict(describe(con, "osm_roads"))["geometry"].startswith("GEOMETRY")
    ok = con.execute("SELECT bool_and(ST_IsValid(geometry)) AND bool_and(ST_X(ST_StartPoint(geometry)) BETWEEN 19"
                     " AND 21) FROM osm_roads").fetchone()[0]
    assert ok  # WKB -> geometry, lon/lat order
    assert manifest.source == "databricks"
    parquet = list((tmp_path / "work" / "databricks").rglob("*.parquet"))
    assert len(parquet) == 4
    con.close()


def test_failed_state_is_source_unavailable_without_token(tmp_path, data_dir, fixtures_dir):
    con = connect(data_dir / "data")
    with respx.mock(assert_all_called=False) as router:
        mock_api(router, fixtures_dir, fail_table="osm_roads")
        with pytest.raises(SourceUnavailable) as exc:
            DatabricksSource(data_dir, tmp_path / "w", env=ENV, poll_interval=0).load(con)
    msg = str(exc.value)
    assert exc.value.exit_code == 3 and "FAILED" in msg and "TABLE_OR_VIEW_NOT_FOUND" in msg
    assert "dapi-FAKE-TOKEN-123" not in msg and "\n" not in msg
    con.close()


def test_http_error_is_source_unavailable(tmp_path, data_dir):
    con = connect(data_dir / "data")
    with respx.mock() as router:
        router.post(f"{HOST}/api/2.0/sql/statements").mock(return_value=httpx.Response(403, json={"error": "x"}))
        with pytest.raises(SourceUnavailable) as exc:
            DatabricksSource(data_dir, tmp_path / "w", env=ENV, poll_interval=0).load(con)
        assert len(router.calls) == 1  # no retry
    assert "403" in str(exc.value)
    con.close()


def test_polling_is_not_retry_and_times_out_with_cancel(tmp_path, data_dir):
    con = connect(data_dir / "data")
    clock = {"t": 0.0}
    running = {"statement_id": "s1", "status": {"state": "RUNNING"}}
    with respx.mock() as router:
        post = router.post(f"{HOST}/api/2.0/sql/statements").mock(return_value=httpx.Response(200, json=running))
        get = router.get(f"{HOST}/api/2.0/sql/statements/s1").mock(return_value=httpx.Response(200, json=running))
        cancel = router.post(f"{HOST}/api/2.0/sql/statements/s1/cancel").mock(return_value=httpx.Response(200,
                                                                                                         json={}))

        def fake_sleep(s):
            clock["t"] += 2

        src = DatabricksSource(data_dir, tmp_path / "w", env=ENV, sleep=fake_sleep, clock=lambda: clock["t"])
        with pytest.raises(SourceUnavailable) as exc:
            src.load(con)
        assert post.call_count == 1 and get.call_count >= 80 and cancel.call_count == 1
    assert "180" in str(exc.value)
    con.close()
