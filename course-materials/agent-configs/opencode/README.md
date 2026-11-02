# OpenCode config example

Reference `opencode.jsonc` for the course, next to the Claude Code, Codex and Copilot examples
in `agent-configs/`. It shows how to set a **default model**, configure
**MCP servers** (with one disabled-by-default for on-demand use), and fixes the
**ACP/IntelliJ "wrong model"** problem.

## Where the file goes

| Scope | Path | Notes |
|---|---|---|
| Global | `~/.config/opencode/opencode.jsonc` | Applies to all projects |
| Project | `./opencode.jsonc` (repo root) | Overrides global for this repo |

Load order (later wins): remote → global → `$OPENCODE_CONFIG` → project.

OpenCode reads **JSONC**, so `//` comments are allowed (same as our
[`../claude/settings.jsonc`](../claude/settings.jsonc); plain `settings.json` has no comments).

## Protected-branch push policy

The example's `permission.bash` object asks for approval by default, including feature-branch pushes. It denies explicit destinations `main`, `master` and `prod` using `git push * main` / `git push * main *` and `git push *:main` / `git push *:main *`, repeated for the other branches. Force denials cover leading and later `--force*` (including `--force-with-lease`) and standalone `-f` flags.

OpenCode accepts `allow`, `ask` and `deny`; `*` matches any text, including spaces, and the last matching rule wins. Keep the catch-all first and the denials after it. The [permissions documentation](https://opencode.ai/docs/permissions/#granular-rules-object-syntax) and [config schema](https://opencode.ai/config.json) define this syntax; local OpenCode 1.18.30 `opencode --help` also describes `--auto` as approving requests that are not explicitly denied.

Bare `git push` names no branch and therefore only asks; approving it can push a checked-out protected branch. Aliases, wrappers, full refs, global Git options and `+` force refspecs can escape these patterns. GitHub/Bitbucket branch protection is the real guard. See the [cross-tool comparison](../README.md#protected-branch-push-policy).

## Default model

Set the top-level `"model"` key as `"<provider>/<model-id>"`:

```jsonc
"model": "openrouter/deepseek/deepseek-v4-pro"
```

- **Model name confirmed:** OpenRouter publishes it as `deepseek/deepseek-v4-pro`
  (DeepSeek V4 Pro — 1.6T-param MoE, 1M context). In OpenCode you prefix it with
  the provider id, so the full string is `openrouter/deepseek/deepseek-v4-pro`
  (two slashes — one for the OpenCode provider, one inside OpenRouter's own id).
- Needs `OPENROUTER_API_KEY` in your environment, or run `opencode auth login`.
- Built-in providers (openrouter, anthropic, openai…) come from models.dev and
  need **no** `provider` block — you only declare custom/local ones (e.g. Ollama).

## The IntelliJ / ACP "default Zen model" problem

**What you saw:** OpenCode added as an ACP (Agent Client Protocol) agent in
IntelliJ used a default "Zen" model instead of the one you last used in the CLI
or Desktop app, and there's no GUI in IntelliJ to change it.

**Why:**

1. **ACP runs the `opencode` CLI directly.** IntelliJ (and Zed) launch
   `opencode acp`, which starts OpenCode as a subprocess speaking JSON-RPC over
   stdio. So yes — it *is* the OpenCode CLI under the hood.
2. **The ACP session reads the config default `model`, not your last-used one.**
   The model you pick interactively in the TUI/Desktop is per-session TUI state,
   not the persisted default. A fresh ACP session ignores it.
3. **With no `model` set, OpenCode falls back to its built-in "opencode zen"
   gateway default** — that's the "Zen" model you saw.

**Fix:** set `"model"` in `opencode.jsonc` (global, or project for per-repo
control). Restart the IDE / reopen the ACP chat. ACP will now use that model.
For a single agent only, use the per-agent `agent.<name>.model` override (see the
commented block at the bottom of the example).

> The ACP protocol does define a "set session model" request, but the current
> JetBrains AI Assistant UI doesn't expose a model picker for ACP agents, so the
> config default is the reliable way to control it.

### Minimal JetBrains ACP registration (`acp.json`)

This is separate from `opencode.jsonc` — it just tells IntelliJ how to launch the
agent. Point `command` at your `opencode` binary:

```jsonc
{
  "agent_servers": {
    "opencode": {
      "command": "/absolute/path/to/bin/opencode",
      "args": ["acp"]
    }
  }
}
```

After editing `acp.json`, restart the IDE if the agent doesn't appear.

## MCP servers (and on-demand JetBrains)

OpenCode's MCP schema differs from Claude Code's `.mcp.json`:

| | Claude `.mcp.json` | OpenCode `opencode.jsonc` |
|---|---|---|
| stdio server | `"type": "stdio"`, `command` (string) + `args` | `"type": "local"`, `command` (**array**) |
| stdio env | `"env"` | `"environment"` |
| http server | `"type": "http"` | `"type": "remote"` |
| disable | `"enabled": false` | `"enabled": false` |

The **JetBrains MCP is `"enabled": false`** here so it isn't loaded on every run
(it's heavy and only useful while IntelliJ is open). To use it on demand: flip
`"enabled": true`, make sure IntelliJ is running with the MCP Server plugin on
the matching `IJ_MCP_SERVER_PORT`, and adjust the install path/version.

> The same JetBrains MCP is also defined in this repo's root `.mcp.json` for
> Claude Code, and is likewise **disabled by default** there — enable on demand.

## Adapt for your machine

1. Replace the Windows IntelliJ paths with your install location (or your OS path).
2. Keep secrets in env vars (`CONTEXT7_API_KEY`, `OPENROUTER_API_KEY`) rather
   than hardcoding them in the file.
3. Trim the Ollama `provider` block to the local models you actually have.
