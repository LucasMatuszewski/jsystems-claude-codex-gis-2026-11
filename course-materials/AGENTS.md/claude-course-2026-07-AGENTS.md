# Repository Guidelines

## Project

This is a **course project** for the "Claude Code – od zera do zespołu agentów AI" training by Łukasz Matuszewski — an **open course** (participants from multiple companies), 2026-07-13..15, 3 days, remote. The app is a multimodal AI assistant built live during the course. The domain, tech stack, and architecture are decided by the group through a structured process: research → PRD → ADR → implementation with agents.

This is only the **base starting repository** for the course; concrete decisions are made live with the group.

**Primary demo stack:** TypeScript/Node.js (Next.js, Vercel AI SDK).
**Java is a first-class participant stack** (Spring Boot, Spring AI, LangChain4j or OpenAI Java SDK — see `course-materials/agent-configs/`); each participant picks their stack during the ADR phase.
Participants may work in any language (Java, Python, C#, Go, Rust, etc.).

All user-facing text in **Polish**.

## Course Delivery Environment (Windows Server 2022 VMs)

Participants work on prepared VMs with preinstalled tools:
- **Agents:** Claude Desktop + Claude Code CLI, Codex (desktop + CLI), OpenCode (desktop + CLI), Antigravity
- **Editors:** `micro` (default `$EDITOR` in git bash, PowerShell and git), Fresh (terminal), Lite XL (default GUI editor for code files). IntelliJ is installed (Java file association) but **slow on VMs — avoid for live work**
- **Runtimes:** Node.js, Bun, Python, .NET runtime (no SDK — not used in this course)
- **LLM access for built apps:** `OPENROUTER_API_KEY` preset in Windows env vars (multimodal models available via OpenRouter)
- Participants clone this repository at course start; the app is built on a **separate branch** per participant/group — `main` stays course-materials-only.

**Key docs** (created during the course — load only when in doubt):
- `docs/PRD.md` — product requirements and acceptance criteria
- `docs/ADR/` — Architecture Decision Records
- `docs/design-guidelines.md` — design system and tokens

---

## Repository Layout

```
app/                 Application built during the course (start: empty scaffold)
assets/              Design tokens, logo, favicon
docs/                PRD, ADR, design system
course-materials/    Notes, scripts, examples, research
course-materials/slides/   Slide decks day-1.html..day-3.html (single-file HTML)
                           + publish-slides.ps1 (sync to the DevPowers site repo;
                           run after EVERY deck change, `-Push` = deploy to production)
```

---

## Agent Workflow

### Before Starting Any Task
1. Read the relevant PRD and ADR files for the affected area.
2. Define the expected behavior from the specification before writing or changing any code.

### TDD Rules
For every feature and bug fix:
1. Start from the specification, not the existing implementation.
2. Write or extend tests **before** production code.
3. Run the new tests and confirm they fail for the expected reason.
4. Implement the minimum code needed to make them pass.
5. Run the full verification suite for the changed scope.
6. Refactor only while tests stay green.

If the area has no suitable test infrastructure yet, add it as part of the task — do not silently skip tests.

Before creating or refreshing an endpoint/database mock for unit or integration tests, make a fresh real request/query in an authorized local/test environment with synthetic data. Save the complete non-secret response verbatim (HTTP status, headers and body, or database rows and type/schema information), then derive the mock from that capture rather than potentially stale documentation. Record date, target, request/query and service version without credentials. If safe capture is unavailable, report the prerequisite; do not invent the response shape.

### Manual QA (required for runtime changes)

Start the real app with the verified command and local synthetic configuration. Exercise the complete changed flow, including success and relevant errors, and check state changes and persistence. Interact with the actual UI or CLI/API; automated tests alone do not establish that the app works. Capture screenshots of changed GUI screens and states, or representative CLI/API commands and results, and inspect runtime logs. Record build, test execution and startup as separate checks, plus manual steps and evidence. Fix failures before committing; missing display/service prerequisites leave runtime QA incomplete. Use no real credentials, participant data or external production services.

### Verification (required before every commit)

Run the commands appropriate for the chosen stack. Typically for a TypeScript project:
```bash
npm test             # unit/integration tests pass
npm run lint         # ESLint — no errors
npm run build        # build succeeds
```

Verify only the scope relevant to your change. If the change affects runtime behavior, confirm the app starts correctly.

**Test Strategy:**
| Type | Mocks | Who |
|---|---|---|
| Unit | All deps | be/fe-dev |
| Integration | Only external LLM API | be-dev |
| E2E | NOTHING (real stack) | qa-engineer |

**Verification:** Always start the app before committing. Tests passing ≠ app working.

**Env Vars:** See `.env.example` (OPENROUTER_API_KEY or OPENAI_API_KEY required)

### Commit Rules
- Commit only after verification passes and the changed scope is in a working state.
- Keep commits focused: one logical change per commit.
- Format: `Area: short summary` (e.g. `Backend:`, `Frontend:`, `Docs:`)
- Do **not** push to remote unless the user explicitly asks.

### Completion Criteria
A task is complete only when:
- Implementation matches the relevant PRD, ADR, and design guidance
- Tests were written first and pass honestly
- Verification for the changed scope passed with no errors or warnings; runtime changes also passed startup and Manual QA with recorded evidence
- The commit message is focused and the repository is in a consistent, reviewable state

---

## Context7 MCP Library IDs

Common libraries (resolve via `resolve-library-id` if the ID changes):

| Library | Context7 ID |
|---|---|
| Vercel AI SDK | `/vercel/ai` |
| Next.js | `/vercel/next.js` |
| React | `/reactjs/react.dev` |
| Tailwind CSS | `/tailwindlabs/tailwindcss.com` |
| Shadcn/ui | `/shadcn-ui/ui` |
| Mastra | `/mastra-ai/mastra` |
