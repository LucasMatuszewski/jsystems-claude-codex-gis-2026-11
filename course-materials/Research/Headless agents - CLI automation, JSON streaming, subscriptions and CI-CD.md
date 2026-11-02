# AI Coding Agents in Headless Mode

## CLI automation, JSON streaming, structured output, subscriptions, and CI/CD

**Validated:** October 1, 2026  
**Tools covered:** Claude Code, OpenAI Codex CLI, Google Antigravity CLI (`agy`), Grok Build, GitHub Copilot CLI, OpenCode

> **Important:** AI coding CLIs are changing extremely quickly. Commands, authentication rules, subscription limits, and billing behavior in this document were validated against current official documentation on October 1, 2026. Revalidate them before using this material much later.

---

# 1. What is "headless mode"?

Interactive coding agents normally start a terminal UI:

```bash
claude
codex
agy
grok
copilot
opencode
```

In **headless**, **non-interactive**, or **programmatic** mode, we instead provide the task directly:

```bash
agent-command "do this task"
```

The agent:

1. receives the task,
2. analyzes the repository,
3. optionally invokes tools and shell commands,
4. may edit files,
5. returns a result,
6. exits.

This makes CLI coding agents usable as ordinary operating-system processes.

For example:

```bash
codex exec "Find the failing tests, fix them, and run the test suite"
```

or:

```bash
claude -p "Review this repository for security problems"
```

This enables several important workflows:

- delegate work locally without keeping an interactive agent open,
- invoke an agent from shell scripts,
- invoke agents from Node.js, Python, Rust, etc.,
- run agents from CI/CD,
- perform automated code review,
- generate migrations, tests, documentation, or release notes,
- create your own higher-level agent orchestrator,
- run several coding agents concurrently,
- capture the entire execution as JSON events.

---

# 2. Three different concepts that should not be confused

There are three increasingly powerful integration levels.

## 2.1 Non-interactive execution

Example:

```bash
claude -p "Fix the tests"
```

The process does some work, prints a response, and exits.

This is sufficient for basic shell scripts.

---

## 2.2 JSON / JSONL event streams

Instead of human-readable terminal output, the CLI emits machine-readable events such as:

```json
{"type":"tool","name":"run_command","command":"npm test"}
{"type":"tool","name":"edit_file","path":"src/auth.ts"}
{"type":"result","status":"success"}
```

The exact schemas differ between products.

Most modern coding agents now support this.

JSON event streams let another program observe:

- agent messages,
- tool calls,
- commands,
- edits,
- token usage,
- costs,
- errors,
- subagents,
- final results.

This is the foundation for building your own agent orchestrator.

---

## 2.3 Schema-constrained structured output

This is different from merely receiving execution events as JSON.

A schema-capable agent can be told:

> Your final result must conform to this JSON Schema.

For example:

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "summary": { "type": "string" },
    "changedFiles": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["success", "summary", "changedFiles"]
}
```

Your program can then reliably consume the result without parsing natural-language text.

As of October 2026, **Claude Code, Codex, and Antigravity CLI expose this directly through their CLIs**. OpenCode supports it through its SDK. Current Grok Build and Copilot CLI documentation exposes JSON event streams but does not document an equivalent CLI flag that constrains the final answer to an arbitrary JSON Schema.

---

# 3. Quick comparison

| Tool | Non-interactive command | JSON event output | Streaming | Final JSON Schema | Subscription usable locally? | Persistent integration |
|---|---|---|---|---|---|---|
| **Claude Code** | `claude -p` | `--output-format json` | `stream-json` | ✅ `--json-schema` | ✅ | Agent SDK |
| **OpenAI Codex** | `codex exec` | `--json` | JSONL | ✅ `--output-schema` | ✅ | `app-server` |
| **Antigravity** | `agy -p` | `--output-format json` | `stream-json` | ✅ `--json-schema` | ✅ | bidirectional `stream-json` |
| **Grok Build** | `grok -p` | `--output-format json` | `streaming-json` | Not documented in CLI | ✅ account auth | ACP |
| **GitHub Copilot** | `copilot -p` | `--output-format json` | JSONL | Not documented in CLI | ✅ | ACP / SDK server |
| **OpenCode** | `opencode run` | `--format json` | NDJSON events | SDK only | ✅ provider-dependent | HTTP server + SDK |

The terminology is annoyingly inconsistent:

```text
Claude       stream-json
Antigravity  stream-json
Grok         streaming-json
Codex        --json
Copilot      --output-format json
OpenCode     --format json
```

All of these can represent streams of newline-delimited JSON events, but their event schemas are different.

---

# 4. Claude Code

## 4.1 Basic headless execution

Claude's non-interactive mode is:

```bash
claude -p "Fix the failing tests"
```

`-p` is an alias of `--print`.

Anthropic explicitly documents this mode for scripts and CI/CD.

Example with tools:

```bash
claude -p \
  "Run the tests and fix any failures" \
  --allowedTools "Bash,Read,Edit"
```

Exit code `0` indicates success; failures produce a non-zero exit code.

---

## 4.2 JSON output

Single JSON result:

```bash
claude -p \
  "Summarize this project" \
  --output-format json
```

Claude returns metadata together with the final result.

---

## 4.3 Streaming JSON

```bash
claude -p \
  "Explain this repository" \
  --output-format stream-json
```

For token-level streaming:

```bash
claude -p \
  "Explain this repository" \
  --output-format stream-json \
  --verbose \
  --include-partial-messages
```

The stream consists of newline-delimited JSON messages. The final message is a result event containing the final answer and session metadata.

---

## 4.4 JSON Schema output

Claude Code supports schema-constrained output directly:

```bash
claude -p \
  "Find the most important problems in this repository" \
  --output-format json \
  --json-schema '{
    "type":"object",
    "properties":{
      "problems":{
        "type":"array",
        "items":{"type":"string"}
      }
    },
    "required":["problems"]
  }'
