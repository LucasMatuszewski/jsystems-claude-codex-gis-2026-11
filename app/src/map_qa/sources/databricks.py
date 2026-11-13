"""DatabricksSource: SQL Statement Execution API -> local Parquet -> same DuckDB views (ADR-001 §3.2, §5, D-11/D-12).

Response shapes follow the real captures in app/tests/fixtures/captures/databricks-*.json (2026-11-12).
"""
from __future__ import annotations

import io
import time
from pathlib import Path
from typing import Any, Callable

import duckdb
import httpx
import pyarrow.ipc as ipc
import pyarrow.parquet as pq

from map_qa.core.errors import MissingCredential, SourceUnavailable
from map_qa.core.models import InputManifest, TableInfo
from map_qa.sources import MAP_VIEWS, sql_literal
from map_qa.sources.files import (
    LOCAL_ONLY_VIEWS, hash_file, hash_warnings, read_sources_json, register_views, snapshots_from,
)
from map_qa.sources.http import make_client
from map_qa.sources.schema import check_schema, describe

ENV_VARS = ("DATABRICKS_HOST", "DATABRICKS_TOKEN", "DATABRICKS_SQL_WAREHOUSE_ID")
TERMINAL_FAIL = {"FAILED", "CANCELED", "CLOSED"}
# Type alignment with the local files (facts from the T30 captures, ADR-001 §5).
CASTS = {"photos": {"captured_at": "TIMESTAMPTZ", "bytes": "BIGINT", "width": "BIGINT", "height": "BIGINT"}}
DROP = {"_rescued_data"}
INT_TO_BIGINT = {"photos", "photo_road_links"}  # local CSVs are read as BIGINT


def required_env(env: dict[str, str]) -> tuple[str, str, str]:
    for name in ENV_VARS:
        if not env.get(name):
            raise MissingCredential(name)
    host = env["DATABRICKS_HOST"].strip().rstrip("/")
    if not host.startswith("https://"):
        host = "https://" + host
    return host, env["DATABRICKS_TOKEN"], env["DATABRICKS_SQL_WAREHOUSE_ID"]


def _safe(msg: Any, secret: str) -> str:
    text = " ".join(str(msg or "").split())[:300]
    return text.replace(secret, "***") if secret else text


