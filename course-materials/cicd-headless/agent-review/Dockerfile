# CI image with four coding-agent CLIs for headless code and security reviews.
#
# Debian slim instead of Alpine: the CLIs and their bundled tools (ripgrep,
# native helpers, optional Playwright) expect glibc and bash; on Alpine (musl)
# some of them fail or need extra compatibility packages.
#
# Build and push once, then use it as the job image in any CI:
#   docker build -t registry.example.com/agent-ci:1 .
#   docker push registry.example.com/agent-ci:1
FROM node:24-bookworm-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      git curl jq ripgrep python3 ca-certificates openssh-client \
 && rm -rf /var/lib/apt/lists/* \
 && git config --system --add safe.directory '*'

# Pinned versions: reviews stay reproducible; bump them deliberately.
ARG COPILOT_VERSION=1.0.88
ARG CLAUDE_CODE_VERSION=2.1.283
ARG CODEX_VERSION=0.165.0
ARG OPENCODE_VERSION=1.18.32
RUN npm install -g \
      @github/copilot@${COPILOT_VERSION} \
      @anthropic-ai/claude-code@${CLAUDE_CODE_VERSION} \
      @openai/codex@${CODEX_VERSION} \
      opencode-ai@${OPENCODE_VERSION} \
 && npm cache clean --force

# No auto-updates or telemetry prompts inside CI.
ENV CI=true \
    COPILOT_AUTO_UPDATE=false \
    DISABLE_AUTOUPDATER=1

WORKDIR /workspace
