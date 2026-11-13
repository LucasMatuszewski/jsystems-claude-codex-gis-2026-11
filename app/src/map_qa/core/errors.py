"""Errors mapped to exit codes (ADR-000 §6, ADR-004 §5). Messages: one Polish line, no secrets."""
from __future__ import annotations


class MapQaError(Exception):
    exit_code = 1

    def __init__(self, message: str) -> None:
        super().__init__(" ".join(str(message).split()))


class ConfigError(MapQaError):
    exit_code = 2


class SourceUnavailable(MapQaError):
    exit_code = 3


class MissingCredential(SourceUnavailable):
    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(f"Brak wymaganej zmiennej środowiskowej {name}.")


class SchemaMismatch(MapQaError):
    exit_code = 4

    def __init__(self, table: str, column: str, detail: str = "") -> None:
        self.table, self.column = table, column
        extra = f" ({detail})" if detail else ""
        super().__init__(f"Niezgodny schemat wejścia: tabela {table}, kolumna {column}{extra}.")


class InputChanged(MapQaError):
    exit_code = 5

    def __init__(self, path: str) -> None:
        self.path = path
        super().__init__(f"Plik wejściowy zmienił się w trakcie uruchomienia: {path}.")
