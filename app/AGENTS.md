# app/ — map-qa CLI (stack rules)

- Python 3.12, uv. Run everything from the repo root: `uv run --project app map-qa …`, `uv run --project app pytest app/tests -rs`. On Windows set `PYTHONUTF8=1`.
- Package `map_qa` lives in `app/src/map_qa/`; module boundaries and dependency direction: `docs/ADR/000-main-architecture.md` §3–4 (`cli → pipeline → (sources, normalize, matching, photo_reading, report) → core`).
- Dependencies are pinned with `==` (ADR-000 §2). Only the orchestrator edits `pyproject.toml` / `uv.lock`.
- Only `sources` and `photo_reading` may import `httpx` (ADR-000 TAC-04). Only `photo_reading/evaluator.py` opens label files (ADR-003 TAC-003-03).
- Distances only on EPSG:2180 geometry; SQL distance columns carry the `_2180` suffix (ADR-002 TAC-002-01).
- API mocks (respx) only from real captures in `tests/fixtures/captures/` (ADR-003 §5.8). E2E and manual tests never mock OpenRouter or Databricks.
- Tests calling real endpoints are marked `real_api` and skip with a reason when credentials are missing.
- Inputs in `course-materials/exercise-data/map-qa/` are read-only; work files go to `course-materials/exercise-data/map-qa/data/`, reports to `reports/map-qa/`.
- Report text is Polish; identifiers and file names English. CLI errors: one Polish line on stderr, exit codes per ADR-004 §5.
