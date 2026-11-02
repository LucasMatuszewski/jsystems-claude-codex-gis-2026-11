# Codex custom commands compared with Claude Code

Checked: 2026-10-16. Local CLI reports `0.162.1`; source snapshot is main commit `6b991972c5b539198dcea9bac4fc14e57559c3af` (2026-10-15). Main-only findings below are not a claim that the installed release exposes them.

## Answer

Codex has reusable prompts, but there is no verified `.codex/commands/` directory equivalent to Claude's `.claude/commands/` convention. Distinguish these mechanisms:

| Mechanism | Scope and invocation |
|---|---|
| Legacy custom prompts | Official docs describe `~/.codex/prompts/<name>.md`, invoked with `/prompts:<name>` and optional named/positional arguments. **Deprecated; use skills.** Local Codex-home files are not repository-shared commands. [Custom prompts](https://developers.openai.com/codex/custom-prompts/) |
| Skills | Repository `.agents/skills/<name>/SKILL.md` or user `~/.agents/skills/<name>/SKILL.md`. Invoke explicitly with `$name`; the description can also trigger selection. Bundle scripts/references when useful. [Skills](https://developers.openai.com/codex/skills/) |
| Built-in slash commands | Implemented by the harness, such as `/model`, `/diff`, `/skills`, `/plugins`. A Markdown filename does not add a built-in command. [Command docs](https://learn.chatgpt.com/docs/developer-commands?surface=cli), [source enum](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/tui/src/slash_command.rs) |
| Presets, in inspected main | `/presets` opens saved reusable inputs, including prompts and existing slash-command text. Source uses numbered slots `0`-`9` under `tui.presets`; this is not a directory of newly registered named commands. [Dispatch](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/tui/src/chatwidget/slash_dispatch.rs), [implementation](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/tui/src/chatwidget/quick_dials.rs), [config types](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/config/src/types.rs) |
| Plugins | Package/distribute skills and integrations. They do not establish support for Claude's command-directory schema. [Plugin skills and conversion guidance](https://developers.openai.com/plugins/guides/submit-claude-plugin) |

The main snapshot no longer contains the old custom-prompt directory loader; the remaining `custom_prompt_view` is a text-entry UI, not proof of file-command discovery. Official legacy documentation and current main should not be conflated. UNVERIFIED: legacy prompt loading and `/presets` availability in the running 0.162.1 TUI; neither was exercised interactively. Check the actual `/` menu before teaching a version-specific feature.

## Recommended migration from a Claude command

1. Take the instructions from `.claude/commands/review-change.md`; inspect its frontmatter and tool assumptions rather than copying them blindly. Claude still supports that convention, but now recommends skills for new workflows. [Claude skills and commands](https://code.claude.com/docs/en/skills).
2. Create `.agents/skills/review-change/SKILL.md` in the target project with Codex-compatible metadata and the prompt body:

```markdown
---
name: review-change
description: Review the current diff for correctness, regressions, and missing tests when asked for a change review.
---

Read the requested files and the current diff. Report concrete findings with
file references and severity. Do not edit files or publish comments unless asked.
Treat scope supplied after the skill name as the user's review scope.
```

3. Replace Claude's `$ARGUMENTS` interpolation with ordinary explicit task input; do not assume Codex performs the same template substitution in a skill. Move `allowed-tools`, hooks, shell snippets, subagent directives and provider-specific options to supported Codex mechanisms after review.
4. Start a fresh target-project session if needed for discovery, then enter `$review-change focus on parser errors`. Verify selection and behavior against a synthetic diff. Sharing the checked-in skill now shares the procedure; it does not share credentials or session history.

For a one-line personal shortcut, use `/presets` only if the installed UI offers it. For an existing legacy prompt, `/prompts:review-change` may remain usable in versions that still load it, but creating new deprecated files is not the recommended migration.
