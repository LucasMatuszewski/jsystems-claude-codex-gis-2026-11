# Agent managers, multiplexers and remote agents

> Moved from [Course INDEX - AI in Programming](../Course%20INDEX%20-%20AI%20in%20Programming.md) on 2026-10-02 to keep the notes short. Facts verified 2026-10-01; dates and sources are on each item.

## Agent managers / multiplexers - work with many agents at once (links verified 01.10.2026)

- **[Herdr](https://herdr.dev)** (open source, Rust, 03.2026): terminal multiplexer built for agents - "the runtime your coding agents live on"; real terminals kept open by a background server, so agent work survives closed lids and lost SSH connections
  - Organizes work into **workspaces / tabs / panes**, recognizes coding agents running inside panes and tracks their state: **idle, working, blocked, done** (blocked = agent waits at an approval/question dialog)
  - **Vendor-neutral**: run claude, codex, opencode, grok side by side; every agent in a normal terminal, you keep your own subscriptions and configs
  - `herdr` CLI (JSON output) starts agents, splits panes, sends prompts (`herdr agent prompt ... --wait`), waits for state changes - scriptable, works for agents controlling agents
  - Docs: [herdr.dev/docs](https://herdr.dev/docs) | Source: [herdrdev/herdr](https://github.com/herdrdev/herdr) (~42k stars, 10.2026) | vs tmux/Zellij/cmux/Warp: [herdr.dev/compare](https://herdr.dev/compare)
- **[Beads](https://github.com/gastownhall/beads)** - "memory upgrade for your coding agent": git-backed distributed graph issue tracker (powered by Dolt), shared structured memory so agents survive context loss between sessions. By Steve Yegge; [announcement](https://steve-yegge.medium.com/introducing-beads-a-coding-agent-memory-system-637d7d92514a) (10.2025), [HN 11.2025](https://news.ycombinator.com/item?id=46075616). `github.com/steveyegge/beads` redirects here
- **[Paseo](https://paseo.sh)** - open-source orchestrator: local daemon manages agents, clients on desktop, mobile (iOS/Android), web and CLI; Claude Code, Codex, Copilot, OpenCode, Gemini, Cursor CLI and 25+ more via ACP. Source: [getpaseo/paseo](https://github.com/getpaseo/paseo)
- **[Orca](https://www.onorca.dev)** - open-source (MIT) desktop app "Agent Development Environment" by Stably AI: any coding agent with your own subscription, each in its own worktree, one dashboard; macOS/Windows/Linux + mobile companion. Source: [stablyai/orca](https://github.com/stablyai/orca) (~83k stars, 10.2026)
- **[T3 Code](https://t3.codes)** - "the open-source control plane for coding agents" from Theo Browne ([t3.gg](https://t3.gg)): desktop + web GUI, parallel worktrees with a single live diff; run with `npx t3@alpha` (no verified GitHub repo yet, 01.10.2026)
- **[Codex App](https://developers.openai.com/codex/app)** - OpenAI's own desktop app (single-vendor)
- **[Conductor](https://conductor.build)** - macOS app: team of coding agents (Claude Code, Codex, Cursor, OpenCode) in the cloud, isolated git worktree per task, built-in diff review; [review 2026](https://vibecoding.app/blog/conductor-review)
- **[Vibe Kanban](https://www.vibekanban.com)** - open-source Kanban board to orchestrate parallel coding agents. Source: [BloopAI/vibe-kanban](https://github.com/BloopAI/vibe-kanban)

## Herdr vs Codex App - two ways to run many agents

- **Herdr = vendor-neutral runtime you control**: claude/codex/opencode/grok side by side in one window, each in a plain terminal with your subscriptions, keys and configs; orchestrate via CLI or let one agent drive others (verified 01.10.2026)
- **Codex App = single-vendor desktop app**: OpenAI models only; tasks, cloud containers, GitHub integration and worktrees packaged for you, zero setup
- **Where agents run**: Herdr keeps agents on YOUR machines (laptop, desktop, VPS, saved SSH boxes) and the persistent server survives disconnects; Codex App pushes work to OpenAI's cloud (local worktree tasks supported too)
- **Trade-off**: Herdr costs nothing extra and works with every CLI agent, but you own the machines, updates and safety; Codex App is zero-ops and mobile-friendly, but locks the workflow to the OpenAI ecosystem
- They combine well: watch Codex CLI in a Herdr pane next to Claude Code, while Codex App handles cloud tasks

## Remote agents - delegate over SSH and cloud

- **Herdr remote machines**: saved SSH machines show up as workspaces; `herdr --machine <label> agent list / prompt ...` runs and steers agents on other computers without opening the TUI (both machines need an API-compatible Herdr server). The persistent server keeps agents alive after you close the laptop (verified 01.10.2026)
- **Codex App cloud tasks**: work runs in OpenAI cloud containers with GitHub integration, hand off from desktop or phone: [Codex Cloud docs](https://developers.openai.com/codex/cloud), [Codex Mobile](https://chatgpt.com/codex/mobile/)
- **Codex CLI headless**: `codex exec` for non-interactive runs in scripts and CI: [Non-interactive mode](https://developers.openai.com/codex/noninteractive)
- NEW: **`codex agents`** dashboard + **`codex queue`** (Codex CLI 0.149.0) - list running local/remote sessions and append follow-up messages by session name or ID; official docs page not yet published (checked 01.10.2026), community guides: [aq.dev](https://aq.dev/guides/codex-background-agents-and-the-agents-dashboard), [proflead.dev](https://proflead.dev/posts/openai-codex-agents-dashboard-codex-queue)
