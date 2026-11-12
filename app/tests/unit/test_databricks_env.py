"""PRD AC-03, ADR-001 §8 'Databricks brak zmiennej': exit 3, names the variable, creates no report."""
import io

import pytest

from map_qa.cli import main
from map_qa.core.errors import MissingCredential
from map_qa.sources.databricks import required_env


@pytest.mark.parametrize("missing", ["DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_SQL_WAREHOUSE_ID"])
def test_required_env_names_missing(missing):
    env = {"DATABRICKS_HOST": "https://h", "DATABRICKS_TOKEN": "t", "DATABRICKS_SQL_WAREHOUSE_ID": "w"}
    env.pop(missing)
    with pytest.raises(MissingCredential) as exc:
        required_env(env)
    assert missing in str(exc.value)


def test_cli_without_token_exits_3_and_writes_nothing(tmp_path):
    out_dir = tmp_path / "out"
    err = io.StringIO()
    env = {"DATABRICKS_HOST": "https://h.cloud.databricks.com", "DATABRICKS_SQL_WAREHOUSE_ID": "w",
           "MAP_QA_SOURCE": "databricks"}
    code = main(["run", "--output-dir", str(out_dir)], env=env, stdout=io.StringIO(), stderr=err)
    assert code == 3
    assert "DATABRICKS_TOKEN" in err.getvalue() and err.getvalue().count("\n") == 1
    assert not out_dir.exists()
