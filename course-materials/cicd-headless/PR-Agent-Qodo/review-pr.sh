#!/usr/bin/env bash
# Portable community PR-Agent launcher: any CI system or a local shell with Docker.
# Execute from trusted CI configuration. See README.md for the variables.
set -euo pipefail

command_name="${1:-review}"
case "$command_name" in
  review|describe|improve) ;;
  *) printf 'Allowed commands: review, describe, improve\n' >&2; exit 2 ;;
esac

# Model endpoint: any OpenAI-compatible API. Defaults target OpenRouter.
REVIEW_API_BASE="${REVIEW_API_BASE:-https://openrouter.ai/api/v1}"
REVIEW_MODEL="${REVIEW_MODEL:-openai/gpt-6-luna}"
REVIEW_MAX_TOKENS="${REVIEW_MAX_TOKENS:-250000}"
# Dry run by default: the review is printed in the log and nothing is posted.
# Set REVIEW_PUBLISH=true to publish the comment on the pull request.
REVIEW_PUBLISH="${REVIEW_PUBLISH:-false}"
REVIEW_REASONING_EFFORT="${REVIEW_REASONING_EFFORT:-low}"

: "${PR_AGENT_IMAGE:?Set an approved digest-pinned PR-Agent CLI image}"
: "${GIT_PLATFORM:?Set github, gitlab, bitbucket, bitbucket_server, azure or gitea}"
: "${PR_URL:?Set the full PR URL from trusted job metadata}"
: "${REVIEW_API_KEY:?Inject the API key of the model endpoint}"
if [[ ! "$PR_AGENT_IMAGE" =~ @sha256:[a-f0-9]{64}$ ]]; then
  printf 'PR_AGENT_IMAGE must end with @sha256:<64 hex characters>\n' >&2
  exit 2
fi
if [[ ! "$REVIEW_API_BASE" =~ ^https://[A-Za-z0-9.-]+(:[0-9]+)?(/[A-Za-z0-9._/-]*)?$ ]]; then
  printf 'REVIEW_API_BASE must be an HTTPS URL without query or credentials\n' >&2
  exit 2
fi
if [[ ! "$REVIEW_MODEL" =~ ^[A-Za-z0-9._:/-]+$ ]]; then
  printf 'REVIEW_MODEL must be the model ID exactly as the endpoint expects it\n' >&2
  exit 2
fi
if [[ ! "$REVIEW_MAX_TOKENS" =~ ^[1-9][0-9]{3,6}$ ]] || (( REVIEW_MAX_TOKENS > 1050000 )); then
  printf 'REVIEW_MAX_TOKENS must be a whole number of tokens between 1000 and 1050000\n' >&2
  exit 2
fi
case "$REVIEW_PUBLISH" in
  true|false) ;;
  *) printf 'REVIEW_PUBLISH must be true or false\n' >&2; exit 2 ;;
esac
case "$REVIEW_REASONING_EFFORT" in
  none|minimal|low|medium|high) ;;
  *) printf 'REVIEW_REASONING_EFFORT must be none, minimal, low, medium or high\n' >&2; exit 2 ;;
esac

# PR-Agent reads the key from OPENAI__KEY. The "openai/" prefix selects its
# OpenAI-compatible client, which sends REVIEW_MODEL to REVIEW_API_BASE.
export OPENAI__KEY="$REVIEW_API_KEY"
model="openai/$REVIEW_MODEL"

args=(run --rm --cap-drop ALL --security-opt no-new-privileges
  --env "CONFIG__GIT_PROVIDER=$GIT_PLATFORM"
  --env "CONFIG__MODEL=$model"
  --env "OPENAI__API_BASE=$REVIEW_API_BASE"
  --env 'CONFIG__FALLBACK_MODELS=[]'
  --env "CONFIG__CUSTOM_MODEL_MAX_TOKENS=$REVIEW_MAX_TOKENS"
  --env "CONFIG__MAX_MODEL_TOKENS=$REVIEW_MAX_TOKENS"
  --env 'CONFIG__RESTRICTED_MODE=true'
  --env 'CONFIG__PROPAGATE_TOOL_ERRORS=true'
  --env 'CONFIG__OUTPUT_RUN_DETAILS=true'
  --env "CONFIG__PUBLISH_OUTPUT=$REVIEW_PUBLISH"
  --env 'PR_REVIEWER__PERSISTENT_COMMENT=true'
  --env 'PR_REVIEWER__INLINE_KEY_ISSUES=false'
  --env 'PR_REVIEWER__NUM_MAX_FINDINGS=5'
  --env 'PR_REVIEWER__ENABLE_LARGE_PR_CHUNKING=true'
  --env 'PR_REVIEWER__MAX_NUMBER_OF_CALLS=4'
  --env 'PR_DESCRIPTION__PUBLISH_DESCRIPTION_AS_COMMENT=true'
  --env "CONFIG__NO_TEMPERATURE_MODELS=[\"$model\"]"
  --env OPENAI__KEY --entrypoint python)

