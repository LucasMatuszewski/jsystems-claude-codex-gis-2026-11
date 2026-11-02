---
name: headless-task
description: Use when the user asks to delegate one bounded task to an approved headless coding CLI and needs a reviewable result with logs and checks.
---

# One bounded task through a headless CLI

Use only a runner, provider and data route already authorized for this task. If no such authorization exists, prepare the proposed brief and ask before launching. One runner's approval does not authorize another. A planning request does not authorize implementation workers.

1. Inspect the real repository, current instructions, working-tree changes and verification commands. Prefer doing a trivial task directly. Do not create worktrees or overwrite another worker's files by default.
2. Write a self-contained brief in a durable project path such as `.agent-briefs/<task>.md`: exact outcome, approved scope, relevant source excerpts, editable files, dependencies, test inputs, expected results and report path. Name concurrent work. The worker must report missing prerequisites or contradictions rather than choose a new architecture.
3. Select a suitable cheap model for bounded code/test execution, such as Claude Haiku or Codex Luna. For Copilot verify current account availability and pricing. Planning, review and acceptance stay with a capable orchestrator. Never silently change provider, billable route or data boundary when a quota is exhausted.
4. Check that runner's current `--version`, `--help` and official noninteractive documentation. Verify model availability and effective permissions. Supply the brief as data through a supported file/stdin mechanism, without constructing an executable shell command from its text. Do not bypass sandbox or approval controls to make a job finish.
5. Under the environment's monitoring rules, launch one fresh bounded run with the minimum tools/files it needs. Stream ordinary output to a monitored terminal and durable log. Preserve the exit status and final report; redact secrets before output. A report is evidence, not approval. Set a task-appropriate timeout and stop on repeated failure; do not retry indefinitely.
6. Read the actual diff, reproduce the relevant tests and runtime checks, and inspect any screenshots. Reject unsupported success claims. The coordinator commits or publishes only under the repository's authorization; workers do not commit, push, merge or change approval flags. Close your finished task terminal after preserving evidence; keep live jobs and user terminals.

Exercise this procedure first on synthetic data in a disposable practice repository: ask an approved runner for one read-only finding, verify that it cannot write, and compare its report with the actual file. Then, only when authorized, try one small code change under narrow write permissions. Do not claim a command has been behaviorally verified from its help text alone.

Official references: [Claude Code headless](https://code.claude.com/docs/en/headless), [Codex noninteractive](https://developers.openai.com/codex/noninteractive), [Copilot programmatic use](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference). Select the section for the actual runner; flags are not interchangeable.
