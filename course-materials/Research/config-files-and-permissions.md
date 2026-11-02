# Config files and permissions - Claude Code, Codex, Copilot CLI

> Moved from [Course INDEX - AI in Programming](../Course%20INDEX%20-%20AI%20in%20Programming.md) on 2026-10-02 to keep the notes short. Facts verified 2026-10-01; dates and sources are on each item.

## Permissions

**Claude Code - settings.json permissions**: `permissions` block with `allow` / `deny` / `ask` arrays; evaluated **deny, then ask, then allow** (first match wins; a broad deny beats a narrower allow - allows can't punch holes in denies): [Configure permissions](https://code.claude.com/docs/en/permissions)

```json
{
  "permissions": {
    "allow": [
      "Bash(npm run test:*)",
      "Bash(git diff:*)",
      "Bash(git log:*)",
      "WebFetch(domain:docs.oracle.com)"
    ],
    "ask": [
      "Bash(git push *)",
      "WebFetch(domain:*)"
    ],
    "deny": [
      "Bash(git add -A)",
      "Bash(git add .)",
      "Read(./.env)",
      "Read(./secrets/**)",
      "Edit(/src/generated/**)"
    ]
  }
}
```

- Syntax: `Tool(specifier)`; `Bash(npm run *)` = prefix match; `:*` suffix is documented as equivalent to a trailing space-asterisk; compound commands (`&&`, `||`, `;`, `|`) are matched per subcommand
- WebFetch: `WebFetch(domain:example.com)`, `WebFetch(domain:*.example.com)` (subdomains only, NOT the bare domain), `WebFetch(domain:*)` (everything else - pair with `ask` to review other domains)
- Path rules (Read/Edit only) are gitignore-style with anchors: `//path` (fs root), `~/path` (home), `/path` (relative to the settings file), `./path` (cwd); `!` negation works within one file
- Where the files live (precedence high to low): enterprise `managed-settings.json` > `--settings` flag > `.claude/settings.local.json` (personal, gitignored) > `.claude/settings.json` (team, in repo) > `~/.claude/settings.json` (user): [Settings](https://code.claude.com/docs/en/settings)
- A small built-in read-only set (`ls`, `cat`, grep, read-only git...) never prompts unless you add an ask/deny rule for it

**Codex - config.toml & permissions**: docs at [Configuration reference](https://developers.openai.com/codex/config-reference)

- **Config layers, strongest first:** trusted project `.codex/config.toml` > selected **profile** `~/.codex/<name>.config.toml` (`codex --profile <name>`) > user `~/.codex/config.toml`. A project config is loaded only for **trusted** projects and cannot set provider/auth/notify/profile keys, but an ordinary key in it (for example `model`) overrides the selected profile
- **`approval_policy`:** `on-request` (pause & ask before commands) | `never` (non-interactive) | `{ granular = {...} }` (per-category allow/auto-reject); ~~`untrusted`~~ removed (CLI 0.149.0+), `on-failure` deprecated
- **`sandbox_mode`:** `read-only` | `workspace-write` (tunables: `sandbox_workspace_write.network_access`, `writable_roots`) | `danger-full-access`; newer alternative: `default_permissions = ":workspace"` (don't mix with `sandbox_mode`)
- **Allow/deny specific commands = Rules** (Starlark, per layer): user `~/.codex/rules/default.rules`, project `<repo>/.codex/rules/` - [Rules](https://developers.openai.com/codex/rules); `decision` = `allow` / `prompt` / `forbidden`, **most restrictive wins**; TUI "always allow" writes a rule there automatically; test: `codex execpolicy check --rules ~/.codex/rules/default.rules -- gh pr view 7888`

```starlark
prefix_rule(
    pattern = ["gh", "pr", "view"],
    decision = "prompt",
    justification = "Viewing PRs is allowed with approval",
)
```

- Enterprise admins enforce rules org-wide via `requirements.toml`

**Copilot CLI - where permission rules live**:

- Saved approvals: **`~/.copilot/permissions-config.json`**, per location (Git repo root or cwd), object `locations` > `tool_approvals` + `allowed_directories`. Allow only - **no deny rules in this file**; `/reset-allowed-tools` clears session grants + saved approvals for the location: [Config dir reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-config-dir-reference)
- Deny rules are **flags/URL lists, not repo files**; **deny always wins** over allow and `--allow-all`:
  - `--allow-tool='shell(git:*)' --deny-tool='shell(git push)'` - all git commands except `git push`
  - `--deny-tool=write` - no file writes
  - `--allow-tool='MyMCP(create_issue), MyMCP(delete_issue)'` - allow two tools of an MCP server ([Allowing and denying tool use](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/allowing-tools))
- Command matching is literal except a trailing `:*` prefix (`git:*` matches `git status`, `git push`; `git*` matches nothing special); no regex
- URLs: **`allowedUrls` / `deniedUrls`** in `~/.copilot/settings.json` (JSONC), supports `*.github.com` wildcards; `deniedUrls` always wins; repo `.github/copilot/settings.json` can add `deniedUrls` (union, can never remove)
- Session commands: `/permissions [default|assisted|allow-all|show]`, `/permissions reset`, `/yolo`; enterprise policy `permissions.disableBypassPermissionsMode`: `"disable"` blocks everything, `"allow-auto-only"` still permits `/permissions assisted`
- UNCONFIRMED: `defaultPermissionMode: 'assisted'` in settings.json (reported experimental in CLI 1.0.88 on the [Copilot Q&A page](https://devpowers.com/szkolenia/COURSE-SITE/pytania.html)) - absent from the current settings schema (checked 2026-10-01, CLI v1.0.91)

### Example files in this repo

- Claude Code: [project `.claude/settings.json`](../../.claude/settings.json) (allow/deny + pom.xml security hook), [`agent-configs/claude/settings.json`](../agent-configs/claude/settings.json), commented version with the reasoning behind each rule: [`agent-configs/claude/settings.jsonc`](../agent-configs/claude/settings.jsonc)
- Codex: [project `.codex/config.toml`](../../.codex/config.toml) (`approval_policy`, `sandbox_mode`, network), Java/Spring variant: [`agent-configs/codex/config.toml`](../agent-configs/codex/config.toml)
- Copilot CLI: `--allow-tool` / `--deny-tool` flags in [`agent-configs/copilot/start-copilot.sh`](../agent-configs/copilot/start-copilot.sh) and [`start-copilot.ps1`](../agent-configs/copilot/start-copilot.ps1)
- Hooks that block secrets in all three tools: [`hooks-example/`](../hooks-example/)

## Claude Code: enterprise (managed) settings vs your config

Org-wide policy file **`managed-settings.json`** - same JSON shape as settings.json, highest precedence, users cannot override: [Managed settings](https://code.claude.com/docs/en/managed-settings)
- Paths: macOS `/Library/Application Support/ClaudeCode/`, Linux/WSL `/etc/claude-code/`, Windows `C:\Program Files\ClaudeCode\`; also deliverable via MDM or claude.ai console ([server-managed settings](https://code.claude.com/docs/en/server-managed-settings))
- What a company can centrally enforce: **permission rules** (deny/ask/allow + `allowManagedPermissionRulesOnly: true` = managed rules are the ONLY source), model & `availableModels`, `env`, hooks (`allowManagedHooksOnly`), MCP servers, block `bypassPermissions` mode, marketplaces, minimum version, login org
- Settings precedence (highest wins): managed > `--settings` flag > `.claude/settings.local.json` > `.claude/settings.json` > `~/.claude/settings.json`: [Settings](https://code.claude.com/docs/en/settings)
- **Can the company block YOUR CLAUDE.md/AGENTS.md?** Default: NO - no managed key touches project/user memory files; the org's managed `CLAUDE.md` is additive on top. Only if the org explicitly sets `pluginConfigs."agents-md@builtin".options.instructionFiles: "managed-only"` in managed-settings.json do your project/local/user CLAUDE.md, `.claude/rules/` and all AGENTS.md get left out ([memory docs](https://code.claude.com/docs/en/memory)); subdirectory rules still load on demand. A repo can never do this (project/local settings are ignored for that key)
- Check what actually applied: `/doctor`, `/context`, and [Debug your configuration](https://code.claude.com/docs/en/debug-your-config)

## Statusline (Claude Code)

Custom status line under the prompt: `statusLine` in settings.json runs your command after each turn with session JSON on stdin: [Statusline docs](https://code.claude.com/docs/en/statusline)
- Easiest: type `/statusline show model name and context percentage` - Claude Code generates the script and wires settings for you
- Manual example in `~/.claude/settings.json`:

```json
{
  "statusLine": {
    "type": "command",
    "command": "~/.claude/statusline.sh",
    "padding": 2,
    "refreshInterval": 30
  }
}
```

- `~/.claude/statusline.sh` (chmod +x; script echoes to stdout, one echo = one row):

```bash
#!/bin/bash
input=$(cat)
MODEL=$(echo "$input" | jq -r '.model.display_name // "?"')
CTX=$(echo "$input" | jq -r '.context_window.used_percentage // 0')
echo "$MODEL | context: ${CTX}%"
```

- stdin JSON fields: `model.display_name`, `workspace.current_dir`, `cost.total_cost_usd`, `context_window.used_percentage`, `rate_limits.*` (Pro/Max limits live in the statusline!), `effort.level`, `version`
- Runs locally, uses **no API tokens**; options `refreshInterval`, `padding`; many fields are null early in a session, so use `// 0` fallbacks
- By default the script re-runs only on session events (new message, model or mode change), so it goes quiet while you are idle. `refreshInterval: 30` also re-runs it every 30 seconds, which keeps countdowns (rate-limit resets, cache expiry) moving

- Full example in this repo (git branch, model + effort, context bar, cost, Pro/Max 5h + weekly usage with reset countdown, cache hit rate with expiry countdown): [`agent-configs/claude/statusline.sh`](../agent-configs/claude/statusline.sh)
