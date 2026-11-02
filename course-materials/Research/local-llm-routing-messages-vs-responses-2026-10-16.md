# Local LLM routing: Messages, Responses, and Chat Completions

Checked: 2026-10-16. Documentation and source review, not an inference benchmark. Local CLI: `codex-cli 0.162.1`. Source snapshot: `openai/codex` main, `6b991972c5b539198dcea9bac4fc14e57559c3af` (2026-10-15). Main is not the installed release; do not infer release availability from main alone.

## Why changing the URL is not always enough

Claude Code sends Anthropic Messages requests (`POST /v1/messages`). Codex sends OpenAI Responses requests (`POST /v1/responses`). A server exposing only OpenAI Chat Completions (`POST /v1/chat/completions`) implements a different protocol. Translation must map conversation items, tool calls/results, reasoning, errors, and streaming events; changing the hostname does not translate JSON. [vLLM Claude Code integration](https://docs.vllm.ai/en/latest/serving/integrations/claude_code/), [Codex provider source](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/model-provider-info/src/lib.rs).

In that source, `model_provider` selects a built-in or custom `[model_providers.<id>]` entry. Its `wire_api` field defaults to `responses`. `WireApi` has only the `Responses` variant; deserializing `chat` returns an explicit removal error. `ollama-chat` is also rejected. There is no supported `wire_api = "chat"` escape hatch: put a Responses-compatible endpoint or translating proxy in front of a Chat-Completions-only server. The selected base URL normally ends in `/v1`, not `/v1/responses`. [Provider selection and protocol definition](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/model-provider-info/src/lib.rs), [configuration reference](https://developers.openai.com/codex/config-reference/).

## Routing options

| Option | Agent-facing protocol and practical use |
|---|---|
| Ollama | Native Anthropic-compatible Messages and OpenAI-compatible Responses endpoints. Responses was added in 0.13.3; documentation limits it to stateless requests, without `previous_response_id` or `conversation`. Use the local server for local models; selecting an Ollama cloud model sends inference off-machine. [Messages](https://docs.ollama.com/api/anthropic-compatibility), [Responses](https://docs.ollama.com/api/openai-compatibility) |
| vLLM | Current server docs list Responses as well as Chat Completions; the Claude Code integration implements Messages. Useful for shared GPU serving. Model-specific chat templates, reasoning/tool parsers, and automatic tool choice still matter. Older deployments may expose fewer APIs. [Server](https://docs.vllm.ai/en/latest/serving/online_serving/), [Claude Code](https://docs.vllm.ai/en/latest/serving/integrations/claude_code/) |
| LiteLLM proxy | Self-hosted gateway with `/v1/messages` and `/v1/responses`. Can bridge Responses to Chat Completions. For a custom `openai/` backend, explicitly set `use_chat_completions_api: true`; otherwise Responses may simply be forwarded to an unsupported upstream path. [Messages](https://docs.litellm.ai/docs/anthropic_unified), [Responses bridge](https://docs.litellm.ai/docs/response_api#calling-non-responses-api-endpoints-responses-to-chatcompletions-bridge) |
| claude-code-router | Third-party routing/gateway project. Review the installed version's protocol adapters and routes; its current architecture differs from older tutorials. Do not assume a Claude-oriented router also accepts Codex Responses requests. Exact deployed adapter compatibility is UNVERIFIED. [Maintainer repository](https://github.com/musistudio/claude-code-router) |
| OpenRouter | Hosted gateway offering stateless Responses (no `store: true` or `previous_response_id`) and Anthropic integration. This is external inference, not an on-prem local server. Check the chosen provider's retention and regional processing before sending private data. [Responses](https://openrouter.ai/docs/api/reference/responses/overview), [Claude Code](https://openrouter.ai/docs/cookbook/coding-agents/claude-code-integration) |
| LM Studio | Local serving with `/v1/responses` and `/v1/messages`, alongside Chat Completions. The changelog dates Responses to 0.3.29 and Messages to 0.4.1. Check the running server/engine, model and tool support. [Endpoint comparison](https://lmstudio.ai/docs/developer/rest), [API changelog](https://lmstudio.ai/docs/developer/api-changelog) |

## Minimal agent examples

For Claude Code against an already-running local Ollama server with a downloaded, tools-capable model (replace `local-tools-model` with its actual model ID):

```bash
ANTHROPIC_BASE_URL=http://127.0.0.1:11434 ANTHROPIC_AUTH_TOKEN=ollama ANTHROPIC_API_KEY= claude --model local-tools-model
```

`ollama` above is a non-secret local placeholder, not a cloud key. Launch from a shell without cloud-specific model overrides; otherwise auxiliary/subagent calls may still request a different model. For vLLM or LM Studio, use that server's Messages base URL and configured model/authentication. [Ollama setup](https://docs.ollama.com/integrations/claude-code).

For Codex, copy the following example to `~/.codex/local.config.toml`, replacing the model ID with one actually served. Do not add `/responses` to `base_url`:

```toml
model = "local-tools-model"
model_provider = "private_local"

[model_providers.private_local]
name = "Local Responses server"
base_url = "http://127.0.0.1:11434/v1"
wire_api = "responses"
```

```bash
codex --profile local -s read-only
```

This uses the verified 0.162.1 profile-file layout. Change the port to `1234` for a default LM Studio server or `4000` for a default LiteLLM proxy, after verifying its endpoint. Add `env_key` referencing an environment-variable name when the server requires authentication. Never embed a real key. Existing examples: [Codex profiles](../agent-configs/README.md#codex-profiles).

A LiteLLM route for a Chat-Completions-only local server can look like this; configure the proxy separately and then point Codex to its `/v1` base:

```yaml
model_list:
  - model_name: local-tools-model
    litellm_params:
      model: openai/local-tools-model
      api_base: http://127.0.0.1:8000/v1
      use_chat_completions_api: true
```

This is a configuration template, not a claim that every model passes an agent tool loop. See the [LiteLLM bridge configuration](https://docs.litellm.ai/docs/response_api#calling-non-responses-api-endpoints-responses-to-chatcompletions-bridge).

## Compatibility and private inference checks

- Verify a complete synthetic tool loop, including streamed tool arguments, tool-result IDs, errors, cancellation, and the next model response. A successful text completion proves little about agent compatibility.
- Reasoning items, encrypted reasoning, signatures and vendor-specific tool types may not translate. Do not replay opaque provider-specific state across backends without documented support. Check stateless versus stored Responses behavior.
- Match the model's real context limit, server allocation and Codex's declared window. A client-side `model_context_window` value does not allocate server KV cache or improve a short-context model.
- For on-prem inference, keep model weights, gateway, logs and inference in the approved network. Disable or block cloud fallback and review telemetry, downloads, web search, MCP servers and other tools separately. A loopback inference URL alone does not establish an air gap.
- Bind local servers to loopback unless authenticated network serving is intentional; use TLS/authentication for shared deployments. Capture only synthetic, non-secret traffic when testing protocol adapters.

These are validation recommendations. UNVERIFIED: end-to-end behavior, latency, isolation and model quality for the workshop machines; no inference server or private-data workload was started for this research. See also [local worker models](local-models-as-agent-workers.md).
