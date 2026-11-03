# /// script
# requires-python = ">=3.12"
# dependencies = []
# ///
"""Wywołuje SQL Statement Execution REST API przez zmienne środowiskowe."""
from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import time
from urllib.error import HTTPError
from urllib.request import Request, urlopen


def make_request(statement: str, warehouse_id: str) -> dict:
    if not statement.strip():
        raise ValueError("Zapytanie SQL jest puste")
    if not warehouse_id.strip():
        raise ValueError("Brak identyfikatora SQL warehouse")
    return {"warehouse_id": warehouse_id, "statement": statement, "wait_timeout": "10s", "on_wait_timeout": "CONTINUE", "disposition": "INLINE", "format": "JSON_ARRAY"}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--statement", default="SELECT count(*) AS photos FROM workspace.map_qa.photos")
    parser.add_argument("--warehouse", default=os.environ.get("DATABRICKS_SQL_WAREHOUSE_ID"))
    parser.add_argument("--request-file", type=Path, help="Zapisz sam JSON żądania dla CLI; bez wykonania SQL i bez tokenu")
    parser.add_argument("--timeout", type=float, default=180)
    args = parser.parse_args()
    host = os.environ.get("DATABRICKS_HOST", "").rstrip("/")
    token = os.environ.get("DATABRICKS_TOKEN", "")
    if not host.startswith("https://") or not token:
        parser.error("Wymagane zmienne DATABRICKS_HOST (HTTPS) i DATABRICKS_TOKEN; nie wklejaj wartości do agenta")
    if args.timeout <= 0:
        parser.error("--timeout musi być dodatni")

    def api(path: str, body: dict | None = None) -> dict:
        request = Request(host + path, data=json.dumps(body).encode() if body is not None else None, headers={"Authorization": "Bearer " + token, "Content-Type": "application/json"})
        with urlopen(request, timeout=min(args.timeout, 60)) as response:
            return json.load(response)

    warehouse = args.warehouse
    if not warehouse:
        available = api("/api/2.0/sql/warehouses").get("warehouses", [])
        if not available:
            raise ValueError("Brak dostępnego SQL warehouse")
        warehouse = available[0]["id"]
    request = make_request(args.statement, warehouse)
    if args.request_file:
        args.request_file.parent.mkdir(parents=True, exist_ok=True)
        with args.request_file.open("x", encoding="utf-8") as handle:
            json.dump(request, handle, ensure_ascii=False, indent=2)
        print("Zapisano JSON żądania bez nagłówków uwierzytelniających")
        return
    result = api("/api/2.0/sql/statements", request)
    statement_id = result["statement_id"]
    started = time.monotonic()
    while result.get("status", {}).get("state") in ("PENDING", "RUNNING"):
        if time.monotonic() - started > args.timeout:
            print(json.dumps({"statement_id": statement_id, "state": result["status"]["state"], "note": "Upłynął czas oczekiwania klienta. Zapytanie może nadal działać; sprawdź status przez CLI."}, ensure_ascii=False))
            raise SystemExit(3)
        time.sleep(2)
        result = api("/api/2.0/sql/statements/" + statement_id)
    # INLINE results may come in several chunks: follow next_chunk_internal_link until all rows are read.
    chunk = result.get("result") or {}
    rows = list(chunk.get("data_array") or [])
    while chunk.get("next_chunk_internal_link"):
        chunk = api(chunk["next_chunk_internal_link"])
        rows.extend(chunk.get("data_array") or [])
    manifest = result.get("manifest", {})
    expected = manifest.get("total_row_count")
    if result["status"]["state"] == "SUCCEEDED" and expected is not None and expected != len(rows):
        raise ValueError(f"Odczytano {len(rows)} z {expected} wierszy")
    # Print only result/schema/status. Never request or print authentication config.
    print(json.dumps({"statement_id": statement_id, "state": result["status"]["state"], "schema": manifest.get("schema"), "rows": rows, "row_count": len(rows), "chunks": manifest.get("total_chunk_count"), "truncated": manifest.get("truncated")}, ensure_ascii=False, indent=2))
    if result["status"]["state"] != "SUCCEEDED":
        raise SystemExit(2)


if __name__ == "__main__":
    try:
        main()
    except HTTPError as exc:
        print(f"Databricks HTTP {exc.code}. Nie zapisano tokenu ani odpowiedzi błędu.")
        raise SystemExit(2)
    except (ValueError, OSError, KeyError):
        print("Nie udało się wykonać zapytania. Sprawdź zmienne, uprawnienia i identyfikator warehouse; nie wyświetlaj sekretów.")
        raise SystemExit(2)
