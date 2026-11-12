# Implementation plan — Map QA CLI (`map-qa`)

> **Status: DRAFT — awaiting human review.** Planning does not authorize execution, new agents, publication or merge.
> Date: 2026-11-12 · Branch: `Map-App-Implementation` · Author: orchestrator (Claude Code, Opus 5.5)

Sources of truth (linked, not copied): [PRD](../PRD.md), [ADR-000](../ADR/000-main-architecture.md), [ADR-001](../ADR/001-data-sources-and-normalization.md), [ADR-002](../ADR/002-spatial-matching.md), [ADR-003](../ADR/003-photo-reading-decisions.md), [ADR-004](../ADR/004-report-and-cli.md), data facts in [profile.md](../../reports/map-qa/profile.md), repository rules in [AGENTS.md](../../AGENTS.md).

## 1. Goal and scope

Build the whole MVP from the PRD as one CLI application, in phases ordered so that each phase ends in a runnable, demonstrable state:

| Phase | Demonstrable result | Main PRD flow |
|---|---|---|
| 0. Foundations | `uv run --project app map-qa --help` works, tests run | – |
| **1. First vertical slice** | `map-qa run` on local files → speed-limit statuses for photo–road pairs in `report.md`, `report.html`, `results.json`, `run_manifest.json` | [§4.1](../PRD.md#41-map-only-comparison-no-model-calls) steps 1–3, 5–7 (speed only) |
| 2. Flow 4.1 complete | + surface/lit, completeness table, `map-qa report --from` | [§4.1](../PRD.md#41-map-only-comparison-no-model-calls) |
| 3. Databricks source | `--source databricks`, `--compare-sources` | [§4.3](../PRD.md#43-data-source-selection) |
| 4. Photo reading (paid, gated) | tiered reading, budget, cache, evaluation | [§4.2](../PRD.md#42-photo-reading-with-tiered-escalation-model-calls-enabled), [§4.4](../PRD.md#44-re-run-from-cache) |
| 5. Hardening and release | cross-cutting guards, final QA, review, PR | all |

Decisions taken with the human on 2026-11-12 (recorded here, to be written into ADRs by T00):

- **Scope:** plan the whole app in logical phases; the human may later run all phases without stopping.
- **`poor_heading_alignment`:** informational flag; `link_status` stays `ok` ([ADR-002 §3.4](../ADR/002-spatial-matching.md)).
- **HTML report:** plain semantic HTML (inline CSS, `lang="pl"`, no JS, no external assets). No design reference exists (`docs/design-guidelines.md` and `assets/design-tokens.json` are absent), so visual QA checks structure, Polish text and counters only ([AGENTS.md Manual QA](../../AGENTS.md)).
- **Tracker:** the `Status` column of the matrix in §5 is the single execution tracker (no GitHub issues/projects exist).

## 2. Current state (verified 2026-11-12)

| Item | Observed |
|---|---|
| Application code | `app/` contains only `README.md` (generic scaffold checklist, not stack-specific). No `pyproject.toml`, no package, no tests, no entry point. |
| Branch / HEAD | `Map-App-Implementation` @ `8e705ec`, pushed to `origin`. |
| Working tree | Uncommitted user changes in `.claude/settings.json`, `.mcp.json`, `AGENTS.md` — **out of scope, must stay intact and unstaged**. |
| Docs | PRD and ADR-000…004 (Accepted; ADR-000/001/002 updated with profile facts). No `docs/design-guidelines.md`. `docs/plans/` created by this plan. |
| Input data | `course-materials/exercise-data/map-qa/` (read-only). `data/` sub-folder is git-ignored (cache, ledger, DuckDB extensions). |
| Outputs | `reports/map-qa/profile.md` is tracked. Generated report files are **not** git-ignored (contradicts [ADR-000 §3](../ADR/000-main-architecture.md) — see U2). |
| Tracker | GitHub issues: none. Projects: none. Open PRs: #6 (older ADRs, `worktree-prototype-a`), #8 (unrelated course material). |
| Worktrees | Only the main checkout. |

**Tool and command verification**

| Command | Result |
|---|---|
| `uv --version` | `uv 0.13.7` (Python 3.12.16 is downloaded by `uv run --python 3.12`) |
| `uv run --project app pytest app/tests` | **Baseline failure:** `error: Failed to spawn: pytest — program not found` (no project yet) |
| `uv run --project app map-qa --help` | **Baseline failure:** `Failed to spawn: map-qa — program not found` |
| `codex --version` / `codex exec --help` | `codex-cli 0.167.2`; headless `exec`, `exec review`, `-m`, `-s`, `-C`, `-o`, `--json`, `--ephemeral` present |
| `codex debug models` | Slugs include `gpt-6.1-sol`, `gpt-6-luna` |
| `opencode --version` / `opencode run --help` | `v2.2.5`; `run`, `-m`, `--format json`, `-f`, `--title`, `--auto` present |
| `opencode models` | `xiaomi-token-plan-ams/mimo-v2.6-flash`, `…/mimo-v2.6-pro` available |
| `claude --version` | `2.1.322`; this session's Agent tool accepts `model: haiku` |
| `databricks version` | `v1.26.0` (env variables are set in the human's terminal only) |
| Windows note | Python output with box characters needs `PYTHONUTF8=1` (observed with DuckDB in `profile_data.py`). |

Not yet verified (first steps after authorization): an actual `codex exec` and `opencode run` round-trip on a no-op brief (T01-S), and whether DuckDB `spatial` installs offline inside the Codex sandbox (it will not — see §6).

## 3. Unresolved decisions (need the human before the named task)

| ID | Decision | Blocks | Recommendation |
|---|---|---|---|
| U1 | **Contradiction:** [ADR-001 §3.2](../ADR/001-data-sources-and-normalization.md) registers `reference_labels`/`sign_labels` views in `DataSource`, but [ADR-003 TAC-003-03](../ADR/003-photo-reading-decisions.md) says only `Evaluator` may open label files. | T00, T10 | `DataSource` registers map views only; `Evaluator` opens label files itself. Amend ADR-001 §3.2 in T00. |
| U2 | [ADR-000 §3](../ADR/000-main-architecture.md) says `reports/map-qa/` is ignored except `.gitkeep`, but `profile.md` is tracked and nothing is ignored. | T00 | Ignore only generated files (`report.md`, `report.html`, `results.json`, `run_manifest.json`, `sample_manifest.json`); keep `profile.md` tracked; amend ADR-000 §3. |
| U3 | [ADR-000 §11](../ADR/000-main-architecture.md) questions 1–3 (implicit limits, road-class scope, evidence age). | Not blocking Phases 1–3 | Keep the current ADR defaults (`implicit_only` → `not_comparable`; flag, don't exclude per ADR-002 D-22). Revisit after the Phase 1 demo. |
| U4 | Phase 4 prerequisites: confirm `openai/gpt-6-luna` in the OpenRouter catalog, `OPENROUTER_API_KEY` set by the human, budget (≤ 3 capture requests, then ≤ 100 requests / < 1 USD). | T43, T47 | Human gate; without it Phase 4 stops after offline components with `missing_capture` skips (fallback in §8). |
| U5 | PR target and the stale PR #6. | T16, T51 | One PR `Map-App-Implementation → main`, opened as **draft** after Phase 1, marked ready after Phase 5. Close #6 as superseded (human action). |
| U6 | New shared config `opencode.json` (permissions for headless OpenCode). | T01 | Approve; content in §7.3. |

## 4. Architecture guardrails for every task

- Module boundaries, dependency direction and file layout: [ADR-000 §3–4](../ADR/000-main-architecture.md). Commands are run from the repo root: `uv run --project app …`.
- Pinned versions: [ADR-000 §2 "Przypięte wersje"](../ADR/000-main-architecture.md). Only the orchestrator edits `app/pyproject.toml` and `app/uv.lock`.
- Exit codes and Polish one-line errors: [ADR-004 §5](../ADR/004-report-and-cli.md).
- TDD per [AGENTS.md TDD Rules](../../AGENTS.md): failing behavioral test first, observed failure reason recorded in the handoff.
- API mocks only from real captures ([ADR-000 §10](../ADR/000-main-architecture.md), [ADR-003 §5.8](../ADR/003-photo-reading-decisions.md)).
- Anything not decided in an ADR is **not** invented in a brief: the worker reports it, the orchestrator writes a proposed ADR amendment for human approval.

## 5. Dependency matrix (authoritative tracker)

Legend — **Owner/model:** `ORCH` = orchestrator (Claude Code, Opus 5.5, this session); `CC-Haiku` = Claude Code ad hoc subagent, `model: haiku`; `CX-Sol` = `codex exec -m gpt-6.1-sol`; `CX-Luna` = `codex exec -m gpt-6-luna`; `OC-MiMo` = `opencode run -m xiaomi-token-plan-ams/mimo-v2.6-flash`; `HUMAN` = you. **Status:** `todo` / `in-progress` / `review` / `done` / `blocked`. Every row = one commit, created by ORCH after it reproduces the checks (format `Area: summary` per [AGENTS.md Commit Rules](../../AGENTS.md)). Paths under `app/` are abbreviated: `src/` = `app/src/map_qa/`, `tests/` = `app/tests/`.

### Phase 0 — Foundations (serial)

| ID | Task | Observable outcome | PRD/ADR links | Prerequisites | Owner/model | Editable files | Verification and handoff | Status |
|---|---|---|---|---|---|---|---|---|
| T00 | Record decisions in ADRs | ADR-001 §3.2 (U1), ADR-000 §3 (U2), ADR-002 §3.4 (`poor_heading_alignment` informational) amended; `.gitignore` ignores generated report files | ADR-000 §3, ADR-001 §3.2, ADR-002 §3.4, ADR-003 TAC-003-03 | Human approves U1, U2 | ORCH | `docs/ADR/000-*.md`, `docs/ADR/001-*.md`, `docs/ADR/002-*.md`, `.gitignore` | `git diff --check`; links resolve; `git check-ignore reports/map-qa/report.md` → ignored, `profile.md` → not ignored. Commit `Docs: record plan decisions in ADRs` | todo |
| T01 | Scaffold uv project and CLI entry point | `map-qa --help` prints usage with `run`, `report`, `capture`; pytest discovers tests | ADR-000 §2–3, ADR-004 §3.1, D-41 | T00 | ORCH (shared lockfile) | `app/pyproject.toml`, `app/uv.lock`, `src/__init__.py`, `src/__main__.py`, `src/cli.py` (stub `main(argv)`), `tests/conftest.py`, `tests/e2e/test_cli_smoke.py`, `app/AGENTS.md`, `app/map_qa.example.toml`, `opencode.json` (U6) | **Red first:** `test_cli_smoke` fails with "program not found". Then `uv sync --project app`; `uv run --project app pytest app/tests -rs` (record pass/skip counts); `uv run --project app map-qa --help` (exit 0). Pre-install DuckDB `spatial` into `course-materials/exercise-data/map-qa/data/.duckdb_extensions/`. Commit `Backend: scaffold map_qa package and CLI entry point` | todo |
| T01-S | Delegation smoke test | Each headless worker edits one scratch file in `.agent-briefs/out/` and reports back; no repo file changes | §7 | T01 | ORCH | none in repo | `git status` unchanged except ignored `.agent-briefs/`. Failure → that worker type is replaced by CC-Haiku (fallback §8). No commit | todo |
| T02 | Core contracts | Status enums, `RunConfig` with precedence CLI > `MAP_QA_*` > TOML > defaults, secret-key rejection, error types → exit codes | ADR-000 §5–6, ADR-004 §3.2, §5, §8 rows "Pierwszeństwo configu", "Sekret w TOML", "Kody wyjścia" | T01 | CC-Haiku (serial: shared contract) | `src/core/__init__.py`, `src/core/enums.py`, `src/core/config.py`, `src/core/errors.py`, `src/core/paths.py`, `tests/unit/test_config.py`, `tests/unit/test_errors.py` | Red: precedence and secret tests fail on import. Green: unit tests pass. ORCH reruns full suite. Commit `Backend: add core enums, RunConfig and exit-code errors` | todo |

### Phase 1 — First vertical slice: speed limits on local files

| ID | Task | Observable outcome | PRD/ADR links | Prerequisites | Owner/model | Editable files | Verification and handoff | Status |
|---|---|---|---|---|---|---|---|---|
| T10 | `FilesSource`, schema contract, input manifest | DuckDB views `osm_roads`, `overture_segments`, `photos`, `photo_road_links`; `InputManifest` with rows, sha256 vs `sources.json`, snapshot dates; `SchemaMismatch` → exit 4 | PRD AC-01, AC-04; ADR-001 §3.1–3.2, §4, §8 "Kontrakt schematu"; ADR-000 TAC-03 | T02 | OC-MiMo (parallel with T11, T14) | `src/sources/__init__.py`, `src/sources/files.py`, `src/sql/views_files.sql`, `tests/integration/test_files_source.py`, `tests/fixtures/schema_expected.json` | Red: test fails (module missing). Green: row counts 99 768 / 85 405 / 561 / 561; hashes equal `sources.json → files`; removed column → `SchemaMismatch`. `schema_expected.json` generated from a real `DESCRIBE`, compared with [profile.md §3](../../reports/map-qa/profile.md). Commit `Backend: load local map-qa files into DuckDB with input manifest` | todo |
| T11 | Speed normalization (OSM + Overture) | `SpeedRule` lists keep `raw`; all `maxspeed*` keys parsed incl. vehicle/lane rules as conditional; `comparable_value` | PRD AC-07, AC-08; ADR-001 §3.3 (incl. 2026-11-12 profile rows), D-13, §8 speed rows, TAC-001-01…03 | T02 | CX-Sol (parallel with T10, T14) | `src/normalize/__init__.py`, `src/normalize/speed.py`, `tests/unit/test_speed_osm.py`, `tests/unit/test_speed_overture.py` | Red: every ADR-001 §8 speed row fails. Green: all rows pass incl. `implicit_only`, `maxspeed:hgv`, `maxspeed:lanes`. Pure functions on dicts/structs; no file I/O. Commit `Backend: normalize OSM and Overture speed rules` | todo |
| T12 | Photo–road pairs and `link_status` | View `pairs` with `distance_m_recomputed` in EPSG:2180 (`always_xy`), flags mapped per ADR-002 §3.4 table incl. real flag names | PRD AC-09, AC-10; ADR-002 §3.1–3.4, §4–5, §8, TAC-002-01…03 | T10 (view names), T02 | CC-Haiku (parallel with T11 if still running) | `src/matching/__init__.py`, `src/matching/pairs.py`, `src/sql/pairs.sql`, `tests/unit/test_bearing.py`, `tests/integration/test_pairs.py` | Red: axis-order oracle (Rynek Główny vs pyproj `always_xy=True`) and spot-check fail. Green: 3 seeded pairs within 0.5 m; median Δ < 0.05 m; `ambiguous_candidates` → `ambiguous`; `poor_heading_alignment` → `ok` + flag; 3 `no_candidate`. Commit `Backend: build photo-road pairs with EPSG:2180 distance check` | todo |
| T13 | Speed comparison statuses | Exactly one speed status per pair from the PRD set | PRD AC-06, AC-07, AC-08, AC-10; ADR-001 §3.3 status table; ADR-002 §3.5, §5, TAC-002-02 | T11, T12 | CC-Haiku | `src/matching/compare.py`, `tests/unit/test_compare_speed.py`, `tests/integration/test_compare_speed.py` | Red: status table cases fail. Green: invariant `count(comparisons_speed) = count(pairs)`; `ambiguous` never `agree/disagree`; missing tag never `disagree`. Commit `Backend: assign speed comparison statuses` | todo |
| T14 | Report model and renderers | `ReportModel` → `report.md`, `report.html`, `results.json`; Polish text, disclaimer, attribution, empty states, escaping | PRD AC-21…26, §9.2, §11 disclaimer; ADR-004 §3.4–3.6, §4, §8, TAC-004-01…02; ADR-000 D-04 | T02 | CX-Luna (parallel with T10, T11) | `src/report/__init__.py`, `src/report/model.py`, `src/report/render.py`, `src/templates/report.md.j2`, `src/templates/report.html.j2`, `tests/unit/test_render.py`, `tests/integration/test_report_consistency.py`, `tests/fixtures/report_model_min.json` | Red: escaping, empty-state and MD = HTML = JSON counter tests fail. Green: `<script>` escaped, no `src="http`, relative thumbnails or placeholder, `Brak kandydatów` with 0. Uses a fixture model only (no pipeline yet). Commit `Backend: render Markdown, HTML and JSON reports from ReportModel` | todo |
| T15 | Pipeline and `map-qa run` (integration) | `uv run --project app map-qa run` on files writes 4 files, prints paths and counts, exit 0; input hashes before = after | PRD AC-01, AC-04, AC-21, §9.1; ADR-000 §6, TAC-02, TAC-03; ADR-004 §3.4, §5, §7 | T10, T13, T14 | ORCH (shared integration) | `src/pipeline.py`, `src/cli.py`, `src/report/model.py` (wiring only), `tests/e2e/test_run_files.py` | Red: e2e subprocess test fails (no `run`). Green: 4 files, header `Źródło danych: pliki lokalne`, snapshot dates 2026-11-01 / 2026-10-21.0, run < 120 s. Record build (`uv sync`), tests (counts) and startup separately. Commit `Backend: wire map-qa run pipeline for local files` | todo |
| T16 | **Gate 1:** manual QA, independent review, draft PR | Evidence pack: CLI stdout, exit code, HTML screenshot, one traced row (photo → link → `tags` → rules → status) | AGENTS.md Manual QA; ADR-004 §8 "Ręczna kontrola końcowa" | T15 | ORCH + CX-Sol review + HUMAN | `docs/plans/implementation-plan.md` (Status column only) | `PYTHONUTF8=1 uv run --project app map-qa run`; Playwright CLI screenshot of `reports/map-qa/report.html`; `codex exec review --base main -m gpt-6.1-sol` (read-only, findings only); ORCH triages findings; HUMAN accepts. Draft PR only after explicit human approval (U5). | todo |

### Phase 2 — Complete map-only flow

| ID | Task | Observable outcome | PRD/ADR links | Prerequisites | Owner/model | Editable files | Verification and handoff | Status |
|---|---|---|---|---|---|---|---|---|
| T20 | Surface and `lit` normalization | `SurfaceValue` classes and `lit` classes with `raw` kept | PRD AC-07 (between), AC-08; ADR-001 §3.4, §8 "Nawierzchnia" | T16 | CC-Haiku (parallel with T21, T23) | `src/normalize/surface.py`, `src/normalize/lit.py`, `tests/unit/test_surface.py`, `tests/unit/test_lit.py` | Red → Green per ADR-001 §8; real `SELECT DISTINCT road_surface.value` checked against the mapping, unknown → `unknown_value`. Commit `Backend: normalize surface and lit values` | todo |
| T21 | Completeness table | Counts/percentages for all roads and photo-linked roads with explicit denominators | PRD AC-11; ADR-001 §3.5, §8 "Kompletność" | T16 | OC-MiMo (parallel) | `src/normalize/completeness.py`, `src/sql/completeness.sql`, `tests/integration/test_completeness.py` | Red → Green; totals equal manifest rows; linked population ≤ 561; numbers cross-checked with [profile.md §9](../../reports/map-qa/profile.md). Commit `Backend: compute attribute completeness` | todo |
| T22 | Surface comparison + report sections (integration) | Two statuses per pair; completeness and surface in report | PRD AC-06, AC-11, AC-23; ADR-002 §3.5, §5 invariant | T20, T21 | ORCH (hotspots: `compare.py`, templates, pipeline) | `src/matching/compare.py`, `src/pipeline.py`, `src/report/model.py`, `src/templates/*.j2`, related tests | Red: invariant `count(comparisons) = 2 × count(pairs)` fails. Green + full suite + `map-qa run` manual check. Commit `Backend: add surface comparison and completeness to report` | todo |
| T23 | `map-qa report --from results.json` | Re-render without network, identical `report.md` except render date | ADR-004 §3.1, §8 "Re-render" | T16 | CX-Luna (parallel) | `src/report/rerender.py`, `tests/integration/test_rerender.py` | Red → Green with a results fixture produced by T15's real run (copied into `tests/fixtures/`). ORCH wires the subcommand in `cli.py` at integration. Commit `Backend: re-render report from results.json` | todo |
| T24 | **Gate 2:** Flow 4.1 QA | Same evidence pack as T16 plus completeness table check | AGENTS.md Manual QA | T22, T23 | ORCH + HUMAN | plan Status column | As T16 (review by CX-Sol on the phase diff). | todo |

### Phase 3 — Databricks source

| ID | Task | Observable outcome | PRD/ADR links | Prerequisites | Owner/model | Editable files | Verification and handoff | Status |
|---|---|---|---|---|---|---|---|---|
| T30 | Real Databricks capture | One `SELECT … LIMIT 5` from `photos` with `ARROW_STREAM` + `EXTERNAL_LINKS`; status, headers (no `Authorization`), body saved verbatim with date, query, CLI/API version | ADR-001 §5 (incl. "Zweryfikowane 2026-11-12"), D-11; AGENTS.md mock rule | T24; HUMAN sets `DATABRICKS_*` in the terminal | ORCH + HUMAN | `tests/fixtures/captures/databricks-photos-limit5.json` | Capture contains no token or host secret. If the workspace refuses `EXTERNAL_LINKS`, stop and write a proposed ADR-001 D-11 amendment (no plan assumption). Commit `Tests: add real Databricks statement capture` | todo |
| T31 | `DatabricksSource` | Materialization to Parquet under `map-qa/data/databricks/<statement_id>/`, same views, WKB → geometry, missing var → exit 3 | PRD AC-02, AC-03, AC-05; ADR-001 §3.2, §5, D-11, D-12, §8, TAC-001-04 | T30 | CX-Sol | `src/sources/databricks.py`, `src/sources/http.py`, `tests/unit/test_databricks_env.py`, `tests/integration/test_databricks_source.py` | Red: respx test from the T30 capture fails. Green: no second POST per table; polling ≠ retry; token never in logs. Commit `Backend: add Databricks source over SQL Statement API` | todo |
| T32 | Source selection and `--compare-sources` | `--source`/`MAP_QA_SOURCE`, side-by-side counts and key sets | PRD §4.3, AC-02, AC-03; ADR-001 §3.2; ADR-004 §3.2 | T31 | ORCH (cli/pipeline hotspot) | `src/cli.py`, `src/pipeline.py`, `src/sources/compare.py`, `tests/integration/test_compare_sources.py` | Red → Green with respx capture. Commit `Backend: select data source and compare sources` | todo |
| T33 | **Gate 3:** live parity run | `map-qa run --source databricks` and `--compare-sources` with real token: counts 99 768 / 85 405 / 561 / 561 | PRD AC-02, AC-05; ADR-001 §8 "Parzystość źródeł" | T32 | HUMAN + ORCH | plan Status column | Output scanned for token value (AC-05). Review on phase diff. | todo |

### Phase 4 — Photo reading (paid steps are human-gated)

| ID | Task | Observable outcome | PRD/ADR links | Prerequisites | Owner/model | Editable files | Verification and handoff | Status |
|---|---|---|---|---|---|---|---|---|
| T40 | Sample planner and image preparation | Deterministic 15 + 10 sample (seed 42, ≤ 2 per sequence), `sample_manifest.json` with IDs/paths only; prepared JPEG per ADR-003 §3.2 | PRD AC-14; ADR-003 §3.1–3.2, D-34, §8 "Próbka", "Przygotowanie obrazu" | T24 | CC-Haiku (parallel with T41, T42) | `src/photo_reading/sample.py`, `src/photo_reading/image.py`, `tests/unit/test_sample.py`, `tests/unit/test_image.py` | Red → Green. Sample reads labels only through the `Evaluator` loader API (U1). Commit `Backend: plan photo sample and prepare images` | todo |
| T41 | Budget ledger, cache, circuit breaker | Limits enforced before calls; cache hit costs nothing; first error opens breaker | PRD AC-13, AC-17, AC-18; ADR-003 §5.5–5.6, D-33, §8 budget/cache rows, TAC-003-02 | T24 | CX-Sol (parallel) | `src/photo_reading/budget.py`, `src/photo_reading/cache.py`, `tests/unit/test_budget.py`, `tests/unit/test_cache.py` | Red → Green with injected clock and fake transport counters (no API shape asserted). Commit `Backend: add request budget ledger and decision cache` | todo |
| T42 | Payload builder, clients, capture recorder | Payload allowlist; `map-qa capture --kind …` command; redaction of headers/base64 | PRD AC-12; ADR-003 §4.1, §5.1, §5.4, §5.8, §8 "Brak wycieku"; ADR-004 §3.1 | T24 | CX-Luna (parallel) | `src/photo_reading/payload.py`, `src/photo_reading/clients.py`, `src/photo_reading/capture.py`, `tests/unit/test_payload.py`, `tests/unit/test_capture_redaction.py` | Red: leak test fails. Green: serialized payload has exactly 2 `state` items, no IDs/labels/coordinates. No API mock created here. ORCH wires `capture` subcommand. Commit `Backend: build neutral payloads and capture recorder` | todo |
| T43 | Real OpenRouter captures | `decisions-luna-200.json`, `decisions-jev-200.json`, `chat-tier2-200.json` (+ any observed error) | ADR-003 §5.8, §9; ADR-000 §11 (model ID) | T42; **U4 approved**, `OPENROUTER_API_KEY` set by HUMAN | HUMAN + ORCH | `tests/fixtures/captures/*.json`, `docs/ADR/003-*.md` §9 (measured cost/latency) | ≤ 3 paid requests, each confirmed `y/N`. ADR-000 TAC-05 meta test passes. If tier-2 model lacks images/`json_schema`: stop, proposed ADR-003 D-32 amendment. Commit `Tests: add real OpenRouter captures and measured costs` | todo |
| T44 | Escalator and response validation | tier 1 → tier 2 → abstain / `model_unavailable`; no retry | PRD AC-16, AC-17, AC-18, AC-20; ADR-003 §4.2, §5.2–5.4, §5.7, §8 rows, TAC-003-04 | T40, T41, T43 | CX-Sol (parallel with T45) | `src/photo_reading/escalator.py`, `src/photo_reading/validate.py`, `tests/unit/test_escalator.py`, `tests/integration/test_decisions_contract.py` | Red → Green with respx replaying T43 captures; 429 → exactly 1 request. Commit `Backend: escalate photo questions across tiers` | todo |
| T45 | Evaluator | Accuracy on `certain` labels only, explicit denominators, 5-image Luna/Jev comparison | PRD AC-15, AC-19, AC-20; ADR-003 §5.9, TAC-003-03 | T40 | CC-Haiku (parallel with T44) | `src/photo_reading/evaluator.py`, `tests/unit/test_evaluator.py` | Red → Green; `answered = 0` → "nieokreślone". Commit `Backend: evaluate photo readings against reference labels` | todo |
| T46 | Wire photo reading (integration) | `--model-reading` with confirmation prompt, `--yes`, report sections 4–5 | PRD §4.2, §9.1–9.2; ADR-004 §3.3, §7; ADR-003 §3 | T44, T45 | ORCH | `src/pipeline.py`, `src/cli.py`, `src/report/model.py`, `src/templates/*.j2`, `tests/e2e/test_run_cached.py` | Red: e2e with pre-filled cache expects 0 new requests. Green + full suite. Commit `Backend: integrate tiered photo reading into run` | todo |
| T47 | **Gate 4:** paid evaluation run | ≤ 100 requests, < 1 USD; second run 0 requests and identical predictions | PRD AC-13, AC-18; ADR-003 §8 "Rzeczywisty odczyt" | T46; U4 | HUMAN + ORCH | plan Status column | Ledger rows = POST count = report counter (TAC-003-02). Review on phase diff. | todo |

### Phase 5 — Hardening and release

| ID | Task | Observable outcome | PRD/ADR links | Prerequisites | Owner/model | Editable files | Verification and handoff | Status |
|---|---|---|---|---|---|---|---|---|
| T50 | Cross-cutting guard tests | Secret scan of all outputs, base64 scan, import boundaries, SQL distance guard | PRD AC-05; ADR-000 TAC-04, TAC-06; ADR-002 TAC-002-01; ADR-003 TAC-003-01, TAC-003-03; ADR-004 TAC-004-03 | T47 (or T33 if Phase 4 is cut) | CX-Luna | `tests/e2e/test_guards.py`, `tests/unit/test_import_boundaries.py`, `tests/unit/test_sql_guard.py` | Each guard first shown to catch a controlled mutation, mutation reverted. Commit `Tests: add secret, import and SQL guards` | todo |
| T51 | **Final gate:** QA, independent review, PR | Full evidence pack; review findings triaged; PR marked ready | All PRD AC; AGENTS.md Completion Criteria | T50 | ORCH + CX-Sol + HUMAN | plan Status column, PR description | `uv sync`, full `pytest -rs`, `map-qa run` (files), screenshots; `codex exec review --base main -m gpt-6.1-sol`; second read by a capable Claude model; HUMAN accepts. Push and PR only on explicit request. | todo |

**Critical path:** T00 → T01 → T02 → T10 → T12 → T13 → T15 → T16 → T20/T21 → T22 → T24 → T30 → T31 → T32 → T33 → T42 → T43 → T44 → T46 → T47 → T50 → T51. T43 and T47 wait on the human and the API budget; they are the largest schedule risk.

**Parallel groups (disjoint files, independent inputs):** {T10, T11, T14} after T02 · {T12 ‖ T11} · {T20, T21, T23} · {T40, T41, T42} · {T44, T45}. Every brief in a group names the other concurrent tasks and their files.

## 6. Shared-file hotspots and serialization rules

| File / area | Rule |
|---|---|
| `app/pyproject.toml`, `app/uv.lock` | ORCH only (T01). Workers never run `uv add`, `uv lock` or `uv sync`; a missing dependency is reported, not added. |
| `src/core/*` (enums, config, errors) | Created in T02; later changes only by ORCH between parallel groups. |
| `src/cli.py`, `src/pipeline.py` | ORCH only (integration tasks T15, T22, T32, T46). |
| `src/templates/*.j2`, `src/report/model.py` | T14 creates; afterwards ORCH only. |
| `src/matching/compare.py` | T13 creates; T22 extends (serial). |
| `tests/conftest.py`, `tests/fixtures/captures/` | ORCH only. |
| `docs/ADR/*`, `docs/plans/*`, `.gitignore`, `opencode.json` | ORCH only. |
| User's uncommitted `.claude/settings.json`, `.mcp.json`, `AGENTS.md` | Never staged or edited; ORCH stages explicit paths only. |
| DuckDB `spatial` extension, network | Pre-installed by ORCH in T01. Codex `workspace-write` has no network by default, so workers run offline. |

One checkout is enough: all parallel tasks have disjoint files. A git worktree (`../jsystems-claude-codex-gis-2026-11-worktrees/<branch>/`, per the global worktree convention) is requested only if two workers must edit the same file, which this plan avoids.

## 7. Delegation mechanics

### 7.1 Roles

- **Orchestrator (ORCH):** makes architectural decisions, resolves contradictions, writes briefs just before dispatch, reads every diff, reproduces checks, commits, updates Status. It does not delegate acceptance.
- **Workers:** implement one row against its brief, run the named tests, report observed results and contradictions. They do not change scope, edit files outside the brief, commit, push or accept their own work.
- **Review:** CX-Sol (`codex exec review`) plus ORCH; final acceptance by HUMAN.
- **Agent definitions:** ad hoc subagents with an exact brief, no new role files. No `.claude/agents/` definitions exist and no recurring role justifies one yet. Reconsider a short `test-writer` definition only if the same restrictions are repeated in 3+ briefs.
- **Harness check:** if any mechanism fails T01-S, the same matrix runs sequentially with CC-Haiku or ORCH alone.

### 7.2 Brief contract (`.agent-briefs/<ID>.md`, git-ignored, durable on disk)

Compiled by ORCH immediately before dispatch:

1. Task ID, goal, observable outcome (copied from the matrix row).
2. Concurrent tasks and their files ("do not touch").
3. Exact editable files; everything else read-only.
4. Relevant excerpts: ADR rules, current contracts (signatures from `src/core`), predecessor outputs (e.g. view names, real `DESCRIBE` columns), sample input rows with expected results.
5. Ordered steps: write failing test → run and paste the failure → minimal code → run tests → report.
6. Exact commands: `uv run --project app pytest app/tests/<path> -rs` (with `PYTHONUTF8=1`).
7. Forbidden: dependency changes, network calls, git commit/push, editing tests to pass, inventing API shapes.
8. Report format: files changed, Red output, Green output (counts/skips), open questions/contradictions.

Links to PRD/ADR sections are included for traceability; the brief is self-contained so a small model does not need to rediscover the architecture.

### 7.3 Commands (PowerShell, run from the repo root by ORCH)

**Claude Code subagent (CC-Haiku).** In this session: Agent tool, `subagent_type: general-purpose`, `model: haiku`, prompt = "Read and execute `.agent-briefs/<ID>.md` exactly; report as section 8 requires." Runs in the background; ORCH is notified on completion.

**Codex headless (CX-Sol / CX-Luna)**, verified flags from `codex exec --help` (0.167.2). `model_reasoning_effort` and `sandbox_workspace_write.network_access` are valid config keys per Context7 `/openai/codex`:

```powershell
$env:PYTHONUTF8 = "1"
Get-Content .agent-briefs/T11.md -Raw | codex exec -C . -m gpt-6.1-sol -c model_reasoning_effort="high" -s workspace-write --ephemeral --json -o .agent-briefs/out/T11.last.md - > .agent-briefs/out/T11.jsonl
# simple tasks: -m gpt-6-luna -c model_reasoning_effort="medium"
# review (read-only, findings only):
codex exec review --base main -m gpt-6.1-sol -o .agent-briefs/out/review-gate1.md
```

**OpenCode headless (OC-MiMo)**, verified flags from `opencode run --help` (v2.2.5) and the model ID from `opencode models`:

```powershell
opencode run -m xiaomi-token-plan-ams/mimo-v2.6-flash --title T10 --format json -f .agent-briefs/T10.md --auto "Execute the attached brief exactly. Edit only the files it lists. Do not commit." > .agent-briefs/out/T10.jsonl
```

`--auto` approves everything not explicitly denied, so T01 adds a project `opencode.json` (U6). Syntax per Context7 `/websites/opencode_ai` (permissions; the last matching rule wins):

```json
{
  "$schema": "https://opencode.ai/config.json",
  "permission": {
    "bash": { "*": "allow", "git commit *": "deny", "git push *": "deny", "uv add *": "deny", "uv lock *": "deny", "uv sync *": "deny" },
    "edit": { "*": "allow", "course-materials/*": "deny", "docs/*": "deny" },
    "external_directory": "deny",
    "webfetch": "deny"
  }
}
```

### 7.4 Acceptance of a worker result (every row)

1. `git status --short` and `git diff` limited to the brief's editable files. Any other change is reverted with `git restore <that path>`; user files are never touched.
2. ORCH reruns the named tests and the full suite (`uv run --project app pytest app/tests -rs`) and records counts and skips.
3. For runtime rows, ORCH runs the real CLI and checks the output by hand.
4. ORCH stages explicit paths, commits under the row's message, and sets Status `done`.

## 8. Failure, rollback and fallback

- **Worker fails or exceeds scope:** discard only that row's files (`git restore`/delete new files), re-brief once with the observed failure; second failure → ORCH executes the row. Tests are never weakened ([AGENTS.md](../../AGENTS.md)).
- **Bad commit discovered later:** `git revert <sha>` of that row's single commit; dependent rows return to `todo`.
- **Contradiction or missing architecture:** stop the row, mark `blocked`, write a proposed ADR amendment, ask the human.
- **Tool or quota loss:** Codex/OpenCode unavailable → reassign to CC-Haiku; all subagents unavailable → ORCH runs the matrix sequentially.
- **Time runs short — smaller fallbacks, in order:**
  1. Deliver Phases 0–2 (full map-only flow on files) and skip Databricks and photo reading.
  2. Deliver only Phase 1 with the HTML renderer cut from T14: `report.md` + `results.json` + `run_manifest.json`. This fails AC-22/AC-25 for HTML and must be reported as such.
- **No OpenRouter access or budget:** Phase 4 stops after T40–T42 with integration tests skipped as `missing_capture`; the report shows `Odczyt modelem nie był uruchomiony`.
- **Databricks refuses `EXTERNAL_LINKS`:** stop at T30; proposed ADR-001 amendment (e.g. `INLINE` chunks for small tables) before T31.

## 9. Review gates

| Gate | After | Evidence required | Who accepts |
|---|---|---|---|
| Plan review | this draft | Answers to U1, U2, U5, U6; approval of matrix and owners | HUMAN |
| Gate 1 | T15 | CLI run log, exit code, HTML screenshot, one traced row, test counts, CX-Sol review triage | HUMAN (then optional draft PR) |
| Gate 2 | T23 | as Gate 1 + completeness check vs profile | HUMAN |
| Gate 3 | T32 | live parity counts, secret scan | HUMAN |
| Gate 4 | T46 | paid run counters ≤ limits, cached rerun = 0 requests | HUMAN |
| Final | T50 | full suite, QA pack, two independent reviews, PR description | HUMAN (merge is a separate decision) |

## 10. First bounded task after authorization

**T00 — record plan decisions in ADRs** (ORCH, docs only, one commit). It needs only U1 and U2 answered, has no code or dependency risk, and unblocks T01. T01 and T01-S follow; the first worker dispatch is the parallel group {T10, T11, T14} after T02.