```

The validated result appears under:

```text
structured_output
```


This is considerably safer than asking:

```text
Please respond with JSON.
```

because the CLI actually validates the requested schema.

---

# 5. Claude Code billing: subscription versus API

This changed several times during 2026 and is important.

## Normal `claude -p`

As of October 1, 2026:

```bash
claude -p "..."
```

**can consume the normal Claude subscription allowance**.

Anthropic had announced a separate Agent SDK credit system, but that change was paused. Anthropic's current notice explicitly says that `claude -p` and Agent SDK usage continue to consume subscription usage limits and that the previously announced separate Agent SDK monthly credit is not currently active.

### Important environment-variable trap

If this exists:

```bash
ANTHROPIC_API_KEY=...
```

Claude Code uses the API key instead of your subscription.

In `-p` mode the API key wins automatically.

Anthropic explicitly documents:

```bash
unset ANTHROPIC_API_KEY
```

when you want to return to subscription authentication.

Therefore:

```text
Claude OAuth login
       ↓
claude -p
       ↓
subscription usage

ANTHROPIC_API_KEY
       ↓
claude -p
       ↓
Claude Platform / API billing
```

---

# 6. Claude `--bare` changes the situation

Anthropic now recommends `--bare` for deterministic scripted and SDK use:

```bash
claude --bare -p "Summarize README.md"
```

Bare mode skips automatic discovery of:

- hooks,
- skills,
- custom commands,
- subagents,
- plugins,
- MCP servers,
- auto memory,
- `CLAUDE.md`,
- other normal interactive context.

That makes automation more reproducible and is particularly useful in CI.

However:

> **`--bare` does not use the subscription OAuth login.**

For Anthropic-hosted models it requires:

```bash
ANTHROPIC_API_KEY
```

or another explicitly configured provider credential.

So:

```text
claude -p
→ can use subscription

claude --bare -p
→ does not use subscription OAuth
→ API/provider credentials required
```

Anthropic also states that `--bare` is the recommended mode for scripted and SDK calls and is intended to become the default for `-p` in a future release.

### Practical guideline

Use:

```bash
claude -p
```

for **personal/local subscription-backed delegation**.

Prefer:

```bash
claude --bare -p
```

with proper machine credentials for **deterministic production CI automation**.

---

# 7. Claude usage after subscription limits

Pro and Max users can optionally enable **usage credits**.

After the included plan allowance has been exhausted, additional Claude and Claude Code usage can then continue at standard API rates.

These charges are separate from the subscription and can be disabled or capped.

For predictable costs during training or personal automation, participants who do not want overage charges should disable usage credits.

---

# 8. OpenAI Codex CLI

Codex has a particularly clean non-interactive interface.

## 8.1 Headless execution

```bash
codex exec "Fix the failing tests"
```

or:

```bash
codex e "Fix the failing tests"
```

OpenAI describes `codex exec` as the mode for **scripted or CI-style runs that should finish without human interaction**.

---

## 8.2 JSON event streaming

```bash
codex exec --json \
  "Review this repository"
