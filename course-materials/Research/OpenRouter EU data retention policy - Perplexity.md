# OpenRouter: data retention, EU data residency and contracts for EU companies

> **Updated 2026-10-02:** rewritten and validated against the official OpenRouter docs. Original research by Perplexity.
>
> **Question:** Does OpenRouter have data retention, data residency and privacy policies suitable for larger EU companies and government? Can EU companies sign contracts with it? Can it route only to EU providers and keep all data in the EU?

**Short answer:** Yes, with conditions. OpenRouter does not store prompts by default, offers Zero Data Retention (ZDR) and training opt-out controls on every plan, and on **Business or Enterprise** plans offers **EU in-region routing**: requests are decrypted only in the EU and routed only to EU provider endpoints. "All data stays in the EU" still depends on the models you pick, on avoiding the few features that are not regional (Batch API, server tools), and on a contract your legal team accepts. DPA and SCC availability is reported only by third parties and must be confirmed with OpenRouter.

## What OpenRouter stores

OpenRouter itself ([Data Collection docs](https://openrouter.ai/docs/guides/privacy/data-collection)):

- **Prompts and responses are not stored by default.** Storing them is opt-in, via "Private Input & Output Logging" in the Observability settings.
- **Request metadata is always stored** (token counts, latency, model, timestamps) for billing, reporting and model rankings. It does not include prompt or response content.
- **No retention period is published for metadata.** Third-party reviewers flag this as a risk for strict data-minimisation audits ([anarlog](https://anarlog.so/blog/openrouter-data-retention-policy/)).

Downstream providers:

- OpenRouter is a routing layer, so every prompt also goes to the model provider (OpenAI, Anthropic, Google, Mistral, etc.), and **that provider's** retention and training policy applies too.
- OpenRouter exposes each endpoint's data policy and lets you block providers that retain or train on your data (next section).

## Zero Data Retention and training controls

Available to **all OpenRouter users**, not only Enterprise ([ZDR docs](https://openrouter.ai/docs/guides/features/zdr), [Sovereign AI docs](https://openrouter.ai/docs/guides/features/sovereign-ai)):

- **ZDR** routes requests only to endpoints whose providers do not store your data for any period of time, which also means no training on it. Enforce it account-wide in [privacy settings](https://openrouter.ai/settings/privacy), per model group (Anthropic, OpenAI, Google, SpaceXAI, all others), or per request:

  ```json
  "provider": { "zdr": true }
  ```

- **Data collection denial** routes only to providers that do not collect your data for training or analytics:

  ```json
  "provider": { "data_collection": "deny" }
  ```

- Caveats:
  - ZDR is a **routing constraint**. It filters which endpoints are eligible; it does not change a provider's own policy.
  - In-memory prompt caching does **not** count as retention, so cached endpoints stay ZDR-eligible.
  - Third-party plugins and tools such as web search are **not covered** by ZDR.
  - Providers with unclear policies are treated conservatively, as retaining and training.
  - Per-request `zdr: true` can only tighten account-level settings, never loosen them.

## EU in-region routing

From the official [In-Region Routing docs](https://openrouter.ai/docs/guides/features/in-region-routing):

- **Plans:** Business and Enterprise only. Business is self-serve via [Settings > Manage plan](https://openrouter.ai/settings/manage-plan); Enterprise via the [enterprise form](https://openrouter.ai/enterprise/form).
- **Base URLs:** EU `https://eu.openrouter.ai/api/v1`, US `https://us.openrouter.ai/api/v1`.
- **Guarantee:** the request is decrypted within the region and routed only to provider endpoints in that region. Prompts and completions are processed entirely in-region and never leave it.
- **No fallback:** if OpenRouter has not onboarded an EU endpoint for the requested model, the request **fails with an error** instead of going to another region. Global and cross-region deployments and multi-model routers are excluded.
- **Not regional yet:**
  - The **Batch API** runs on US infrastructure.
  - Input & Output Logging is skipped on regional domains, even when enabled.
  - Web search, web fetch, files, image generation, Fusion and shell server tools are unavailable on the EU domain.
- **Enforcement:** set `allowed_data_regions` (`global` / `europe` / `us`) in workspace [Guardrails](https://openrouter.ai/docs/guides/features/guardrails). Requests on any other domain are rejected with HTTP 403.
- **BYOK:** your own provider keys (AWS Bedrock, Azure, Vertex AI, OpenAI, Baseten) need matching EU regional deployments ([BYOK docs](https://openrouter.ai/docs/guides/overview/auth/byok)).
- **EU models:** current list at [openrouter.ai/models?region=eu](https://openrouter.ai/models?region=eu), or via API at `https://eu.openrouter.ai/api/v1/models` or `https://openrouter.ai/api/v1/models?region=eu`. The list changes often, so it is linked rather than copied here.

Earlier 2026 third-party write-ups claimed that EU routing still passed through a US gateway component ([InferCheck](https://infercheck.eu/en/provider/openrouter), [Requesty](https://www.requesty.ai/blog/openrouter-eu-alternative-european-ai-gateway)). The current official docs contradict this; the real exceptions are the non-regional features listed above.

## Privacy policy, DPA and GDPR

- OpenRouter publishes a [privacy policy](https://openrouter.ai/privacy) and terms of service.
- OpenRouter does not train its own foundation models; any training on prompts happens at downstream providers, which you can block with the controls above.
- **DPA and SCCs: unverified.** The official docs do not mention a DPA, GDPR or Standard Contractual Clauses. A third-party GDPR profile ([InferCheck](https://infercheck.eu/en/provider/openrouter)) reports an online DPA and SCCs for transfers. Confirm both in the privacy policy or the enterprise contract.
- Upstream providers act as effective sub-processors with their own policies, and they are not exhaustively listed by OpenRouter. Some consultancies note that a gateway makes compliance more complex than calling a single EU provider directly ([vensas](https://vensas.de/en/blog/openrouter-llm-gateway-eu)).

## Building an EU-only, no-retention setup

Technically possible today:

1. **Business or Enterprise plan** with the EU base URL `https://eu.openrouter.ai/api/v1`.
2. **Guardrails** with `allowed_data_regions: europe`, so nothing can bypass the EU domain.
3. **ZDR and `data_collection: "deny"`** enforced account-wide.
4. **Only EU-eligible models**, checked against the [EU model list](https://openrouter.ai/models?region=eu); expect errors, not silent fallback, for anything else.
5. **Avoid non-regional features:** Batch API, web search and other server tools.
6. **Your own stack stays EU-only too:** no non-EU logging, analytics or session-replay tools around the integration.

## Practical implications for larger EU companies and government

- **Data retention policy:** you can document that OpenRouter does not log prompts by default, enforces ZDR and denies provider data collection. Pair this with the policy of each provider you route to.
- **Contracts:** mid-size and large EU companies can usually work with the published policies plus a DPA. Public-sector clients typically need written assurances on EU residency and sub-processors, which means negotiating with OpenRouter's enterprise team.
- **Strict end-to-end EU residency:** in-region routing now covers this technically. If a client still requires a provider that is EU-based as a company, EU-hosted gateways market themselves as OpenRouter-compatible (a base URL and API key change).
- **Recommended path:** enable ZDR and data collection denial now (free, all plans), then move to a Business or Enterprise plan with EU routing and guardrails when a client requires EU residency, and get the DPA and sub-processor terms in writing.

## Sources

Official OpenRouter documentation, checked 2026-10-02:

- [In-Region Routing](https://openrouter.ai/docs/guides/features/in-region-routing)
- [Sovereign AI](https://openrouter.ai/docs/guides/features/sovereign-ai)
- [Zero Data Retention](https://openrouter.ai/docs/guides/features/zdr)
- [Data Collection](https://openrouter.ai/docs/guides/privacy/data-collection)
- [Guardrails](https://openrouter.ai/docs/guides/features/guardrails)
- [BYOK](https://openrouter.ai/docs/guides/overview/auth/byok)
- [Privacy Policy](https://openrouter.ai/privacy)
- [EU model list](https://openrouter.ai/models?region=eu)

Third-party sources from the original research, not re-verified:

- [InferCheck GDPR profile](https://infercheck.eu/en/provider/openrouter)
- [anarlog: OpenRouter data retention policy](https://anarlog.so/blog/openrouter-data-retention-policy/)
- [meetily: OpenRouter LLM privacy](https://meetily.ai/llm-privacy/openrouter)
- [vensas: OpenRouter LLM gateway in the EU](https://vensas.de/en/blog/openrouter-llm-gateway-eu)
- [Requesty: European AI gateway](https://www.requesty.ai/blog/openrouter-eu-alternative-european-ai-gateway)
