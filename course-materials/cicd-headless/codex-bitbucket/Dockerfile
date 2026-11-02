# Build from this folder; publish to your trusted CI registry after verification.
FROM node:24-bookworm-slim
ARG CODEX_VERSION=0.165.0
RUN apt-get update && apt-get install --no-install-recommends -y python3 ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && npm install -g @openai/codex@${CODEX_VERSION}
WORKDIR /opt/reviewer
COPY review.py review.schema.json prompt.md ./
ENTRYPOINT []
CMD ["python3", "/opt/reviewer/review.py", "--help"]
