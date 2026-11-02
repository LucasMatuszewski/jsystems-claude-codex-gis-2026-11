---
Hint: add to your CLAUDE.md or create as a skill to use by Fable or Opus (orchestrators / managers) than should delegate to expert models by their strengths
---

## Model Orchestration - picking the right model for workflows and subagents

Rankings, higher = better. Last reviewed 2026-07-14 - models change fast; re-verify scores when a new major version lands. All CLI plans are flat-rate/near-unlimited, so the only real cost is Fable's Claude tokens and time. Intelligence = how hard a problem the model can handle unsupervised. Taste = UI/UX, design quality, marketing copy.

| model | Token cost | intelligence | taste | vision | primary role |
|---|---|---|---|---|---|
| fable-5 (you, Claude Code) | high | 10 | 9 | yes | Orchestrator, architecture, plans, final review and judgment |
| gpt-5.6 Sol (Codex CLI `codex`) | low | 9 | 7 | yes (attach image paths) | WORKHORSE: implementation, bulk/mechanical work, refactors, data analysis, backend, Rust. Use gpt-5.6 Sol, NOT the older gpt-5.5 (much worse) |
| grok-4.5 (xAI Grok CLI `grok`) | zero | 8 | 8 | model yes, but CLI has no image flag (reads workspace files); use agy for vision | Fast workhorse #2: well-specified mechanical batches, bulk edits, overflow when Codex is tight, and the taste fallback if GLM is busy. 500K ctx, fast, token-efficient |
| gemini (Antigravity CLI `agy`) | zero | 7 | 7 | yes, best visual describer | RESEARCH agent (best Google data access), image/screenshot description, independent second opinions, long-context reads. Authenticated on this WSL2 box (verified 2026-07-12). Headless: `agy --mode accept-edits -p "..."`. If it ever reports "authentication timed out", the login lapsed - run `agy` once interactively to re-auth |
| glm-5.2 (OpenCode CLI `opencode`) | zero | 7 | 9 (best copy/humor, very good GUI/design) | NO - text only, never send images/screenshots | PRIMARY taste model: UI/UX, GUI/design, CSS, React components, and copywriting. Best humor/jokes of any model, strongest in English, solid in Polish too. Configured in opencode via Lucas's CodingPlan and working on this WSL2 box (verified 2026-07-12). Route all taste-sensitive work here first (grok-4.5 is the fallback) |

How to apply:
- You (Fable) are the Orchestrator. Do NOT waste your context window on bulk code, whole-codebase reads, computer use, or mechanical work. Delegate, then read the report.
- QUOTA ECONOMY (hard rule): NEVER use Fable (yourself) or Codex for image description or routine web research - both are reserved for hard work (architecture, implementation, review). Images/screenshots -> `agy -p`. Web research -> `agy -p` (best Google data access). Never send images to glm-5.2 (text-only).
- Default delegation target for implementation/mechanical work is gpt-5.6 Sol via `codex exec`.
- Taste-sensitive work (UI, GUI/design, CSS, PL/EN copy, course/landing content, marketing) -> glm-5.2 via `opencode` (primary). grok-4.5 is the fallback when GLM is busy.
- Use `agy` for vision and for an independent third perspective on important decisions.
- These are defaults, not limits. Standing permission to escalate: if a cheaper model's output doesn't meet the bar, rerun with a smarter model (or do it yourself) without asking. Judge the output, not the price tag.
- Use free models to explore, gather info, and try things BEFORE spending Fable tokens on decisions.
- Reviews: Fable does final review; optionally add an independent `codex exec` / `codex review` pass. Treat CLI output as evidence, not authority - verify claims before relaying them.
- Reasoning effort: keep Fable on `high`. Never xhigh/max (looping, worse output, token furnace).

Headless invocation patterns (WSL2 bash; install paths and PATH/nvm caveats are in ~/AGENTS.md):
- Codex: `codex exec --sandbox workspace-write "..."` (use `--full-auto` only when you also want network; workspace-write is enough for file edits). Reads a brief file well: point it at `.agent-briefs/<task>.md`.
- Grok: `grok --always-approve -p "..."` (auto-approves tools, prints result, runs in the cwd).
- Antigravity: `agy --mode accept-edits -p "..."` (needs prior interactive login).
- OpenCode: `opencode run "..."` (verified headless on this box 2026-07-14: default agent `build`, model glm-5.2). WARNING: in opencode `-p` is basic-auth password, NOT prompt. Useful flags: `-m provider/model`, `--format json`, `-c` / `-s <id>` to continue a session, `-f <file>` to attach files (text only, GLM has no vision). `--auto` auto-approves all permissions - treat it like `--full-auto` (blocked unless explicitly authorized).
- Redirect stdin from /dev/null for all of them in background jobs to avoid stdin-hang.
- The auto-mode classifier blocks `--dangerously-skip-permissions` / `--full-auto` unless Lucas has explicitly authorized running that agent with permissions off. Prefer the scoped sandbox/approve flags above; they clear auto mode.

Delegation workflow (matches the .agent-briefs convention):
- Write a self-contained brief to `.agent-briefs/<task>.md` with all context, exact changes, and a "Definition of done"; tell the agent to read it and not commit/push.
- Give each parallel agent a DIFFERENT file/scope so edits don't collide (no shared-file races). For same-file work, serialize or use git worktrees.
- After any delegated implementation, YOU verify: inspect `git status` and `git diff`, run the cheapest reliable check (typecheck/lint/focused tests, or drive the UI) before accepting. You commit; the delegates do not.

Using CLI models inside Workflows/subagents (the `model` param only takes Claude models, so wrap):
- Spawn a thin Claude wrapper agent (`model: 'sonnet', effort: 'low'`) whose prompt tells it to write a self-contained CLI prompt, run the CLI via Bash, and return the report (use `schema` for structured output).
- Label wrappers with the real worker prefix, e.g. `{label: 'gpt-5.6:migrate'}` / `{label: 'grok-4.5:slides'}` - the UI shows the wrapper's Claude model, so the label is the only signal of the real worker.
- CLI runs can exceed Bash's 10-minute timeout: pass an explicit timeout or run in background and poll the report file.
- Workflow token budgets only count Claude tokens; CLI work is free and invisible to `budget.spent()`.


Only the coordinator may switch branches, stage changes, write the Git index or create commits in the shared checkout. Workers edit only their assigned files and return a diff; they do not run Git writes. Worktrees do not eliminate same-file merge conflicts.
