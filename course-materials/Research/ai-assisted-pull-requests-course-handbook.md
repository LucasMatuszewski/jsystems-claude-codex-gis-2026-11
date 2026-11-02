# AI-Assisted Pull Requests and Code Reviews

## Platform-neutral automation with open-source tools

**Participant handbook · Version 1.0 · Research checked: 2 October 2026**

**Companion CI examples:** [community PR-Agent 0.47.0 on GitHub, GitLab, Bitbucket, Azure DevOps, Jenkins, Bamboo and Gitea](../cicd-headless/PR-Agent-Qodo/README.md), and [Codex headless with custom Bitbucket Cloud/Jira Cloud REST publication](../cicd-headless/codex-bitbucket/README.md). The examples document their configuration and offline checks; live integration still needs a pilot on your chosen host.

**Audience:** Developers, technical leads, platform engineers, and security practitioners working across different companies, programming languages, Git hosting platforms, and CI/CD systems.

**Prerequisites:** Basic familiarity with Git branches, commits, pull requests, command-line tools, and CI jobs. The container examples use Bash and a Linux-compatible Docker environment. Your application does not need to use Python or JavaScript simply because a review tool does.

### What this material helps you do

Design an effective pull-request process, automate its repetitive work, and introduce AI review without tying your organization to GitHub or a particular programming language. The main implementation path uses community **PR-Agent**. Alternatives include **AI Review**, **Kodus**, and a custom coding agent combined with **Danger JS** or **reviewdog**.

The process designs, example policies, and exercises are recommendations to adapt-not claims that every organization should use identical merge rules. Product capabilities and licensing are linked to primary sources. Server versions, subscription features, and tool defaults can change: check the exact release you deploy.

> **Lab boundary:** Use a disposable or explicitly approved training repository, synthetic data, restricted bot credentials, and a company-approved model endpoint. The examples are reference configurations, not evidence of successful integration with your company's private infrastructure.

### Learning outcomes

After completing the material, you should be able to:

- Organize small, understandable pull requests with clear ownership and review expectations.
- Distinguish Git hosting, CI execution, AI analysis, and review publication.
- Choose between a ready-made reviewer and a customizable agent workflow.
- Run PR-Agent against a supported self-managed GitLab or Bitbucket Server/Data Center installation.
- Explain how inline comments, summaries, annotations, and merge gates differ.
- Introduce automation with bounded permissions, reliable reruns, and measurable results.

## Contents

