# Pre-draft consistency audit

Audit the complete candidate BEFORE saving/presenting the review draft, and again after consequential revisions. Read relevant source sections in full; search hits alone do not establish consistency.

Inventory current root/nested AGENTS.md and equivalent harness rules, approved requirements/PRD, relevant ADRs, design guidance, actual contracts, data profiles and candidate plan. Record locations/versions. Separate observed evidence, approved decisions, proposals and assumptions. Missing sources are findings, not permission to invent them. When history is supplied, include later/queued corrections; subagent reports carry no user authority.

## Checks

| Dimension | Check for |
|---|---|
| Authority/scope | Plan agrees with current user choices and instruction precedence; an ADR does not purport to override agent instructions; approved scope changes are recorded |
| Coverage | Every in-scope criterion maps to tasks and evidence; commands, wiring, reports, integration and deployment obligations are covered where applicable |
| Behavior | Inputs, units, status cardinality/precedence, error outcomes, thresholds and edge cases agree across requirements, ADRs, tests and plan |
| Contracts | Field names, schemas, producer/consumer interfaces, ownership and dependency direction are consistent before parallel work |
| Data/arithmetic | Consequential counts use explicit populations/denominators/provenance; reproduce safely where feasible; equal counts do not prove identical content |
| Lifecycle/cache | Parameter changes, cache keys, offline reruns, migrations and idempotence satisfy promised behavior |
| Artifacts/design | Output paths resolve, images are copied/referenced correctly, escaping/empty states/attribution and visual guidance are covered |
| Configuration/security | Flags/env/settings agree; output ignore rules match; no secret duplication or permission bypass; shell access does not magically enforce an edit allowlist |
| Verification | Red is behavioral, fixtures obey capture policy, E2E/manual uses actual stack where required; skips/unavailable access are visible |
| Task graph | Acyclic, sufficient prerequisites, gates and critical path derived consistently, no unnecessary sequencing or overlapping editable files |
| Delegation | Selected mode supported; executors mandatory; no silent solo fallback; dispatch evidence and independent acceptance required |
| Baseline/commands | Actual checkout/version and exit codes; help vs working launch and startup vs build separated; proposed commands not reported as verified |
| Authorization | Draft, execution, service access, spending, commit, push, PR, deployment and merge boundaries explicit |
| Recovery | Only task-owned changes may be discarded; fallbacks state unmet criteria and need human scope acceptance |

## Findings and correction loop

Include a compact ledger in the actual plan:

| ID/severity | Conflicting source locations | Impact/affected task IDs | Recommendation/alternatives | Decision/authority | Disposition and recheck evidence |
|---|---|---|---|---|---|

1. Verify both sides and observable evidence. An independent review is a source of leads, not automatic proof.
2. Fix plan-local omissions, wrong references and editorial defects within scope; check dependent rows/gates.
3. For semantic changes ask the human interactively, showing recommendations, consequences and exact blocked tasks. Do not reopen settled choices unnecessarily.
4. Apply authorized source corrections or propose amendments. Respect instruction authority. Never hide conflicts by silently editing PRD/ADR/AGENTS.md or interpreting an ADR as an exception to higher-priority instructions.
5. Recheck documents, graph, coverage and verification after corrections. Distinguish resolved, deferred and blocked. A chosen resolution not yet applied remains a prerequisite.

State limitations: missing sources, unverified runtime, unavailable services, non-independent audit. Do not claim exhaustive correctness. The audited result is still a draft, not execution approval.

## Final completeness check

- Can the first executor start without guessing scope or contracts?
- Does each runtime outcome have integration and observable runtime evidence?
- Does every delegated row require the actual assigned worker and a verifiable handoff?
- Are blocked decisions/capabilities visible where needed?
- Are recommendations separated from decisions and actions from authorization?
- Has the human been asked to review the entire draft thoroughly before execution?