```

`--json` changes stdout into a **newline-delimited JSON event stream**, one object for each state change.

This makes Codex easy to integrate into another process.

---

## 8.3 JSON Schema result

Create:

```json
{
  "type": "object",
  "properties": {
    "success": { "type": "boolean" },
    "summary": { "type": "string" },
    "changed_files": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["success", "summary", "changed_files"],
  "additionalProperties": false
}
```

Save it as:

```text
result.schema.json
```

Then:

```bash
codex exec \
  --output-schema result.schema.json \
  "Implement the requested feature and report the result"
```

OpenAI documents `--output-schema` as a JSON Schema describing the expected final response shape.

You can also combine event tracing with structured output:

```bash
codex exec \
  --json \
  --output-schema result.schema.json \
  "Analyze this repository"
```

---

# 9. Codex subscription versus API billing

Codex supports two OpenAI authentication paths:

```text
Sign in with ChatGPT
→ subscription access

Sign in with API key
→ usage-based API access
```

This distinction is explicitly documented by OpenAI.

Local subscription usage:

```bash
codex login
codex exec "..."
```

The browser OAuth session is cached and reused.

API authentication:

```bash
printenv OPENAI_API_KEY | codex login --with-api-key
```

With an API key, usage is billed through the OpenAI Platform at standard API pricing rather than using included ChatGPT plan usage.

OpenAI currently recommends API-key authentication as the default for programmatic CI/CD workflows.

For ChatGPT Enterprise, OpenAI additionally supports **Codex access tokens** for trusted non-interactive automation that needs ChatGPT workspace entitlements without browser login.

---

# 10. Codex sandboxing

Codex provides explicit sandbox modes:

```bash
--sandbox read-only
--sandbox workspace-write
--sandbox danger-full-access
```

For example, a review job should normally use:

```bash
codex exec \
  --sandbox read-only \
  "Review this repository and report bugs"
```

A task that must modify the checkout can use:

```bash
codex exec \
  --sandbox workspace-write \
  "Fix the failing tests"
```

There is also:

```bash
--yolo
```

which bypasses approvals and sandboxing.

OpenAI explicitly labels this dangerous and recommends it only inside an isolated runner.

---

# 11. Codex with local models

Codex also supports:

```bash
codex exec --oss ...
```

with supported local providers such as:

```text
Ollama
LM Studio
```

This provides another automation model:

```text
Codex agent runtime
+
local model
+
no OpenAI inference bill
```


---

# 12. Google Antigravity CLI (`agy`)

Antigravity currently has one of the richest headless protocols.

## 12.1 Basic headless mode

```bash
agy -p "Fix the failing tests"
```

Aliases:

```bash
agy --print "..."
agy --prompt "..."
```

The result goes to stdout while diagnostics go to stderr.

Headless mode uses cached Antigravity credentials. Google recommends authenticating once through an interactive `agy` session. If an unauthenticated non-interactive environment has no terminal, the process exits with an authentication error instead of hanging.

---

# 13. Antigravity output formats

Human-readable:

```bash
agy -p "Explain this project"
```

Single JSON object:

```bash
agy -p \
  "Explain this project" \
  --output-format json
```

Streaming events:

```bash
agy -p \
  "Explain this project" \
  --output-format stream-json
```

`stream-json` emits NDJSON events such as:

```text
init
step_update
result
```

Tool events can contain command parameters, outputs, token usage, and subagent information.

---

# 14. Antigravity JSON Schema

Antigravity directly supports:

```bash
agy -p \
  "Analyze this repository" \
  --output-format json \
  --json-schema result.schema.json
```

The response contains fields including:

```text
structured_output
json_schema
```

The schema also applies to the terminal result event when streaming.

This puts Antigravity in the same category as Claude Code and Codex for reliable structured orchestration.

---

# 15. Persistent Antigravity process

Antigravity has a particularly useful feature for custom orchestrators:

```bash
agy \
  --input-format stream-json \
  --output-format stream-json
```

Instead of spawning a new process for every task, your application can keep one `agy` process alive.

You send NDJSON messages into stdin:

```json
{"event":"user","message":{"content":"Inspect the repository"}}
```

receive events from stdout, wait for:

```json
{"event":"result", ...}
```

and then send another prompt.

The same process keeps conversation context.

Google explicitly describes this mode as suitable for applications that dynamically choose subsequent prompts based on previous answers.

This is excellent for building a custom parent agent in Node.js, Python, Rust, etc.

---

# 16. Antigravity subscription and billing

Antigravity CLI is part of Antigravity's plan-based quota system.

Current Google documentation says **all plans receive access to product features including the CLI**.

Quota differs by plan:

- Google AI Ultra → highest quota and five-hour refreshes,
- Google AI Pro → high quota and five-hour refreshes until the weekly limit,
- users without Pro/Ultra → weekly baseline quota.

Pro and Ultra users can optionally consume purchased AI credits after baseline quota is exhausted.

Google currently says Antigravity does **not** support BYOK or BYO endpoints for obtaining additional rate limits.

Therefore local headless automation can naturally consume the user's normal Antigravity quota.

The caveat is CI:

```text
agy headless
→ expects cached authenticated credentials
```

A fresh ephemeral CI machine without existing authentication will fail authentication.

That makes Antigravity especially convenient for:

- local automation,
- developer workstations,
- long-lived authenticated runners,

while ephemeral production CI requires more deliberate credential provisioning.

---

# 17. Grok Build

## 17.1 Headless execution

```bash
grok -p "Fix the failing tests"
```

xAI explicitly documents this for scripts, bots, and machine-oriented work.

Useful options include:

```bash
--session-id
--resume
--continue
--cwd
--max-turns
--allow
--deny
--sandbox
```

For deterministic automated environments xAI recommends disabling update checks:

```bash
grok --no-auto-update -p "..."
```


---

# 18. Grok JSON streaming

Single JSON object:

```bash
grok -p \
  "Review this repository" \
  --output-format json
```

Streaming:

```bash
grok -p \
  "Review this repository" \
  --output-format streaming-json
```

Notice the spelling:

```text
Antigravity → stream-json
Grok        → streaming-json
```

Grok emits newline-delimited incremental JSON events.

---

# 19. Grok structured output

Current Grok Build CLI documentation exposes:

```text
plain
json
streaming-json
```

but I found **no documented Grok Build CLI equivalent** of:

```text
--json-schema
--output-schema
```

in the current headless or CLI reference.

Therefore course participants should treat Grok's JSON output as **machine-readable execution/result serialization**, not as documented schema-enforced final output.

The underlying xAI APIs have their own structured-output capabilities, but that should not be confused with a Grok Build CLI feature.

---

# 20. Grok subscription/account versus API key

Normal Grok Build can authenticate through a Grok account.

For remote/headless machines:

```bash
grok login --device-auth
```

uses device-code authentication.

For CI/CD, xAI explicitly documents:

```bash
export XAI_API_KEY="xai-..."
grok -p "Review this diff" --output-format json
```

and recommends `XAI_API_KEY` for CI/CD and headless automation.

Therefore:

```text
Browser/device authentication
→ Grok account entitlement

XAI_API_KEY
→ xAI API account / API billing
```

The current Grok Build website says that Grok Build is **available to try for free**.

However, the current CLI documentation does not enumerate consumer-plan CLI quotas precisely enough to state that every Grok subscription tier receives a particular fixed amount of Grok Build CLI usage.

For course material, avoid promising a particular Grok Build quota unless it is rechecked immediately before the course.

---

# 21. Grok ACP integration

For applications that need a persistent agent rather than repeated CLI calls:

```bash
grok agent stdio
```

starts Grok as an **Agent Client Protocol (ACP)** agent.

The protocol runs as JSON-RPC over stdin/stdout.

Instead of:

```text
spawn Grok
→ task
→ exit
→ spawn Grok again
```

you can build:

```text
your Node.js application
        ↕ JSON-RPC
Grok ACP process
        ↕
agent session
```

This is preferable for more sophisticated agent orchestration.

---

# 22. GitHub Copilot CLI

## 22.1 Programmatic mode

Copilot's one-shot interface is:

```bash
copilot -p "Fix the failing tests"
```

or:

```bash
copilot --prompt "..."
```

GitHub explicitly documents this mode for scripts, automation, and CI/CD.

To prevent the agent from waiting for human clarification:

```bash
copilot -p \
  "Run the tests and fix failures" \
  --no-ask-user
```

Permissions can be narrowed:

```bash
--allow-tool='shell(npm:*)'
--allow-tool='write'
```

GitHub recommends granting only the tools required for the task.

---

# 23. Copilot JSON output

```bash
copilot -p \
  "Review this repository" \
  --output-format json
```

The current programmatic reference says this emits **JSONL - one JSON object per line**.

Current official CLI documentation does not document an arbitrary final-result equivalent of:

```text
--json-schema
--output-schema
```

Therefore JSONL is excellent for monitoring the agent but should not be treated as guaranteed final-result schema enforcement.

---

# 24. Copilot subscription and automation

Copilot CLI is available with GitHub Copilot plans, subject to organization policy where applicable.

Locally, users normally authenticate through GitHub OAuth.

For automated environments, supported authentication variables include:

```text
COPILOT_GITHUB_TOKEN
GH_TOKEN
GITHUB_TOKEN
```


These are **GitHub authentication tokens**, not provider API keys.

Using one does not automatically mean:

```text
OpenAI API billing
```

or:

```text
Anthropic API billing
```

The request can still be handled as GitHub Copilot usage.

---

# 25. Copilot in GitHub Actions

Copilot has unusually good first-party GitHub Actions integration.

With a user PAT, AI usage is attributed to that user's Copilot seat.

With the built-in:

```text
GITHUB_TOKEN
```

in an organization-owned repository, usage can instead be metered directly to the organization when the appropriate Copilot policy is enabled.

GitHub recommends this organization-attributed approach for GitHub Actions automation because the token is short-lived and scoped to the workflow.

Example concept:

```yaml
permissions:
  contents: read
  copilot-requests: write

steps:
  - uses: actions/checkout@v6

  - name: AI review
    env:
      GITHUB_TOKEN: ${{ github.token }}
    run: |
      copilot -p \
        "Review this repository for likely defects. Do not modify files." \
        --output-format json \
        --no-ask-user
```

The organization must allow Copilot CLI requests billed to the organization for this model.

---

# 26. Copilot AI-credit limits

Copilot allows a programmatic session budget:

```bash
copilot -p \
  "Implement the feature" \
  --max-ai-credits 50
```

The agent stops when it reaches the configured soft session limit.

GitHub currently describes one AI credit as `$0.01` and notes that session caps are soft because an in-progress request may finish after the boundary has been crossed.

This is useful for unattended automation because one accidental agent loop cannot consume an unlimited session budget.

---

# 27. Copilot BYOK

Copilot also supports using external model providers.

When BYOK provider credentials are configured, model inference can be sent to your chosen provider rather than GitHub-hosted inference.

In that configuration:

```text
GitHub Copilot interface/runtime
+
your OpenAI / Anthropic / Azure credentials
```

means provider usage is billed according to that provider.

GitHub authentication is not required merely to use BYOK inference, although GitHub-hosted features may still require it.

This should not be confused with:

```text
COPILOT_GITHUB_TOKEN
```

which is a GitHub authentication token.

---

# 28. Copilot as a persistent agent server

Copilot provides two advanced integration modes.

## ACP

```bash
copilot --acp --stdio
```

or:

```bash
copilot --acp --port 3000
```

ACP support is currently in public preview.

The protocol uses NDJSON and is explicitly intended for scenarios including:

- custom clients,
- IDE integrations,
- CI/CD,
- multi-agent systems.


## Copilot SDK headless server

```bash
copilot --headless --port 4321
```

starts a persistent backend process.

Applications using the Copilot SDK can connect to it instead of starting a new CLI process for every task. Multiple SDK clients can share the server.

---

# 29. OpenCode

OpenCode differs from the other tools because it is a **provider-independent coding-agent runtime**.

## 29.1 Non-interactive mode

```bash
opencode run "Fix the failing tests"
```

This sends one task without opening the interactive UI.

---

# 30. OpenCode JSON

```bash
opencode run \
  --format json \
  "Review this repository"
```

The current CLI documentation says this emits **newline-delimited JSON events** suitable for scripts.

---

# 31. OpenCode structured output

The current `opencode run` CLI documentation does not expose a documented `--json-schema` flag.

However, the **OpenCode SDK does** support validated structured output:

```ts
const result = await client.session.prompt({
  path: { id: sessionId },
  body: {
    parts: [
      {
        type: "text",
        text: "Analyze this repository"
      }
    ],
    format: {
      type: "json_schema",
      schema: {
        type: "object",
        properties: {
          summary: { type: "string" }
        },
        required: ["summary"]
      }
    }
  }
})
```

Validated data is available under:

```ts
result.data.info.structured_output
```


So:

```text
OpenCode CLI event JSON       ✅
OpenCode CLI JSON Schema      not documented
OpenCode SDK JSON Schema      ✅
```

---

# 32. OpenCode as a headless HTTP service

OpenCode can also become a persistent server:

```bash
opencode serve
```

This exposes an HTTP API described by an OpenAPI 3.1 specification.

The server includes event-stream endpoints and is the same underlying architecture used by OpenCode clients.

OpenCode explicitly recommends the server for programmatic integration.

This enables:

```text
your application
      ↓ HTTP
OpenCode server
      ↓
agent sessions
      ↓
configured model provider
```

instead of spawning `opencode run` for every task.

---

# 33. OpenCode subscriptions versus API keys

Because OpenCode supports many providers, there is no single billing model.

Current OpenCode documentation explicitly supports subscription-backed authentication for several providers.

## ChatGPT Plus / Pro

OpenCode currently supports:

```text
/connect
→ OpenAI
→ ChatGPT Plus/Pro
```

using browser authentication.

Therefore OpenCode can use eligible ChatGPT subscription access instead of an OpenAI API key.

---

## GitHub Copilot

OpenCode explicitly supports:

```text
/connect
→ GitHub Copilot
→ device-code OAuth
```

using the user's GitHub Copilot subscription.

---

## SuperGrok / Grok subscription

OpenCode also supports xAI device-code OAuth:

```text
/connect
→ xAI
→ SuperGrok Subscription
```

The current documentation says that supported Grok/X Premium plans providing the necessary Grok access do not require a separate `XAI_API_KEY`.

---

# 34. Important: Claude subscriptions in OpenCode

This is an important exception.

OpenCode's own provider documentation explicitly warns that plugins using **Claude Pro/Max subscription models through OpenCode are prohibited by Anthropic**, and states that OpenCode stopped bundling such plugins starting with version 1.3.0.

Therefore course participants should **not** be taught to use Claude Pro/Max subscription credentials through OpenCode.

If they want Anthropic models in OpenCode, the safe documented approach is to use supported Anthropic API/provider credentials.

This is different from using:

```bash
claude -p
```

inside the official Claude Code product, where subscription usage is currently supported.

---

# 35. OpenCode Go

OpenCode additionally offers **OpenCode Go**, its own subscription.

Current pricing is:

```text
$5 first month
$10/month afterwards
```

on the current V2 page.

The subscription provides an API-key-shaped credential:

```text
OpenCode Go subscription
→ API key credential
→ included Go subscription quota
```

The presence of an "API key" here therefore does **not** mean ordinary pay-per-token billing.

OpenCode Go has included usage limits, and users can optionally enable fallback to PAYG console balance after those limits are reached.

This illustrates an important general rule:

> **The existence of a key or token does not by itself tell you how usage is billed.**

A credential can authenticate:

- a subscription,
- a user account,
- an organization,
- or a PAYG API account.

Always check the billing model behind the credential.

---

# 36. Recommended local subscription-backed commands

Once the tools have been authenticated interactively, a developer can delegate work locally like this.

## Claude

Make sure an unwanted API key is not overriding the subscription:

```bash
unset ANTHROPIC_API_KEY

claude -p \
  "Run the unit tests, diagnose failures, fix the implementation, and rerun the tests."
```

---

## Codex

```bash
codex login

codex exec \
  --sandbox workspace-write \
  "Run the tests, fix failures, and verify the final result."
```

---

## Antigravity

Authenticate once interactively:

```bash
agy
```

then:

```bash
agy -p \
  "Run the tests, fix failures, and verify the result."
```

---

## Grok Build

After browser/device authentication:

```bash
grok -p \
  "Run the tests, fix failures, and verify the result."
```

---

## Copilot

After GitHub authentication:

```bash
copilot -p \
  "Run the tests, fix failures, and verify the result." \
  --no-ask-user
```

---

## OpenCode

Configure the desired provider once with:

```text
/connect
```

then:

```bash
opencode run \
  "Run the tests, fix failures, and verify the result."
```

---

# 37. A better delegation pattern: isolated Git worktrees

For autonomous write tasks, default to one checkout with disjoint files/folders and a dependency plan; only the coordinator changes branches, stages files or creates commits. Use a temporary Git worktree only when agents must change the same files in parallel in separate checkouts. Agree contracts, integrate sequentially and resolve conflicts before tests; worktrees do not eliminate merge conflicts. Put a no-default-worktrees rule in AGENTS.md because dependency installs consume disk and CPU and agents often forget cleanup. The following commands illustrate that explicit exception:

```bash
git worktree add ../agent-task -b ai/task
cd ../agent-task
```

Then run the coding agent there:

```bash
codex exec \
  --sandbox workspace-write \
  "Implement issue #123 and run the tests"
```

or:

```bash
claude -p \
  "Implement issue #123 and run the tests" \
  --allowedTools "Read,Edit,Bash"
```

When finished:

```bash
git diff
git status
```

This gives the agent an isolated checkout and makes its changes easy to inspect or discard.

The same architecture works particularly well when several agents execute tasks concurrently:

```text
main repository
      │
      ├── worktree-task-a → agent A
      ├── worktree-task-b → agent B
      └── worktree-task-c → agent C
```

---

# 38. Capture an agent trace as JSONL

JSONL traces are valuable for:

- debugging,
- observability,
- cost analysis,
- audit logs,
- agent evaluations,
- detecting tool use,
- measuring regressions.

Examples:

## Codex

```bash
set -o pipefail

codex exec \
  --json \
  "Run the tests and diagnose failures" \
  | tee codex-trace.jsonl
```

## Antigravity

```bash
set -o pipefail

agy -p \
  "Run the tests and diagnose failures" \
  --output-format stream-json \
  | tee agy-trace.jsonl
```

## Grok

```bash
set -o pipefail

grok -p \
  "Run the tests and diagnose failures" \
  --output-format streaming-json \
  | tee grok-trace.jsonl
```

## Copilot

```bash
set -o pipefail

copilot -p \
  "Run the tests and diagnose failures" \
  --output-format json \
  --no-ask-user \
  | tee copilot-trace.jsonl
```

## OpenCode

```bash
set -o pipefail

opencode run \
  --format json \
  "Run the tests and diagnose failures" \
  | tee opencode-trace.jsonl
```

---

# 39. Programmatically run an agent from TypeScript

Because these tools are ordinary processes, Node.js can spawn them.

```ts
import { spawn } from "node:child_process";
import { createInterface } from "node:readline";

type JsonEvent = Record<string, unknown>;

async function runJsonAgent(
  command: string,
  args: string[],
  onEvent: (event: JsonEvent) => void,
): Promise<number> {
  const child = spawn(command, args, {
    stdio: ["ignore", "pipe", "pipe"],
  });

  const lines = createInterface({
    input: child.stdout,
  });

  lines.on("line", (line) => {
    if (!line.trim()) return;

    try {
      onEvent(JSON.parse(line));
    } catch {
      console.warn("Non-JSON stdout:", line);
    }
  });

  child.stderr.on("data", (chunk) => {
    process.stderr.write(chunk);
  });

  return await new Promise<number>((resolve, reject) => {
    child.once("error", reject);

    child.once("exit", (code) => {
      resolve(code ?? 1);
    });
  });
}
```

Run Codex:

```ts
const exitCode = await runJsonAgent(
  "codex",
  [
    "exec",
    "--json",
    "Inspect the repository and report all failing tests",
  ],
  (event) => {
    console.log("Codex event:", event);
  },
);

if (exitCode !== 0) {
  throw new Error(`Codex failed: ${exitCode}`);
}
```

Equivalent argument arrays include:

```ts
const commands = {
  claude: [
    "claude",
    [
      "-p",
      "Inspect the repository",
      "--output-format",
      "stream-json",
      "--verbose",
    ],
  ],

  codex: [
    "codex",
    [
      "exec",
      "--json",
      "Inspect the repository",
    ],
  ],

  antigravity: [
    "agy",
    [
      "-p",
      "Inspect the repository",
      "--output-format",
      "stream-json",
    ],
  ],

  grok: [
    "grok",
    [
      "-p",
      "Inspect the repository",
      "--output-format",
      "streaming-json",
    ],
  ],

  copilot: [
    "copilot",
    [
      "-p",
      "Inspect the repository",
      "--output-format",
      "json",
      "--no-ask-user",
    ],
  ],

  opencode: [
    "opencode",
    [
      "run",
      "--format",
      "json",
      "Inspect the repository",
    ],
  ],
};
```

Using `spawn(command, args)` rather than building a shell command string also reduces shell-injection risk.

---

# 40. Schema-first orchestration

When a CLI supports JSON Schema, define the contract first.

For example:

```json
{
  "type": "object",
  "properties": {
    "status": {
      "type": "string",
      "enum": ["success", "partial", "failed"]
    },
    "summary": {
      "type": "string"
    },
    "changed_files": {
      "type": "array",
      "items": {
        "type": "string"
      }
    },
    "tests_passed": {
      "type": "boolean"
    },
    "follow_up_required": {
      "type": "boolean"
    }
  },
  "required": [
    "status",
    "summary",
    "changed_files",
    "tests_passed",
    "follow_up_required"
  ],
  "additionalProperties": false
}
```

Then use the same conceptual contract across agents.

## Codex

```bash
codex exec \
  --json \
  --output-schema task-result.schema.json \
  "Implement the feature and verify it"
```

## Antigravity

```bash
agy -p \
  "Implement the feature and verify it" \
  --output-format stream-json \
  --json-schema task-result.schema.json
```

## Claude

Claude currently expects the schema value through `--json-schema`; for example:

```bash
claude -p \
  "Implement the feature and verify it" \
  --output-format json \
  --json-schema "$(cat task-result.schema.json)"
```

For Grok, Copilot, or the OpenCode CLI, validate the agent's final JSON in your application yourself or move to the corresponding SDK/API where structured output is available.

---

# 41. CI/CD pattern: AI code review

A relatively safe CI use case is **read-only code review**.

The agent should not need permission to modify files or deploy anything.

Conceptually:

```text
checkout
   ↓
read-only AI agent
   ↓
structured findings
   ↓
CI artifact / PR comment / job summary
```

For Codex:

```bash
codex exec \
  --sandbox read-only \
  --json \
  "Review the changes against main. Report likely bugs and security problems. Do not modify anything."
```

For Claude, an even safer pattern is feeding the diff through stdin:

```bash
git diff origin/main...HEAD |
  claude --bare -p \
    "Review this diff for correctness and security problems. Do not suggest cosmetic changes." \
    --output-format json
```

Here Claude does not need filesystem or shell permission to obtain the diff.

---

# 42. CI/CD pattern: autonomous repair

A more powerful pipeline might be:

```text
checkout
   ↓
create isolated workspace
   ↓
run tests
   ↓
agent diagnoses failure
   ↓
agent edits files
   ↓
run tests again
   ↓
collect diff
   ↓
human review / PR
```

The crucial difference is that the agent now has write and command-execution permissions.

Use an isolated runner or container.

For Codex:

```bash
codex exec \
  --sandbox workspace-write \
  --json \
  "Run the tests, fix the failures, and rerun all affected tests."
```

For Grok:

```bash
grok --no-auto-update \
  -p "Run the tests, fix failures, and rerun them." \
  --output-format streaming-json \
  --sandbox <your-restricted-profile>
```

For Copilot, explicitly allow only required commands and file writes rather than enabling every tool.

---

# 43. Recommended CI authentication by tool

## Claude

For deterministic ephemeral CI:

```text
ANTHROPIC_API_KEY
+
claude --bare -p
```

This is API/provider usage, not subscription OAuth.

---

## Codex

Default official guidance for programmatic CI:

```text
OPENAI_API_KEY
+
codex login --with-api-key
+
codex exec
```

API billing applies.

Enterprise environments can instead consider Codex access tokens where appropriate.

---

## Antigravity

`agy -p` uses cached credentials.

It works naturally on already-authenticated machines and persistent runners.

A fresh unauthenticated ephemeral runner will fail authentication, and Antigravity currently does not offer ordinary BYOK as a mechanism for obtaining more quota.

---

## Grok

xAI explicitly documents:

```text
XAI_API_KEY
```

for CI/CD and headless automation.

---

## Copilot

In GitHub Actions:

```text
GITHUB_TOKEN
```

is particularly attractive for organization-owned automation.

Outside Actions:

```text
COPILOT_GITHUB_TOKEN
```

or other supported GitHub credentials can authenticate the CLI.

---

## OpenCode

OpenCode's own CI example recommends:

```text
provider API key stored as CI secret
+
opencode run --standalone
```


Because OpenCode is provider-independent, the exact credential depends on the selected model provider.

---

# 44. Subscription-backed automation versus production CI

A useful rule for participants is:

## Personal/local delegation

Prefer existing authenticated subscription sessions where officially supported.

Examples:

```text
Claude Code      → Claude subscription
Codex            → ChatGPT subscription
Antigravity      → Google AI / Antigravity quota
Grok Build       → Grok account entitlement
Copilot CLI      → Copilot subscription
OpenCode         → supported provider subscription
```

This is convenient for:

- personal scripts,
- local automation,
- experiments,
- training exercises,
- developer productivity tools.

---

## Shared production CI

Prefer:

- machine-oriented credentials,
- short-lived tokens where available,
- organization-attributed billing,
- explicit spending limits,
- isolated runners,
- predictable permissions.

Do not build organizational production automation around someone's personal cached browser session unless the provider explicitly supports and recommends that architecture.

---

# 45. Persistent integration options

Repeatedly spawning a CLI is simple but not always efficient.

For more advanced software, consider persistent protocols:

| Tool | Persistent/programmatic option |
|---|---|
| Claude | Claude Agent SDK |
| Codex | Codex `app-server` |
| Antigravity | bidirectional `--input-format stream-json` |
| Grok | ACP via `grok agent stdio` |
| Copilot | ACP or Copilot SDK headless server |
| OpenCode | `opencode serve` + OpenAPI/SDK |

This architecture:

```text
Application
    │
    ├── create session
    ├── send task
    ├── consume events
    ├── react to result
    └── send next task
          ↓
persistent agent runtime
```

is preferable when building an actual multi-agent application.

For simple CI jobs, one-shot commands remain easier to operate.

---

# 46. Example: parent agent delegates to two coding agents

A custom orchestrator could do:

```text
Issue
 ↓
Planner
 ↓
┌────────────────────┬────────────────────┐
│ Codex              │ Claude             │
│ implementation     │ independent review │
└────────────────────┴────────────────────┘
 ↓
Verifier
 ↓
Tests
 ↓
PR
```

Workers normally use disjoint files in one checkout and emit JSONL events. Separate worktrees are an explicit exception for necessary parallel changes to the same files, with coordinator-owned Git writes and sequential integration.

The parent process does not need to understand terminal UI output.

It only consumes machine-readable events and structured final results.

This is a major advantage of modern CLI agents over older "AI terminal assistants".

---

# 47. Security rules for unattended agents

Headless coding agents are not ordinary text-generation commands.

They can often:

- read files,
- change files,
- execute shell commands,
- access the network,
- inspect environment variables,
- interact with Git,
- use MCP tools,
- invoke subagents.

Treat them as **code-execution systems**.

## Recommended rules

1. **Grant the minimum necessary permissions.**

A review job generally does not need file writes.

2. **Use an isolated runner for autonomous modification.**

Containers, disposable VMs, or isolated worktrees are preferable.

3. **Never give broad autonomous permissions to untrusted repository content.**

A repository itself can contain instructions, hooks, agent configuration, MCP configuration, or malicious prompt-injection content.

4. **Do not expose production secrets unnecessarily.**

Only provide credentials required for the particular task.

5. **Prefer short-lived machine credentials.**

For example, GitHub Actions `GITHUB_TOKEN` is preferable to a permanent personal token when the workflow supports it.

6. **Set budgets and limits where available.**

For example:

```bash
copilot --max-ai-credits ...
grok --max-turns ...
```

7. **Set execution timeouts in your own orchestrator.**

Never assume an autonomous agent will always terminate.

8. **Check exit status as well as model output.**

An eloquent final message does not mean the process succeeded.

9. **Verify changes deterministically.**

After the agent finishes:

```bash
npm test
npm run typecheck
npm run lint
```

or the equivalent project checks.

10. **Treat agent output as untrusted input.**

Even structured JSON should be validated before triggering destructive downstream actions.

---

# 48. Claude-specific CI security caveat

There is an especially important Claude Code detail.

Without `--bare`, `claude -p` can load normal project/user configuration including:

- hooks,
- MCP configuration,
- plugins,
- skills,
- Claude configuration.

Anthropic notes that a `-p` session does not display the normal workspace trust dialog before doing this.

This is one major reason `--bare` is preferable for deterministic CI.

Do not blindly run ordinary:

```bash
claude -p
```

inside an untrusted checked-out repository with sensitive credentials.

---

# 49. Do not confuse event JSON with trusted structured output

Suppose this:

```bash
copilot -p "Find the bugs" --output-format json
```

returns JSONL.

That does **not** mean the final model message is guaranteed to match:

```ts
type Result = {
  bugs: Bug[];
  severity: number;
};
```

JSON event serialization only guarantees the transport representation.

If your program depends on a data contract:

### Prefer

```text
Claude --json-schema
Codex --output-schema
Antigravity --json-schema
OpenCode SDK json_schema
```

### Otherwise

validate the result yourself:

```ts
const result = ResultSchema.safeParse(data);

if (!result.success) {
  throw new Error("Agent returned an invalid result");
}
```

Libraries such as Zod, Valibot, JSON Schema validators, or equivalent runtime validators are appropriate for this.

---

# 50. Recommended architecture for a TypeScript orchestrator

A production-oriented TypeScript application might separate concerns like this:

```text
AgentAdapter
│
├── ClaudeAdapter
├── CodexAdapter
├── AntigravityAdapter
├── GrokAdapter
├── CopilotAdapter
└── OpenCodeAdapter
```

Expose one application-level interface:

```ts
interface AgentAdapter {
  runTask(task: AgentTask): Promise<AgentResult>;
}
```

For example:

```ts
type AgentTask = {
  cwd: string;
  prompt: string;
  allowWrites: boolean;
};

type AgentResult = {
  success: boolean;
  summary: string;
  changedFiles: string[];
};
```

Each adapter translates this into the appropriate CLI:

```text
Claude      → -p + stream-json
Codex       → exec --json
Antigravity → -p --output-format stream-json
Grok        → -p --output-format streaming-json
Copilot     → -p --output-format json
OpenCode    → run --format json
```

Your application then deals with **one internal protocol** rather than six incompatible CLI protocols.

---

# 51. Recommended course exercise

A useful hands-on exercise is:

## Step 1 - delegate locally

Ask participants to run:

```bash
<agent> "Analyze this repository and identify the most important technical-debt issue."
```

using the headless command for their chosen agent.

## Step 2 - switch to JSON events

Capture the execution trace:

```bash
<agent-json-command> > trace.jsonl
```

## Step 3 - parse the events

Write a small Node.js program that reports:

```text
number of model turns
number of shell commands
files changed
final result
```

## Step 4 - add an isolated worktree

Let the agent implement a small task in the existing checkout by default. Use a temporary worktree only for the necessary same-file parallel-work exception described in section 37, with an agreed integration and cleanup plan.

## Step 5 - verify deterministically

Run tests independently of the agent.

## Step 6 - structured output

Where supported, require:

```json
{
  "success": true,
  "summary": "...",
  "changedFiles": ["..."],
  "testsPassed": true
}
```

through JSON Schema.

## Step 7 - orchestrate two agents

Have one agent implement the change and another review it.

This demonstrates the real conceptual shift:

> AI coding agents are no longer only interactive developer tools. They can also act as programmable workers controlled by ordinary software.

---

# 52. Validated billing/authentication summary

| Tool | Subscription/account-backed local headless | Machine/API path | Important caveat |
|---|---|---|---|
| **Claude** | ✅ `claude -p` | `ANTHROPIC_API_KEY` | API key overrides subscription; `--bare` does not use subscription OAuth |
| **Codex** | ✅ ChatGPT login | OpenAI API key | API key uses standard API pricing |
| **Antigravity** | ✅ cached Antigravity/Google AI credentials | plan/enterprise-specific auth | fresh unauthenticated CI fails; no general BYOK for extra limits |
| **Grok Build** | ✅ Grok account/device OAuth | `XAI_API_KEY` | exact current consumer CLI quotas not fully enumerated |
| **Copilot CLI** | ✅ GitHub Copilot entitlement | GitHub machine token or BYOK | GitHub token ≠ model-provider API key |
| **OpenCode** | ✅ depends on provider | provider API keys | Claude Pro/Max via OpenCode is explicitly warned against |

---

# 53. Validated JSON capability summary

| Tool | Human result | One JSON result | JSON event stream | Schema-constrained final result |
|---|---:|---:|---:|---:|
| Claude Code | ✅ | ✅ | ✅ | ✅ |
| Codex | ✅ | - | ✅ JSONL | ✅ |
| Antigravity | ✅ | ✅ | ✅ NDJSON | ✅ |
| Grok Build | ✅ | ✅ | ✅ NDJSON | Not documented in CLI |
| Copilot CLI | ✅ | - | ✅ JSONL | Not documented in CLI |
| OpenCode CLI | ✅ | - | ✅ NDJSON | SDK only |

---

# 54. Corrections to earlier research

A few details changed or required clarification while this report was being revalidated.

## Claude Agent SDK credits

Anthropic previously announced separate monthly Agent SDK credits.

That change is currently **paused**.

`claude -p` still draws from subscription limits when subscription authentication is used.

---

## Claude `--bare`

The new/recently emphasized `--bare` mode changes authentication semantics.

It deliberately does not use subscription OAuth, so it should not be presented as equivalent to ordinary subscription-backed `claude -p`.

---

## OpenCode subscription integrations

Current OpenCode documentation now explicitly documents:

- ChatGPT Plus/Pro OAuth,
- GitHub Copilot subscription authentication,
- SuperGrok/xAI device OAuth.

Therefore these should no longer be described merely as uncertain legacy integrations.

---

## Claude Pro/Max through OpenCode

This should **not** be included as a recommended subscription integration.

Current OpenCode documentation explicitly says Anthropic prohibits the relevant Pro/Max integration approach.

---

## Grok Build subscriptions

Grok Build currently advertises free access to try the product, and account/device authentication works.

However, current official CLI documentation does not provide a sufficiently precise universal mapping between every consumer subscription and CLI quota.

Therefore this report deliberately does not promise a particular Grok CLI quota.

---

# 55. Final practical recommendation

For teaching **local agent delegation using existing subscriptions**, the clearest commands are:

```bash
claude -p "..."
codex exec "..."
agy -p "..."
grok -p "..."
copilot -p "..."
opencode run "..."
```

Then introduce machine-readable execution:

```bash
claude -p "..." --output-format stream-json
codex exec --json "..."
agy -p "..." --output-format stream-json
grok -p "..." --output-format streaming-json
copilot -p "..." --output-format json
opencode run --format json "..."
```

Then introduce **structured contracts**:

```text
Claude       --json-schema
Codex        --output-schema
Antigravity  --json-schema
OpenCode     SDK json_schema
```

Finally move from CLI calls to persistent integrations when building real applications:

```text
Claude Agent SDK
Codex app-server
Antigravity bidirectional stream-json
Grok ACP
Copilot ACP / SDK
OpenCode HTTP API / SDK
```

The key architectural lesson is:

> **A modern coding agent can be treated as a programmable worker.**

Interactive terminal interfaces are only one way to use them.

The same agents can be invoked from scripts, CI pipelines, backend services, orchestration systems, evaluation harnesses, and multi-agent workflows-while their tool calls and results are consumed as structured machine-readable events.

For local experimentation, subscription-backed authentication can make this surprisingly inexpensive. For shared production automation, use the provider's supported machine-authentication mechanism, explicit budgets, least-privilege permissions, sandboxed execution, and deterministic verification.