1. [The pull-request lifecycle](#1-the-pull-request-lifecycle)
2. [Organizing work for faster reviews](#2-organizing-work-for-faster-reviews)
3. [What to automate-and what to keep human](#3-what-to-automate-and-what-to-keep-human)
4. [A platform-neutral architecture](#4-a-platform-neutral-architecture)
5. [Choosing tools](#5-choosing-tools)
6. [Understanding PR-Agent](#6-understanding-pr-agent)
7. [Lab: PR-Agent on your Git platform](#7-lab-pr-agent-on-your-git-platform)
8. [Running the same workflow in different CI systems](#8-running-the-same-workflow-in-different-ci-systems)
9. [Custom agents with reusable publication tools](#9-custom-agents-with-reusable-publication-tools)
10. [Reliable comments, reruns, and review state](#10-reliable-comments-reruns-and-review-state)
11. [Security review and safe agent execution](#11-security-review-and-safe-agent-execution)
12. [Older servers, CLIs, APIs, and MCP](#12-older-servers-clis-apis-and-mcp)
13. [Beyond review: controlled CI/CD automation](#13-beyond-review-controlled-cicd-automation)
14. [Measuring quality and rolling out](#14-measuring-quality-and-rolling-out)
15. [Exercises and discussion answers](#15-exercises-and-discussion-answers)
16. [Implementation checklist and takeaways](#16-implementation-checklist-and-takeaways)
17. [Primary sources and further reading](#17-primary-sources-and-further-reading)

---

## 1. The pull-request lifecycle

A **pull request (PR)** proposes integrating a change into another branch. GitLab calls the equivalent collaboration object a **merge request (MR)**. This handbook uses "PR" generically. A PR is more than a diff: it is the place where a team explains intent, records evidence, discusses risks, and decides whether a change is ready.

A useful working lifecycle is:

```text
Agree on the problem and acceptance criteria
                    |
Create a focused change and self-review it
                    |
Open a draft PR with context and test evidence
                    |
Run formatting, tests, and security checks
                    |
Run AI review and publish bounded feedback
                    |
Author and human reviewers verify the findings
                    |
Update the change and review the latest revision
                    |
Merge under the team's normal controls
                    |
Deploy, observe, and respond to regressions
```

AI can assist at several stages. It does not replace the underlying agreement about what the change should accomplish.

### Four questions every review should answer

**Does the change solve the intended problem?** A correct implementation of the wrong requirement is still a bad outcome.

**Is the behavior correct and appropriately tested?** Consider normal operation, boundary conditions, failures, and interaction with existing code.

**Is the change safe to operate and maintain?** Think about authorization, data handling, performance, compatibility, migrations, and observability.

**Is the evidence sufficient for this level of risk?** A documentation correction and a payment-processing change should not require identical review effort.

Google's engineering review guidance is a useful baseline: review design, functionality, complexity, tests, naming, comments, and documentation, rather than treating review as a formatting exercise. [Review guidance][google-review]

### Responsibilities remain explicit

| Role | Primary responsibility |
|---|---|
| Author | Explain intent, self-review, provide evidence, and address or discuss findings. |
| Human reviewer | Evaluate correctness and trade-offs; challenge assumptions and decide whether concerns are resolved. |
| Security or domain specialist | Assess changes requiring specialized knowledge or additional authorization. |
| Automation owner | Maintain the bot, integrations, prompts, credentials, costs, and failure handling. |
| AI reviewer | Produce evidence-backed observations and suggestions within its assigned scope. |

The bot should not become the only "person" who understands a change. Name the humans responsible for the merge decision.

## 2. Organizing work for faster reviews

### Prefer coherent changes over arbitrary size limits

A small PR is not merely one with few lines. It should have one understandable purpose and a reviewable set of consequences. Separate unrelated refactoring, formatting, dependency updates, and behavior changes when doing so makes the result easier to reason about. Google's small-change guidance explains why focused changes are easier to review and less costly to diagnose or revert. [Small changes][google-small]

Do not impose a universal line-count rule. A large generated file may require little manual inspection, while a two-line authorization change may require substantial scrutiny. Ask whether the author can explain the change and its risk clearly.

### Adapt the branch strategy to the organization

The following are practical organization patterns, not mandatory requirements:

| Pattern | How to organize reviews | Automation consideration |
|---|---|---|
| Short-lived feature branches | Keep each PR focused and integrate frequently. | Re-review on meaningful updates; avoid an expensive full review after every tiny push. |
| Trunk-based development with short PRs | Keep the integration path short and use feature flags where appropriate. | Prioritize fast feedback and keep slow, broad analysis separate from the critical path. |
| Stacked or dependent PRs | State which PR depends on which; review each change against its intended parent. | The reviewer must use the correct base, or it may report the same changes repeatedly. |
| Release and maintenance branches | Explain which supported version the change targets. | Provide the relevant compatibility constraints rather than assuming the newest framework or runtime. |
| Monorepositories | Identify affected components and their owners. | Apply component-specific context and tests; do not upload unrelated projects by default. |

Whatever the pattern, **record the exact revisions reviewed**. A rebase, force-push, or target-branch update can change the relevant diff even when the PR number stays the same.

### Use a PR template that captures evidence

The following template can be adapted to any Git platform. Configure its storage location using your platform's conventions.

```markdown
## Problem and intended outcome
What should change, and why? Link the approved ticket or requirement.

## Scope
What changed? What is deliberately outside this PR?

## Risk and compatibility
Does this affect permissions, public interfaces, persisted data,
performance, deployment order, or supported versions?

## Verification
Commands or checks actually run:
Results and relevant artifacts:
Checks not run, and why:

## Deployment and rollback
Configuration, migration, feature-flag, and rollback considerations:

## Reviewer focus
Which decisions or files deserve particular attention?
```

AI can draft this text, but the author must correct it. In particular, "tests should pass" is not test evidence, and generated prose must not claim that tests ran when they did not.

### Establish a review contract

Agree on who reviews each kind of change, what makes a concern blocking, and how disagreements are resolved. Use explicit labels or equivalent conventions such as **blocking defect**, **question**, and **non-blocking suggestion**.

For the first AI pilot, a sensible policy is one summary plus a small number of high-value findings. Reserve human time for behavior, risks, and trade-offs; let formatters and linters handle established mechanical rules. Review should improve the codebase, not demand perfection or impose personal preferences. [Review standard][google-standard]

## 3. What to automate and what to keep human

### Use complementary layers of feedback

| Layer | Suitable work | What it does not establish |
|---|---|---|
| Formatting and linting | Formatting, conventional errors, project-specific mechanical rules. | That the business behavior is correct. |
| Compilation and type checking | Language-level constraints and interface compatibility within their scope. | That runtime behavior or external assumptions are correct. |
| Automated tests | Behavior covered by actual test cases and environments. | That untested behavior is safe. |
| Security and dependency scanners | Known vulnerability patterns, dependency advisories, and configured policies. | That every security flaw has been found. |
| AI review | Contextual explanations, suspicious logic, missing cases, requirement comparisons, and review summaries. | A proof of correctness or a security certification. |
| Human review | Intent, trade-offs, domain understanding, and accountable decisions. | A guarantee that defects cannot escape. |

This is a proposed division of responsibilities. Keep existing quality controls while evaluating the additional value of AI.

### Good first automation targets

Start with work that is easy to inspect: a change summary, a reviewer guide, test-gap suggestions, or evidence-backed comments. More advanced tasks can include comparing a change to acceptance criteria, investigating a failing test, and proposing a narrowly scoped fix.

Avoid beginning with autonomous merge approval, broad repository writes, production deployment decisions, or automatic suppression of security findings. Those actions have consequences that are harder to validate and reverse.

### Define what a useful finding looks like

A helpful finding identifies **where the problem is, the scenario that triggers it, the evidence, the consequence, and a possible correction**.

Weak finding:

> This function may have security issues. Consider improving validation.

Stronger finding in a hypothetical training repository:

> The updated order lookup accepts an order identifier without checking the authenticated customer's ownership. If two customers know each other's identifiers, the new path can return another customer's order. Restore the ownership restriction and add a cross-customer access test.

The second finding is testable. It can still be wrong-for example, authorization may be enforced elsewhere-but it gives the reviewer something specific to investigate.

### Ask for uncertainty, not artificial confidence

Use instructions such as:

```text
Prioritize defects introduced by this change.
Explain a concrete failing scenario and cite the relevant code.
Inspect surrounding callers and tests before claiming a missing check.
Do not claim that commands ran unless their results are available.
Distinguish a demonstrated issue from an unresolved question.
Report fewer findings rather than inventing problems.
State what was not reviewed or could not be verified.
```

These instructions improve the review contract; they do not make the model infallible. Verify findings against code and tests.

## 4. A platform-neutral architecture

### Separate four concerns

```text
Git platform                     CI or workflow executor
PRs, diffs, comments, APIs         Scheduling, runtime, secrets, artifacts
           \                     /
            \                   /
             Review workflow
        Context -> analysis -> validation
                      |
                  Publisher
        Summary, inline comment, annotation,
              status, or proposed patch
```

The **Git platform** and the **executor** need not be the same product. Bitbucket can host a repository while Jenkins runs its tests. GitLab can host an MR while an external workflow runs its AI review. Atlassian documents publishing Bitbucket build status from Bamboo, Jenkins, or another build tool through its REST API. [Bitbucket and external builds][bitbucket-builds]

A fifth decision is **where the model runs**. Hosting the reviewer on your own server does not imply that the model is local. PR-Agent supports different model providers; the chosen endpoint determines where the model receives its input. [Model configuration][pr-models]

### "Works on any CI" is a conditional statement

A containerized workflow is portable when the executor can launch the approved runtime, reach the required services, receive PR metadata, inject credentials safely, and retain its outputs.

A reviewer is compatible with a Git platform only when an adapter can perform the needed operations against the **installed server version**. A generic Git clone supplies code, but does not supply a universal API for posting PR comments.

Therefore, evaluate two separate capabilities:

| Question | What to check |
|---|---|
| Can we run the workflow here? | OS/CPU support, container or executable policy, networking, secrets, timeouts, storage. |
| Can it integrate with this repository service? | Provider adapter, API version, authentication, diff access, comments, statuses, suggestions, webhooks. |

### Choose a deployment pattern

**A one-shot CI job** is a good starting point when a team already has an appropriate runner. The job reviews a PR, publishes its result, and exits. A persistent bot service is unnecessary for this initial workflow.

**A webhook service** receives events and can react to PR creation, updates, or comment commands. PR-Agent documents GitLab and Bitbucket Server webhook deployments. Its GitLab guide explicitly distinguishes pipeline execution from comment-event handling. [GitLab deployment][pr-gitlab] · [Bitbucket deployment][pr-bitbucket]

**A shared internal review service** adds a queue, centrally managed policy, isolated workers, and per-project credentials. This is a proposed production architecture for organizations with many repositories-not a claim that every reviewed tool supplies all those components.

**A custom agent pipeline** separates an investigative coding agent from a trusted publisher. This is useful when the team needs custom tests, tools, or business context beyond a predefined review workflow.

## 5. Choosing tools

### Open-source reviewers and integration building blocks

Licensing below describes the inspected repositories, not every hosted service associated with them. Inspect the license and dependency policy for the exact revision you adopt.

| Tool | Category and licensing | Useful fit | Important boundary |
|---|---|---|---|
| **Community PR-Agent** | Ready-made reviewer; current repository license is MIT. | Review, descriptions, suggestions, and questions with existing Git-platform adapters. | Feature parity varies by provider; its text skills are not a general shell-execution loop. |
| **AI Review** (`Nikita-Filonov/ai-review`) | CI-oriented reviewer; Apache-2.0. | Multiple Git providers, inline and summary feedback, optional repository-exploration agent mode. | Validate output quality and compatibility on your actual server and language stack. |
| **Kodus** | Self-hostable review product; AGPL-3.0 core with separately licensed enterprise code. | A centrally managed service rather than only a pipeline command. | Open-core: verify which required features belong to the community edition. |
| **Danger JS** | Programmable review and publication framework; MIT. | Combine existing PR integrations with rules and findings produced by your chosen agent. | Not an AI reviewer by itself; you supply the analysis and a small publishing adapter. |
| **reviewdog** | Diagnostic publication tool; MIT. | Connect linters, scanners, or structured AI findings to platform reporters. | An annotation or Code Insights report is not the same thing as a conversational review thread. |

Sources: [PR-Agent repository][pr-repo], [license][pr-license], and [configuration][pr-settings]; [AI Review][ai-review] and [license][ai-license]; [Kodus][kodus] and [license][kodus-license]; [Danger][danger-repo] and [license][danger-license]; [reviewdog][reviewdog] and [license][reviewdog-license].

**PR-Agent's status:** Qodo transferred the project to a community organization. The maintained community repository is distinct from Qodo's commercial offering and has published releases. Do not assume that an old commercial-product name, an old checkout, and the current community project are identical. [Handover announcement][pr-handover] · [Community releases][pr-releases]

**AI Review's practical difference:** Its optional agent mode can inspect a repository with tools before producing a review. The installable Python package is named `xai-review`, which differs from the repository name. [Project documentation][ai-review]

**Kodus's practical difference:** It targets a more product-like deployment. Its self-hosting information includes GitLab Self-Managed and Bitbucket Data Center. Plan for administration, upgrades, persistence, and a feature-edition check rather than assuming a one-command classroom setup. [Self-hosting information][kodus-hosting]

### Commercial products belong in the comparison

Open source is useful for inspectability, deployment control, customization, and portability. It does not automatically mean lower total operating cost or better findings. A managed product may reduce integration and maintenance work; a self-hosted system gives you more responsibility as well as more control.

| Product | Why evaluate it? | What to verify before selecting it |
|---|---|---|
| **CodeRabbit** | Commercial AI review with documented integrations beyond GitHub, including GitLab, Azure DevOps, and Bitbucket options. | Exact host/version support, self-hosting or private-network requirements, plan restrictions, permissions, and data flow. |
| **Codacy** | Commercial code-quality/security analysis with AI-assisted capabilities. | Do not assume every AI feature works on every provider or that historical on-premises documentation describes the current offering. |
| **Qodo** | Commercial AI review offering related historically to PR-Agent. | Treat it as a separate product; compare its current contract, deployment, features, and integrations independently. |

CodeRabbit's current documentation includes self-managed GitLab and Bitbucket Data Center, and a separate self-hosted offering. It is therefore inaccurate to describe all commercial AI reviewers as GitHub-only. [Platform overview][coderabbit-platforms] · [Self-hosted overview][coderabbit-hosting]

For Codacy, the documentation inspected distinguishes **AI Reviewer**, currently described as GitHub-only, from **AI-enhanced comments** on GitLab and Bitbucket. Its current pricing FAQ states that on-premises Git deployments are not supported by the current offering. Historical self-hosted pages should not be used as a present-day compatibility guarantee. [Codacy AI documentation][codacy-ai] · [Current product FAQ][codacy-pricing]

### A practical selection rule

Start with **PR-Agent** for a ready-made review workflow. Evaluate **AI Review** when repository exploration matters. Consider **Kodus** for a centrally administered product. Use **a coding agent plus Danger or reviewdog** when you need custom behavior but do not want to rebuild the platform-publishing layer.

This is a suggested evaluation order, not a benchmark ranking. Test the options on representative changes before adopting one.

## 6. Understanding PR-Agent

### Commands and expected outputs

PR-Agent supplies predefined workflows rather than requiring you to write every prompt and API call yourself. Its provider matrix includes GitLab, Bitbucket, Azure DevOps, and Gitea as well as GitHub; individual tools and publishing features differ across providers. [Supported platforms][pr-platforms]

| Command | Typical purpose | How to use it responsibly |
|---|---|---|
| `review` / `/review` | Produce a reviewer-oriented assessment of the change. | Verify findings and disclose incomplete coverage. |
| `describe` / `/describe` | Draft change descriptions and a walkthrough; diagram generation is configurable. | Preserve the author's intent and verify generated descriptions. |
| `improve` / `/improve` | Suggest focused code improvements. | Treat a suggested patch as untrusted code until reviewed and tested. |
| `ask` / `/ask` | Answer a question about the change. | Distinguish repository evidence from assumptions or unavailable context. |

The slash form is a comment command when the appropriate event integration is deployed. The non-slash form is used by the CLI. [Review][pr-review] · [Describe][pr-describe] · [Improve][pr-improve] · [Ask][pr-ask]

Generated Mermaid diagrams can help explain a flow. They are not guaranteed to be complete UML models, and an older Git interface may display their source rather than render them. Keep a text explanation as a portable alternative. [Description and diagrams][pr-describe]

### PR-Agent is not an unrestricted coding agent

Its documented skills integration injects textual `SKILL.md` content and reference Markdown. It does not execute a skill's scripts or turn a review into a general-purpose tool-use loop. If a workflow requires arbitrary investigation or test execution, use an appropriate agent runtime or run approved tools in separate stages. [Skills configuration][pr-settings]

This distinction prevents a common mistake: putting an API script beside a skill file and expecting PR-Agent to execute it automatically.

### Configuration should be small and trusted

PR-Agent supports repository, shared/global, and external configuration. Repository `.pr_agent.toml` is normally read from the default branch. The documentation warns against selecting a configuration branch from untrusted PR input because configuration can affect model endpoints and review behavior. [Configuration guide][pr-config]

For a course repository, start with a minimal policy on the protected default branch:

```toml
[pr_reviewer]
require_security_review = true
persistent_comment = true
num_max_findings = 3
inline_key_issues = false
extra_instructions = """
Focus on new correctness and authorization defects.
Describe a concrete failing scenario and relevant evidence.
Do not report formatting preferences or claim unperformed tests.
Explain missing context rather than inventing behavior.
"""

[pr_description]
publish_description_as_comment = true
enable_pr_diagram = true
```

The settings above are documented configuration keys. Start with summary feedback. Enable `inline_key_issues` only after confirming that the selected provider/version supports the desired output; provider support is not uniform, including for Bitbucket Server. [Configuration reference source][pr-settings]

The description-as-comment option avoids making description replacement the first classroom experiment. It does not remove the need to verify the generated text. [Description settings][pr-describe]

> Configuration is privileged input. Protect changes to review policy, prompts, model routing, and publishing logic as carefully as changes to a deployment pipeline.

## 7. Lab: PR-Agent on your Git platform

### Goal

Review an existing PR on a supported internal Git service, publish feedback, and repeat the process after a code update-without a GitHub integration or a new CI-controller plugin.

### Step 1: prepare the environment

Have the instructor or platform owner supply the following:

| Input | Purpose |
|---|---|
| An approved, disposable repository and open PR | A safe place to create comments and test behavior. |
| Exact Git product and server version | Compatibility testing; "Bitbucket" alone is insufficient. |
| `PR_AGENT_IMAGE` | An approved container image reference pinned to a digest. |
| `REVIEW_MODEL` and model credentials | A model identifier and authentication approved by the organization. |
| Git bot credentials | Access to read the PR and publish only the required outputs. |
| Network and certificate configuration | Access to the Git API, model endpoint, and registry through approved paths. |
| A trusted execution location | A workstation or runner where contributors cannot replace the review script. |

The current PR-Agent GitLab guide states a **GitLab 15.7+** requirement and requires the MR `/diffs` endpoint. It also discusses server-side diff limits. Do not infer support for older GitLab releases from the fact that the CLI can start. [GitLab compatibility][pr-gitlab]

For Bitbucket, choose the **Server/Data Center** configuration explicitly. The Cloud provider and Cloud Pipelines example are not substitutes for it. [Bitbucket installation][pr-bitbucket]

### Step 2: create a restricted bot identity

Use a dedicated service identity rather than a developer's broad personal credentials. Determine the required permissions from the operations you enable: reading code, posting comments, changing descriptions, setting statuses, and pushing commits are different needs.

In GitLab, do not assume `CI_JOB_TOKEN` can publish MR comments. Its documented Notes API access is read-only. Use a suitable bot credential supported by the installation and approved by its administrator. [Job-token permissions][gitlab-job-token]

Store secrets in the CI secret store or approved vault. Do not commit `.env` files containing credentials, place secrets in example YAML, paste them into prompts, or expose them through shell tracing.

### Step 3: use a reusable launcher

Save the following as **`review-pr.sh`** in a trusted location. It deliberately requires an approved digest-pinned image and restricts the commands exposed by the wrapper.

This example wires an **Anthropic API credential** to illustrate one model-provider setup. For Azure, Bedrock, another provider, or a local model, replace the provider configuration as a unit using the model guide. A CLI subscription login is not automatically a substitute for the reviewer's API credentials. [Model setup][pr-models]

```bash
#!/usr/bin/env bash
set -euo pipefail

command_name="${1:-review}"
case "$command_name" in
  review|describe|improve) ;;
  *) printf 'Allowed commands: review, describe, improve\n' >&2; exit 2 ;;
esac

: "${PR_AGENT_IMAGE:?Set an approved image pinned by digest}"
: "${GIT_PLATFORM:?Set gitlab or bitbucket_server}"
: "${PR_URL:?Set the full PR URL from trusted job metadata}"
: "${REVIEW_MODEL:?Set an approved provider/model identifier}"
: "${ANTHROPIC__KEY:?Inject the model API credential securely}"

if [[ ! "$PR_AGENT_IMAGE" =~ @sha256:[a-f0-9]{64}$ ]]; then
  printf 'PR_AGENT_IMAGE must end with @sha256:<64 hex characters>\n' >&2
  exit 2
fi

args=(
  run --rm
  --cap-drop ALL
  --security-opt no-new-privileges
  --env "CONFIG__GIT_PROVIDER=$GIT_PLATFORM"
  --env "CONFIG__MODEL=$REVIEW_MODEL"
  --env 'CONFIG__FALLBACK_MODELS=[]'
  --env 'CONFIG__RESTRICTED_MODE=true'
  --env 'CONFIG__PROPAGATE_TOOL_ERRORS=true'
  --env ANTHROPIC__KEY
  --entrypoint python
)

case "$GIT_PLATFORM" in
  gitlab)
    : "${GITLAB__URL:?Set the trusted GitLab base URL}"
    : "${GITLAB__PERSONAL_ACCESS_TOKEN:?Inject the GitLab bot token}"
    server_url="${GITLAB__URL%/}"
    args+=(--env GITLAB__URL --env GITLAB__PERSONAL_ACCESS_TOKEN)
    ;;
  bitbucket_server)
    : "${BITBUCKET_SERVER__URL:?Set the trusted Bitbucket base URL}"
    : "${BITBUCKET_SERVER__BEARER_TOKEN:?Inject the Bitbucket bot token}"
    server_url="${BITBUCKET_SERVER__URL%/}"
    args+=(--env BITBUCKET_SERVER__URL --env BITBUCKET_SERVER__BEARER_TOKEN)
    ;;
  *) printf 'Unsupported provider in this wrapper\n' >&2; exit 2 ;;
esac

# A basic origin-prefix check; the caller must also validate repository
# identity and permissions. Enforce network allowlists independently.
if [[ "$server_url" != https://* || "$PR_URL" != "$server_url/"* ]]; then
  printf 'PR URL must belong to the configured HTTPS Git service\n' >&2
  exit 2
fi

docker "${args[@]}" "$PR_AGENT_IMAGE" \
  -m pr_agent.cli --pr_url "$PR_URL" "$command_name"
```

The launcher adapts PR-Agent's documented CLI, provider configuration, and error propagation. It forwards secret variable **names**, not literal secret values in the Docker command line. [CLI installation][pr-cli] · [Server provider][pr-bitbucket] · [Configuration keys][pr-settings]

This is a training launcher, not a complete multi-tenant service. It does not implement authenticated webhooks, robust URL parsing, persistent queues, cross-run deduplication, or independent publication-credential isolation. Never point it at arbitrary user-supplied URLs. Apply the production controls in Sections 10 and 11.

The image is the runtime, not a security boundary by itself. Some environments will require additional runtime hardening or a different approved execution mechanism. For custom certificate authorities, configure trust in the relevant Git client and model client rather than disabling TLS verification. [GitLab certificate configuration][pr-gitlab]

### Step 4: review a GitLab MR

Set non-secret values for your training environment. The image, model identifier, and credentials should already have been supplied securely.

```bash
export GIT_PLATFORM=gitlab
export GITLAB__URL=https://gitlab.example.internal
export PR_URL="$GITLAB__URL/training/review-demo/-/merge_requests/12"

bash review-pr.sh review
```

Inspect the result in the MR. Then run the optional description exercise:

```bash
bash review-pr.sh describe
```

Check whether the generated summary preserves the intended behavior, accurately describes the tests, and explains the change without unnecessary noise.

### Step 5: adapt to Bitbucket Server/Data Center

Use the same launcher, but supply the Server provider and credentials:

```bash
export GIT_PLATFORM=bitbucket_server
export BITBUCKET_SERVER__URL=https://bitbucket.example.internal
export PR_URL="$BITBUCKET_SERVER__URL/projects/TRAIN/repos/review-demo/pull-requests/12"

bash review-pr.sh review
```

`BITBUCKET_SERVER__BEARER_TOKEN` must be injected separately. Do not replace it with a Bitbucket Cloud credential unless the installed integration explicitly supports that authentication scheme. [Server authentication][pr-bitbucket]

### Step 6: test the behavior, not just installation

Make one small corrective commit, wait for the intended trigger or rerun the job, and inspect the result. Compare the reported location, reviewed revision, summary, and existing comments.

Record the outcome:

```markdown
Git product / edition / version:
Reviewer version / container digest:
Model / endpoint / policy version:
PR identifier and reviewed commit:

Summary published correctly:
Inline comments supported and positioned correctly:
Rerun behavior and duplicate handling:
Behavior after a new commit:
Behavior on missing permissions or model failure:
Known limitations:
```

A successful model response is not sufficient. The lab succeeds when the feedback reaches the correct PR, represents the correct revision, and its limitations are visible.

## 8. Running the same workflow in different CI systems

### Keep the review logic outside platform-specific YAML

The shared launcher or review container should own the review logic. Each CI integration should mainly supply credentials, PR identity, trusted configuration, and execution limits.

| Executor | Practical integration pattern | What must be supplied explicitly |
|---|---|---|
| GitLab CI/CD | A job using the review image or a trusted external review service. | MR URL, instance URL, bot credential, model configuration. |
| Jenkins | A trusted Pipeline stage or centrally managed job invoking the launcher. | PR metadata from the SCM integration/webhook and scoped credential binding. |
| Bamboo | A configured script/container task in a trusted plan. | PR metadata and secure variables; do not assume Cloud Pipelines variables exist. |
| Argo Workflows | A container template running the CLI directly. | Validated PR parameters, Secret references, network policy, and an event trigger. |
| Azure Pipelines | A trusted script/container task or service invocation. | Repository-provider configuration and PR metadata appropriate to the host. |
| GitHub Actions | A workflow using the same approved runtime or the tool's supported action. | Token permissions and event trust boundaries, especially for forked PRs. |

These are integration patterns, not identical vendor-certified recipes. The Git host determines the provider adapter; the executor determines how the process starts. Jenkins documents credential binding and shell execution, while Argo documents direct container execution. [Jenkins Pipeline][jenkins-pipeline] · [Argo containers][argo]

### Example: a manual GitLab training job

This is a **standalone training pipeline**, not a replacement for existing production stages. It uses the same CLI directly because it already runs inside the review image.

> Run this only in a trusted classroom repository. Same-project PRs are not automatically trustworthy: their authors may be able to change pipeline code. For untrusted changes, use a centrally controlled job/service that contributors cannot modify. Do not remove secret protections merely to make the example run.

Configure `PR_AGENT_IMAGE`, `REVIEW_MODEL`, `ANTHROPIC__KEY`, and `GITLAB__PERSONAL_ACCESS_TOKEN` through approved CI settings.

```yaml
stages:
  - ai_review

ai_review:
  stage: ai_review
  image:
    name: "$PR_AGENT_IMAGE"
    entrypoint: [""]
  variables:
    CONFIG__GIT_PROVIDER: "gitlab"
    CONFIG__FALLBACK_MODELS: "[]"
    CONFIG__RESTRICTED_MODE: "true"
    CONFIG__PROPAGATE_TOOL_ERRORS: "true"
  script:
    - |
      set -eu
      : "${REVIEW_MODEL:?Missing approved model}"
      : "${ANTHROPIC__KEY:?Missing model credential}"
      : "${GITLAB__PERSONAL_ACCESS_TOKEN:?Missing GitLab bot token}"
      export GITLAB__URL="$CI_SERVER_URL"
      export CONFIG__MODEL="$REVIEW_MODEL"
      export PR_URL="${CI_MERGE_REQUEST_PROJECT_URL}/-/merge_requests/${CI_MERGE_REQUEST_IID}"
      cd /app
      python -m pr_agent.cli --pr_url "$PR_URL" review
  rules:
    - if: '$CI_PIPELINE_SOURCE == "merge_request_event" && $CI_MERGE_REQUEST_SOURCE_PROJECT_ID == $CI_PROJECT_ID'
      when: manual
    - when: never
  allow_failure: true
```

The manual start is intentional for the first exercise. After testing, a trusted integration can trigger the same operation automatically. `allow_failure: true` makes this AI job advisory; it must not weaken other test or security jobs. Keep failures visible rather than replacing errors with a misleading "no issues found." The CLI invocation follows the documented pipeline approach. [PR-Agent pipeline guide][pr-gitlab]

### Example: a Jenkins stage with scoped credentials

The following stage assumes a **trusted** Pipeline definition, the launcher at `/opt/course-review/review-pr.sh`, a Docker-capable agent, and non-secret inputs configured by the job owner. Credential identifiers are examples to create in Jenkins.

```groovy
stage('AI review') {
    steps {
        withCredentials([
            string(credentialsId: 'review-gitlab-token',
                   variable: 'GITLAB__PERSONAL_ACCESS_TOKEN'),
            string(credentialsId: 'review-model-key',
                   variable: 'ANTHROPIC__KEY')
        ]) {
            sh '/opt/course-review/review-pr.sh review'
        }
    }
}
```

Do not run PR-controlled build scripts in this credential scope. Masking log output is not equivalent to preventing a process from reading a secret. [Jenkins credential handling][jenkins-pipeline]

### Argo: launch the reviewer, not Docker inside Docker

An Argo container template can invoke the process directly. The following is the **container portion**, not a complete Workflow manifest:

```yaml
container:
  image: "{{workflow.parameters.pr-agent-image}}"
  command: ["python", "-m", "pr_agent.cli"]
  args: ["--pr_url", "{{inputs.parameters.pr-url}}", "review"]
```

Declare the parameters and environment variables in the surrounding template, reference approved Kubernetes Secrets, and authenticate the system submitting the workflow. A parameterized workflow does not itself listen for Git events; connect a webhook receiver or your existing event system separately. [Argo workflow example][argo]

### Automatic runs and comment commands are different features

A job triggered by PR creation does not automatically react to `/review` typed in a comment. Interactive commands require the relevant comment event to reach a configured handler. Start with CI-triggered review; add an authenticated webhook deployment when conversation-driven workflows become useful. [GitLab event behavior][pr-gitlab]

## 9. Custom agents with reusable publication tools

A general-purpose coding agent is useful when the reviewer must inspect callers, follow data flow, read tests, or run approved diagnostics. You do not need to teach that agent how to construct every GitLab or Bitbucket API request.

Use this separation:

```text
Trusted orchestrator
  - authenticates the event and selects a repository
  - records base/head revisions and loads approved policy
              |
Isolated analysis stage
  - reads the selected code and context
  - uses only permitted tools
  - produces structured findings
              |
Trusted validation and publication stage
  - checks the output and reviewed revision
  - maps findings to valid locations
  - uses Danger, reviewdog, or a provider adapter
              |
PR feedback and auditable execution status
```

### Choose the agent independently of the Git host

| Runtime | Documented automation entry point | Output caveat |
|---|---|---|
| Codex CLI | `codex exec`; schema-constrained final output is available. | JSON event streams and the final structured result are different outputs. |
| Claude Code | `claude -p`; JSON output and JSON Schema options are available. | The result may be inside an envelope, including `structured_output` for schema output. |
| OpenCode | `opencode run`; JSON event output is available. | Raw JSON events are not automatically a single review document. |

Consult each runtime's current authentication and permission configuration. Headless execution means non-interactive execution, not permission to do everything. [Codex automation][codex] · [Claude automation][claude-headless] · [OpenCode CLI][opencode-cli] · [OpenCode permissions][opencode-permissions]

### Define your own review contract

This is an **example schema for this course**, not a built-in PR-Agent, Danger, or reviewdog format:

```json
{
  "summary": "The change simplifies order lookup but removes an ownership restriction.",
  "findings": [
    {
      "path": "src/orders/service.ts",
      "line": 84,
      "severity": "high",
      "title": "Order lookup does not restrict the customer",
      "evidence": "The changed lookup filters by order ID, not by authenticated customer ID.",
      "recommendation": "Restore the ownership restriction and add a cross-customer test."
    }
  ],
  "limitations": [
    "Tests were inspected but not executed."
  ]
}
```

The example uses a TypeScript-style path, but the contract can represent findings in Java, C#, Python, Go, Rust, PHP, SQL, configuration files, or another text-based codebase. The selected analyzers and model still need evaluation on that language and framework.

A minimal JSON Schema for **`review.schema.json`** is:

```json
{
  "type": "object",
  "additionalProperties": false,
  "required": ["summary", "findings", "limitations"],
  "properties": {
    "summary": { "type": "string" },
    "limitations": {
      "type": "array",
      "items": { "type": "string" }
    },
    "findings": {
      "type": "array",
      "items": {
        "type": "object",
        "additionalProperties": false,
        "required": [
          "path", "line", "severity", "title", "evidence", "recommendation"
        ],
        "properties": {
          "path": { "type": "string" },
          "line": { "type": "integer" },
          "severity": { "type": "string", "enum": ["low", "medium", "high"] },
          "title": { "type": "string" },
          "evidence": { "type": "string" },
          "recommendation": { "type": "string" }
        }
      }
    }
  }
}
```

The schema checks shape, not truth or publishability. Your validator must additionally check positive line numbers, allowed repository-relative paths, size limits, eligible diff locations, and actual execution status. A line in this simple contract refers to the **new-file side**; put deleted-line or unlocatable findings in the summary unless you extend the contract.

For a controlled Codex analysis stage, an invocation can look like this:

```bash
codex exec \
  --sandbox read-only \
  --output-schema /trusted/review.schema.json \
  -o /review-output/raw-review.json \
  "$(cat /trusted/review-prompt.txt)"
```

The orchestrator must prepare the checkout, prompt, authentication, writable output directory, and tool restrictions. A read-only sandbox restricts writes; it does not mean that secrets in the process environment are unreadable. Follow the runtime's automation guidance and do not run untrusted code in a credential-bearing environment. [Codex non-interactive configuration][codex]

### Publish through Danger JS

Danger provides established GitLab and Bitbucket Server integrations and a programmable API for comments. The application under review does not have to be written in JavaScript; Node.js can exist only in the publishing job. [GitLab integration][danger-gitlab] · [Bitbucket Server integration][danger-bitbucket]

The following is the **core of a trusted Dangerfile**, not a complete validator. It consumes a post-validation intermediate file created by your trusted pipeline-not the raw model response. The publisher must already have sanitized comment content, checked line locations, and rechecked the current PR revision.

```typescript
import { readFileSync } from "node:fs";
import { markdown, warn } from "danger";

type ValidatedReview = {
  headSha: string;
  summaryMarkdown: string;
  findings: Array<{
    path: string;
    line: number;
    commentMarkdown: string;
  }>;
};

const report = JSON.parse(
  readFileSync("/review-output/validated-review.json", "utf8")
) as ValidatedReview;

const expectedHead = process.env.EXPECTED_HEAD_SHA;
if (!expectedHead || report.headSha !== expectedHead) {
  throw new Error("Review revision does not match this publication job");
}

markdown(report.summaryMarkdown);
for (const finding of report.findings) {
  warn(finding.commentMarkdown, finding.path, finding.line);
}
```

`warn` and `markdown` are documented Danger APIs. The TypeScript type assertion above is not runtime validation. Keep the validator, dependencies, and Dangerfile outside PR-controlled execution. [Danger API reference][danger-api]

Danger removes much of the provider-specific publication work, but you still own the conversion from your review contract to its API and the security checks around it.

### Publish through reviewdog

reviewdog connects analysis outputs to existing reporters. Use a supported diagnostic format, such as RDJSON, or write a small converter from your own schema. Arbitrary model JSON is not automatically reviewdog input. [reviewdog documentation][reviewdog]

Its GitLab discussion reporter is useful for MR feedback. Its Bitbucket Server integration uses **Code Insights reports and annotations**, which are not ordinary conversation threads. Choose based on the feedback experience you need, and verify the reporter against the installed server version. [Reporter documentation][reviewdog]

**Rule of thumb:** Use a dedicated reviewer for ready-made review workflows; use Danger for programmable PR interaction; use reviewdog for diagnostic-style findings.

## 10. Reliable comments, reruns, and review state

### Treat output types as different capabilities

| Output | Best use | Integration detail |
|---|---|---|
| Summary comment | Reviewer guide, overall observations, and limitations. | Prefer updating an identifiable bot comment rather than adding endless summaries. |
| Inline discussion | A finding tied to a specific part of the change. | Requires correct path, side, line, and revision information. |
| Suggested patch | A small proposed correction. | Platform-specific syntax; applying it changes code and still requires review. |
| Annotation or Code Insights report | Structured scanner-style findings. | Not necessarily a replyable or resolvable review thread. |
| Commit/PR status | Communicate whether a job completed or a policy passed. | Define its meaning; do not confuse successful execution with safe code. |
| CI artifact | Full report, diagnostics, and audit data. | Set access controls and retention; it may contain source or sensitive context. |

GitLab's inline discussion API illustrates why a generic `file + line` call is insufficient: its positioning model includes diff revision information and old/new path and line details. [Discussions API][gitlab-discussions]

### Design publication as a deterministic operation

A recommended publisher should:

1. Read the current PR metadata and compare it to the recorded review snapshot.
2. Validate the report, normalize paths, and map each finding to an eligible location.
3. Sanitize text, neutralize unwanted mentions, and enforce a comment budget.
4. Find an existing bot-owned comment or finding and update it where appropriate.
5. Publish with the correct revision information and record the outcome.

If the revision changed, cancel or rerun the analysis, or clearly publish the result as applying to the older revision. A fresh metadata check reduces races but is not atomic with publication; use revision-aware API anchors and include the reviewed SHA in the report.

### Distinguish three kinds of identity

**Run identity:** repository, PR, base/head revisions, tool version, model, and policy version. Use this to deduplicate identical analysis requests.

**Finding identity:** normalized issue category, file, and relevant code context. Keep a stable relationship across nearby revisions rather than using the line number alone.

**Comment identity:** the provider's existing comment/thread identifier and the bot account that owns it. Update only comments the integration is allowed to manage.

A finding's line number can move after unrelated edits. A new commit does not automatically mean a reported issue is fixed. Never resolve a human reviewer's objection merely because the bot no longer mentions it.

### Make partial analysis visible

A proposed report footer can state:

```text
Reviewed revision: <head SHA>
Diff basis: <base or merge-base SHA>
Coverage: 8 of 10 changed files examined
Not examined: generated file; patch unavailable
Execution: completed with limited coverage
Tests: not executed by this reviewer
```

If the tool cannot reliably calculate coverage, say **coverage unknown** instead of inventing counts. Large diffs, missing patches, output truncation, model timeouts, and failed tool calls must not become "no findings."

For Git-based custom workflows, understand the diff basis. A comparison from the merge base answers a different question from a direct comparison of two branch tips. Git documents these forms separately; record which one the workflow uses and ensure required history is available in shallow checkouts. [Git diff documentation][git-diff]

### Common operational failures

| Symptom | Likely area to investigate | Safer response |
|---|---|---|
| The bot can clone but cannot comment. | Credential scope, bot role, or wrong provider. | Test the specific publication permission. |
| Summary works; inline feedback fails. | Invalid position, old revision, deleted file, or unsupported feature. | Use a summary fallback and inspect adapter/version support. |
| Every push creates duplicate comments. | Missing finding identity or persistent-comment behavior. | Add stable identities and update owned comments. |
| The bot says the PR is empty. | Wrong base, missing Git history, API pagination, or omitted diff. | Treat uncertain diff retrieval as incomplete analysis. |
| An API call returns 401/403. | Authentication, permissions, expiry, or policy. | Fail visibly; do not request administrator access as a blanket fix. |
| A model or provider returns 429. | Quota or concurrency limits. | Use bounded retries and backoff; avoid retry storms. |
| A bot comment triggers another bot run indefinitely. | Missing event filtering. | Ignore the bot's own events and make handlers idempotent. |

## 11. Security review and safe agent execution

### Keep deterministic security checks

Semgrep Community Edition supports standalone CI scanning; its documented standalone command is `semgrep scan`. OSV-Scanner provides dependency vulnerability analysis. Both can contribute evidence to a review workflow without making GitHub the repository requirement. [Semgrep CE in CI][semgrep] · [OSV-Scanner][osv]

Run the organization's approved scanners and tests, retain their results, and let the AI explain or investigate them. Do not allow the model to suppress a scanner finding or waive a security gate on its own.

Different tools cover different languages, vulnerability classes, and project layouts. Pin scanner versions and rule sets, check their licenses, and inspect network behavior as well as their output.

### The repository is untrusted input

Source comments, Markdown, tickets, build logs, and retrieved documents can contain instructions intended to manipulate an agent. For example, a file might ask the reviewer to ignore an authorization change or transmit a secret. These are data to analyze, not instructions with authority over the workflow. Agent security guidance explicitly treats prompt injection and tool permissions as relevant risks. [Claude Code security][claude-security]

Prompt instructions are only one layer of defense. Protect the filesystem, tools, network, credentials, and publishing permissions independently. [Secure agent deployment][secure-agents]

### Recommended separation of permissions

| Component | Access it may need | Access to avoid by default |
|---|---|---|
| Context collector | Read the selected repository and approved ticket fields. | Organization-wide repositories and unrelated issues. |
| Analysis worker | Read the snapshot and use bounded investigation tools. | Git write tokens, deployment credentials, unrestricted outbound access. |
| Test worker | Execute tests in an isolated environment with synthetic fixtures. | Production secrets or shared developer home directories. |
| Publisher | Read PR state and create/update approved feedback. | Merging, pushing to protected branches, or running arbitrary commands. |
| Remediation worker, if enabled | Write a dedicated proposal branch under explicit policy. | Direct production changes or merging its own proposal. |

Not every ready-made reviewer separates these components internally. A small trusted CI pilot may combine read and comment permissions in one process; recognize that trade-off rather than claiming isolation that does not exist. Stronger separation is especially valuable for shell-using agents.

### Minimum controls for a pilot

Protect prompts, configuration, tool definitions, dependency locks, and publisher code. Use ephemeral workers and the narrowest practical credentials. Configure timeouts, turn/tool limits, output-size limits, spending controls, and bounded retries. Disable autonomous merge approval and unnecessary repository writes.

Do not expose the host Docker socket, broad Kubernetes permissions, cloud metadata access, personal SSH keys, or a developer's home directory to an investigative agent. Avoid installing unpinned dependencies or executing PR-controlled setup scripts in a job that holds publication or model credentials. The security objective is to limit consequences even when the agent follows a malicious instruction. [Deployment isolation guidance][secure-agents]

For webhook services, authenticate incoming events, validate the actor's authority, restrict repositories, reject replay/duplicate work appropriately, and keep the service off public unauthenticated endpoints. An example webhook URL in a setup guide is not a complete security design.

### Source-code privacy follows the entire data path

Document which systems receive diffs, full files, prompts, issue text, logs, traces, and generated reports. Include the model provider, gateway, telemetry, CI artifacts, and any MCP servers.

Self-hosting the bot does not automatically keep code on-premises. Configure model routing and fallback behavior explicitly, and enforce permitted destinations at the network layer. A fallback model may otherwise have a different data-processing path. PR-Agent's model configuration supports multiple deployment/provider choices; review the one actually in use. [Model routing][pr-models]

Keep company course environments separate. Do not share repository context, bot credentials, persistent agent sessions, or cached review memory between participants from different organizations.

## 12. Older servers, CLIs, APIs, and MCP

### Start with an inventory, not an installation command

Record the Git product, edition, exact version, base URL, authentication method, proxy/CA setup, available event types, runner capabilities, and permitted model endpoints. Test the specific API operations needed by the workflow.

"On-premises" describes deployment location. It does not tell you which API version, comment features, or token types are available.

### `glab` supports self-managed GitLab

GitLab's CLI can work with self-managed instances. Its current project documentation states official support for **GitLab 16.0 and later**, while some commands require newer servers. Commands may work on earlier releases without being supported. [GitLab CLI][glab] · [Version requirements][glab-versions]

A CLI can simplify fetching MR information or posting a note, but it does not eliminate inline-position mapping, token permissions, or the need for a trigger. A dedicated review adapter is usually preferable when it already supports the needed workflow.

### MCP is an interface, not a compatibility guarantee

**Model Context Protocol (MCP)** gives an agent a structured way to call tools. An external MCP server can wrap an existing REST API, so the old application itself does not need native MCP support. The wrapper still depends on the application's API and authentication capabilities.

Atlassian's official remote MCP server is documented as a bridge to **Atlassian Cloud** services. It should not be assumed to support arbitrary old Jira, Confluence, or Bitbucket Server installations. [Official Atlassian MCP][atlassian-mcp]

The community **`sooperset/mcp-atlassian`** project supports Jira and Confluence across Cloud and Server/Data Center deployments. It is not a universal Bitbucket, Bamboo, or Jenkins integration. Check the current compatibility information and test the installed version rather than assuming that "Server support" includes every historical release. [Community Atlassian MCP][community-atlassian]

For a few fixed operations, a small approved REST wrapper may be simpler than deploying MCP. For interactive agents using many approved tools, MCP can provide a reusable interface. Neither approach automatically supplies event handling, authorization policy, queues, or safe publication.

### New Jenkins plugins may require newer controllers

As checked for this material, the Jenkins **AI Agent** plugin requires Jenkins **2.528.3**, and the **MCP Server** plugin requires **2.541.3**. These are compatibility examples, not permanent minimums. [AI Agent plugin][jenkins-ai] · [MCP Server plugin][jenkins-mcp]

On an older controller, use an approved external executable/container job or a separate review service when possible. Do not make a course exercise depend on an unplanned production-controller upgrade. Conversely, a wrapper does not fix security weaknesses in an unsupported server; infrastructure maintenance remains a separate responsibility.

### A useful fallback order

Try a maintained review provider adapter first. Next consider an existing publication framework such as Danger or reviewdog. Use a CLI or approved API library for a small missing operation. Build a custom wrapper only for the remaining gap.

When a server cannot support inline review, a well-structured summary or CI artifact can still provide value. Do not promise identical UX across all platforms.

## 13. Beyond review: controlled CI/CD automation

The same architecture can support additional workflows. Introduce them separately so each has clear permissions, inputs, outputs, and an acceptance test.

| Workflow | Useful automation | Appropriate control |
|---|---|---|
| PR descriptions and release notes | Draft explanations from reviewed changes. | Preserve human intent and verify claims. |
| Requirement checks | Compare implementation with approved acceptance criteria. | Read only necessary ticket fields; report missing context. |
| Failure triage | Summarize failing tests and identify likely causes. | Do not treat the model's explanation as proof of root cause. |
| Suggested tests | Propose focused regression cases. | Review tests for meaningful assertions and run them. |
| Security investigation | Relate scanner findings to changed code. | Keep deterministic gates and specialist escalation. |
| Patch proposals | Create a narrowly scoped correction in a separate branch/PR. | Run normal checks; retain independent human approval. |
| Migration and deployment notes | Highlight ordering, configuration, and rollback concerns. | Keep production execution outside the reviewer's permissions. |

These are design ideas, not a claim that every tool in Section 5 implements each workflow out of the box.

### Avoid a bot-to-bot loop

A fix bot can create a commit that triggers a review bot, which requests another fix, which triggers another review. Bound the number of remediation attempts, ignore appropriate bot-originated events, and require human intervention after the configured limit.

Keep the authoring and reviewing context independent where practical. Another model or a fresh session may provide a different perspective, but independence is not established merely by naming two agents differently. Validate the result with tests and humans rather than assuming "two agents agreed" is proof.

## 14. Measuring quality and rolling out

### Evaluate with representative changes

Prepare a small collection of real, approved historical changes or synthetic PRs with known behavior. Include genuine defects, correct but suspicious-looking code, framework-specific patterns, and changes with missing context.

Use the same cases when comparing reviewers. Record the model, tool version, policy, and available context. A tool that finds an obvious training bug may still struggle with your production architecture.

### Measure outcomes rather than comment volume

| Measure | Useful interpretation |
|---|---|
| Time to first useful feedback | How quickly the author receives an actionable observation-not just a bot greeting. |
| Finding precision | Confirmed actionable findings divided by adjudicated findings. Record unresolved cases separately. |
| Known-defect detection | How many known defects in the evaluation set were found. Do not claim production recall when unknown defects are uncounted. |
| Human triage effort | Time spent checking, dismissing, or clarifying the bot's output. |
| Review completion rate | How often execution and publication finish successfully, with failures and partial coverage distinguished. |
| Duplicate and stale-comment rate | Whether the integration manages updates correctly. |
| End-to-end review duration | Whether the overall PR process improves, accounting for change size and risk. |
| Cost per useful outcome | Model, infrastructure, and maintenance cost relative to validated value. |

An accepted suggestion is not automatically correct, and a dismissed suggestion is not automatically a false positive. Agree on an adjudication method with human reviewers.

### Estimate total cost

Use a model such as:

```text
Monthly cost =
  reviews per month × average analysis runs per review × average model cost per run
  + runner and service infrastructure
  + storage and observability
  + maintenance and human triage effort
```

These are planning variables, not a vendor price quotation. Include retries, large-diff handling, repeated pushes, and interactive commands. Avoid evaluating only the advertised cost of one model call.

### Roll out in stages

**Observe first.** Run on an evaluation set or keep output as a restricted artifact. Check quality, privacy, and compatibility.

**Introduce advisory feedback.** Enable summaries and a limited number of comments in a small set of repositories. Keep a clear owner and an easy disable switch.

**Tune and expand.** Adjust scope and prompts using measured failure cases. Add interactive commands or deeper investigation only when the benefits justify the complexity.

**Consider narrowly defined gates last.** Deterministic checks and established policies are stronger initial gates than a model's overall opinion. Any gate involving AI-derived findings needs an explicit escalation and override process.

Review the configuration after upgrades. Version changes in the reviewer, model, provider adapter, or prompt can change behavior even when the repository is unchanged.

## 15. Exercises and discussion answers

### Exercise A: improve the pull request before adding AI

Take a sample PR containing a behavior change, unrelated formatting, and an undocumented migration. Propose how to split or explain the work. Fill out the PR template in Section 2, identify the likely reviewers, and write the tests you expect to see.

**Deliverable:** A clearer PR description and a justified review plan. Do not assume that installing a reviewer fixes poorly organized work.

### Exercise B: run and assess a ready-made reviewer

Use the PR-Agent lab against the course repository. Include one genuine correctness defect and one suspicious-looking change that is actually safe. Run review, verify the findings manually, fix the genuine defect, and rerun.

**Deliverable:** The compatibility record from Section 7, plus a table of correct findings, false positives, missed defects, and unsupported output features. Explain every classification.

### Exercise C: prove the publisher is safe to rerun

Supply your validator/publisher with a valid finding, a negative line number, a path outside the repository, a finding on an older commit, and an identical finding submitted twice. Use synthetic inputs, not real secrets.

**Deliverable:** Evidence that invalid input is rejected or safely moved to a summary, old revisions are not misrepresented, and duplicate publication is controlled.

### Exercise D: design for an unfamiliar company

Choose one scenario:

| Scenario | Required design decisions |
|---|---|
| Self-managed GitLab with Jenkins | Choose the Git adapter, trusted executor, bot permissions, trigger, and output type. |
| Older Bitbucket Server with Bamboo | Check API/version support; provide a summary fallback if inline review is unavailable. |
| Multiple Git hosts with Argo Workflows | Design validated event inputs, isolated workers, provider-specific publication, and per-company credentials. |
| Restricted network with no approved external model | Identify an approved local/private model option or keep the exercise at deterministic analysis until approval exists. |

**Deliverable:** A one-page architecture, an environment inventory, a compatibility test plan, and a list of assumptions that still require verification.

### Discussion questions

**1. The AI job exited successfully and found no issues. Is the PR safe to merge?**

Not on that evidence alone. Establish what was reviewed, which checks ran, whether output was complete, and whether the required human and policy approvals exist.

**2. A tool runs in Docker. Does that mean it supports every Git platform?**

No. Container execution addresses runtime portability. Reading diffs and publishing PR feedback require a compatible provider integration.

**3. A repository uses GitLab, but CI runs in Jenkins. Which Git provider should the reviewer use?**

GitLab. Jenkins schedules and executes the job; it does not change where the MR and its comments live.

**4. The reviewer can read an MR with `CI_JOB_TOKEN`. Should comment publication work automatically?**

No. Read access is not write access. Check the specific API operation and token permissions. [GitLab token reference][gitlab-job-token]

**5. Does self-hosting PR-Agent mean source code never leaves the network?**

No. Inspect the configured model endpoint and all supporting data flows. [Model configuration][pr-models]

**6. Does adding a Jira MCP server make the old Git server compatible with every reviewer?**

No. Ticket retrieval and Git review publication are separate integrations. MCP does not remove API-version or permission requirements.

**7. Why not have the agent post comments directly with a broad API token?**

That couples analysis with powerful actions. A deterministic publisher is easier to constrain, validate, test, and audit. A direct-writing agent may be acceptable in a narrowly controlled setup, but its extra permissions are an explicit risk decision.

## 16. Implementation checklist and takeaways

### Before the first automated review

- [ ] Record the Git product, edition, version, and required review operations.
- [ ] Choose the reviewer and verify its license and maintenance status.
- [ ] Approve the model endpoint, credentials, data flow, and retention.
- [ ] Protect the job definition, prompts, configuration, and publisher.
- [ ] Use restricted service identities and an isolated execution environment.
- [ ] Pin the runtime and dependencies; configure timeouts and spending limits.
- [ ] Test a summary, an inline finding where supported, a rerun, and a new commit.
- [ ] Test missing permissions, incomplete diffs, invalid output, and model failure.
- [ ] Keep the initial integration advisory and retain normal merge controls.
- [ ] Assign an owner, record known limitations, and provide a disable procedure.

### Reusable environment worksheet

```markdown
Repository host / edition / version:
Repository identifier and allowed base URL:
CI executor and runtime restrictions:
Review tool / version / image digest:
Model endpoint / authentication / approved fallback policy:
Trigger and actor authorization:
Bot identity and required operations:
Trusted prompt and configuration source:
Diff basis and revision handling:
Output types and provider limitations:
Failure, retry, and duplicate policy:
Logging, retention, and cross-project isolation:
Evaluation results:
Operational owner and disable procedure:
```

### Key takeaways

**Improve the review process before adding more automation.** Focused changes, clear intent, and real test evidence help both humans and AI.

**Separate execution from integration.** The CI platform runs the workflow; the Git adapter reads and updates the PR. They can be different products.

**Prefer maintained building blocks over bespoke API scripts.** PR-Agent, AI Review, and Kodus address ready-made review needs. Danger and reviewdog reduce publication work for custom agents.

**Treat every model finding as something to verify.** Keep security scanners, tests, domain expertise, and human accountability.

**Design for reruns and failure from the beginning.** Correct revisions, bounded output, visible limitations, and safe permissions are part of a working review system-not optional finishing touches.

---

## 17. Primary sources and further reading

Links below support the documented product capabilities and configuration examples. The process recommendations and exercises are original teaching material. Research was checked on **2 October 2026**; recheck compatibility and licensing when updating the course. Linked documentation and default-branch files are living resources, not immutable snapshots.

### Review practice and Git

[Small changes][google-small] · [What to look for in review][google-review] · [Review standard][google-standard] · [Git diff reference][git-diff]

### PR-Agent

[Community repository][pr-repo] · [Current license][pr-license] · [Releases][pr-releases] · [Qodo handover announcement][pr-handover] · [Provider matrix][pr-platforms]

[CLI installation][pr-cli] · [GitLab integration][pr-gitlab] · [Bitbucket integration][pr-bitbucket] · [Configuration guide][pr-config] · [Configuration source][pr-settings] · [Model setup][pr-models]

[Review command][pr-review] · [Description and diagrams][pr-describe] · [Code suggestions][pr-improve] · [Questions][pr-ask]

### Alternative reviewers and publishers

[AI Review repository][ai-review] · [AI Review license][ai-license] · [Kodus repository][kodus] · [Kodus license][kodus-license] · [Kodus self-hosting][kodus-hosting]

[Danger repository][danger-repo] · [Danger license][danger-license] · [Danger GitLab integration][danger-gitlab] · [Danger Bitbucket Server integration][danger-bitbucket] · [Danger API][danger-api]

[reviewdog documentation][reviewdog] · [reviewdog license][reviewdog-license]

### Commercial comparison

[CodeRabbit platforms][coderabbit-platforms] · [CodeRabbit self-hosting][coderabbit-hosting] · [Codacy AI features][codacy-ai] · [Codacy current offering and FAQ][codacy-pricing]

### Infrastructure, automation, and security

[GitLab CLI][glab] · [GitLab CLI version support][glab-versions] · [GitLab job tokens][gitlab-job-token] · [GitLab discussion positions][gitlab-discussions]

[Jenkins Pipeline and credentials][jenkins-pipeline] · [Jenkins AI Agent plugin][jenkins-ai] · [Jenkins MCP plugin][jenkins-mcp] · [Argo container workflows][argo] · [Bitbucket integration with external builds][bitbucket-builds]

[Official Atlassian MCP][atlassian-mcp] · [Community Atlassian MCP][community-atlassian]

[Codex non-interactive mode][codex] · [Claude Code programmatic use][claude-headless] · [OpenCode CLI][opencode-cli] · [OpenCode permissions][opencode-permissions]

[Agent security considerations][claude-security] · [Secure agent deployment][secure-agents] · [Semgrep CE in CI][semgrep] · [OSV-Scanner][osv]

[google-small]: https://google.github.io/eng-practices/review/developer/small-cls.html
[google-review]: https://google.github.io/eng-practices/review/reviewer/looking-for.html
[google-standard]: https://google.github.io/eng-practices/review/reviewer/standard.html
[git-diff]: https://git-scm.com/docs/git-diff
[pr-repo]: https://github.com/The-PR-Agent/pr-agent
[pr-license]: https://raw.githubusercontent.com/The-PR-Agent/pr-agent/main/LICENSE
[pr-releases]: https://github.com/The-PR-Agent/pr-agent/releases
[pr-handover]: https://www.qodo.ai/blog/qodo-is-handing-pr-agent-over-to-the-community/
[pr-platforms]: https://docs.pr-agent.ai/overview/supported_platforms/
[pr-cli]: https://docs.pr-agent.ai/installation/locally/
[pr-gitlab]: https://docs.pr-agent.ai/installation/gitlab/
[pr-bitbucket]: https://docs.pr-agent.ai/installation/bitbucket/
[pr-config]: https://docs.pr-agent.ai/usage-guide/configuration_options/
[pr-settings]: https://raw.githubusercontent.com/The-PR-Agent/pr-agent/main/pr_agent/settings/configuration.toml
[pr-models]: https://docs.pr-agent.ai/usage-guide/changing_a_model/
[pr-review]: https://docs.pr-agent.ai/tools/review/
[pr-describe]: https://docs.pr-agent.ai/tools/describe/
[pr-improve]: https://docs.pr-agent.ai/tools/improve/
[pr-ask]: https://docs.pr-agent.ai/tools/ask/
[ai-review]: https://github.com/Nikita-Filonov/ai-review
[ai-license]: https://raw.githubusercontent.com/Nikita-Filonov/ai-review/main/LICENSE
[kodus]: https://github.com/kodustech/kodus-ai
[kodus-license]: https://raw.githubusercontent.com/kodustech/kodus-ai/main/license.md
[kodus-hosting]: https://kodus.io/self-hosted-ai-code-review/
[danger-repo]: https://github.com/danger/danger-js
[danger-license]: https://raw.githubusercontent.com/danger/danger-js/main/LICENSE
[danger-gitlab]: https://danger.systems/js/usage/gitlab.html
[danger-bitbucket]: https://danger.systems/js/usage/bitbucket_server
[danger-api]: https://danger.systems/js/reference.html
[reviewdog]: https://github.com/reviewdog/reviewdog
[reviewdog-license]: https://raw.githubusercontent.com/reviewdog/reviewdog/master/LICENSE
[coderabbit-platforms]: https://docs.coderabbit.ai/platforms/overview
[coderabbit-hosting]: https://docs.coderabbit.ai/self-hosted/overview
[codacy-ai]: https://docs.codacy.com/codacy-ai/codacy-ai/
[codacy-pricing]: https://www.codacy.com/pricing
[glab]: https://docs.gitlab.com/cli/
[glab-versions]: https://gitlab.com/gitlab-org/cli/-/raw/main/README.md
[gitlab-job-token]: https://docs.gitlab.com/ci/jobs/ci_job_token/
[gitlab-discussions]: https://docs.gitlab.com/api/discussions/
[jenkins-pipeline]: https://www.jenkins.io/doc/book/pipeline/jenkinsfile/
[jenkins-ai]: https://plugins.jenkins.io/ai-agent/
[jenkins-mcp]: https://plugins.jenkins.io/mcp-server/
[argo]: https://argo-workflows.readthedocs.io/en/latest/walk-through/hello-world/
[bitbucket-builds]: https://confluence.atlassian.com/spaces/BITBUCKETSERVER100/pages/1680278877/Bamboo%2Bintegration
[atlassian-mcp]: https://github.com/atlassian/atlassian-mcp-server
[community-atlassian]: https://github.com/sooperset/mcp-atlassian
[codex]: https://developers.openai.com/codex/noninteractive/
[claude-headless]: https://code.claude.com/docs/en/headless
[opencode-cli]: https://opencode.ai/docs/cli/
[opencode-permissions]: https://opencode.ai/docs/permissions/
[claude-security]: https://code.claude.com/docs/en/security
[secure-agents]: https://code.claude.com/docs/en/agent-sdk/secure-deployment
[semgrep]: https://docs.semgrep.dev/deployment/oss-deployment
[osv]: https://google.github.io/osv-scanner/
