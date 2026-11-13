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
| R1 | Item builder (`review/items.py`) | Items with model rows, priority, cap | Unit tests Red → Green | done |
| R2 | Export command (`map-qa review export`) | `review/review.html`, `images/`, `context/` from the cache; 0 requests | Unit + E2E on the real cache; ledger unchanged | done |
| R3 | Review page (`templates/review.html.j2`) | Blind form, reveal, overrides, flags, summary, download/load JSON | HTML safety tests; Playwright manual QA (light/dark, reload, download) | done |
| R4 | Commit generated review page, PR | `reports/map-qa/review/` versioned like the other outputs; PR to `Map-App-Implementation` | Full test suite, `map-qa run` still exits 0 | done (`37510f9`, PR opened) |

## Verification log (2026-11-13)

- **Red → Green.** `test_review_items.py` and `test_review_page.py` / `test_review_export.py` first failed on the missing `map_qa.review` modules, then passed.
- **Real export.** `OPENROUTER_API_KEY= map-qa review export`: exit 0, 55 of 55 items (models disagree 9, escalated 5, label disagreement 4, near threshold 1, control 36), "Żądania do modeli: 0"; `ledger.jsonl` SHA-256 identical before and after; 25 prepared images and 10 sign context photos copied (3.9 MB).
- **Full suite.** `pytest app/tests -rs`: 377 passed, 0 skipped (the real-endpoint E2E ran with the key present).
- **Manual QA (Playwright CLI, page served on 127.0.0.1:8765).** Blind mode hides model rows until answer + quality; keyboard `2`/`z`/`Enter` work; reveal shows tier 1 probabilities, tier 2 certainty, comparison model, final decision and AI label with automatic agree/disagree; override, flag, comment and reviewer name survive a reload; answer changed after reveal keeps `answer_before_reveal`; summary dialog shows agreement per role and question; download writes `feedback-<export_id>.json` matching ADR-005 D-55; clearing storage and loading that file restores 2/55; blind mode off shows answers at once and records `blind: false`; dark mode, lightbox 1:1/4× with sharp pixels, 390 px width without horizontal scroll; 0 console errors, no non-local requests.
- **Fixed during QA.** Tier-1 model name missing on escalated items; raw reason codes replaced by Polish text; image-quality buttons wrapped unevenly; the crop box shadow darkened the whole page; long `none`/`unreadable` definitions stretched the compact speed-value grid.
