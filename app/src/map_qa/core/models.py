"""Domain models shared across modules (ADR-000 §5)."""
from __future__ import annotations

from pydantic import BaseModel, Field


class TableInfo(BaseModel):
    name: str
    rows: int
    path: str | None = None
    sha256: str | None = None
    statement_id: str | None = None


class FileHash(BaseModel):
    name: str  # path relative to data_dir (or work_dir for materialized data), forward slashes
    sha256: str
    bytes: int
    expected_sha256: str | None = None
    # sha256 after CRLF -> LF normalization; set only for text files whose raw hash differs from
    # sources.json (Git core.autocrlf=true checkouts on Windows rewrite line endings).
    sha256_lf: str | None = None

    @property
    def expected_match(self) -> str | None:
        """exact | lf_normalized | mismatch | None (no entry in sources.json)."""
        if self.expected_sha256 is None:
            return None
        if self.expected_sha256 == self.sha256:
            return "exact"
        if self.sha256_lf is not None and self.expected_sha256 == self.sha256_lf:
            return "lf_normalized"
        return "mismatch"

    @property
    def matches_expected(self) -> bool | None:
        m = self.expected_match
        return None if m is None else m != "mismatch"


class InputManifest(BaseModel):
    source: str
    tables: list[TableInfo] = Field(default_factory=list)
    files: list[FileHash] = Field(default_factory=list)
    snapshots: dict[str, str] = Field(default_factory=dict)
    warnings: list[str] = Field(default_factory=list)

    def table(self, name: str) -> TableInfo:
        for t in self.tables:
            if t.name == name:
                return t
        raise KeyError(name)


class CompletenessRow(BaseModel):
    source: str
    attribute: str
    population: str  # all / linked
    with_value: int
    total: int
    pct: float
