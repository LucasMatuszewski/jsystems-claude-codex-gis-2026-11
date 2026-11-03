# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb==1.5.6"]
# ///
"""Uruchamia wyłącznie zapytania profilujące dołączone dane."""
from pathlib import Path
import os
import duckdb

if __name__ == "__main__":
    base = Path(__file__).resolve().parent
    os.chdir(base)
    connection = duckdb.connect()
    connection.execute("SET memory_limit='3GB'; SET threads=4")
    for statement in connection.extract_statements((base / "profile.sql").read_text(encoding="utf-8")):
        print(statement.query.strip(), flush=True)
        result = connection.sql(statement.query)
        if result is not None:
            result.show(max_rows=30)
