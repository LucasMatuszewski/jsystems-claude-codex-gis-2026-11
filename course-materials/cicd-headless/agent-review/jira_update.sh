#!/usr/bin/env bash
# Adds the review as a Jira comment on the issue named in the branch and,
# optionally, moves the issue to another status.
#
# Needs JIRA_BASE_URL (https://your-site.atlassian.net), JIRA_EMAIL and
# JIRA_API_TOKEN (id.atlassian.com > Security > API tokens). Optional
# JIRA_TRANSITION, e.g. "In Review" (the transition name shown in Jira).
#
# Usage: bash jira_update.sh .agent-review/review.md
set -euo pipefail

FILE="${1:?Usage: jira_update.sh <markdown-file>}"
BRANCH="${CI_COMMIT_REF_NAME:-${BITBUCKET_BRANCH:-${SYSTEM_PULLREQUEST_SOURCEBRANCH:-$(git rev-parse --abbrev-ref HEAD)}}}"
KEY="$(grep -oE '[A-Z][A-Z0-9]+-[0-9]+' <<<"$BRANCH" | head -1 || true)"
if [[ -z "$KEY" ]]; then
  echo "No Jira key in branch name '$BRANCH'; skipping" >&2
  exit 0
fi

API="$JIRA_BASE_URL/rest/api/2/issue/$KEY"
AUTH=(-u "$JIRA_EMAIL:$JIRA_API_TOKEN" -H "Content-Type: application/json")

# API v2 accepts a plain-text comment; v3 would require Atlassian Document Format.
jq -Rs '{body: .}' "$FILE" | curl -fsS -X POST "${AUTH[@]}" --data @- "$API/comment" > /dev/null
echo "Comment added to $KEY"

if [[ -n "${JIRA_TRANSITION:-}" ]]; then
  ID="$(curl -fsS "${AUTH[@]}" "$API/transitions" |
        jq -r --arg n "$JIRA_TRANSITION" '.transitions[] | select(.name == $n) | .id' | head -1)"
  if [[ -z "$ID" ]]; then
    echo "Transition '$JIRA_TRANSITION' not available for $KEY; status unchanged" >&2
    exit 0
  fi
  jq -n --arg id "$ID" '{transition: {id: $id}}' |
    curl -fsS -X POST "${AUTH[@]}" --data @- "$API/transitions" > /dev/null
  echo "$KEY moved to '$JIRA_TRANSITION'"
fi
