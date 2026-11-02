#!/usr/bin/env bash
# Pre-tool hook for Copilot CLI, Claude Code and Codex: blocks any tool call
# whose input mentions a secrets file (.env, secrets/, private SSH keys, .pem).
# .env.example, .env.sample and .env.template stay allowed.
#
# All three tools send the planned tool call as JSON on stdin and treat
# exit code 2 as "deny". Copilot reads the reason from stdout JSON,
# Claude Code and Codex read it from stderr, so the script writes both.

payload="$(cat)"

# Drop allowed template names first, then look for protected paths.
checked="$(printf '%s' "$payload" | sed -E 's/\.env\.(example|sample|template)//g')"
pattern='(^|[^A-Za-z0-9_-])\.env([^A-Za-z0-9_-]|\.[A-Za-z0-9_-]+|$)|(^|[^A-Za-z0-9_.-])secrets(/|\\\\)|id_(rsa|ed25519|ecdsa)|\.pem([^A-Za-z0-9]|$)'

if printf '%s' "$checked" | grep -Eq "$pattern"; then
  reason="Blocked by block-secrets hook: this call touches a secrets file (.env, secrets/, SSH key or .pem). Use .env.example or ask the user."
  printf '{"permissionDecision":"deny","permissionDecisionReason":"%s"}\n' "$reason"
  printf '%s\n' "$reason" >&2
  exit 2
fi
exit 0
