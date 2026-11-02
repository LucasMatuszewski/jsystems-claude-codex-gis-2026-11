# Agent Harness Comparison: Claude Code & Codex — Full Technical Knowledge File

*Compiled March 2026. Covers: Codex CLI, Codex Desktop App (Windows), Claude Code CLI, Claude Code Desktop App (Cowork + Code tab). Sources: official docs, Anthropic & OpenAI engineering blogs, GitHub issues, community research.*

***
## Part 1 — The "Harness" Concept
The single most important insight from both OpenAI's own engineering post and independent benchmarks: **the execution environment (harness) determines performance more than the underlying model.** [openai](https://openai.com/index/harness-engineering/)

The same model placed in different harnesses scored 78% vs 42% on the same benchmark — a 36-point gap from environment alone.  Everything else in this document flows from that fact. [openai](https://openai.com/index/harness-engineering/)

A harness has three layers:
1. **Sandbox** — what the agent can and cannot touch (filesystem, network, syscalls, processes)
2. **Tool provision model** — how capabilities are made available to the agent (real shell vs typed RPC tools)
3. **State/memory model** — how context persists across steps and sessions

Claude and Codex made fundamentally different choices on all three layers.

***
## Part 2 — Claude Code: Architecture, Sandbox, Tools
### 2.1 The bash harness philosophy
Claude Code's design principle is **"bash is all you need."**  The agent operates directly inside a real shell — it can t can pipe `grep | git | awk | ssh`, improvise novel command combinations, read environment variables, follow symlinks, inspect `~/.ssh/config`.  [sambaiz](https://www.sambaiz.net/en/article/547/)

This is not a design convenience; it is a **consequence of the sandbox model**. When bubblewrap creates a namespace container, it preserves a full shell environment — the agent IS in the system, not talking to it via an intermediary protocol. [lwn](https://lwn.net/Articles/686113/)
### 2.2 Sandbox by operating system
**macOS (Claude Code CLI):**
- When sandbox runtime enabled: **Seatbelt** (Apple's app sandbox, `sandbox-exec`) enforces filesystem + network restrictions. [anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing)
- Write scope: current working directory + explicitly allowed paths
- Network: outbound via an allowlist proxy only (e.g. `github.com`, `npmjs.com` permitted, rest blocked)
- Default (no sandbox runtime): runs as your user, no OS-level jail, only per-command approval prompts

**Linux (Claude Code CLI):**
- When sandbox runtime enabled: **bubblewrap** (`bwrap`) creates new Linux namespaces: `CLONE_NEWNET` (network), `CLONE_NEWPID` (process IDs), `CLONE_NEWNS` (mount), optionally `CLONE_NEWUSER`. [code.claude](https://code.claude.com/docs/en/sandboxing)
- The agent sees only what the launcher mounted: project dir + tools. `/home`, `/etc`, other paths are simply absent from the container's filesystem view.
- Network namespace isolates the agent from all network devices except loopback; outbound traffic only via the proxy.
- Seccomp filters can be added on top to block dangerous syscalls. [sambaiz](https://www.sambaiz.net/en/article/547/)
- Default (no sandbox runtime): runs directly as your user with no OS jail — only approval prompts.

**Windows (Claude Code CLI):**
- **No OS-level sandbox for native Git Bash mode.** Only per-command approval prompts. [code.claude](https://code.claude.com/docs/en/setup)
- **WSL2**: full bubblewrap support identical to Linux. WSL2 explicitly listed as supported; WSL1 is not. [claudefa](https://claudefa.st/blog/guide/sandboxing-guide)
- Recommended secure setup on Windows: run Claude Code inside WSL2 with sandbox runtime enabled.
### 2.3 How the sandbox runtime is enabled (CLI)
Opt-in via `~/.srt-settings.json` or the `@anthropic-ai/sandbox-runtime` (`srt`) wrapper package.  Configuration controls: [anthropic](https://www.anthropic.com/engineering/claude-code-sandboxing)
- Allowed write paths
- Denied read paths (e.g. `~/.aws`, `~/.ssh` can be denied explicitly)
- Outbound network allowlist (domain-level)
- Proxy address for network traffic
### 2.4 Tool provision: MCP + shell
Claude Code exposes capabilities to the agent in two ways: [code.claude](https://code.claude.com/docs/en/mcp)

1. **Real shell** — the agent can run any command available on `$PATH` inside the bubblewrap container. No tool registration needed.
2. **MCP servers** — via `claude mcp add --transport stdio/http <name> mmand/url>`. Both stdio (local process) and HTTP streaming (remote) transports are supported. Remote MCP servers configured at `claude.ai/settings/connectors` auto-sync to CLI when logged into the same account.

**Just-in-time skill loading**: best practice for token efficiency is to store full skill definitions as files and expose only short descriptions in context until needed. Skills are local shell scripts, markdown files, or MCP tool definitions. [openai](https://openai.com/index/harness-engineering/)

**Multi-agent orchestration**: Claude Code can spawn sub-agents (e.g. fast Haiku agents for broad codebase scanning, reporting back to Opus for strategy). Coordination happens in-process or via shared local artifacts (progress JSON, feature lists). Sub-agents share context via structured files and git history rather than message-passing. [openai](https://openai.com/index/harness-engineering/)
### 2.5 State and memory model
- **Within-session**: full shell state, environment variables, files written in the sandbox
- **Cross-session**: `CLAUDE.md` project file as persistent context (auto-loaded on session start); local JSON/markdown artifacts written by previous sessions; standard git history [openai](https://openai.com/index/harness-engineering/)
- **Connectors** (Desktop + CLI, when logged in): Gmail, Google Drive, GitHub, Google Calendar, HubSpot, Notion, Slack, Linear, Jira, and 250+ via Composio MCP aggregator [code.claude](https://code.claude.com/docs/en/mcp)

***
## Part 3 — Claude Desktop App: Cowork + Code Tab (Windows & macOS)
### 3.1 Always-on VM: the fundamental difference from CLI
Claude Desktop (macOS and Windows) **always boots a Linux VM** for the Code and Cowork tabs. This is not optional and is not the same as the CLI's optional bubblewrap sandbox. [claudecowork](https://claudecowork.io/guide/security-setup)

- **macOS**: uses **Apple Virtualization Framework** (`VZVirtualMachine`) to boot a custom Linux rootfs. Apple Silicon optimized (unified memory, ARM virtualization). [micheallanham.substack](https://micheallanham.substack.com/p/claude-cowork-architecture-synthesis)
- **Windows**: uses **Hyper-V** (the Host Compute Service API, `vmcompute` service) to boot a Linux guest VM from a VHDX bundle (`rootfs.vhdx`, ~1.8–2 GB, stored under `cla-code-vm` in the Codex home dir). [github](https://github.com/anthropics/claude-code/issues/29045)
  - Requires **Hyper-V-capable Windows edition**: Pro, Enterprise, or Education. Home edition is not supported — shows "Virtualization is not enabled" error even with VMP/WSL2 enabled. [github](https://github.com/anthropics/claude-code/issues/29887)
  - Creates a dedicated Hyper-V NAT network (`cowork-vm-nat`) managed by HNS. [elliotsegler](https://www.elliotsegler.com/fixing-claude-coworks-network-conflict-on-windows.html)
  - Does **not** require WSL2; uses Hyper-V directly.
### 3.2 Code tab vs Cowork tab: same VM, different UX
Both tabs share the **same Linux VM and the same Claude Code agent engine** running inside that VM. [github](https://github.com/anthropics/claude-code/issues/29045)

- **Code tab**: the Claude Code agent UI, project folder mounted into the VM, full bash harness (same as CLI but running inside the VM's Linux instead of your host OS)
- **Cowork tab**: Cowork UX (connectors, skills, document outputs, scheduled tasks) layered on top of the same Code engine in the same VM [claudecn](https://claudecn.com/en/blog/claude-cowork-architecture/)

The Cowork tab adds these GUI-only features not available in Code tab or CLI: [support.claude](https://support.claude.com/en/articles/13345190-get-started-with-cowork)
- Scheduled/recurring tasks (cron-style, GUI-managed)
- Auto-generated Office-format outputs (Excel with formulas, PowerPoint, Word)
- Visual connector management (drag-and-drop Google Drive/Gmail/GitHub setup)
- "Plugins" for document-format skills (on top of base agent)
### 3.3 Isolation properties of the Desktop VM
- **Strongest isolation of any option**: full VM means macOS/Windows system files are completely invisible inside the guest. A compromised agent cannot touch host OS. [claudecowork](https://claudecowork.io/guide/security-setup)
- **Clean state per session**: each Cowork session starts with a fresh VM state; malware cannot persist across sessions. [claudecowork](https://claudecowork.io/guide/security-setup)
- **File access**: only folders you explicitly grant are mounted into the VM (VirtioFS or Hyper-V file-sharing). [reddit](https://www.reddit.com/r/ClaudeAI/comments/1r2odmy/how_to_fix_claude_cowork_on_windows_every_error/)
- **Network**: agent can browse the web through the VM's network; macOS system files and host network sockets are unreachable. [claudecowork](https://claudecowork.io/guide/security-setup)
- **Credentials**: handled through secure proxy with scoped credentials; SSH keys and cloud credentials are not automatically available inside the VM (unlike CLI). [infoq](https://www.infoq.com/news/2025/11/anthropic-claude-code-sandbox/)
### 3.4 Desktop vs CLI session sharing
Claude Desktop and Claude Code CLI do **not** share sessions or config. They use separate execution environments (VM vs host shell). Connectors configured in `claude.ai/settings/connectors` sync to both, but the agent state, working directories, and session history are separate. [code.claude](https://code.claude.com/docs/en/mcp)

***
## Part 4 — Codex CLI: Architecture, Sandbox, Tools
### 4.1 The RPC harness philosophy
Codex's design principle is **structured, typed tool registration via bidirectional JSON RPC**. The agent does not have a real interactive bash shell by default. Every capability the agent uses must be explicitly registered as a tool in the harness. [openai](https://openai.com/index/harness-engineering/)

This is a **consequence of the sandbox model**: Landlock LSM and AppContainer do not create a new shell environment — they restrict what the existing process can do. The agent is sandboxed from the outside, not given a new contained world to work in. The RPC layer is how Codex defines what that sandboxed process is allowed to *do*. [developers.openai](https://developers.openai.com/codex/cli/reference/)
### 4.2 Sandbox by operating system
**Linux (Codex CLI — default: sandboxed):**
- Uses **Landlock LSM** (Linux Security Module, kernel 5.13+) for filesystem access control. [developers.openai](https://developers.openai.com/codex/cli/reference/)
- Landlock policy is set by Codex itself on process startup — **unprivileged, self-applied** kernel enforcement. [lkml.iu](https://lkml.iu.edu/hypermail/linux/kernel/1609.1/04429.html)
- Default `workspace-write` mode: write access only to the workspace dir and `/tmp`; all other write operations return `EACCES`. Reads of paths outside workspace are generally permitted (no namespace, process still sees the real filesystem tree). [vincentschmalbach](https://www.vincentschmalbach.com/how-codex-cli-flags-actually-work-full-auto-sandbox-and-bypass/)
- **seccomp filters** added on top to block dangerous syscalls (`mount`, `ptrace`, raw socket creation, etc.). [kubernetes](https://kubernetes.io/docs/tutorials/security/seccomp/)
- Network: blocked via proxy env var overrides and stub executables for `curl`/`wget`. No separate network namespace — blocking is policy-based, not namespace-based. [developers.openai](https://developers.openai.com/codex/sandbox)
- **Sandbox is ON by default** — unlike Claude Code CLI which is off by default. [developers.openai](https://developers.openai.com/codex/concepts/sandboxing/)

**macOS (Codex CLI):**
- Uses Seatbelt-style sandbox (same underlying Apple framework as Claude Code on macOS). [developers.openai](https://developers.openai.com/codex/concepts/sandboxing/)
- Same semantic modes: `read-only`, `workspace-write`, `danger-full-access`. [developers.openai](https://developers.openai.com/codex/concepts/sandboxing/)

**Windows (Codex CLI — native, no WSL required):**
- Uses **restricted access token** with **AppContainer-style capability SIDs**. [developers.openai](https://developers.openai.com/codex/windows/)
- Windows Filtering Platform (**WFP**) rules keyed to the AppContainer SID block outbound network traffic. [projectzero](https://projectzero.google/2021/08/understanding-network-access-windows-app.html)
- Filesystem: write access granted only to workspace via **ACL + capability SIDs**; other paths blocked by kernel ACL checks. [news.juno-labs](https://news.juno-labs.com/item/1415)
- Stub executables replace network tools; proxy env vars overridden. [developers.openai](https://developers.openai.com/codex/sandbox)
- **Does not require WSL** — this is the key difference from Claude Code CLI on Windows. [apidog](https://apidog.com/blog/codex-on-windows-wsl/)
- WSL is optional: if you run Codex inside WSL2, the Linux Landlock sandbox applies instead.

**Security note**: A CheckPoint Research vulnerability (Nov 2025) found that `.codex/config.toml` in a project repo can redefine `CODEX_HOME` and inject malicious MCP server commands executed at startup without prompts.  Mitigation: never run `codex` in untrusted repos without reviewing `.codex/` config first. [research.checkpoint](https://research.checkpoint.com/2025/openai-codex-cli-command-injection-vulnerability/)
### 4.3 Sandbox modes (all platforms)
| Mode | Filesystem | Network | Use case |
|---|---|---|---|
| `read-only` | No writes anywhere | Blocked | Audit/review tasks |
| `workspace-write` (default) | Write: workspace + `/tmp` only | Blocked | Normal implementation tasks |
| `danger-full-access` | Unrestricted | Unrestricted | Must be inside your own VM/container |

Controlled via `sandbox_mode` in `~/.codex/config.toml` or `--sandbox` CLI flag. [vincentschmalbach](https://www.vincentschmalbach.com/how-codex-cli-flags-actually-work-full-auto-sandbox-and-bypass/)
### 4.4 Tool provision: JSON RPC + registered skills
Every tool the Codex agent can use must be **explicitly registered in the harness**. OpenAI's engineering team describes building this out over months: [openai](https://openai.com/index/harness-engineering/)

- **Chrome DevTools Protocol (CDP)** wired directly into the runtime → agent gets `captureDOM()`, `takeScreenshot()`, `navigate()`, `validateUIFix()` as named RPC tools
- **PromQL / LogQL endpoints** per worktree → agent can query `service_startup_time_ms` against ephemeral Victoria/Loki stack
- **Git operations** (branch, commit, merge, PR) as typed tools
- **Custom linters** with agent-facing error messages: `error: "expected type annotation, add it now"` — the error IS the remediation instruction

Skills defined in `AGENTS.md` and nested `docs/` with progressive disclosure (short summary at root, full detail in linked subdocs). Agent reads only what's needed.
### 4.5 Multi-agent orchestration model
- Each agent runs in an **isolated git worktree** at `$CODEX_HOME/worktrees/<task-id>`. [developers.openai](https://developers.openai.com/codex/app/windows/)
- Agents coordinate via **git branches and PRs**, not direct message-passing. This prevents cascading failures — an agent writing bad code to its branch does not affect other worktrees. [openai](https://openai.com/index/harness-engineering/)
- Each worktree gets its own **ephemeral observability stack** (LogQL/PromQL), torn down when the task completes. [openai](https://openai.com/index/harness-engineering/)
- Landlock per-process filesystem permissions mean an agent cannot `cd` into a sibling worktree even if it tries. [developers.openai](https://developers.openai.com/codex/cli/reference/)
### 4.6 State and memory model
- **Within-task**: repo files, ephemeral obs stack, registered RPC tool outputs
- **Cross-task**: the repository itself is the **only system of record** — anything not encoded in repo docs/code does not exist to the agent. [openai](https://openai.com/index/harness-engineering/)
- **No equivalent of CLAUDE.md** — instead: `AGENTS.md` (root-level table of contents), `docs/architecture/`, `docs/decisions/`, linter definitions, CI/CD config. [openai](https://openai.com/index/harness-engineering/)
- Sessions shared between CLI and Desktop App: yes — both use `%USERPROFILE%\.codex` (Windows) or `~/.codex` (Linux/macOS). [developers.openai](https://developers.openai.com/codex/app/windows/)

***
## Part 5 — Codex Desktop App (Windows)
### 5.1 Architecture: GUI shell over same engine
Codex App is a **GUI wrapper around the same `codex-rs` agent binary** the CLI uses.  Differences from the CLI: [openai](https://openai.com/index/introducing-the-codex-app/)
- Multi-thread project management (run N agent threads in parallel, each with own worktree)
- Automations (scheduled/background tasks that run while app is open; cloud tasks run without app)
- Skills management UI (register/configure tools)
- Results/diff review panel with PR-style interface

Session history and config are **fully shared** with the CLI. [openai](https://openai.com/index/introducing-the-codex-app/)
### 5.2 Windows-specific execution modes
The Windows app offers two agent execution modes: [developers.openai](https://developers.openai.com/codex/app/windows/)

1. **Native Windows mode (default)**: Commands run in PowerShell. Sandbox is the same AppContainer restricted token + WFP model as the CLI on Windows. No Hyper-V, no WSL required.
2. **WSL mode** (optional, toggle in settings): Commands run in your chosen WSL distribution. Linux Landlock+seccomp sandbox applies. Recommended for Linux-native dev toolchains.

**Critical difference from Claude Desktop**: Codex App does NOT create or manage a Hyper-V VM. It uses OS-native sandboxing primitives. Claude Desktop always creates a Hyper-V VM; Codex App never does.
### 5.3 Session sharing between CLI and App (Windows)
- **Native Windows CLI ↔ App**: shared automatically via `%USERPROFILE%\.codex`. [developers.openai](https://developers.openai.com/codex/app/windows/)
- **WSL CLI ↔ App**: NOT shared by default. WSL uses `~/.codex` (Linux home, different path). To sync: add `export CODEX_HOME=/mnt/c/Users/<user>/.codex` to your WSL shell profile. [developers.openai](https://developers.openai.com/codex/app/windows/)

***
## Part 6 — Isolation Strength Reference
---
## Part 7 — How Tools Reach the Agent: Architectural Contrast
The two tool provision models produce agents that fail differently:

| Failure mode | Claude Code (bash) | Codex (RPC) |
|---|---|---|
| Tool doesn't exist in harness | Improvises shell alternative | Hard fail — no fallback |
| Unexpected file path needed | `cd` anywhere in bubblewrap scope | Landlock blocks it at kernel |
| Network call needed mid-task | Allowlisted proxy permits/denies | WFP/stubs block entirely |
| Novel debugging task | Invents pipeline on the fly | Requires pre-registered tool |
| Reproducibility of same task | Variable (shell improvisation) | High (typed RPC, same tools) |
| Token consumption per task | Higher (3.2–4.2× more than Codex)  [morphllm](https://www.morphllm.com/comparisons/codex-vs-claude-code) | Lower (structured tool calls) |

The bash harness excels at **breadth and improvisation**. The RPC harness excels at **precision and reproducibility** once the harness has been built to cover the task domain.

***
## Part 8 — Task–Tool Fit Matrix
The matrix is derived from the following mechanics:

- **Codebase exploration / architecture planning**: Claude Code CLI wins because the bash harness + full env access + 1M context window lets it navigate codebases ad hoc. Codex's closed RPC harness makes exploration hard — only registered tools exist to the agent.
- **Parallel implementation**: Codex wins because Landlock-isolated worktrees + git-based agent coordination prevents any cross-contamination. Claude Code sub-agents share a bubblewrap container (harder to hermetically isolate per-agent at the kernel level).
- **UI bug reproduction (Chrome DevTools Protocol)**: Codex wins because CDP is a first-party registered tool in the OpenAI harness.  In Claude Code you need a custom `openbrowser` or Playwright MCP server. [openai](https://openai.com/index/harness-engineering/)
- **Performance/observability work**: Codex wins because the ephemeral per-worktree obs stack (PromQL/LogQL) is first-party. [openai](https://openai.com/index/harness-engineering/)
- **Cross-service scripting, SSH, cloud CLIs**: Claude Code CLI wins decisively — it has your SSH agent socket, env vars, cloud CLI configs. Codex's network-off default makes external API calls require explicit sandbox relaxation.
- **Background async tasks**: Codex Cloud wins — tasks continue after you close the app. Perplexity Computer is also strong here. Claude Code CLI requires you to keep the terminal open.
- **Non-coder knowledge work**: Claude Desktop/Cowork wins — GUI, connectors, Office-format outputs, no terminal.
- **Secret / SSH key access**: Claude Code CLI wins. Codex explicitly blocks network and has no SSH-agent equivalent by default.
- **Multi-agent git coordination**: Codex wins — worktree isolation is first-class, git-based coordination is native. [openai](https://openai.com/index/harness-engineering/)

***
## Part 9 — Strategic Architectural Decisions: Repo Structure
This is where the choice becomes a **long-term investment decision**. [openai](https://openai.com/index/harness-engineering/)
### Claude Code–optimized repository
- `CLAUDE.md` at root: persistent context file auto-loaded on every session
- Local markdown artifacts written by agents: progress logs, decision notes, feature checklists
- MCP server config in `.mcp.json` or synced from `claude.ai/settings/connectors`
- Skills as local shell scripts or markdown files, referenced by short descriptions in CLAUDE.md
- No special structure required for docs — agent explores ad hoc via shell
- **Value compounds**: the more context is encoded in CLAUDE.md and local artifacts, the more productive each Claude Code session becomes
### Codex–optimized repository
- `AGENTS.md` at root: table of contents pointing to deeper docs (progressive disclosure)
- `docs/architecture/`, `docs/decisions/`, `docs/api/`: structured docs Claude Code agent would find by exploring; Codex agent needs linked explicitly
- Custom linters in CI with **agent-facing error messages** (the error string IS the remediation instruction)
- `requirements.toml` for org-level approval policy and sandbox mode enforcement
- Ephemeral observability config per worktree (if using the advanced harness)
- **Value compounds**: the more the repo encodes decisions and constraints as machine-readable rules + linters, the more reliable Codex's automated implementation becomes
### Lock-in reality
These structures do not transfer cleanly.  A CLAUDE.md-heavy repo dropped into Codex gives Codex no structured table of contents; Codex agent may ignore it. An AGENTS.md + linter-heavy repo given to Claude Code works, but wastes Claude Code's ability to explore freely. [openai](https://openai.com/index/harness-engineering/)

**Practical mitigation**: maintain both `CLAUDE.md` (for exploration-phase sessions) and `AGENTS.md` (for implementation-phase automation). They serve different agents at different project stages and can coexist.

***
## Part 10 — Recommended Workflow: Hybrid Staging
Based on the tool mechanics, the optimal team workflow is:

1. **Exploration & architecture** → Claude Code CLI (or Desktop/Cowork for non-devs)
   - Full shell, full context, MCP connectors, SSH access
   - Produces: architecture docs, design decisions, CLAUDE.md, feature lists, scaffolding

2. **Encode decisions** → commit to repo as AGENTS.md + structured docs + custom linters
   - Human/Claude Code step: translate exploration insights into machine-readable constraints

3. **Parallel implementation** → Codex CLI/App (local) or Codex Cloud
   - One task per worktree, Landlock-isolated, git-coordinated, reproducible
   - Produces: feature branches, PRs for human review

4. **UI validation / perf testing** → Codex (with CDP + obs stack registered)
   - If harness has CDP: agent reproduces bug, validates fix, confirms metrics
   - Produces: validated PRs

5. **Knowledge work, coordination, async research** → Claude Desktop/Cowork or Perplexity Computer
   - Non-code artifacts: reports, emails, spreadsheets, project tracking

***
## Part 11 — Security Risk Summary
| Risk vector | Claude Code CLI | Claude Desktop/Cowork | Codex CLI | Codex App (Windows) |
|---|---|---|---|---|
| Prompt injection → system damage | High (no sandbox default) | Low (VM isolates host) | Low (Landlock blocks) | Low (AppContainer blocks) |
| Cross-session malware persistence | Medium (filesystem accessible) | Very low (clean VM per session) | Low (workspace-write default) | Low |
| SSH/secret exfiltration | High (env vars accessible) | Medium (not in VM by default) | Very low (no network default) | Very low |
| Malicious repo `.codex/config.toml` | N/A | N/A | High (known CVE, startup injection)  [research.checkpoint](https://research.checkpoint.com/2025/openai-codex-cli-command-injection-vulnerability/) | High |
| Windows Home incompatibility | No sandbox risk, just no sandbox | App won't launch (Hyper-V required)  [github](https://github.com/anthropics/claude-code/issues/29887) | Native sandbox works on all editions | Works on all editions |
| Dependency on external VM infrastructure | None | Hyper-V / Apple VZ required | None | None (optional WSL) |

***
## Part 12 — Quick Reference Decision Table
| Question | Answer |
|---|---|
| "I want to explore a new codebase I've never seen" | Claude Code CLI |
| "I want to write code in parallel across 10 features" | Codex App (worktrees) |
| "I need to reproduce a browser UI bug and fix it" | Codex (with CDP harness) |
| "I need to SSH into a server and run a deploy script" | Claude Code CLI |
| "I want an agent to run overnight without my laptop on" | Codex Cloud or Perplexity Computer |
| "My non-technical colleague needs to organize 2,000 PDFs" | Claude Desktop/Cowork |
| "I'm on Windows Home and want sandboxed agent" | Codex CLI/App (AppContainer, no Hyper-V needed) |
| "I'm on Linux and want maximum isolation" | Claude Code CLI + bubblewrap sandbox runtime |
| "I want to connect agents to Gmail, Notion, GitHub simultaneously" | Claude Code CLI (MCP, account-synced connectors) |
| "I want reproducible, auditable implementation with no external calls" | Codex CLI (`workspace-write`, network blocked) |
