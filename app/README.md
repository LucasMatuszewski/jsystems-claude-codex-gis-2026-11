# map-qa — Map QA CLI (Kraków)

Compares OSM and Overture road attributes (speed limit, surface, lighting, completeness) for photo-linked roads
and, optionally, reads street photos with a tiered AI reading (decision model → general LLM → manual queue).
Writes a Polish Markdown + static HTML report. Requirements: [PRD](../docs/PRD.md); architecture:
[ADR-000](../docs/ADR/000-main-architecture.md) … [ADR-004](../docs/ADR/004-report-and-cli.md).

Run every command from the repository root (Windows: set `PYTHONUTF8=1` first).

## Setup and tests

```powershell
$env:PYTHONUTF8 = "1"
uv sync --project app
uv run --project app pytest app/tests -rs        # module test_run_cached calls the real OpenRouter API
```

## Commands

| Command | What it does |
|---|---|
| `uv run --project app map-qa run` | Local files → `reports/map-qa/report.md`, `report.html`, `results.json`, `run_manifest.json` |
| `… map-qa run --source databricks` | Same pipeline on `workspace.map_qa.*` (needs `DATABRICKS_HOST`, `DATABRICKS_TOKEN`, `DATABRICKS_SQL_WAREHOUSE_ID`) |
| `… map-qa run --compare-sources` | Adds row counts and key sets of both sources to the report header |
| `… map-qa run --model-reading [--yes]` | Paid photo reading (needs `OPENROUTER_API_KEY`); asks `y/N` unless `--yes`; limits: 100 requests, 1 USD |
| `… map-qa report --from reports/map-qa/results.json` | Re-renders the report without network |
| `… map-qa capture --kind {decisions-luna,decisions-jev,chat-tier2,databricks} [--yes] [--image <photo_id>]` | One real request, saved as a safe capture in `app/tests/fixtures/captures/` |
| `… map-qa review export [--max-items 100]` | Manual review page `reports/map-qa/review/review.html` built from the cache only (0 requests, no key needed); open it from disk, judge each decision blind, download `feedback-<export_id>.json` (PRD §14, ADR-005) |

Settings: CLI flags > `MAP_QA_*` env > TOML (`--config`, see `map_qa.example.toml`) > defaults (ADR-004 §3.2).
Secrets come only from environment variables; a TOML key that looks like a secret is rejected (exit 2).

Exit codes: `0` report written (also when the paid loop stopped on an API error), `2` configuration,
`3` source unavailable / missing variable, `4` input schema mismatch, `5` input changed during the run.

## Thumbnails (all photos)

The repository ships 40 photos in `offline/`. To show a thumbnail for every candidate, fetch the rest once into the
git-ignored `data/photos/` (public Panoramax/Mapillary files, hash-checked; a few may return 404 at the source):

```powershell
uv run --python 3.12 --with pillow==12.0.0 python -I app/tools/fetch_photos.py course-materials/exercise-data/map-qa
```

Missing photos are shown as a placeholder linking to the source page (PRD AC-27).

## Work files

Cache, ledger (`ledger.jsonl`), prepared images, DuckDB extensions and the Databricks materialization live in the
git-ignored `course-materials/exercise-data/map-qa/data/`. Inputs are never modified (hash before = after).