class DatabricksSource:
    name = "databricks"

    def __init__(self, data_dir: Path, work_dir: Path, env: dict[str, str], timeout_s: float = 40.0,
                 poll_interval: float = 2.0, poll_timeout: float = 180.0, client: httpx.Client | None = None,
                 sleep: Callable[[float], None] = time.sleep, clock: Callable[[], float] = time.monotonic) -> None:
        self.data_dir, self.work_dir, self.env = Path(data_dir), Path(work_dir), env
        self.timeout_s, self.poll_interval, self.poll_timeout = timeout_s, poll_interval, poll_timeout
        self._client, self.sleep, self.clock = client, sleep, clock

    # -------------------------------------------------------------- HTTP
    def _auth(self, token: str) -> dict[str, str]:
        return {"Authorization": f"Bearer {token}"}  # built here only; never logged

    def _request(self, client: httpx.Client, method: str, url: str, token: str | None, **kw) -> httpx.Response:
        try:
            return client.request(method, url, headers=self._auth(token) if token else None, **kw)
        except httpx.TimeoutException:
            raise SourceUnavailable("Databricks: przekroczono czas odpowiedzi.") from None
        except httpx.HTTPError as exc:
            raise SourceUnavailable(f"Databricks: błąd sieci ({type(exc).__name__}).") from None

    def _json(self, resp: httpx.Response, what: str) -> dict[str, Any]:
        if resp.status_code != 200:
            raise SourceUnavailable(f"Databricks: HTTP {resp.status_code} przy {what}.")
        try:
            return resp.json()
        except ValueError:
            raise SourceUnavailable(f"Databricks: niepoprawna odpowiedź przy {what}.") from None

    def materialize(self, client: httpx.Client, host: str, token: str, warehouse: str, table: str
                    ) -> tuple[str, list[Path], int]:
        statement = f"SELECT * FROM workspace.map_qa.{table}"  # fixed query, no user input
        body = {"warehouse_id": warehouse, "statement": statement, "format": "ARROW_STREAM",
                "disposition": "EXTERNAL_LINKS", "wait_timeout": "30s", "on_wait_timeout": "CONTINUE"}
        doc = self._json(self._request(client, "POST", f"{host}/api/2.0/sql/statements", token, json=body),
                         f"wykonaniu zapytania ({table})")
        sid = doc.get("statement_id", "")
        start = self.clock()
        while (doc.get("status") or {}).get("state") in ("PENDING", "RUNNING"):  # polling, not retry
            if self.clock() - start >= self.poll_timeout:
                try:
                    self._request(client, "POST", f"{host}/api/2.0/sql/statements/{sid}/cancel", token)
                finally:
                    raise SourceUnavailable(f"Databricks: zapytanie ({table}) nie zakończyło się w "
                                            f"{int(self.poll_timeout)} s; anulowano.")
            self.sleep(self.poll_interval)
            doc = self._json(self._request(client, "GET", f"{host}/api/2.0/sql/statements/{sid}", token),
                             f"sprawdzaniu stanu ({table})")
        status = doc.get("status") or {}
        state = status.get("state")
        if state != "SUCCEEDED":
            err = status.get("error") or {}
            raise SourceUnavailable(f"Databricks: stan {state} dla {table}: "
                                    f"{_safe(err.get('message') or err.get('error_code'), token)}")
        out_dir = self.work_dir / "databricks" / sid
        out_dir.mkdir(parents=True, exist_ok=True)
        paths: list[Path] = []
        rows = 0
        result = doc.get("result") or {}
        while True:
            links = result.get("external_links") or []
            next_index = None
            for link in links:
                # presigned URL: fetched WITHOUT the Authorization header
                chunk = self._request(client, "GET", link["external_link"], None)
                if chunk.status_code != 200:
                    raise SourceUnavailable(f"Databricks: HTTP {chunk.status_code} przy pobieraniu wyników ({table}).")
                tbl = ipc.open_stream(io.BytesIO(chunk.content)).read_all()
                path = out_dir / f"{table}-{link.get('chunk_index', len(paths)):05d}.parquet"
                pq.write_table(tbl, path)
                paths.append(path)
                rows += tbl.num_rows
                next_index = link.get("next_chunk_index")
            if next_index is None:
                break
            result = self._json(self._request(
                client, "GET", f"{host}/api/2.0/sql/statements/{sid}/result/chunks/{next_index}", token),
                f"pobieraniu chunku {next_index} ({table})")
        expected = (doc.get("manifest") or {}).get("total_row_count")
        if expected is not None and int(expected) != rows:
            raise SourceUnavailable(f"Databricks: {table} ma {rows} wierszy zamiast {expected} z manifestu.")
        return sid, paths, rows

    # -------------------------------------------------------------- views
    def _register(self, con: duckdb.DuckDBPyConnection, table: str, paths: list[Path]) -> None:
        files = "[" + ", ".join(sql_literal(p.resolve().as_posix()) for p in paths) + "]"
        cols = describe(con, f"read_parquet({files})")
        casts = CASTS.get(table, {})
        select = []
        for name, typ in cols:
            q = '"' + name.replace('"', '""') + '"'
            if name in DROP:
                continue
            if name == "geometry" and typ == "BLOB":
                select.append(f"ST_GeomFromWKB({q}) AS {q}")
            elif name in casts:
                select.append(f"CAST({q} AS {casts[name]}) AS {q}")
            elif typ == "INTEGER" and table in INT_TO_BIGINT:
                select.append(f"CAST({q} AS BIGINT) AS {q}")
            else:
                select.append(q)
        con.execute(f"CREATE OR REPLACE VIEW {table} AS SELECT {', '.join(select)} FROM read_parquet({files})")

    def load(self, con: duckdb.DuckDBPyConnection) -> InputManifest:
        host, token, warehouse = required_env(self.env)
        sources = read_sources_json(self.data_dir)
        manifest = InputManifest(source=self.name, snapshots=snapshots_from(sources))
        client = self._client or make_client(self.timeout_s)
        try:
            for table in MAP_VIEWS:
                sid, paths, rows = self.materialize(client, host, token, warehouse, table)
                self._register(con, table, paths)
                manifest.tables.append(TableInfo(name=table, rows=rows, statement_id=sid,
                                                 path=f"databricks/{sid}/"))
        finally:
            if self._client is None:
                client.close()
        for view in MAP_VIEWS:
            check_schema(con, view)
        # Labels and signs/ are always local (ADR-001 §3.2).
        register_views(con, self.data_dir, LOCAL_ONLY_VIEWS)
        expected = sources.get("files", {})
        manifest.files.append(hash_file(self.data_dir, "sources.json", expected))
        for view, rel in (("signs", "signs/signs.csv"), ("signs_nearest_osm", "signs/nearest_osm.csv")):
            fh = hash_file(self.data_dir, rel, expected)
            manifest.files.append(fh)
            n = con.execute(f"SELECT count(*) FROM {view}").fetchone()[0]
            manifest.tables.append(TableInfo(name=view, rows=n, path=rel, sha256=fh.sha256))
        manifest.warnings.extend(hash_warnings(manifest.files))
        return manifest