# Reasoning models (gpt-6-luna and similar) reject PR-Agent's default temperature,
# so temperature is never sent. Reasoning effort is sent unless REVIEW_REASONING_EFFORT=none;
# use none for a model that does not accept the parameter.
if [[ "$REVIEW_REASONING_EFFORT" != none ]]; then
  args+=(--env "CONFIG__REASONING_EFFORT=$REVIEW_REASONING_EFFORT"
    --env "CONFIG__ADDITIONAL_REASONING_EFFORT_MODELS=[\"$model\"]")
fi

case "$GIT_PLATFORM" in
  github)
    : "${GITHUB__USER_TOKEN:?Inject a GitHub bot token}"
    server_url="https://github.com"
    args+=(--env GITHUB__USER_TOKEN)
    ;;
  gitlab)
    : "${GITLAB__URL:?Set the GitLab HTTPS base URL}"
    : "${GITLAB__PERSONAL_ACCESS_TOKEN:?Inject a GitLab bot token}"
    server_url="$GITLAB__URL"
    args+=(--env GITLAB__URL --env GITLAB__PERSONAL_ACCESS_TOKEN)
    ;;
  bitbucket)
    : "${BITBUCKET__BEARER_TOKEN:?Inject a Bitbucket Cloud repository access token}"
    server_url="https://bitbucket.org"
    args+=(--env 'BITBUCKET__AUTH_TYPE=bearer' --env BITBUCKET__BEARER_TOKEN)
    ;;
  bitbucket_server)
    : "${BITBUCKET_SERVER__URL:?Set the Bitbucket Server/Data Center HTTPS base URL}"
    : "${BITBUCKET_SERVER__BEARER_TOKEN:?Inject a Bitbucket HTTP access token}"
    server_url="$BITBUCKET_SERVER__URL"
    args+=(--env BITBUCKET_SERVER__URL --env BITBUCKET_SERVER__BEARER_TOKEN)
    ;;
  azure)
    : "${AZURE_DEVOPS__ORG:?Set the Azure DevOps organization URL}"
    : "${AZURE_DEVOPS__PAT:?Inject an Azure DevOps bot PAT}"
    server_url="$AZURE_DEVOPS__ORG"
    args+=(--env AZURE_DEVOPS__ORG --env AZURE_DEVOPS__PAT)
    ;;
  gitea)
    : "${GITEA__URL:?Set the Gitea HTTPS base URL}"
    : "${GITEA__PERSONAL_ACCESS_TOKEN:?Inject a Gitea bot token}"
    server_url="$GITEA__URL"
    args+=(--env GITEA__URL --env GITEA__PERSONAL_ACCESS_TOKEN)
    ;;
  *) printf 'Unsupported provider\n' >&2; exit 2 ;;
esac

# Validate origin and optional server/org path before forwarding credentials.
python3 - "$server_url" "$PR_URL" <<'PY'
import sys
from urllib.parse import urlsplit
base, target = map(urlsplit, sys.argv[1:])
if (base.scheme != 'https' or target.scheme != 'https'
    or base.netloc != target.netloc or base.username or target.username
    or base.query or base.fragment or target.query or target.fragment
    or not target.path.startswith(base.path.rstrip('/') + '/')):
    sys.exit('PR URL must belong to the configured HTTPS Git service')
PY

# Forward secret variable names; no secret values appear in the command line.
docker "${args[@]}" "$PR_AGENT_IMAGE" -m pr_agent.cli --pr_url "$PR_URL" "$command_name"
