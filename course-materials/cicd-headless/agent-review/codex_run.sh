#!/usr/bin/env bash
# Runs one headless Codex task in CI through OpenRouter and writes the final answer to a file.
# Building block for your own agent jobs (MR summary, AGENTS.md check, test gaps, failure triage...).
#
#   OPENROUTER_API_KEY  set by the trainer for the whole instance (masked)
#   MODEL               optional, default openai/gpt-6-luna
#   CODEX_SANDBOX       read-only by default; in a Docker job set danger-full-access (see README)
#
# Usage: bash ci/agent-review/codex_run.sh <prompt-file> <output-file>
set -euo pipefail

PROMPT_FILE="${1:?Usage: codex_run.sh <prompt-file> <output-file>}"
OUT="${2:?Usage: codex_run.sh <prompt-file> <output-file>}"
mkdir -p "$(dirname "$OUT")"
# Read the prompt first: a failed $(cat) inside the codex arguments would not stop set -e and
# would start a paid run with an empty prompt.
PROMPT="$(cat "$PROMPT_FILE")"
[ -n "$PROMPT" ] || { echo "Empty prompt file: $PROMPT_FILE" >&2; exit 1; }

codex exec --sandbox "${CODEX_SANDBOX:-read-only}" --skip-git-repo-check --ephemeral \
  -c model_provider=openrouter \
  -c 'model_providers.openrouter={name="OpenRouter",base_url="https://openrouter.ai/api/v1",env_key="OPENROUTER_API_KEY",wire_api="responses"}' \
  -m "${MODEL:-openai/gpt-6-luna}" \
  -o "$OUT" "$PROMPT" > "$OUT.log"

echo "Result written to $OUT"
