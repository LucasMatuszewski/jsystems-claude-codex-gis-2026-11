#!/usr/bin/env bash
# Posts a Markdown file as a pull/merge request comment. Detects the CI from its
# built-in variables; each platform needs one token with PR-comment rights:
#   GitHub Actions   GH_TOKEN (the job's GITHUB_TOKEN with pull-requests: write) + PR_NUMBER
#   GitLab CI        GITLAB_TOKEN - project access token, scope "api", role Reporter+
#   Azure Pipelines  SYSTEM_ACCESSTOKEN mapped from $(System.AccessToken); the build
#                    service needs "Contribute to pull requests" on the repository
#   Bitbucket        BITBUCKET_ACCESS_TOKEN - repository access token with
#                    "pullrequest:write" (app passwords stopped working in July 2026)
#
# Usage: bash post_review_comment.sh .agent-review/review.md
set -euo pipefail

FILE="${1:?Usage: post_review_comment.sh <markdown-file>}"
BODY="$(printf '### Agent review (%s)\n\n' "${AGENT:-agent}"; cat "$FILE")"

if [[ -n "${GITHUB_ACTIONS:-}" ]]; then
  gh pr comment "${PR_NUMBER:?set PR_NUMBER}" --body "$BODY"

elif [[ -n "${CI_MERGE_REQUEST_IID:-}" ]]; then
  curl -fsS -X POST -H "PRIVATE-TOKEN: ${GITLAB_TOKEN:?}" \
    --data-urlencode "body=$BODY" \
    "$CI_API_V4_URL/projects/$CI_PROJECT_ID/merge_requests/$CI_MERGE_REQUEST_IID/notes" > /dev/null

elif [[ -n "${SYSTEM_PULLREQUEST_PULLREQUESTID:-}" ]]; then
  jq -n --arg c "$BODY" '{comments:[{parentCommentId:0,content:$c,commentType:1}],status:1}' |
  curl -fsS -X POST -H "Authorization: Bearer ${SYSTEM_ACCESSTOKEN:?}" -H "Content-Type: application/json" \
    --data @- \
    "${SYSTEM_COLLECTIONURI}${SYSTEM_TEAMPROJECTID}/_apis/git/repositories/${BUILD_REPOSITORY_ID}/pullRequests/${SYSTEM_PULLREQUEST_PULLREQUESTID}/threads?api-version=7.1" > /dev/null

elif [[ -n "${BITBUCKET_PR_ID:-}" ]]; then
  jq -n --arg c "$BODY" '{content:{raw:$c}}' |
  curl -fsS -X POST -H "Authorization: Bearer ${BITBUCKET_ACCESS_TOKEN:?}" -H "Content-Type: application/json" \
    --data @- \
    "https://api.bitbucket.org/2.0/repositories/$BITBUCKET_WORKSPACE/$BITBUCKET_REPO_SLUG/pullrequests/$BITBUCKET_PR_ID/comments" > /dev/null

else
  echo "No pull request detected; review stays in $FILE" >&2
  exit 0
fi
echo "Comment posted"
