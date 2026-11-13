# Plan — manual review page for model decisions

> Date: 2026-11-13 · Branch: `manual-review-tool` (stacked on `Map-App-Implementation`, PR #10) · Owner: orchestrator (Claude Code, Opus 5.5), working alone overnight at the human's request.

Sources of truth: [PRD §14](../PRD.md#14-amendment-2026-11-13-manual-review-of-model-decisions), [ADR-005](../ADR/005-manual-review-tool.md). The main [implementation plan](implementation-plan.md) is closed; this short plan is the tracker for this change.

## Decisions taken with the human (2026-11-13)

- One static HTML + JS page; no Python import of the feedback yet.
- Blind review first, then reveal.
- Results on the page and in the downloaded JSON; reports unchanged.
- Image quality as a review flag only; no re-cutting of sign crops.
- New branch and PR targeting `Map-App-Implementation`.

## Tasks

| ID | Task | Outcome | Verification | Status |
|---|---|---|---|---|
| R0 | PRD §14, ADR-005, ADR-004 note, this plan | Scope recorded | `git diff --check`, links resolve | done |
| R1 | Item builder (`review/items.py`) | Items with model rows, priority, cap | Unit tests Red → Green | todo |
| R2 | Export command (`map-qa review export`) | `review/review.html`, `images/`, `context/` from the cache; 0 requests | Unit + E2E on the real cache; ledger unchanged | todo |
| R3 | Review page (`templates/review.html.j2`) | Blind form, reveal, overrides, flags, summary, download/load JSON | HTML safety tests; Playwright manual QA (light/dark, reload, download) | todo |
| R4 | Commit generated review page, PR | `reports/map-qa/review/` versioned like the other outputs; PR to `Map-App-Implementation` | Full test suite, `map-qa run` still exits 0 | todo |
