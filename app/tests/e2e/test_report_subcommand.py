"""E2E: `map-qa report --from results.json` (ADR-004 §3.1, §5 exit codes)."""
import shutil
import subprocess

from conftest import REPO_ROOT, cli_env


def run(*args):
    return subprocess.run(["uv", "run", "--project", "app", "map-qa", *args], cwd=REPO_ROOT, capture_output=True,
                          text=True, encoding="utf-8", env=cli_env(), timeout=120)


def test_report_from_results(tmp_path, fixtures_dir):
    shutil.copyfile(fixtures_dir / "results_real_run.json", tmp_path / "results.json")
    proc = run("report", "--from", str(tmp_path / "results.json"), "--output-dir", str(tmp_path / "out"))
    assert proc.returncode == 0, proc.stderr
    md = (tmp_path / "out" / "report.md").read_text(encoding="utf-8")
    assert "Źródło danych: pliki lokalne" in md
    assert (tmp_path / "out" / "report.html").is_file()


def test_report_missing_file_exit_2(tmp_path):
    proc = run("report", "--from", str(tmp_path / "missing.json"))
    assert proc.returncode == 2
    assert proc.stderr.startswith("Błąd:") and proc.stderr.count("\n") == 1
