from __future__ import annotations

import os
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = REPO_ROOT / "course-materials" / "exercise-data" / "map-qa"
FIXTURES = Path(__file__).resolve().parent / "fixtures"


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def data_dir() -> Path:
    return DATA_DIR


@pytest.fixture(scope="session")
def fixtures_dir() -> Path:
    return FIXTURES


def cli_env(**extra: str) -> dict[str, str]:
    env = dict(os.environ)
    env["PYTHONUTF8"] = "1"
    env.update(extra)
    return env
