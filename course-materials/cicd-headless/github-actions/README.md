# GitHub review workflows: Community PR-Agent and Azure OpenAI

Use [pr-agent-azure-review.yml](pr-agent-azure-review.yml) for Azure OpenAI with its native deployment configuration. For OpenRouter, OpenAI or any other OpenAI-compatible endpoint, and for other CI platforms, use the [PR-Agent (Qodo) exercise](../PR-Agent-Qodo/README.md). The historical [qodo-pr-agent-review.yml](qodo-pr-agent-review.yml) is a separate Anthropic example; its filename is retained for older course links. Both run **Community PR-Agent v0.47.0**, independently maintained under MIT, rather than commercial Qodo. Activate only one workflow initially to avoid duplicate reviews and charges.

## Prepare Azure first

1. Open Azure AI Foundry with the subscription you intend to bill. Create or select an Azure OpenAI resource and a model deployment. Select an OpenAI model **sold directly by Azure**; Marketplace offers may have different billing and credit eligibility. Check your subscription's credit terms.
2. For this course's pilot, use `gpt-6-luna` if available in your approved region and quota. Create a deployment with a name you choose, e.g. `course-review-luna`. The deployment name and underlying model ID are separate values, even when they happen to match.
3. On the resource's **Keys and Endpoint** page, copy its resource root endpoint and one API key. Never paste the key in a file, commit, PR comment or chat. Verify the resource networking permits your GitHub-hosted runner; private endpoints require a runner with network access.
4. Add the values below in your own repository: **Settings → Secrets and variables → Actions**. Repository variables are suitable for endpoint/deployment/model; only the key must be a secret.

| Kind | Name | Example / purpose |
|---|---|---|
| Secret | `AZURE_OPENAI_API_KEY` | API key of this Azure resource; not an OpenAI Platform key |
| Variable | `AZURE_OPENAI_ENDPOINT` | `https://YOUR-RESOURCE.openai.azure.com` (resource root, without `/openai/v1`, deployment path, or query) |
| Variable | `AZURE_OPENAI_DEPLOYMENT` | `course-review-luna` (exact Azure deployment name) |
| Variable | `PR_AGENT_MODEL` | `gpt-6-luna` (underlying model ID, without `azure/`) |
| Optional variable | `AZURE_OPENAI_API_VERSION` | Default `2025-04-01-preview`, used by this versioned Azure integration |

Azure also offers a current v1 API with `/openai/v1` and no dated `api-version`. This example uses PR-Agent's native Azure deployment configuration instead: `OPENAI__API_TYPE=azure`, root `OPENAI__API_BASE`, separate `OPENAI__DEPLOYMENT_ID`, and a dated API version. Do not mix the two URL conventions. The endpoint variable stays a root URL; the client constructs the deployment request path.

`PR_AGENT_MODEL` configures model capabilities/token counting; `AZURE_OPENAI_DEPLOYMENT` selects the actual billed Azure deployment. They must describe the same model. The workflow adds the chosen model to PR-Agent's reasoning/no-temperature lists. It sets a budget of 250,000 input tokens per model call and reviews a larger diff in up to 4 chunks; PR-Agent's own default of 32,000 made it skip most files of a large PR. A request above 272k input tokens moves `gpt-6-luna` to long-context pricing, which is why the default stays under that line. Lower or raise it with the optional Actions variable `PR_AGENT_MAX_TOKENS` (validated, at most 1,050,000). Fallbacks are disabled, so an unavailable deployment fails instead of using an unexpected provider. Switching models may require different reasoning settings; test the new combination before automatic use.

## Activate and test your fork

