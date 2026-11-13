---
name: write-implementation-plan
description: Create or revise an audited implementation plan from requirements, architecture and repository evidence, with mandatory delegation and human review before execution. Offers native-subagent and mixed headless-CLI modes. Use for planning, not immediate implementation.
---

# Write an implementation plan


Plan the user's chosen scope: a bounded change, a vertical slice, or a phased product. Adapt to the actual project. Do not inherit the source case's stack, models, budgets or product decisions.

Planning is a separate authorization boundary. A request to plan, or approval of a draft for review, does not start implementation, workers, publication or merge. Require explicit execution authorization. Read-only planning/audit agents may run only when authorized by the session or applicable instructions; otherwise audit yourself and disclose the lack of independence.

## 1. Evidence and questions

- Confirm application checkout, branch/HEAD, dirty files, applicable root/nested agent instructions, actual code/contracts, entry points, dependencies, tests, runtime and tracker. Preserve unrelated work.
- Read authoritative PRD/requirements, relevant ADRs and design guidance (or approved equivalents). Record missing sources; do not invent scope or architecture. Teaching examples are not project requirements.
- Discover build/test/startup commands from the actual project. Run safe scoped baseline checks when authorized; capture actual exit codes, not a pipe/filter's exit code. Distinguish observed results from proposed commands. Record failures, counts/skips and unavailable services honestly. Do not make paid calls or modifying changes merely to plan them.
- When session history is supplied, inspect the decision sequence, tool evidence, queued user corrections and audit handoffs. Separate user decisions from assistant proposals, assumptions, repeated metadata and subagent reports. Later user decisions supersede earlier proposals; historical authorizations do not authorize new actions.
- Check information completeness BEFORE constructing the candidate and AGAIN before handoff. Ask about consequential gaps in scope, acceptance, design, interfaces, delegation, access or authority. No minimum question count; do not ask again about settled choices.

Use the harness's interactive question tool when available: self-contained questions, 2–3 meaningful choices, recommended choice first with a reason/tradeoff, and custom-answer support. Do not duplicate an Other option supplied by the UI. If unavailable, ask in chat. Silence is not a required decision. Continue independent investigation while answers are pending.

## 2. Select a delegation path

Honor the user's choice; if unclear, ask interactively:

- **Native subagents (recommended for portability):** only built-in agents in the current harness. Read [the native template](templates/native-subagents.md).
- **Mixed tools:** native agents and selected external headless CLI agents. Read [the mixed template](templates/mixed-cli-agents.md).

Read only the selected template. Verify native mechanisms through exposed tools; external CLIs through installed version/help and configured model IDs, then the project's required documentation sources. A configured ID does not establish access or remaining quota. Do not invent tools or model IDs. Help proves syntax, not successful delegation. Schedule a harmless smoke task after execution authorization and before first implementation dispatch; during planning run it only if separately authorized. Service access/spending still require their applicable authorization. Label dispatch unverified until observed. If implementation was attempted before the smoke gate, record the missed gate and restore it before another attempt; do not retroactively claim success. Do not weaken permissions to make it work.

## 3. Candidate → audit → decisions → review draft

Construct the complete candidate privately. BEFORE first saving or presenting it as a review draft, apply [the consistency audit](references/consistency-audit.md). A permitted private scratch candidate is not a deliverable and must not overwrite an approved plan. In read-only mode retain it in context. Audit revisions before replacing an existing draft.

Produce concrete findings with source locations, affected tasks, impact, recommendation, decision and recheck evidence. An audit heading is not an audit. Prefer an independent read-only reviewer when authorized/available; verify its findings against sources. Re-audit after consequential corrections.

Fix plan-local omissions/editorial defects within scope. Do not silently rewrite approved requirements, architecture, agent rules, permissions or user files. For semantic conflicts, show the conflicting rules, recommend alternatives with consequences and ask the human. Apply authoritative document corrections only if authorized; otherwise provide proposed amendments. An ADR cannot silently override AGENTS.md. Identify blocked tasks; an unapplied resolution is still a prerequisite.

Only after audit and applicable decisions, save/present **DRAFT — awaiting thorough human review**, default `docs/plans/implementation-plan.md` unless the user specified a destination. Deferred questions may remain explicitly blocked in a draft, which is not ready for execution. In read-only Plan mode return the audited draft and destination without claiming it was saved.

## 4. Required plan contents

