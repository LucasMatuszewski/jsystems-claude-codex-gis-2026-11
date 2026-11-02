#!/usr/bin/env bash
set -euo pipefail

# Start Copilot CLI in this repository with a small set of pre-approved read-only commands.
repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../../.." && pwd)"
cd "$repo_root"

# Shell rules use trailing :* prefixes (copilot help permissions, CLI 1.0.88).
# Feature pushes may be approved; explicit main/master/prod and force prefixes are denied.
# Bare push, refspec destinations, other remotes/options and later force flags can escape
# these prefixes. GitHub/Bitbucket branch protection is the real guard.
# Source: https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-command-reference#tool-permission-patterns

exec copilot \
  --allow-tool='shell(git status:*)' \
  --allow-tool='shell(git diff:*)' \
  --allow-tool='shell(git log:*)' \
  --allow-tool='shell(git show:*)' \
  --deny-tool='shell(git push origin main:*)' \
  --deny-tool='shell(git push -u origin main:*)' \
  --deny-tool='shell(git push --set-upstream origin main:*)' \
  --deny-tool='shell(git push origin -u main:*)' \
  --deny-tool='shell(git push origin --set-upstream main:*)' \
  --deny-tool='shell(git push origin master:*)' \
  --deny-tool='shell(git push -u origin master:*)' \
  --deny-tool='shell(git push --set-upstream origin master:*)' \
  --deny-tool='shell(git push origin -u master:*)' \
  --deny-tool='shell(git push origin --set-upstream master:*)' \
  --deny-tool='shell(git push origin prod:*)' \
  --deny-tool='shell(git push -u origin prod:*)' \
  --deny-tool='shell(git push --set-upstream origin prod:*)' \
  --deny-tool='shell(git push origin -u prod:*)' \
  --deny-tool='shell(git push origin --set-upstream prod:*)' \
  --deny-tool='shell(git push upstream main:*)' \
  --deny-tool='shell(git push -u upstream main:*)' \
  --deny-tool='shell(git push --set-upstream upstream main:*)' \
  --deny-tool='shell(git push upstream -u main:*)' \
  --deny-tool='shell(git push upstream --set-upstream main:*)' \
  --deny-tool='shell(git push upstream master:*)' \
  --deny-tool='shell(git push -u upstream master:*)' \
  --deny-tool='shell(git push --set-upstream upstream master:*)' \
  --deny-tool='shell(git push upstream -u master:*)' \
  --deny-tool='shell(git push upstream --set-upstream master:*)' \
  --deny-tool='shell(git push upstream prod:*)' \
  --deny-tool='shell(git push -u upstream prod:*)' \
  --deny-tool='shell(git push --set-upstream upstream prod:*)' \
  --deny-tool='shell(git push upstream -u prod:*)' \
  --deny-tool='shell(git push upstream --set-upstream prod:*)' \
  --deny-tool='shell(git push --force:*)' \
  --deny-tool='shell(git push -u --force:*)' \
  --deny-tool='shell(git push --set-upstream --force:*)' \
  --deny-tool='shell(git push origin --force:*)' \
  --deny-tool='shell(git push -u origin --force:*)' \
  --deny-tool='shell(git push --set-upstream origin --force:*)' \
  --deny-tool='shell(git push origin -u --force:*)' \
  --deny-tool='shell(git push origin --set-upstream --force:*)' \
  --deny-tool='shell(git push upstream --force:*)' \
  --deny-tool='shell(git push -u upstream --force:*)' \
  --deny-tool='shell(git push --set-upstream upstream --force:*)' \
  --deny-tool='shell(git push upstream -u --force:*)' \
  --deny-tool='shell(git push upstream --set-upstream --force:*)' \
  --deny-tool='shell(git push -f:*)' \
  --deny-tool='shell(git push -u -f:*)' \
  --deny-tool='shell(git push --set-upstream -f:*)' \
  --deny-tool='shell(git push origin -f:*)' \
  --deny-tool='shell(git push -u origin -f:*)' \
  --deny-tool='shell(git push --set-upstream origin -f:*)' \
  --deny-tool='shell(git push origin -u -f:*)' \
  --deny-tool='shell(git push origin --set-upstream -f:*)' \
  --deny-tool='shell(git push upstream -f:*)' \
  --deny-tool='shell(git push -u upstream -f:*)' \
  --deny-tool='shell(git push --set-upstream upstream -f:*)' \
  --deny-tool='shell(git push upstream -u -f:*)' \
  --deny-tool='shell(git push upstream --set-upstream -f:*)' \
  --deny-tool='shell(git push --force-with-lease:*)' \
  --deny-tool='shell(git push -u --force-with-lease:*)' \
  --deny-tool='shell(git push --set-upstream --force-with-lease:*)' \
  --deny-tool='shell(git push origin --force-with-lease:*)' \
  --deny-tool='shell(git push -u origin --force-with-lease:*)' \
  --deny-tool='shell(git push --set-upstream origin --force-with-lease:*)' \
  --deny-tool='shell(git push origin -u --force-with-lease:*)' \
  --deny-tool='shell(git push origin --set-upstream --force-with-lease:*)' \
  --deny-tool='shell(git push upstream --force-with-lease:*)' \
  --deny-tool='shell(git push -u upstream --force-with-lease:*)' \
  --deny-tool='shell(git push --set-upstream upstream --force-with-lease:*)' \
  --deny-tool='shell(git push upstream -u --force-with-lease:*)' \
  --deny-tool='shell(git push upstream --set-upstream --force-with-lease:*)' \
  --deny-tool='shell(git reset:*)' \
  --deny-tool='shell(git clean:*)' \
  --deny-tool='shell(env:*)' \
  --deny-tool='shell(printenv:*)' \
  --deny-tool='shell(ssh:*)' \
  --deny-tool='shell(scp:*)' \
  --deny-tool='shell(curl:*)' \
  --deny-tool='shell(wget:*)' \
  --deny-tool='write(.env)' \
  --deny-tool='write(.env.local)' \
  "$@"