1. Fork the course repository and enable Actions in **your fork**. Secrets and variables are not inherited: add all four required values in the fork. GitHub's built-in `GITHUB_TOKEN` is supplied automatically for each job.
2. If the active workflow is not already present, copy `pr-agent-azure-review.yml` to `.github/workflows/pr-agent-azure-review.yml` and commit it to the fork's default branch. Manual dispatch requires the workflow on that branch.
3. Create an open, non-draft PR from a branch **inside your fork**, targeting its default branch. Use a small synthetic change with an intentional defect. PRs from another fork are skipped.
4. Choose **Actions → Community PR-Agent Azure Review → Run workflow**, enter that PR's number, and select the default branch. The preflight fails with a named error if any required key/variable is missing, before a model call. It also rejects non-root endpoints, closed/draft PRs and foreign repository heads.
5. Check both the workflow conclusion and the actual review comment. A successful job alone does not prove the model gave useful feedback. Confirm the defect is identified, the run details show the configured model, and the reviewed commit is current.
6. Fix the defect and push another commit. Confirm the automatic `synchronize` path updates the persistent review comment; then use `/review` with current write/maintain/admin repository permission to check the comment-command path. Existing comments should be updated, not multiplied.

The automatic path uses the digest-pinned GitHub-action image. Manual dispatch uses the matching digest-pinned CLI image because the upstream action runner does not handle `workflow_dispatch`. Initial automatic runs perform only `/review`; `/describe`, `/improve` and `/ask` remain explicit maintainer commands. Comment triggers check the author's current repository permission through the GitHub API; read/triage relationships alone are insufficient. They can add API usage. Neither path checks out or executes reviewed PR code. Job-level concurrency prevents unrelated comments from cancelling active reviews.

The workflow grants read access to repository contents and write access to PR/issue feedback. Repository/global PR-Agent settings and extra repository context are disabled so the example uses the trusted workflow configuration. Model output remains advisory; keep tests, scanners and human approvals.

For the Anthropic example, set secret `ANTHROPIC_API_KEY` and variable `PR_AGENT_MODEL` to an available `anthropic/<model-id>` instead. It performs review, description and suggestions automatically; that consumes more model calls. It also fails fast without the key/model. Do not run both examples with one shared `PR_AGENT_MODEL` value: their model ID formats differ.

## Checks and live evidence

```bash
python3 -m unittest discover -s course-materials/cicd-headless/github-actions -p 'test_*.py' -v
actionlint course-materials/cicd-headless/github-actions/pr-agent-azure-review.yml
```

Offline contracts execute the actual preflight with a fake GitHub CLI and synthetic key. They verify missing credentials/variables, invalid endpoints/PR numbers, and rejection of closed/draft/fork PRs. Live pilot on **2 October 2026**, using an existing `gpt-6-luna` Azure deployment:

- Automatic PR-open run succeeded. The model identified the intentionally inverted owner check in a synthetic authorization fixture (1,634 input / 242 output tokens; one model call).
- Manual dispatch succeeded against the course-material PR. Its 32,000-token budget excluded the long research handbook, and the published review explicitly reported that coverage limit.
- Large-PR run, 3 October 2026: with the 250,000-token budget and chunking, a 438,500-token diff (306 files) was reviewed in 2 calls with no files skipped for budget. With the earlier 32,000 limit the same PR had 261 files skipped.
- Standalone corrected-push run succeeded through the `synchronize` path, with the corrected fixture and persistent review update.
- Maintainer `/review` run succeeded after checking the caller's repository permission. The same review comment was updated after fixing the defect, and the earlier finding moved to resolved history.

The synthetic validation PR is disposable and is not merged. No authenticated Bitbucket/Jira pilot is implied by these GitHub/Azure results. Missing-key failure and read/triage rejection are exercised offline with synthetic inputs; no real secret was removed to run those checks.

## Primary sources

- [Community PR-Agent repository and v0.47.0 release](https://github.com/The-PR-Agent/pr-agent/releases/tag/v0.47.0)
- [PR-Agent Azure configuration template](https://github.com/The-PR-Agent/pr-agent/blob/v0.47.0/pr_agent/settings/.secrets_template.toml) and [GitHub action runner](https://github.com/The-PR-Agent/pr-agent/blob/v0.47.0/pr_agent/servers/github_action_runner.py)
- [Azure OpenAI API lifecycle and URL conventions](https://learn.microsoft.com/en-us/azure/foundry/openai/api-version-lifecycle), [models sold directly by Azure](https://learn.microsoft.com/en-us/azure/foundry/foundry-models/concepts/models-sold-directly-by-azure)
- [GitHub Actions secrets](https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets), [workflow dispatch](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/manually-run-a-workflow)