- Agreed scope/exclusions, outcomes, exact source links, observed baseline and explicit scope changes.
- Small demonstrable phases and ONE authoritative task matrix: ID, outcome, requirement/ADR/design links, prerequisites, mandatory executor/harness/model or supported role, exact editable files, verification/handoff evidence, commit boundary and status/tracker link. Use the existing tracker, not a competing status authority.
- Every in-scope acceptance criterion mapped to implementation AND verification. Include entry-point wiring, packaging, migrations, reports and cross-component integration where applicable. Isolated modules do not complete a user flow.
- Critical path, independent parallel groups, shared-file owners/serialization, recovery/rollback and smaller fallback with unmet criteria explicitly listed. Reduced scope needs human acceptance; never call failed criteria complete.
- Verification appropriate to scope: behavioral Red → Green for features/bugs, characterization before behavior-preserving refactoring, integration after dependencies, real runtime/manual QA, independent review and human acceptance. Distinguish build, tests and startup; add missing test infrastructure. Documentation-only rows need document checks, not artificial runtime tests.
- External contracts/captures/mocks follow project rules: plan safe real capture before deriving mocks, real E2E/manual endpoints where required, and distinguish product budget caps from testing authorization. Do not invent response shapes or fake successful runs.
- Durable just-in-time briefs, review gates, first bounded task after authorization, and separate publication/PR/merge boundaries.

A blocked review draft may explicitly mark an editable-file allowlist or other consequential field unresolved, with a discovery prerequisite. It must never present that row as executable: resolve exact files, ownership, contracts and required decisions before dispatch. Do not invent paths to fill a table.

Derive gates/critical path from the matrix; freeze shared contracts before parallel consumers. Prefer one checkout with disjoint files. Follow local worktree approval/naming rules when needed.

## 5. Binding executor contract: embed verbatim in every plan

The actual plan must contain this contract; linking to the skill alone is insufficient:

> **Executor assignments are binding.** After explicit execution authorization, dispatch every delegated task to the native subagent or headless CLI agent assigned in its matrix row. The orchestrator MUST NOT implement delegated tasks itself, silently replace executor/model/tool, or collapse delegation into a solo run for speed, convenience, context savings, quota or failed launch. Only rows explicitly assigned ORCHESTRATOR may be implemented by the orchestrator. It may investigate blockers, reproduce checks, review diffs and perform explicitly assigned integration; a functional rewrite of worker output is implementation and requires a reassignment decision.
>
> Before implementing each row, record the authorized executor, durable brief and actual dispatch evidence: native agent/task ID, or CLI run/session identity plus log path. Require substantive worker output: files/diff, observed Red/Green evidence where applicable, counts/skips, runtime evidence and contradictions. Never mark a delegated row done without dispatch evidence and orchestrator acceptance. Starting a token/no-op agent while doing its implementation yourself does not satisfy delegation.
>
> If the assigned mechanism/model is unavailable, denied, fails or exhausts quota: stop that row, record the observed failure, and ask the human to choose retry, a named replacement or explicit solo execution. Independent authorized rows may continue. Use an alternative only if the human has already explicitly approved it for this row/condition, and log it. A generic failure paragraph is not fallback authorization. Update the matrix and audit the impact before dispatching a replacement. Never weaken sandbox, approvals or file restrictions to launch a worker.

Compile self-contained briefs immediately before dispatch: task goal, relevant source excerpts/current contracts, predecessor artifacts, concurrent tasks, exact editable files, ordered test/implementation steps, input/output examples, permitted commands/restrictions, acceptance evidence and report format. Workers report contradictions, cannot expand scope or accept their own work. Orchestrator reads diffs and reproduces checks. Discard only changes proven owned by the task; never blanket-clean a dirty shared checkout.

## 6. Finish at the human review gate

Check final links, coverage, decisions, feasibility and consistency. Report draft path (or unsaved destination), selected mode, audit summary/limits, recommended improvements, remaining decisions and first bounded task.

Explicitly ask the user to **read the entire audited draft thoroughly**, including scope, task ownership, dependencies, verification, audit dispositions and blocked decisions. Request corrections and use interactive choices for remaining decisions. Do not combine the request with automatic execution. Stop at draft review even when no questions remain.

When refining the workflow or diagnosing similar failures, read [source-session lessons](references/session-lessons.md). They explain evidence and prevention, not universal product requirements.
