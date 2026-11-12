from __future__ import annotations

import re
import subprocess
from pathlib import Path

import pytest

from tests.conftest import FIXTURES, REPO_ROOT, cli_env

FAKE_SECRETS = ("dapi-FAKE-GUARD-7f3a91", "sk-or-v1-FAKE-GUARD-55aa")
LONG_B64 = re.compile(r"[A-Za-z0-9+/]{65,}={0,2}")


def find_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for secret in FAKE_SECRETS:
            if secret in text:
                violations.append(f"{path.name}: leaked fake secret")
        if path.suffix.lower() in {".md", ".html", ".json", ".jsonl"}:
            scrubbed = re.sub(r"https?://\S+", "", text)
            if LONG_B64.search(scrubbed):
                violations.append(f"{path.name}: long base64 sequence")
    return violations


@pytest.fixture(scope="module")
def cli_output(tmp_path_factory: pytest.TempPathFactory) -> Path:
    out = tmp_path_factory.mktemp("guard-cli-output")
    completed = subprocess.run(
        ["uv", "run", "--project", "app", "map-qa", "run", "--output-dir", str(out)],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        encoding="utf-8",
        env=cli_env(DATABRICKS_TOKEN=FAKE_SECRETS[0], OPENROUTER_API_KEY=FAKE_SECRETS[1]),
        timeout=300,
    )
    assert completed.returncode == 0, completed.stdout + "\n" + completed.stderr
    assert (out / "run_manifest.json").is_file()
    for secret in FAKE_SECRETS:  # T51 review: console output is an output too (AC-05)
        assert secret not in completed.stdout and secret not in completed.stderr
    return out


def test_cli_outputs_and_capture_fixtures_are_clean(cli_output: Path) -> None:
    assert find_violations(cli_output) == []
    for capture in sorted((FIXTURES / "captures").glob("*.json")):
        scrubbed = re.sub(r"https?://\S+", "", capture.read_text(encoding="utf-8"))
        assert LONG_B64.search(scrubbed) is None, str(capture)


def test_output_guard_detects_secret_and_base64_mutations(tmp_path: Path) -> None:
    output = tmp_path / "out"
    output.mkdir()
    (output / "report.md").write_text(FAKE_SECRETS[0], encoding="utf-8")
    assert any("secret" in item for item in find_violations(output))
    (output / "report.md").write_text("A" * 100, encoding="utf-8")
    assert any("base64" in item for item in find_violations(output))


def test_databricks_error_path_does_not_echo_token(tmp_path: Path) -> None:
    """T51 review: the fake token must not appear in stdout/stderr on the Databricks path (AC-05, TAC-06).
    The host is unresolvable on purpose, so no request reaches a real workspace."""
    out = tmp_path / "out"
    completed = subprocess.run(
        ["uv", "run", "--project", "app", "map-qa", "run", "--source", "databricks", "--output-dir", str(out)],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", timeout=300,
        env=cli_env(DATABRICKS_TOKEN=FAKE_SECRETS[0], DATABRICKS_HOST="https://dbc-guard.invalid",
                    DATABRICKS_SQL_WAREHOUSE_ID="wh-guard", OPENROUTER_API_KEY=FAKE_SECRETS[1]),
    )
    assert completed.returncode == 3, completed.stderr
    for secret in FAKE_SECRETS:
        assert secret not in completed.stdout and secret not in completed.stderr
    assert completed.stderr.count("\n") == 1 and not out.exists()

