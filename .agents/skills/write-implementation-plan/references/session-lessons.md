# Lessons from the source session

Source: Claude session `5beb0e98-757a-46ec-b1d8-cbaa6f726290`, Map QA ADR and Plan; substantive work on 2026-11-12. Its 1,264 records included conversation, tool evidence, queued corrections and a delegated audit. Access to that machine/transcript is NOT required to use this skill.

## How the plan was created

1. Profiled local data, resolved environment/encoding issues and compared table counts through a real read-only external query. Equal counts were correctly distinguished from identical contents.
2. Updated ADRs from data findings. New behavioral rules appeared during this update, exposing the need to distinguish facts from proposed product decisions.
3. Received a detailed planning prompt for one demonstrable slice, with no implementation yet.
4. Inspected actual code/scaffold, Git changes, requirements/ADRs, tracker, baseline commands, tool versions/help/models; checked documentation for headless settings. Help established syntax, not a successful dispatch.
5. Asked four consequential interactive questions about scope, flag behavior, missing design guidance and tracker. The human expanded scope to the whole MVP in phases and chose the other defaults explicitly.
6. Saved a roughly 34,000-character draft with six phases, about 30 tasks, dependency/ownership matrix, tests, integration, gates, delegation and fallback. Committed it on request.
7. Only AFTER draft delivery, a further human request triggered an independent cross-document audit. The orchestrator verified major findings. The audit identified F1–F19 plus coverage gaps.
8. After authorization, corrected PRD, ADRs and plan in focused commits. Incorporated queued instructions requiring real model endpoints for manual/E2E tests and a later API-gateway decision.

The user later reported that the implementing orchestrator ignored assigned workers and did everything itself. This implementation behavior is USER-REPORTED, not demonstrated by the planning transcript. It motivates mandatory assignments, dispatch evidence and human-approved substitutions.

## Mistakes and prevention

| Historical finding | Reusable prevention |
|---|---|
| Audit after draft delivery/commit | Audit a complete private candidate before handing off the draft |
| F1: per-pair vs per-pair/attribute status counts | Compare domain invariants, counters, requirements and tests |
| F2: acceptance rule stricter than approved examples | Trace mixed conditional/unconditional cases through rules and expected outputs |
| F3: thumbnails resolved from the wrong directory | Define image copying/path semantics; validate a portable real report |
| F4: changed threshold invalidated offline-cache promise | Trace parameter changes through cache keys and rerun behavior |
| F5: quoted count covered a different population | Recompute against explicit rules, population and provenance |
| F6: model fields drifted across ADRs | Freeze authoritative shared contracts before parallel workers |
| F7: overlapping missing statuses lacked precedence | Specify ordered decision rules and boundary cases |
| F8: error vs abstention and numeric vs categorical thresholds differed | Align requirements, architecture, settings and outcome tests |
| F9: missing subcommand wiring and complete capture path | Trace user flow through entry point, integration, transport and output |
| F10: ADR/mock policy conflicted with agent instructions | Surface conflict; follow instruction authority; obtain an explicit decision |
| F11: promised hashes exceeded manifest contents | Define the hashed set and provenance per checksum |
| F12: flags/env/config keys diverged | Maintain one canonical configuration contract |
| F13: worst-case reservations exceeded budget | Check worst-case arithmetic; separate product caps and testing authorization |
| F14: capture schema differed in three places | Link one canonical schema and audit consumers |
| F15: shell allow-all bypassed edit restrictions | Preserve real permission boundaries; do not claim text allowlists enforce a sandbox |
| F16: stale HEAD, wrong gate, excess sequencing, wrong criterion, false Red | Audit graph, references and observable behavioral failure evidence |
| F17: nested keys described as columns | Verify actual data shape before assigning queries |
| F18: missing attribution and valid answer values | Check actual source data and output obligations |
| F19: language rule changed but existing documents differed | Agree migration; separate translation from semantic corrections |
| Extra: missing photo/map comparison, report flags/counters, final coverage | Map each criterion to implementation AND verification including integration |
| Solo fallback weakened assigned ownership | Embed binding assignments; require substantive dispatch/handoff evidence and human-approved changes |
| Blanket rollback could discard shared dirty files | Discard only changes proven to belong to the failed task |

One profile count remained historical after a narrower rule was recomputed (1,475 vs 1,453 under the corrected rule). This teaches population definitions and provenance, not an expected count for another project.

## Repeat these strengths

- Verify checkout/baseline; do not invent a replacement app or assume commands.
- Use data facts to expose questions, and ask about behavior rather than silently deciding it.
- Ask targeted interactive questions with recommendations; preserve the human's scope correction.
- Plan demonstrable vertical increments even for a whole product.
- Keep one dependency matrix/status authority, exact editable files and serialized shared contracts.
- Compile durable self-contained briefs just before dispatch using current predecessor outputs.
- Separate implementation, independent review, reproduced checks and human acceptance.
- Verify serious audit findings against actual sources before changing documents.
- Keep planning, execution, service use, publication and merge authorizations distinct.

Do not universalize this case's model IDs, prices, endpoint paths, budgets, account details, stack or permission configuration. Discover current project equivalents when relevant.
