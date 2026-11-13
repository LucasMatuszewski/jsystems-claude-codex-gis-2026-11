# Template: native subagents only

Adapt the shape below to scope. Replace field instructions with project facts. Apply the pre-draft audit before delivery and embed the FULL execution contract from SKILL.md. Do not put external agent CLI invocations in this mode.

---

# Implementation plan: [chosen outcome]

> DRAFT — awaiting thorough human review. Execution is not authorized.
> Date/revision: [value]. Checkout/branch/HEAD: [observed values].
> Delegation mode: NATIVE SUBAGENTS ONLY.

## Scope, sources and baseline

Agreed outcomes, exclusions, useful increments and approved scope changes. Exact PRD/requirements, ADR/architecture, design and agent-instruction links. Missing sources and impact. Actual code/contracts, dirty files to preserve, tracker, discovered commands and baseline evidence with exit codes/counts/skips. Separate build, tests, startup and unverified checks.

## Decisions and pre-draft audit

| Finding/decision | Source locations | Impact/blocked task IDs | Recommendation/alternatives | Human decision | Applied correction/recheck or open status |
|---|---|---|---|---|---|

State audit coverage/limits and worthwhile improvements outside scope. Unresolved blockers prevent affected work from executing.

## Execution and delegation contract

Insert the FULL binding contract from SKILL.md here; it must be visible to someone who only reads this plan.

List actual native tools, supported roles/models and concurrency limits with discovery evidence. Do not copy another harness's API syntax. If model selection is unsupported, disclose it and resolve consequential model requirements with the human.

Schedule an authorized harmless native smoke task before first implementation dispatch. Until run, mark successful dispatch unverified. Missing native support blocks delegation; it does not authorize external CLI or solo substitution.

## Phases and authoritative task matrix

Outline demonstrable phases, deriving dependencies from one matrix. Use the existing tracker, or this Status column if agreed when none exists.

| ID/phase | Observable deliverable | Requirement/ADR/design links | Prerequisites | Mandatory native executor/role/model | Editable files | Red → Green or scoped checks; runtime evidence | Commit boundary | Status/tracker |
|---|---|---|---|---|---|---|---|---|

Assign bounded implementation/test work to native workers. Reserve architecture, shared contracts, lockfiles and explicit integration rows for ORCHESTRATOR where justified. Do not assign all implementation to ORCHESTRATOR to avoid delegation. Review must be independent of authorship.

## Coverage and scheduling

| In-scope criterion | Implementation task(s) | Verification task/evidence |
|---|---|---|

Critical path, disjoint-file parallel groups, frozen contracts, shared-file owners, integration gates and concurrency limits. Follow repository worktree rules only when necessary.

## Dispatch and acceptance

1. After explicit execution authorization, compile a durable `.agent-briefs/<ID>.md` or project equivalent with current source excerpts/contracts, predecessor evidence, concurrent edits, exact files, steps/tests and report requirements.
2. Invoke the ACTUAL native tool with assigned role/model and brief. Record native task/agent ID and result location. Do not call a shell agent CLI.
3. Collect substantive worker output; review diff, reproduce checks, manually exercise changed runtime and record acceptance before marking done. A reviewer cannot approve its own implementation.

| Task | Assigned executor | Brief | Native dispatch/task ID and result | Check evidence | Orchestrator acceptance | Approved reassignment, if any |
|---|---|---|---|---|---|---|

## Verification, recovery and gates

Actual commands for behavioral Red/Green, integration after dependencies, capture/mock policy, real manual flow and screenshots/design reference where applicable. Document-only work uses document checks. Keep build/test/startup evidence separate.

On launch failure/quota/bad output, stop that row and request retry or reassignment approval. No automatic solo/CLI fallback. Preserve unrelated work; define task-owned rollback and reduced scope with unmet criteria requiring human acceptance.

List gate prerequisites from the matrix, evidence and reviewers. State commit/push/PR/deployment/merge boundaries as applicable.

## Human review and first task

Name first bounded task AFTER explicit execution authorization, required decisions and acceptance evidence.

Ask: **Please read the entire audited draft thoroughly: scope, task ownership, dependencies, verification, audit corrections and unresolved decisions. What should change?** Use interactive questions for remaining choices. Stop here; do not launch implementation.
