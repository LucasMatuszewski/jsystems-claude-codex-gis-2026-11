# Codex headless review in Bitbucket Cloud with Jira Cloud

Checked on **2 October 2026** against local Codex CLI **0.160.0**, [Codex non-interactive documentation](https://developers.openai.com/codex/noninteractive/), and the Atlassian REST APIs. This example runs Codex directly and uses our Python REST adapter for context and publication.

The example targets **Bitbucket Cloud + Jira Cloud**. Bitbucket Server/Data Center uses `/rest/api/1.0/...`; Jira Data Center uses its own API/authentication. Those require separate adapters. For the broader cross-platform comparison, read the [AI-assisted PR handbook](../../Research/ai-assisted-pull-requests-course-handbook.md).

## Flow

1. **Collect:** read PR metadata, source/destination commit hashes, paginated changed-file metadata and the PR diff. Find one Jira key in the title/source branch, check its allowed project, confirm the configured shared audience and unrestricted issue security, then use only ticket summary, description and status. Save `context.json`.
2. **Analyze:** run `codex exec` in a fresh directory with a read-only sandbox, all agent tools disabled, a trusted prompt and JSON output schema. Pass only the supplied diff/ticket context and model credential. Validate the final response and save `review.json`.
3. **Publish:** validate the report and PR identity; recheck both current commit hashes; create or update the bot's Bitbucket summary comment and Jira comment. Jira API v3 comments use Atlassian Document Format (ADF).

The publisher chooses destinations from validated CI metadata, not model output. It updates only comments matching both the stable marker and configured bot identity. Jira keys must be unambiguous, belong to `JIRA_PROJECT_KEYS`, and match a trusted PR-to-issue mapping. If no key is found, review continues without Jira context/publication; if a linked ticket cannot be fetched, collection fails.

This is a diff review, not a full repository investigation. No repository checkout, build scripts or tests are executed. The agent must report that limitation. It does not approve, merge, push or transition tickets.

## Install the trusted runtime

Build from this directory:

```bash
docker build -t registry.example.com/course-codex-review:0.160.0 .
docker run --rm registry.example.com/course-codex-review:0.160.0 codex --version
docker push registry.example.com/course-codex-review:0.160.0
```

Replace the example registry reference in [bitbucket-pipelines.yml](bitbucket-pipelines.yml) with your actual registry image, preferably pinned to its digest. Configure pull credentials for a private registry. The image installs the pinned CLI and trusted [review.py](review.py), [prompt](prompt.md) and [schema](review.schema.json). These files are executed from `/opt/reviewer`, never from the reviewed PR.

Merge the pipeline example into the repository's `bitbucket-pipelines.yml`. It disables clone and uses three sequential steps with artifacts passed between them. Create three deployment environments in the order shown; configure their permissions and environment types/order as required by your Bitbucket workspace.

## Variables and permissions

Set non-secret `JIRA_PROJECT_KEYS` (e.g. `COURSE,SHOP`) as a repository variable. Configure `JIRA_PR_ISSUE_MAP` in the trusted context and publication environments, e.g. `{"training/demo#7":"COURSE-42"}`. The key is `workspace/repository#PR-number`; the value is the authorized Jira issue. The PR title/branch may suggest a ticket, but cannot authorize reading or commenting on it. An administrator or trusted webhook/orchestrator must confirm the association and inject this map before the run; do not construct it from the same contributor-controlled title/branch. A missing or mismatched association fails before ticket access. For automated use, resolve the association in your trusted integration service and supply a one-entry map for the triggering PR.

Before enabling Jira context, an administrator must verify that every reader of this Bitbucket repository can also read the selected Jira project. Set `JIRA_SHARED_AUDIENCE_PROJECT_KEYS` only for projects whose audience has been verified for this repository. An empty/missing value blocks linked-ticket collection and publication; the ordinary project allowlist is not sufficient. Public repositories require ticket content approved for public disclosure. The adapter also rejects non-null or missing issue-security metadata and rechecks identity/security after comment scans immediately before each Bitbucket/Jira write. Returned issue keys must exactly match the authorized key; old aliases of moved issues are refused. This is a trusted administrative assertion, not an automatic ACL comparison; revalidate it when project/repository permissions change. Do not use a broadly privileged bot as evidence of shared visibility.

Scope credentials to the indicated **deployment environment**, rather than exposing them as shared repository variables.

| Environment | Variables | Permissions / purpose |
|---|---|---|
| `review-context` | Secured `BITBUCKET_ACCESS_TOKEN`; `JIRA_BASE_URL`, `JIRA_EMAIL`, secured `JIRA_API_TOKEN` | Bitbucket repository/PR read; Jira Browse Projects / issue visibility. Use a repository access token with Bearer auth. |
| `review-analysis` | Secured `CODEX_API_KEY`; `CODEX_MODEL` | Approved OpenAI API model; no Bitbucket/Jira credentials. API usage has its own billing. |
| `review-publish` | Secured `BITBUCKET_ACCESS_TOKEN`; `BITBUCKET_BOT_UUID`; `JIRA_BASE_URL`, `JIRA_EMAIL`, secured `JIRA_API_TOKEN`; `JIRA_BOT_ACCOUNT_ID` | Bitbucket PR comment read/write; Jira Browse Projects, Add Comments and Edit Own Comments. |

Bitbucket supplies `BITBUCKET_WORKSPACE`, `BITBUCKET_REPO_SLUG` and `BITBUCKET_PR_ID` in PR pipeline steps. Do not treat `BITBUCKET_COMMIT` as the PR source SHA: Pipelines can analyze a merge checkout. This adapter obtains source/destination hashes directly from the API. It rejects fork PRs and refuses publication when either revision changes.

`BITBUCKET_ACCESS_TOKEN` is a **repository access token**, sent as `Authorization: Bearer ...`; an Atlassian user API token is a different credential type and may require another authentication scheme. Do not use retired app passwords. Obtain the bot UUID/account ID through your administrators or the relevant authenticated identity API; do not guess them. Use Jira email + an unscoped Cloud API token with the configured site URL for this Basic-auth example. Scoped Jira tokens use different gateway URLs/scopes; adapt and verify that setup separately.

The subprocess receives an explicit environment allowlist and fresh, existing `HOME`/`CODEX_HOME` directories. It uses `--ignore-user-config`, `--ignore-rules`, `--ephemeral`, `--strict-config`, `--sandbox read-only`, `--output-schema` and `-o`. A trusted one-model catalog removes shell, apply-patch and other model capabilities; explicit configuration disables command execution, plugins/apps, delegation, search and auxiliary tools. The resulting model request has `tools: []`, and the dispatcher rejects unexpected shell/apply-patch calls. Read-only sandboxing alone would still allow a shell to read the API key, so it is not the credential boundary. Model stdout/stderr are suppressed; the adapter reports sanitized stage errors. This policy is verified for pinned CLI 0.160.0; rerun the native test before changing that version. The sandbox still needs a supported Linux runner.

## API calls used

| Operation | REST endpoint |
|---|---|
| Read PR and revision | `GET https://api.bitbucket.org/2.0/repositories/{workspace}/{repo}/pullrequests/{id}` |
| Fetch diff | `GET .../pullrequests/{id}/diff` (same-origin API redirect allowed) |
| Check changed files | `GET .../pullrequests/{id}/diffstat`, following pagination |
| Find/create/update PR comment | `GET/POST .../pullrequests/{id}/comments`, `PUT .../comments/{comment_id}` |
| Read ticket | `GET {jira-site}/rest/api/3/issue/{key}?fields=summary,description,status,security` |
| Recheck ticket security before publication | `GET {jira-site}/rest/api/3/issue/{key}?fields=security` |
| Find/create/update ticket comment | `GET/POST .../issue/{key}/comment`, `PUT .../comment/{comment_id}` |

The adapter uses Python's standard library, TLS verification and timeouts. It rejects foreign-origin redirects/pagination before forwarding authorization. Diff responses over 120 KB, API responses over 2 MB, or a patch count different from the changed-file count fail rather than silently truncate. These checks cannot prove that every server-side patch contains every line; large/binary changes still need human inspection.

Findings must point to added new-side lines parsed from the supplied patch. Deleted lines, rename source paths and invented line numbers are rejected. Model fields are rendered in protected text fences and mentions are neutralized before publication; the rendered comment has a 24 KB budget. Configuration, stale revisions, invalid patches, HTTP status and model timeout/exit failures have distinct sanitized diagnostics without response bodies or credentials.

## Run the stages from a trusted runner

With the matching stage credentials injected securely:

```bash
python3 /opt/reviewer/review.py collect --directory review-artifacts
python3 /opt/reviewer/review.py analyze --directory review-artifacts
python3 /opt/reviewer/review.py publish --directory review-artifacts
```

Use the pipeline stages to scope credentials; the three commands illustrate the interface. Do not run them against a real repository as an installation check, because `publish` writes comments.

## Operational limits

- The YAML is an internal training example. A contributor who can replace a credential-bearing pipeline can steal its credentials, regardless of clone settings or deployment separation. For untrusted branches/forks, use an authenticated webhook and a centrally trusted runner/pipeline definition. Restrict deployment access as well.
- Serialize publication per PR in the orchestration layer. Marker-based upsert makes sequential reruns update comments, but simultaneous first runs can create duplicates. Revision and ticket-visibility checks are not atomic with the API write; Jira and Bitbucket offer no cross-system conditional transaction. Keep audience permissions stable during a run and serialize administrative permission changes as well as publication. Both hashes are included in the comment so its reviewed revision remains explicit.
- Bitbucket and Jira writes are not one transaction. A Jira failure after a Bitbucket comment fails the stage; retry updates the Bitbucket comment and retries Jira. Never replace an API/model error with "no findings".
- Artifacts contain source code and selected ticket text. Apply your retention/access policy and approved model/data route; do not publish them as public build artifacts. No real ticket data is included in this course example.
- The Jira comment records the result without automatically changing ticket status. Review output is advisory; existing tests, scanners and human approvals remain separate gates.

## Verification

Run the offline contract suite from the repository root:

```bash
python3 -m unittest discover -s course-materials/cicd-headless/codex-bitbucket -p 'test_*.py' -v
```

Synthetic fixtures exercise context collection, ticket extraction, revision races, partial diffs, paginated bot-comment updates, ADF payloads, invalid findings and removal of publication credentials from the Codex subprocess. External APIs and model execution are replaced in the default suite. The optional native test below runs the installed pinned CLI against a loopback fake Responses server, with a synthetic key; it checks empty tool registration and rejects adversarial tool calls without invoking a paid model.

```bash
RUN_CODEX_NATIVE_TESTS=1 python3 -m unittest discover -s course-materials/cicd-headless/codex-bitbucket -p test_codex_tools.py -v
```

This test requires Codex 0.160.0 on `PATH` and permission to bind a loopback port. **No authenticated Bitbucket/Jira integration, paid model call or container build was performed by the offline suite.**

For a live pilot, build the image and use a disposable same-repository PR with a synthetic Jira ticket: confirm ticket context; verify the two comments; rerun to confirm updates; push a new commit between analysis/publication and verify stale output is refused. Test API/model failures and permissions before enabling automatic runs.

## Primary sources

- [Codex 0.160.0 tool registration](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/core/src/tools/spec_plan.rs) and [static model catalog](https://github.com/openai/codex/blob/rust-v0.160.0/codex-rs/models-manager/src/manager.rs)
- [Codex non-interactive mode](https://developers.openai.com/codex/noninteractive/) and local `codex exec --help` at 0.160.0
- [Bitbucket PR API](https://developer.atlassian.com/cloud/bitbucket/rest/api-group-pullrequests/), [API authentication](https://developer.atlassian.com/cloud/bitbucket/rest/intro/#authentication), [repository access tokens](https://support.atlassian.com/bitbucket-cloud/docs/repository-access-tokens/)
- [Jira issues API](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issues/), [comments and ADF](https://developer.atlassian.com/cloud/jira/platform/rest/v3/api-group-issue-comments/), [Basic authentication](https://developer.atlassian.com/cloud/jira/platform/basic-auth-for-rest-apis/)
