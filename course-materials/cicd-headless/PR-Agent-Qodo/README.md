# PR-Agent (Qodo) exercise: AI code review in your CI/CD

In this exercise you add an AI reviewer to pull requests on the platform you actually use at work. The same reviewer, the same four variables and the same model run on every platform in this folder; only the pipeline file differs.

Checked on **3 October 2026** against [release v0.47.0](https://github.com/The-PR-Agent/pr-agent/releases/tag/v0.47.0), source commit `8e5a9295973b24af4b70cafd0b660a230811ef9e`, and the published Docker manifests.

## PR-Agent and Qodo: two different things

**PR-Agent** started as Qodo's open-source code review agent. Qodo handed it over to the community on 23 April 2026 ([announcement](https://www.qodo.ai/blog/qodo-is-handing-pr-agent-over-to-the-community/)). It now lives at [The-PR-Agent/pr-agent](https://github.com/The-PR-Agent/pr-agent) under the MIT licence, with [community documentation](https://docs.pr-agent.ai/). You run it yourself and bring your own model API key.

**[Qodo](https://www.qodo.ai/)** is the company's commercial review platform. It continues separately, with its own hosted features and pricing.

Old `qodo-ai/pr-agent` links redirect to the community repository. Everything in this folder uses community PR-Agent; nothing here needs a Qodo account. Documentation for commercial features (for example `/test`) is not a promise about the community tool.

For the full comparison, deployment architecture, security, review quality and older-server compatibility, read the [AI-assisted pull requests and code reviews handbook](../../Research/ai-assisted-pull-requests-course-handbook.md).

## The exercise

**Goal:** a pull request with a deliberate defect gets a review comment from PR-Agent that names the defect, and the comment is updated after you push the fix.

### 1. Pick your path

Use the platform you work on. If you cannot add pipelines or secrets there (in many companies only DevOps can), use **GitHub Actions in your own fork** of the course repository: it needs nothing but a GitHub account. If you do not want to use any CI at all, run the review from your own machine.

| Your platform | File | Run by the course on a live system? |
|---|---|---|
| GitHub (recommended fallback) | [github-actions.yml](github-actions.yml) | Same structure as the live-tested [Azure variant](../github-actions/README.md); this OpenAI-compatible variant was not run on GitHub |
| GitLab.com / Self-Managed | [gitlab-ci.yml](gitlab-ci.yml) | **Yes**, self-managed GitLab 19.5.3 with a Docker runner, 30.10.2026 (see [Tested on GitLab](#tested-on-gitlab-setup-and-an-example-review)) |
| Bitbucket Cloud | [bitbucket-pipelines.yml](bitbucket-pipelines.yml) | No |
| Azure DevOps (Azure Repos Git) | [azure-pipelines.yml](azure-pipelines.yml) | No |
| Jenkins + Bitbucket Server / Data Center | [Jenkinsfile](Jenkinsfile) with [review-pr.sh](review-pr.sh) | No |
| Bamboo + Bitbucket Server / Data Center | [bamboo-specs.yaml](bamboo-specs.yaml) with [review-pr.sh](review-pr.sh) | No |
| Gitea / Forgejo | [gitea-actions.yml](gitea-actions.yml) | No |
| No CI at all (your machine + Docker) | [review-pr.sh](review-pr.sh), see [Local run](#local-run-no-ci-needed) | **Yes**, against a GitHub PR through OpenRouter |

"No" means the file was written from the PR-Agent v0.47.0 documentation and checked for syntax, and the launcher it shares was tested, but nobody ran it on that platform. Expect to adjust it, and tell the trainer what you had to change.

### 2. Set the model endpoint

Every file reads the same variables. The defaults point at [OpenRouter](https://openrouter.ai/) and `gpt-6-luna`, so with the trainer's course key you only set one secret.

| Variable | Required | Default | Meaning |
|---|---|---|---|
| `REVIEW_API_KEY` | yes, as a **secret** | - | API key of the model endpoint |
| `REVIEW_API_BASE` | no | `https://openrouter.ai/api/v1` | Any OpenAI-compatible endpoint |
| `REVIEW_MODEL` | no | `openai/gpt-6-luna` | Model ID exactly as that endpoint expects it |
| `REVIEW_MAX_TOKENS` | no | `250000` | Input token budget per model call |

The endpoint is a variable, so the same pipeline works with another provider:

| Provider | `REVIEW_API_BASE` | `REVIEW_MODEL` |
|---|---|---|
| OpenRouter (default) | `https://openrouter.ai/api/v1` | `openai/gpt-6-luna` |
| OpenAI directly | `https://api.openai.com/v1` | `gpt-6-luna` |
| Azure OpenAI (v1 API) | `https://YOUR-RESOURCE.openai.azure.com/openai/v1` | your **deployment name** |
| Any other OpenAI-compatible gateway | its `/v1` base URL | its model ID |

Only the OpenRouter row was run by the course. For Azure with the native deployment configuration (resource root URL, separate deployment and API version), use the live-tested [Azure workflow](../github-actions/README.md) instead.

How the variables reach PR-Agent: the key becomes `OPENAI__KEY`, the base URL becomes `OPENAI__API_BASE`, and the model becomes `CONFIG__MODEL=openai/<REVIEW_MODEL>`. The `openai/` prefix tells PR-Agent to use its OpenAI-compatible client; with OpenRouter the full value is therefore `openai/openai/gpt-6-luna`, which is correct.

**About the key.** Put it only in your platform's secret store. Never in a file, a commit, a PR comment or a chat. A key shared by the trainer is for the course only and is revoked afterwards.

### 3. Add the pipeline

Open the file for your platform; its header comment lists the secrets and where the file goes. The details that differ:

- **GitHub:** copy `github-actions.yml` to `.github/workflows/pr-agent-review.yml` on the default branch of your fork. Add the secret under **Settings → Secrets and variables → Actions**. Secrets are not inherited by forks.
- **GitLab:** merge `gitlab-ci.yml` into `.gitlab-ci.yml`. Needs GitLab **15.7+** and a bot token in `GITLAB__PERSONAL_ACCESS_TOKEN`; `CI_JOB_TOKEN` cannot write merge request comments. The job is manual and advisory.
- **Bitbucket Cloud:** merge into `bitbucket-pipelines.yml`. Use a repository access token in `BITBUCKET__BEARER_TOKEN`; app passwords are not a setup option.
- **Azure DevOps:** create the variable group `pr-agent`, then add the pipeline as **Build Validation** on the target branch. YAML `pr:` triggers do not fire for Azure Repos Git.
- **Jenkins / Bamboo:** the CI server only launches `review-pr.sh`. Install a reviewed copy of the script on the agent; do not run the one from the pull request branch. For Bamboo, copy `bamboo-specs.yaml` to `bamboo-specs/bamboo.yaml` in the repository root (the only path Bamboo scans) and give the agents that have Docker the `pr-agent-review` capability.
- **Gitea:** copy to `.gitea/workflows/pr-agent-review.yml`. The runner needs Docker.

### Tested on GitLab: setup and an example review

The GitLab job was run end to end on 2026-10-30 on a self-managed GitLab 19.5.3 with a Docker runner, in a Java course project with Checkstyle and unit-test jobs before it.

- **Variables** (project **Settings → CI/CD → Variables**, type Variable, scope `*`, **Masked and hidden**, expansion off): `REVIEW_API_KEY` (an OpenRouter key with a spend limit) and `GITLAB__PERSONAL_ACCESS_TOKEN` (a project access token from **Settings → Access tokens**: Developer role, `api` scope, with expiry; its identity becomes the comment author). On a self-managed server an administrator can set `REVIEW_API_KEY` once under **Admin → Settings → CI/CD → Variables**; a project variable with the same name takes precedence. Keep the bot token project-specific.
- **Protect variable:** leave it unchecked if reviews run from ordinary feature branches; protected variables reach only protected branches.
- **Job behaviour:** manual and advisory (`allow_failure: true`), only for merge requests from the same project; it ignores repository settings files, so the reviewed branch cannot change the reviewer.
- **What the reviewer found in its own setup:** in same-project merge requests any pipeline job can read the CI variables, so the manual rule on the review job does not protect the key or the token. Restrict who can push and run pipelines, or use protected branches for the variables.

![PR-Agent review comment on a GitLab merge request: estimated effort, a security concern about CI variables exposed to same-project merge request pipelines, and the focus area Secret Exposure](gitlab-pr-agent-review-2026-10-30.png)

### 4. Prove it works

1. Create a branch with a small, deliberate defect. A good one: an authorization check with the condition inverted, or an off-by-one in a loop.
2. Open a pull request (not a draft) inside your own repository or fork.
3. Wait for the pipeline, then read the review comment. A green job is not the result; the comment is.
4. Push a commit that fixes the defect and confirm the same comment is updated instead of a second one appearing.

**Done when:** the review names your defect, the run details show the model you configured, and the comment changed after the fix.

**Then discuss:** what did the reviewer miss? What would it cost per month on your team's PR volume? Who may edit the pipeline file, and what could they do with the key?

## Local run (no CI needed)

With Docker and a token for your Git host, [review-pr.sh](review-pr.sh) runs the same review from your shell. This is also the fastest way to try a setting before putting it in a pipeline.

```bash
export PR_AGENT_IMAGE='pragent/pr-agent:0.47.0@sha256:7d98954c29289846a08faf00aaea0f1f1375b1676cd8a2ed303e0af07010af7a'
export GIT_PLATFORM=github
export PR_URL='https://github.com/YOUR-ACCOUNT/YOUR-REPO/pull/1'
# REVIEW_API_KEY and GITHUB__USER_TOKEN: set them in your shell from your secret store.
bash review-pr.sh review
```

The launcher is a dry run by default: it prints the review in the log and posts nothing. Add `export REVIEW_PUBLISH=true` to post the comment on the pull request. `GIT_PLATFORM` accepts `github`, `gitlab`, `bitbucket`, `bitbucket_server`, `azure` and `gitea`, each with its own credential variables (the script names the missing one). The script validates the image digest, the endpoint URL and that the PR URL belongs to the configured Git host before it forwards any credential, and it forwards secret variable **names**, never values, on the command line.

Example non-secret configuration for Bitbucket Server/DC:

```bash
export GIT_PLATFORM=bitbucket_server
export BITBUCKET_SERVER__URL='https://bitbucket.example.com'
export PR_URL='https://bitbucket.example.com/projects/COURSE/repos/demo/pull-requests/7'
# REVIEW_API_KEY and BITBUCKET_SERVER__BEARER_TOKEN are injected by CI.
bash review-pr.sh review
```

## Reference

### Git hosts, providers and credentials

| Git host | Provider | Credential variables |
|---|---|---|
| GitHub.com | `github` | Action: `GITHUB_TOKEN`; CLI: `GITHUB__USER_TOKEN` |
| GitLab.com / Self-Managed | `gitlab` | `GITLAB__URL`, `GITLAB__PERSONAL_ACCESS_TOKEN` |
| Bitbucket Cloud | `bitbucket` | `BITBUCKET__AUTH_TYPE=bearer`, `BITBUCKET__BEARER_TOKEN` |
| Bitbucket Server / Data Center | `bitbucket_server` | `BITBUCKET_SERVER__URL`, `BITBUCKET_SERVER__BEARER_TOKEN` |
| Azure Repos Git | `azure` | `AZURE_DEVOPS__ORG`, `AZURE_DEVOPS__PAT` |
| Gitea / Forgejo | `gitea` | `GITEA__URL`, `GITEA__PERSONAL_ACCESS_TOKEN` |

The provider selects the Git API adapter; CI only launches it. That is why Jenkins and Bamboo need no PR-Agent plugin, and why PR-Agent's documentation has no Bamboo page. Bitbucket Cloud and Server/DC have different URLs and credentials. Tools, summary comments, inline findings and suggestions have different support across providers. Start with a summary, then check the [provider matrix](https://docs.pr-agent.ai/overview/supported_platforms/) for the selected feature.

PR-Agent also documents Gerrit and AWS CodeCommit; they are not covered here.

### Model settings that matter

- **Token budget.** PR-Agent's own default is 32,000 input tokens. On a large PR that reviews a small slice and lists the rest under "Review coverage" as skipped. The examples set `250000` and enable chunking with up to 4 calls, which covers about 1M tokens of diff.
- **Why 250,000 and not 1M.** `gpt-6-luna` accepts about 1.05M tokens, but a request above 272k input tokens is billed on the long-context meter (reported as about 2x input and 1.5x output for the whole request). Staying under that line keeps large reviews at the normal rate. Set `REVIEW_MAX_TOKENS` higher if you prefer one call that sees the whole PR.
- **Temperature and reasoning.** `gpt-6-luna` rejects PR-Agent's default temperature while reasoning is active. The examples therefore add the model to PR-Agent's no-temperature list and send `reasoning_effort=low`. A model that does not accept a reasoning parameter needs that setting removed (in `review-pr.sh`: `REVIEW_REASONING_EFFORT=none`).
- **Fallbacks are empty** and `CONFIG__PROPAGATE_TOOL_ERRORS=true`, so an unavailable model fails visibly instead of silently using another one. An AI error does not prove that a PR has no defects.
- API billing is separate from any coding CLI subscription.

### Review, describe, improve and slash commands

`review`, `describe` and `improve` are CLI commands. `/review`, `/describe`, `/improve` and `/ask` are comment commands **only when an event listener is deployed**. GitLab, Bitbucket, Azure and Gitea pipeline runs can publish comments, but they do not listen for slash commands in comments; add an authenticated webhook service separately for that. The GitHub workflow includes the `issue_comment` integration and limits it to users with write, maintain or admin permission.

The examples run `review` only. Add explicit `describe` or `improve` calls after checking the platform's support and permissions; each one is another model call.

### What changed from the historical Qodo workflow

The older Anthropic workflow is kept as [../github-actions/qodo-pr-agent-review.yml](../github-actions/qodo-pr-agent-review.yml) for existing course links.

- Its filename is preserved, but its title and runtime identify community PR-Agent.
- Automatic runs use the versioned, digest-pinned **GitHub Action image**. The upstream `The-PR-Agent/pr-agent@v0.47.0` action references rolling `pragent/pr-agent:github_action`; pinning only its Git ref does not pin the container. The examples pin both the runtime version and digest.
- `workflow_dispatch` requires a PR number and invokes the **CLI** explicitly. The v0.47.0 action runner has no `workflow_dispatch` event handler, so a manual dispatch alone does not review a PR.
- `synchronize` uses the current push-trigger configuration with explicit commands. Automatic opening/reopening and maintainer comment commands use the action runner.
- Current spelling is `committable_code_suggestions`; the older `commitable_code_suggestions` alias is deprecated. Old settings absent from the current configuration, including suggestion checkboxes, wiki tracking and `suggestions_depth`, were removed.
- GitHub uses `contents: read`, `issues: write` and `pull-requests: write`; description output is a comment, and restricted mode blocks elevated operations. No local checkout is required.

### Reproducible runtime

The CLI image is:

```text
pragent/pr-agent:0.47.0@sha256:7d98954c29289846a08faf00aaea0f1f1375b1676cd8a2ed303e0af07010af7a
```

The GitHub Action image is:

```text
pragent/pr-agent:0.47.0-github_action@sha256:31b9aac6ab067bada9a0c1b001d30ebc500ea4487e00a93c18c59b9ef5fa66db
```

These are multi-platform manifest digests inspected in the public registry on 2 October 2026. Recheck the release, changelog, dependency policy and digest when upgrading. A tag or GitHub Action image is not interchangeable with a CLI image: the CLI image has an entrypoint. The examples clear or override that entrypoint and run `python -m pr_agent.cli` from `/app`.

### Credentials and trusted execution

Use a dedicated bot. Grant API read and comment/label permissions for the enabled outputs. Writing a description, approving a PR, pushing a branch and merging are separate operations; do not grant them merely because the reviewer can comment.

Keep the model endpoint out of anything a pipeline user can set at run time. Whoever can change `REVIEW_API_BASE` for a run receives the API key, because the reviewer sends the key to that address. That is why the Jenkins and Bamboo examples fix the endpoint in the pipeline definition and do not expose it as a build parameter or plan variable. On GitLab, restrict who may override pipeline variables; on GitHub, repository variables can be changed only by people who can already read the secret's use.

Protect the pipeline definition, `.pr_agent.toml` on the default branch, model routing and prompts. A contributor who can edit a secret-bearing pipeline can exfiltrate its secrets even if the job has no checkout. The direct YAML examples are for an approved internal training repository; use a trusted external pipeline/template or webhook controller before accepting untrusted branches or forks. In Jenkins and Bamboo, the installed launcher and pipeline definition must come from trusted configuration, not from the pull request. Do not disable TLS verification for self-managed hosts.

## Verification

Offline launcher tests:

```bash
python3 -m unittest discover -s course-materials/cicd-headless/PR-Agent-Qodo -p 'test_*.py' -v
bash -n course-materials/cicd-headless/PR-Agent-Qodo/review-pr.sh
```

The tests execute the real shell wrapper with a synthetic Docker executable and cover provider routing for all six providers, the endpoint and model variables, CLI arguments, secret-name forwarding and rejection before execution. They also parse every pipeline file and check that each one uses the shared variables and the pinned image.

Live evidence, 3 October 2026: `review-pr.sh` reviewed a GitHub pull request through OpenRouter with `openai/gpt-6-luna` as a dry run (one model call, completed). The first attempt failed with "doesn't support temperature=0.2 while reasoning is active", which is why the no-temperature setting is in every file. **No other platform file in this folder has been run on its platform.**

Before adoption on any host, run one synthetic PR: confirm a comment appears; introduce and fix a real defect; rerun; inspect comment persistence, bot identity, diff coverage and error behaviour. Do not treat passing launcher tests as platform integration evidence.

## Primary sources

- [v0.47.0 action runner](https://github.com/The-PR-Agent/pr-agent/blob/v0.47.0/pr_agent/servers/github_action_runner.py), [configuration](https://github.com/The-PR-Agent/pr-agent/blob/v0.47.0/pr_agent/settings/configuration.toml), [Docker entrypoints](https://github.com/The-PR-Agent/pr-agent/blob/v0.47.0/docker/Dockerfile), [release image publishing](https://github.com/The-PR-Agent/pr-agent/blob/v0.47.0/.github/workflows/publish.yml)
- [Changing a model, OpenAI-compatible endpoints and OpenRouter](https://docs.pr-agent.ai/usage-guide/changing_a_model/)
- [GitHub integration](https://docs.pr-agent.ai/installation/github/), [CLI and local installation](https://docs.pr-agent.ai/installation/locally/)
- [GitLab integration](https://docs.pr-agent.ai/installation/gitlab/), [Bitbucket Cloud and Server/DC](https://docs.pr-agent.ai/installation/bitbucket/), [Azure DevOps integration](https://docs.pr-agent.ai/installation/azure/), [Gitea integration](https://docs.pr-agent.ai/installation/gitea/)
- [Qodo](https://www.qodo.ai/) and the [handover announcement](https://www.qodo.ai/blog/qodo-is-handing-pr-agent-over-to-the-community/)