def record_capture(env: dict[str, str], captures_dir: Path, name: str = "databricks-photos-limit5",
                   out=None, timeout_s: float = 40.0) -> Path:
    """`map-qa capture --kind databricks`: one real `SELECT * ... photos LIMIT 5` (ARROW_STREAM + EXTERNAL_LINKS),
    statement JSON + first chunk written per the ADR-003 §5.8 capture schema (replaces app/tools script)."""
    import hashlib

    from map_qa.core.capture import build_capture, mask_host, write_capture

    host, token, warehouse = required_env(env)
    statement = "SELECT * FROM workspace.map_qa.photos LIMIT 5"
    body = {"warehouse_id": warehouse, "statement": statement, "format": "ARROW_STREAM",
            "disposition": "EXTERNAL_LINKS", "wait_timeout": "30s", "on_wait_timeout": "CONTINUE"}
    ver = f"httpx {httpx.__version__}; Databricks SQL Statement Execution API 2.0"
    captures_dir = Path(captures_dir)
    src = DatabricksSource(Path("."), Path("."), env=env, timeout_s=timeout_s)
    with make_client(timeout_s) as client:
        t0 = time.monotonic()
        resp = src._request(client, "POST", f"{host}/api/2.0/sql/statements", token, json=body)
        elapsed = (time.monotonic() - t0) * 1000
        try:
            doc = resp.json()
        except ValueError:
            doc = {"raw_text": resp.text[:2000]}
        links = (doc.get("result") or {}).get("external_links") or [] if isinstance(doc, dict) else []
        if links:
            t1 = time.monotonic()
            chunk = src._request(client, "GET", links[0]["external_link"], None)
            chunk_file = f"{name}.chunk0.arrow"
            captures_dir.mkdir(parents=True, exist_ok=True)
            (captures_dir / chunk_file).write_bytes(chunk.content)
            write_capture(build_capture(
                target="databricks", endpoint="<presigned external_link>", method="GET", status=chunk.status_code,
                response_headers=dict(chunk.headers), response_body=None,
                elapsed_ms=(time.monotonic() - t1) * 1000, request_meta={"chunk_index": 0, "statement": statement},
                client_version=ver, body_file=chunk_file, body_sha256=hashlib.sha256(chunk.content).hexdigest()),
                captures_dir / f"{name}.chunk0.json")
        meta = {"host": mask_host(host), "statement": statement,
                "body": {k: ("<warehouse_id>" if k == "warehouse_id" else v) for k, v in body.items()}}
        path = write_capture(build_capture(
            target="databricks", endpoint="/api/2.0/sql/statements", method="POST", status=resp.status_code,
            response_headers=dict(resp.headers), response_body=doc, elapsed_ms=elapsed, request_meta=meta,
            client_version=ver), captures_dir / f"{name}.json")
    if out is not None:
        out.write(f"Zapisano capture: {path} (HTTP {resp.status_code})\n")
    return path
