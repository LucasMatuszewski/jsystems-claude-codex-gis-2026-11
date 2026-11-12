"""RunConfig and its loading: CLI > env > TOML > defaults (ADR-004 §3.2)."""
from __future__ import annotations

import fnmatch
import tomllib
from collections.abc import Mapping
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from map_qa.core.errors import ConfigError

SECRET_PATTERNS = ("*token*", "*key*", "*secret*")


class RunConfig(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    source: Literal["files", "databricks"] = "files"
    data_dir: Path = Path("course-materials/exercise-data/map-qa")
    output_dir: Path = Path("reports/map-qa")
    work_dir: Path = Path("course-materials/exercise-data/map-qa/data")
    model_reading: bool = False
    yes: bool = False
    compare_sources: bool = False
    max_images: int = Field(25, ge=1)
    max_requests: int = Field(100, ge=0)
    max_cost_usd: float = Field(1.00, ge=0)
    reserve_usd_tier1: float = Field(0.002, gt=0)
    reserve_usd_tier2: float = Field(0.004, gt=0)
    reserve_usd_compare: float = Field(0.002, gt=0)
    tier1_model: str = "openai/gpt-6-luna-decisions"
    compare_model: str = "typesafe/jev-1.14"
    tier2_model: str = "openai/gpt-6-luna"
    t1_threshold: float = Field(0.80, ge=0, le=1)
    t1_threshold_compare: float = Field(0.80, ge=0, le=1)
    tier2_accept: Literal["high", "medium", "low"] = "high"
    timeout_s: float = Field(40, gt=0)
    question_set_version: str = "qs-v1"
    seed: int = 42
    config_path: Path | None = None

    def public_dict(self) -> dict[str, Any]:
        """Config copy for run_manifest.json / report (never contains secrets)."""
        return {k: (str(v) if isinstance(v, Path) else v) for k, v in self.model_dump().items()}


# Keys only settable via CLI flags (ADR-004 §3.2 rows with "–" in the TOML column).
CLI_ONLY = {"yes", "compare_sources", "config_path"}
TOML_KEYS = set(RunConfig.model_fields) - CLI_ONLY


def _is_secret_key(key: str) -> bool:
    low = key.lower()
    return any(fnmatch.fnmatch(low, pat) for pat in SECRET_PATTERNS)


def _read_toml(path: Path) -> dict[str, Any]:
    try:
        with open(path, "rb") as fh:
            data = tomllib.load(fh)
    except FileNotFoundError:
        raise ConfigError(f"Nie znaleziono pliku konfiguracji: {path}.") from None
    except tomllib.TOMLDecodeError as exc:
        raise ConfigError(f"Niepoprawny plik TOML {path}: {exc}.") from None
    for key in data:
        if _is_secret_key(key):
            raise ConfigError(
                f"Plik konfiguracji zawiera klucz wyglądający na sekret ({key}); sekrety tylko w zmiennych środowiskowych.")
        if key not in TOML_KEYS:
            raise ConfigError(f"Nieznany klucz konfiguracji: {key}.")
    return data


def load_config(cli: Mapping[str, Any], env: Mapping[str, str]) -> RunConfig:
    values: dict[str, Any] = {}
    config_path = cli.get("config") or env.get("MAP_QA_CONFIG")
    if config_path:
        values.update(_read_toml(Path(config_path)))
        values["config_path"] = Path(config_path)
    if env.get("MAP_QA_SOURCE"):
        values["source"] = env["MAP_QA_SOURCE"]
    for key, val in cli.items():
        if key == "config" or val is None:
            continue
        values[key] = val
    try:
        return RunConfig(**values)
    except ValidationError as exc:
        first = exc.errors()[0]
        loc = ".".join(str(p) for p in first["loc"])
        raise ConfigError(f"Niepoprawna konfiguracja: {loc}: {first['msg']}.") from None
