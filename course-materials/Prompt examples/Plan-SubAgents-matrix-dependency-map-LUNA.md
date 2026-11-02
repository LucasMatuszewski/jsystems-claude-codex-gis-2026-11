# Implementation plan from the current PRD and ADRs

Create a reviewable implementation plan for one demonstrable vertical slice of our application. Do not implement it or launch agents yet. Follow the applicable AGENTS.md and use the approved PRD, ADRs and design guidance in this application's repository. Ask for their paths only when they are missing or ambiguous; teaching examples in course-materials are not project requirements.

Inspect the current code, working-tree status, entry points and tests. Report what actually exists, the commands you verified and any baseline failure. Use the existing application scaffold or approved legacy checkout; do not replace it with a fresh application. Resolve consequential gaps with targeted questions, without a minimum question count. Keep unrelated work intact.

Save the draft in docs/plans/<feature>-implementation-plan.md, unless I named another destination. In a read-only Plan mode, return the complete draft and destination first, then save it when writing is permitted. Mark it as draft awaiting my review. Link exact PRD criteria, ADR sections and design guidance instead of copying their contents. Missing architecture belongs in a proposed ADR, not an invented plan assumption.

Use small verified phases and one authoritative dependency matrix:

| Task | Observable outcome | PRD/ADR links | Prerequisites | Owner/model | Editable files | Verification and handoff |
|---|---|---|---|---|---|---|

Give each row a bounded deliverable, acceptance evidence and commit boundary. Plan a failing behavioral test before implementation, integration checks after dependent components, manual runtime verification, an independent review and a pull request for the finished slice. Use the application's actual commands. A green build alone does not prove startup or the user flow. State the critical path, shared-file hotspots, failure/rollback handling and a smaller fallback if time, tools or model access run out. Use the existing tracker for execution status.

The strong orchestrator makes architectural decisions, resolves contradictions, prepares briefs and accepts results. Prefer cheap small workers for bounded implementation and test-writing: Claude Code Haiku; Codex Luna; Copilot the cheapest currently available suitable model allowed by the organization's policy and current plan pricing. Check the actual model picker and official pricing before choosing Copilot's model: access and charges vary, so do not assume an old 0x list still applies. Record the chosen model, provider and budget constraint; escalate when evidence shows the task exceeds the worker's ability. Review and final acceptance stay with a capable model and the human.

Recommend ad hoc subagents by default for a one-off task: an exact brief matters more than a new role file. Use short custom definitions only for a recurring role with reusable tool restrictions or expertise. Existing named roles may be reused after inspecting them, without assuming their model or permissions suit this task. Verify the active harness supports the requested agent mechanism; otherwise execute the same matrix sequentially with one agent. Do not manufacture custom roles merely to match a tutorial.

Parallelize only tasks with independent inputs and disjoint editable files. Tell every worker which other work is concurrent. Serialize shared contracts, lockfiles, migrations and integration. Use one checkout by default, with disjoint files/folders and a dependency plan. Request a worktree only when agents must edit the same files in parallel; follow the repository approval policy and remove it afterwards.

After I authorize execution, compile each task's self-contained brief just before dispatch. Put it in a durable project path such as .agent-briefs/<task>.md, not a disposable temporary file. Include the relevant source excerpts, current contracts, predecessor outputs, exact editable files, ordered steps, test inputs and expected results. Link the authoritative documents for traceability, but do not make a small worker rediscover the whole architecture. The worker reports contradictions and observed results; it cannot change the agreed scope or accept its own work. The orchestrator reads the diff and reproduces the relevant checks before integrating and committing under the repository's policy.

Finish with the saved plan link, unresolved decisions, the first bounded task and the review gate. Planning does not authorize execution, new agents, publication or merge.

## Exercise: turn the session into your own planning skill

After reviewing the plan, identify which planning steps would be useful in another project. With the group, write a small SKILL.md containing a precise trigger, required inputs, the dependency-matrix contract, source-link rules, model/ownership policy and the stop-for-review boundary. Remove this application's domain, client names and decisions. Test the skill on a second small feature: does it find the real sources, ask only missing questions, avoid overlapping files and stop before implementation? Refine it from the observed result.

Optional external example for comparison: [write-implementation-plan, public PR #28](https://github.com/EdukeyTeam/agent-toolbox/pull/28). It is a pending proposal, not a required installation or an approved dependency of this exercise. Inspect its current state and compare its plan/brief separation with your own skill.


Only the coordinator may switch branches, stage changes, write the Git index or create commits in the shared checkout. Workers edit only their assigned files and return a diff; they do not run Git writes. Worktrees do not eliminate same-file merge conflicts.
