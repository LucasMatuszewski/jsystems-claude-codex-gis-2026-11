from __future__ import annotations

import re
from pathlib import Path

from tests.conftest import REPO_ROOT

DISTANCE_CALL = re.compile(r"\b(?:ST_Distance|ST_DWithin|ST_Distance_Sphere)\s*\(([^)]*)\)", re.I)


def find_violations(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.rglob("*.sql")):
        for line_no, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            line = line.split("--", 1)[0]
            for match in DISTANCE_CALL.finditer(line):
                args = [part.strip() for part in match.group(1).split(",")]
                geoms = [a for a in args if not re.fullmatch(r"[0-9.]+", a)]  # ST_DWithin radius literal is allowed
                if any(not re.fullmatch(r"[A-Za-z_][A-Za-z0-9_]*_2180", arg) for arg in geoms):
                    violations.append(f"{path.name}:{line_no}: distance arguments must end in _2180")
    return violations


def test_repository_sql_distance_functions() -> None:
    assert find_violations(REPO_ROOT / "app/src/map_qa/sql") == []


def test_sql_guard_detects_mutation(tmp_path: Path) -> None:
    sql_dir = tmp_path / "sql"
    sql_dir.mkdir()
    (sql_dir / "bad.sql").write_text("select ST_Distance(geometry, other);\n", encoding="utf-8")
    assert find_violations(sql_dir)
    (sql_dir / "bad.sql").write_text("select ST_DWithin(a_2180, b_2180, 25);\n", encoding="utf-8")
    assert find_violations(sql_dir) == []
