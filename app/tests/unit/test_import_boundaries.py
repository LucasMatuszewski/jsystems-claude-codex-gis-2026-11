from __future__ import annotations

import ast
from pathlib import Path

from tests.conftest import REPO_ROOT


def find_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.rglob("*.py")):
        rel = path.relative_to(root).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=rel)
        except SyntaxError as exc:
            violations.append(f"{rel}: syntax error: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                names = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and node.module:
                names = [node.module]
            else:
                continue
            if "httpx" in names or any(name.startswith("httpx.") for name in names):
                if not (rel.startswith("sources/") or rel.startswith("photo_reading/")):
                    violations.append(f"{rel}: forbidden httpx import")
            if rel.startswith("core/"):
                for name in names:
                    if name.startswith("map_qa.") and not name.startswith("map_qa.core"):
                        violations.append(f"{rel}: core imports {name}")
        if rel != "photo_reading/evaluator.py":
            source = path.read_text(encoding="utf-8")
            if "reference_labels" in source or "labels.csv" in source:
                violations.append(f"{rel}: label-file reference outside evaluator")
    return violations


def test_repository_import_boundaries() -> None:
    assert find_violations(REPO_ROOT / "app/src/map_qa") == []


def test_import_guard_detects_mutation(tmp_path: Path) -> None:
    root = tmp_path / "map_qa"
    (root / "report").mkdir(parents=True)
    (root / "sources").mkdir()
    (root / "report/render.py").write_text("def f():\n    import httpx\n", encoding="utf-8")
    (root / "sources/files.py").write_text('open("reference_labels.csv")\n', encoding="utf-8")
    assert any("httpx" in item for item in find_violations(root))
    assert any("label-file" in item for item in find_violations(root))
    (root / "core").mkdir()
    (root / "core/config.py").write_text("from map_qa.report.model import ReportModel\n", encoding="utf-8")
    assert any("core imports map_qa.report.model" in item for item in find_violations(root))
