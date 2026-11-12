"""T30 dev script: one real Databricks SQL Statement Execution capture (ARROW_STREAM + EXTERNAL_LINKS).

Usage (repo root): uv run --project app python app/tools/capture_databricks.py --table photos --name databricks-photos-limit5
Reads DATABRICKS_HOST / DATABRICKS_TOKEN / DATABRICKS_SQL_WAREHOUSE_ID from the environment (values never printed).
Writes the statement JSON capture and the first chunk (Arrow IPC bytes) next to it. SELECT only.
"""
from __future__ import annotations

import argparse
import hashlib
import os
import sys
import time
from pathlib import Path

import httpx

from map_qa.core.capture import build_capture, mask_host, write_capture

TABLES = {"photos", "osm_roads", "overture_segments", "photo_road_links", "missing_table_error_capture"}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--table", choices=sorted(TABLES), required=True)
    ap.add_argument("--name", required=True)
    ap.add_argument("--out", default="app/tests/fixtures/captures")
    args = ap.parse_args()
    missing = [v for v in ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_SQL_WAREHOUSE_ID") if not os.environ.get(v)]
    if missing:
        print(f"Brak zmiennej: {', '.join(missing)}", file=sys.stderr)
        return 3
    host = os.environ["DATABRICKS_HOST"].rstrip("/")
    if not host.startswith("https://"):
        host = "https://" + host
    statement = f"SELECT * FROM workspace.map_qa.{args.table} LIMIT 5"
    body = {"warehouse_id": os.environ["DATABRICKS_SQL_WAREHOUSE_ID"], "statement": statement,
            "format": "ARROW_STREAM", "disposition": "EXTERNAL_LINKS", "wait_timeout": "30s",
            "on_wait_timeout": "CONTINUE"}
    out = Path(args.out)
    auth = {"Authorization": f"Bearer {os.environ['DATABRICKS_TOKEN']}"}
    with httpx.Client(timeout=40.0, follow_redirects=False) as client:
        t0 = time.monotonic()
        r = client.post(f"{host}/api/2.0/sql/statements", json=body, headers=auth)
        elapsed = (time.monotonic() - t0) * 1000
        doc = r.json()
        polls = 0
        while r.status_code == 200 and doc.get("status", {}).get("state") in ("PENDING", "RUNNING") and polls < 90:
            time.sleep(2)
            polls += 1
            r = client.get(f"{host}/api/2.0/sql/statements/{doc['statement_id']}", headers=auth)
            doc = r.json()
        meta = {"host": mask_host(host), "statement": statement,
                "body": {k: ("<warehouse_id>" if k == "warehouse_id" else v) for k, v in body.items()},
                "polls": polls}
        ver = f"httpx {httpx.__version__}; Databricks SQL Statement Execution API 2.0"
        chunk_file = chunk_sha = None
        links = (doc.get("result") or {}).get("external_links") or []
        if r.status_code == 200 and links:
            t1 = time.monotonic()
            chunk = client.get(links[0]["external_link"])  # presigned URL: no Authorization header
            chunk_ms = (time.monotonic() - t1) * 1000
            chunk_file = f"{args.name}.chunk0.arrow"
            (out / chunk_file).parent.mkdir(parents=True, exist_ok=True)
            (out / chunk_file).write_bytes(chunk.content)
            chunk_sha = hashlib.sha256(chunk.content).hexdigest()
            write_capture(build_capture(
                target="databricks", endpoint="<presigned external_link>", method="GET", status=chunk.status_code,
                response_headers=dict(chunk.headers), response_body=None, elapsed_ms=chunk_ms,
                request_meta={"chunk_index": 0, "statement": statement}, client_version=ver,
                body_file=chunk_file, body_sha256=chunk_sha), out / f"{args.name}.chunk0.json")
        write_capture(build_capture(
            target="databricks", endpoint="/api/2.0/sql/statements", method="POST", status=r.status_code,
            response_headers=dict(r.headers), response_body=doc, elapsed_ms=elapsed, request_meta=meta,
            client_version=ver), out / f"{args.name}.json")
    state = doc.get("status", {}).get("state")
    print(f"HTTP {r.status_code}, state={state}, links={len(links)}, chunk={'tak' if chunk_file else 'nie'}")
    return 0 if state == "SUCCEEDED" or args.table == "missing_table_error_capture" else 1


if __name__ == "__main__":
    sys.exit(main())
