#!/usr/bin/env bash
# Teaching examples, not a shell parser or a security boundary.
set -eu
deny() { printf '%s\n' "$1" >&2; exit 2; }
command -v jq >/dev/null || deny 'Hook requires jq. Install jq and retry.'
payload=$(cat)
printf '%s' "$payload" | jq -e 'type == "object"' >/dev/null 2>&1 || deny 'Hook requires a JSON object on stdin.'
field() { printf '%s' "$payload" | jq -r "$1" 2>/dev/null || deny 'Hook input has an unsupported shape.'; }
cwd=$(field '.cwd // "."')
case "${1:-}" in
  shell)
    cmd=$(field '.tool_input.command // .tool_input.cmd // empty')
    [ -n "$cmd" ] || deny 'Shell hook received no command; inspect the tool payload.'
    if printf '%s' "$cmd" | grep -Eq 'git[[:space:]]+push.*(--force|[[:space:]]-f([[:space:]]|$)|(^|[[:space:]:/])main([[:space:]]|$))'; then
      deny 'Push blocked: use a feature branch and a normal push; ask the owner about protected branches or rewritten history.'
    fi
    # A bare `git push` on main pushes main (push.default=simple), so check the current branch too.
    current=$(git -C "$cwd" symbolic-ref --short -q HEAD 2>/dev/null || true)
    if printf '%s' "$cmd" | grep -Eq 'git[[:space:]]+push' && { [ "$current" = main ] || [ "$current" = master ]; }; then
      deny "Push blocked: the current branch is $current. Create a feature branch and push that instead."
    fi
    if printf '%s' "$cmd" | grep -Eq '(^|[[:space:];|&])rm[[:space:]].*(--recursive|-[[:alpha:]]*[rR])'; then
      deny 'Recursive rm blocked: inspect targets and remove specific files without recursive flags.'
    fi
    if printf '%s' "$cmd" | grep -Eq '(curl|wget)[[:space:]].*\|[[:space:]]*(ba)?sh([[:space:]]|$)'; then
      deny 'Download piped to a shell blocked: save the script and review it before running it.'
    fi
    if printf '%s' "$cmd" | grep -Eq 'chmod[[:space:]].*(-R|--recursive).*777'; then
      deny 'Recursive chmod 777 blocked: choose narrow permissions for specific paths.'
    fi
    ;;
  writes)
    # Codex apply_patch uses command; Claude Write/Edit use content/new_string.
    text=$(field '[.tool_input.content, .tool_input.new_string, .tool_input.command] | map(select(type == "string")) | join("\n")')
    [ -n "$text" ] || exit 0
    if printf '%s' "$text" | grep -Eiq -- '(AKIA|ASIA)[A-Z0-9]{16}|-----BEGIN ([A-Z0-9]+ )?PRIVATE KEY-----|ghp_[A-Za-z0-9_]{20,}|github_pat_[A-Za-z0-9_]{20,}|password[[:space:]]*[:=][[:space:]]*[^[:space:]]+'; then
      deny 'Write blocked: possible credential. Use an environment variable or a synthetic placeholder; never repeat the matched value.'
    fi
    ;;
  java)
    # Explicit opt-in: never guess the build system or run input from the agent.
    [ -n "${HOOK_JAVA_CHECK:-}" ] || exit 0
    if [ "$(field '.stop_hook_active // false')" = true ]; then
      printf '%s\n' 'Java gate already requested a correction; stopping is allowed to avoid a loop. Report any remaining failure.' >&2
      exit 0
    fi
    command -v timeout >/dev/null || deny 'Java gate requires GNU timeout.'
    cd "$cwd" || deny 'Java gate cannot enter cwd.'
    git rev-parse --show-toplevel >/dev/null 2>&1 || deny 'Java gate requires a Git checkout.'
    changed=$(git diff --name-only; git diff --cached --name-only; git ls-files --others --exclude-standard -- ':/')
    printf '%s\n' "$changed" | grep -Eq '\.java$' || exit 0
    # Keep raw compiler output out of model context: it may contain source data.
    if timeout --kill-after=2s 15s bash -c "$HOOK_JAVA_CHECK" >/dev/null 2>&1; then
      exit 0
    else
      status=$?
      deny "Java check failed (exit $status; timeout 124). Run the configured check, inspect errors and fix or report the blocker before finishing."
    fi
    ;;
  context)
    cd "$cwd" || deny 'Context hook cannot enter cwd.'
    branch=$(git symbolic-ref --short -q HEAD 2>/dev/null || printf 'detached-or-no-repository')
    if changes=$(git status --porcelain=v1 -uno 2>/dev/null); then
      count=$(printf '%s\n' "$changes" | grep -c . || true)
    else
      count=unknown
    fi
    jq -n --arg context "Branch: $branch. Changed tracked entries: $count (untracked files excluded). Read AGENTS.md and agreed requirements; preserve existing edits and use synthetic data." \
      '{hookSpecificOutput:{hookEventName:"SessionStart",additionalContext:$context}}'
    ;;
  *) deny 'Usage: guard.sh shell|writes|java|context' ;;
esac
