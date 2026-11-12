import subprocess

from conftest import REPO_ROOT, cli_env


def test_help_lists_three_subcommands():
    proc = subprocess.run(
        ["uv", "run", "--project", "app", "map-qa", "--help"],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8", env=cli_env(),
    )
    assert proc.returncode == 0, proc.stderr
    for sub in ("run", "report", "capture"):
        assert sub in proc.stdout
