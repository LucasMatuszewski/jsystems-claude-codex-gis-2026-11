# Codex configuration examples

The examples target Codex CLI 0.162.1 and were re-checked on 2026-10-31 with 0.166.0 (the project config loads without errors and a `.env` read is refused): named filesystem/network permission profiles, automatic approval review and Starlark command rules. Read [PERMISSIONS.md](PERMISSIONS.md) for the Claude mapping, platform limits, Windows prompts and doctor diagnostics.

| File | Use |
|---|---|
| [config.toml](config.toml) | Complete example with model/provider/MCP settings and five permission profiles |
| [permissions.toml](permissions.toml) | Minimal permission example with the same five profiles |
| [rules/course.rules](rules/course.rules) | Curated `allow`, `prompt` and `forbidden` command examples |
| [examples/claude-command-parity.rules](examples/claude-command-parity.rules) | Inactive literal comparison with Claude Bash permissions |
| [PERMISSIONS.md](PERMISSIONS.md) | Semantics, installation, Windows behavior and validation |

Merge selected settings into a trusted project's `.codex/config.toml`, then copy the curated rules to `.codex/rules/course.rules`. For deliberate user-wide scope use `~/.codex/config.toml` and `~/.codex/rules/`. Preserve provider choices and do not install the inactive comparison alongside the curated rules.

Avoid mixing legacy `sandbox_mode` and named-profile selectors. Higher-precedence selectors determine the effective syntax; a lower-precedence user setting does not automatically defeat a project profile. Reload the session and inspect `/permissions`, `/status` and `codex doctor --all`.

`course-workspace` permits workspace editing and public command network access, while denying the named environment files and secrets inside workspace roots. `course-root` is an equivalent named preset. Other profiles demonstrate workspace review, writes limited to `docs/`, and an optional two-host JetBrains policy. Only one profile is selected. Inherited temporary directories remain writable.

The active rules keep explicit `prompt` for `curl`/`wget` and the narrow `git`/`git.exe worktree add` prefix; broad read, Git, build, runtime, Docker-inspection and shell-wrapper prompts were removed because they review even sandboxed commands. Worktree creation must ask, including inside the sandbox; `git -C <dir> worktree add` does not match that prefix and still requires permission under the shared instructions. Ordinary work uses sandbox permissions and `on-request` escalation. `auto_review` handles eligible approval requests, not every edit or allowed network connection. In 0.162.1 active denied reads survive command allows and approved escalation. Hosted search, apps and MCPs have separate controls.

Feature branches may be pushed and PRs opened. Explicit `origin`/`upstream` pushes to `main`, `master` and `prod`, common upstream-option variants and force-flag prefixes are forbidden. Ordinary pushes have no explicit rule. Token prefixes miss bare push, refspec destinations such as `HEAD:main`, alternate remotes/options and some force forms; GitHub/Bitbucket branch protection is the real guard. See [PERMISSIONS.md](PERMISSIONS.md#feature-branch-pushes-and-protected-branches) for the Claude/Copilot equivalents and limits. The headless review script still forbids all pushes.

The 4000-token setting is a default history-truncation budget with tool-specific overrides, not a universal hard output limit. Inspect logs through bounded searches and excerpts. Linux sandbox masks can appear as empty `.env*`/`secrets` files and `.agents`/`.aws` directories; retain exact denials and do not delete masked paths.

Native Windows requires a backend that enforces denied reads. The provisioned legacy `elevated` backend can ask for administrator approval during setup or repair; ordinary refresh avoids UAC. Firewall dialogs are separate and need their named executable checked. See the mapping guide before considering MXC or changing security settings. User-level MCP warnings and environment diagnostics should be fixed at their source.

## Separate course account

To use a training account next to a company one, see [separate-course-account](separate-course-account/README.md): a second `CODEX_HOME` with analysis and implementation profiles.
