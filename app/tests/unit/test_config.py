from pathlib import Path

import pytest

from map_qa.core.config import RunConfig, load_config
from map_qa.core.errors import ConfigError


def write_toml(tmp_path: Path, text: str) -> Path:
    p = tmp_path / "cfg.toml"
    p.write_text(text, encoding="utf-8")
    return p


def test_defaults_without_any_source():
    cfg = load_config(cli={}, env={})
    assert cfg.source == "files"
    assert cfg.output_dir == Path("reports/map-qa")
    assert cfg.data_dir == Path("course-materials/exercise-data/map-qa")
    assert cfg.work_dir == Path("course-materials/exercise-data/map-qa/data")
    assert cfg.model_reading is False
    assert cfg.max_images == 25 and cfg.max_requests == 100 and cfg.max_cost_usd == 1.0
    assert (cfg.reserve_usd_tier1, cfg.reserve_usd_tier2, cfg.reserve_usd_compare) == (0.02, 0.04, 0.02)
    assert cfg.tier1_model == "openai/gpt-6-luna-decisions"
    assert cfg.compare_model == "typesafe/jev-1.14"
    assert cfg.tier2_model == "openai/gpt-6-luna"
    assert cfg.t1_threshold == 0.80 and cfg.t1_threshold_compare == 0.80
    assert cfg.tier2_accept == "high"
    assert cfg.timeout_s == 40 and cfg.question_set_version == "qs-v1" and cfg.seed == 42


def test_precedence_cli_over_env_over_toml(tmp_path):
    toml = write_toml(tmp_path, 'source = "files"\nmax_requests = 7\n')
    cfg = load_config(cli={"config": toml, "source": "files"}, env={"MAP_QA_SOURCE": "databricks"})
    assert cfg.source == "files"
    cfg = load_config(cli={"config": toml}, env={"MAP_QA_SOURCE": "databricks"})
    assert cfg.source == "databricks"
    assert cfg.max_requests == 7


def test_config_path_from_env(tmp_path):
    toml = write_toml(tmp_path, "max_requests = 9\n")
    cfg = load_config(cli={}, env={"MAP_QA_CONFIG": str(toml)})
    assert cfg.max_requests == 9


def test_missing_toml_is_config_error(tmp_path):
    with pytest.raises(ConfigError):
        load_config(cli={"config": tmp_path / "nope.toml"}, env={})


@pytest.mark.parametrize("key", ["api_key", "token_limit", "openrouter_secret", "DATABRICKS_TOKEN"])
def test_secret_like_key_in_toml_rejected(tmp_path, key):
    toml = write_toml(tmp_path, f'{key} = "x"\n')
    with pytest.raises(ConfigError) as exc:
        load_config(cli={"config": toml}, env={})
    assert exc.value.exit_code == 2
    assert key in str(exc.value)


def test_unknown_key_rejected(tmp_path):
    toml = write_toml(tmp_path, "foo = 1\n")
    with pytest.raises(ConfigError):
        load_config(cli={"config": toml}, env={})


def test_invalid_value_rejected(tmp_path):
    with pytest.raises(ConfigError):
        load_config(cli={"source": "s3"}, env={})
    with pytest.raises(ConfigError):
        load_config(cli={"tier2_accept": "sometimes"}, env={})
    with pytest.raises(ConfigError):
        load_config(cli={"t1_threshold": 1.5}, env={})


def test_cli_none_values_do_not_override(tmp_path):
    toml = write_toml(tmp_path, "max_requests = 5\n")
    cfg = load_config(cli={"config": toml, "max_requests": None}, env={})
    assert cfg.max_requests == 5


def test_public_dump_has_no_secret_fields():
    dumped = load_config(cli={}, env={}).public_dict()
    assert isinstance(dumped, dict)
    assert all("token" not in k and "secret" not in k for k in dumped)
    assert isinstance(RunConfig.model_fields, dict)
