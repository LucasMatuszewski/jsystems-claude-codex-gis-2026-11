#!/usr/bin/env bash
# Headless code or security review of the current branch with one of four agent CLIs.
#
# Usage:
#   AGENT=copilot|claude|codex|opencode bash agent_review.sh <base-branch> [prompt-file] [out-dir]
#
# Writes <out-dir>/review.md (default .agent-review/). The agent may read files
# and run git diff/log/show, but cannot edit files or push.
#
# Authentication (set as secret CI variables):
#   LLM_PROVIDER=openrouter  one OPENROUTER_API_KEY works for all four agents
#   LLM_PROVIDER=native      each tool's own account:
#     copilot  COPILOT_GITHUB_TOKEN - fine-grained PAT owned by a user (not an org)
#              with the "Copilot Requests" permission; uses that user's AI credits
#     claude   ANTHROPIC_API_KEY
#     codex    CODEX_API_KEY (OpenAI API key; supported only by codex exec)
#     opencode any provider key opencode supports, e.g. OPENROUTER_API_KEY
# Optional:
#   REVIEW_MODEL                      model id (OpenRouter ids with openrouter)
#   CODEX_SANDBOX                     read-only (default). In a Docker job without user
#                                     namespaces bubblewrap cannot start; there the container
#                                     is the boundary, so set danger-full-access.
#   JIRA_BASE_URL, JIRA_EMAIL, JIRA_API_TOKEN
#                                     adds the Jira issue named in the branch
#                                     (e.g. feature/SHOP-123-returns) to the prompt
set -euo pipefail

BASE="${1:?Usage: agent_review.sh <base-branch> [prompt-file] [out-dir]}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROMPT_FILE="${2:-$HERE/prompts/code-review.md}"
OUT="${3:-.agent-review}"
AGENT="${AGENT:-copilot}"
PROVIDER="${LLM_PROVIDER:-openrouter}"
MODEL="${REVIEW_MODEL:-}"
CODEX_OPENROUTER=()
OPENROUTER_DEFAULT_MODEL="openai/gpt-6-luna"

mkdir -p "$OUT"
git fetch --no-tags origin "$BASE"
git diff "origin/$BASE...HEAD" > "$OUT/changes.diff"
if [[ ! -s "$OUT/changes.diff" ]]; then
  printf '## Summary\n\nNo changes to review.\n' > "$OUT/review.md"
  exit 0
fi

CONTEXT="The diff to review is in $OUT/changes.diff (base: origin/$BASE)."

# Optional Jira context: the agent sees what the issue asked for.
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
BRANCH="${CI_COMMIT_REF_NAME:-${BITBUCKET_BRANCH:-${SYSTEM_PULLREQUEST_SOURCEBRANCH:-$BRANCH}}}"
ISSUE_KEY="$(grep -oE '[A-Z][A-Z0-9]+-[0-9]+' <<<"$BRANCH" | head -1 || true)"
if [[ -n "$ISSUE_KEY" && -n "${JIRA_BASE_URL:-}" && -n "${JIRA_API_TOKEN:-}" ]]; then
  if curl -fsS -u "$JIRA_EMAIL:$JIRA_API_TOKEN" \
      "$JIRA_BASE_URL/rest/api/3/issue/$ISSUE_KEY?fields=summary,description,status" \
      > "$OUT/jira-issue.json"; then
    CONTEXT="$CONTEXT The Jira issue $ISSUE_KEY is in $OUT/jira-issue.json."
  fi
fi

PROMPT="$(cat "$PROMPT_FILE")

$CONTEXT"

case "$PROVIDER:$AGENT" in
  openrouter:copilot)
    export COPILOT_PROVIDER_BASE_URL="https://openrouter.ai/api/v1"
    export COPILOT_PROVIDER_API_KEY="$OPENROUTER_API_KEY"
    MODEL="${MODEL:-$OPENROUTER_DEFAULT_MODEL}" ;;
  openrouter:claude)
    export ANTHROPIC_BASE_URL="https://openrouter.ai/api"
    export ANTHROPIC_AUTH_TOKEN="$OPENROUTER_API_KEY"
    export ANTHROPIC_API_KEY=""
    MODEL="${MODEL:-anthropic/claude-sonnet-latest}" ;;
  openrouter:codex)
    CODEX_OPENROUTER=(-c model_provider=openrouter
      -c 'model_providers.openrouter={name="OpenRouter",base_url="https://openrouter.ai/api/v1",env_key="OPENROUTER_API_KEY",wire_api="responses"}')
    MODEL="${MODEL:-$OPENROUTER_DEFAULT_MODEL}" ;;
  openrouter:opencode)
    MODEL="openrouter/${MODEL:-$OPENROUTER_DEFAULT_MODEL}" ;;
esac

case "$AGENT" in
  copilot)
    copilot -p "$PROMPT" -s --no-ask-user ${MODEL:+--model "$MODEL"} \
      --allow-tool 'shell(git diff:*)' --allow-tool 'shell(git log:*)' --allow-tool 'shell(git show:*)' \
      --deny-tool 'write' --deny-tool 'shell(git push:*)' \
      > "$OUT/review.md" ;;
  claude)
    claude -p "$PROMPT" ${MODEL:+--model "$MODEL"} \
      --allowedTools "Read" "Grep" "Glob" "Bash(git diff:*)" "Bash(git log:*)" "Bash(git show:*)" \
      > "$OUT/review.md" ;;
  codex)
    codex exec --sandbox "${CODEX_SANDBOX:-read-only}" --skip-git-repo-check --ephemeral \
      "${CODEX_OPENROUTER[@]}" ${MODEL:+-m "$MODEL"} \
      -o "$OUT/review.md" "$PROMPT" > "$OUT/codex.log" ;;
  opencode)
    OPENCODE_CONFIG_CONTENT='{"permission":{"edit":"deny","webfetch":"deny","bash":{"*":"deny","git diff*":"allow","git log*":"allow","git show*":"allow"}}}' \
      opencode run ${MODEL:+-m "$MODEL"} "$PROMPT" > "$OUT/review.md" ;;
  *)
    echo "Unknown AGENT: $AGENT (use copilot, claude, codex or opencode)" >&2
    exit 1 ;;
esac

echo "Review written to $OUT/review.md"
