"""PRD §4.3 step 4, ADR-001 §3.2 '--compare-sources'; ADR-004 §3.1 'capture --kind databricks' (respx from captures)."""
import io
import json

import respx

from map_qa.sources import connect
from map_qa.sources.compare import compare_sources
from map_qa.sources.databricks import DatabricksSource, record_capture
from map_qa.sources.files import FilesSource
from tests.integration.test_databricks_source import ENV, HOST, mock_api


def test_compare_reports_counts_and_key_differences(tmp_path, data_dir, fixtures_dir):
    con = connect(data_dir / "data")
    FilesSource(data_dir).load(con)
    with respx.mock(assert_all_called=False) as router:
        mock_api(router, fixtures_dir)
        rows = compare_sources(con, DatabricksSource(data_dir, tmp_path / "w", env=ENV, poll_interval=0),
                               work_dir=data_dir / "data")
    by = {r.table: r for r in rows}
    assert set(by) == {"osm_roads", "overture_segments", "photos", "photo_road_links"}
    assert by["osm_roads"].selected_rows == 99768 and by["osm_roads"].other_rows == 5
    assert by["osm_roads"].equal is False
    assert by["photos"].keys_only_other == 0  # the 5 captured photos exist locally
    assert by["photos"].keys_only_selected == 556
    # the selected source's views are untouched
    assert con.execute("SELECT count(*) FROM photos").fetchone()[0] == 561
    con.close()


def test_record_capture_writes_safe_capture(tmp_path, fixtures_dir):
    with respx.mock(assert_all_called=False) as router:
        mock_api(router, fixtures_dir)
        out = io.StringIO()
        path = record_capture(ENV, tmp_path, name="photos-test", out=out)
        assert len([c for c in router.calls if c.request.method == "POST"]) == 1
    doc = json.loads(path.read_text(encoding="utf-8"))
    assert doc["target"] == "databricks" and doc["status"] == 200
    assert "dapi-FAKE-TOKEN-123" not in path.read_text(encoding="utf-8")
    assert HOST.split("//")[1] not in path.read_text(encoding="utf-8")
    assert doc["response_body"]["status"]["state"] == "SUCCEEDED"
    assert (tmp_path / "photos-test.chunk0.arrow").is_file()
