---
title: "ChatGPT subscription allowances vs Enterprise credits  -  a quantified comparison"
created: 2026-10-12
updated: 2026-10-12
status: "research snapshot  -  update before reuse"
tags:
  - ai
  - openai
  - chatgpt
  - codex
  - enterprise
  - pricing
  - finops
  - training
aliases:
  - "ChatGPT credits vs Plus and Business allowances"
  - "Codex subscription subsidization 2026"
---

# ChatGPT subscriptions vs Enterprise credits: usage, limits and apparent subsidization

**Research cut-off:** 12 October 2026 · **Currency:** USD, excluding taxes · **Focus:** ChatGPT Work/Codex agentic coding, with notes about ordinary ChatGPT chat.  
**Intended use:** Technical courses, FinOps workshops, procurement discussions and training repositories.

> [!summary] Main findings
> - **Plus ($20/month) and Business Standard ($25/month, or $20/month billed annually) have the same *published five-hour Work/Codex estimates*.** They also have weekly controls. OpenAI does **not** publicly guarantee that their *weekly* quotas are exactly the same. [S1], [S2], [S3]
> - OpenAI's **Standard Business** subscription includes agentic usage; it does **not** give you a 625-credit balance. **Premium Business** costs $125/month ($100 annually), includes approximately **5× Standard's agentic allowance**, and removes the five-hour restriction, though longer-window limits remain. Pro subscriptions also currently lack the Work/Codex five-hour restriction. [S2], [S3], [S4]
> - For **credit-based Work/Codex standard token rates**, **1 credit corresponds to $0.04 of API-list-priced tokens**: 25 credits ≈ $1. This is backed by a $100 = 2,500-credit OpenAI promotion and matching rate cards. It does **not** measure OpenAI's actual computing costs or guarantee every enterprise contract buys credits for four cents. [S5], [S6], [S7]
> - Independent Plus benchmarks imply that a **highly utilized $20 subscription may include about $200-300/month of API-list-equivalent *Work/Codex* activity**, roughly **5,000-7,500 credit-equivalents**. Several independent estimates cluster near **$283-290/month**. These are measured-window extrapolations or capacity estimates, **not official grants, average-user spend or directly measured Business limits**. [S8], [S9], [S10]
> - As a **Business Standard proxy**, that means a **$25 seat** may expose the user to **8-12× its fee** in list-priced agentic capacity *if the allowance is fully usable*. The **personal $20 Plus seat** yields the same approximate dollar capacity on a supported like-for-like workload, hence **10-15× its fee**. This is **not** evidence that OpenAI spends 8-15× the fee on inference. [S8], [S9], [S10], [S11]
> - A hypothetical **3,000 Enterprise credits** equal **$120 of standard-rate token-metered purchasing power**, if the applicable contract follows the standard rate card. **If those are 3,000 credits *per month*,** the subscription benchmark is **about 1.7-2.5× that metered amount**. If they are annual, the comparison is radically different. [S5], [S6]

> [!warning] Do not conflate these three units
> **Subscription allowance** = a non-transferable capacity budget enforced by usage windows; **workspace credits** = a spendable metering unit used by credit-based plans; **API dollars** = the list price of comparable token traffic, not the model provider's marginal GPU/energy cost. "Credit-equivalents" in this report are an **analytical conversion** - they are *not* credits placed in a Plus or Business account.

## 1. What each plan actually buys

| Offering | Advertised price | Work/Codex allowance model | Five-hour Work/Codex window? | Notes |
|---|---:|---|---|---|
| **ChatGPT Plus (personal)** | **$20/month** | Included allowance + weekly cap; optional purchased credits after limit | **Yes** | API calls billed separately. |
| **Business Standard** | **$25/month**, or **$20/month billed annually** | Included per-seat allowance; optional shared paid credit pool *after* included limit | **Yes** | At least 2 paid seats per self-serve workspace; same published five-hour estimates as Plus. |
| **Business Premium** | **$125/month**, or **$100/month billed annually** | About **5× Standard's included agentic usage**, plus optional credits | **No** | Other windows, including weekly limits, still matter. This is a *seat type*, not the "Pro" reasoning setting. |
| **ChatGPT Pro personal tiers** | **$100 / $200 / $500 monthly** | Higher included usage; limits depend on tier and model | **Currently no** | Weekly allowances still exist; $500 adds eligible Ultrafast access. |
| **Enterprise/Edu, credit-based flexible pricing** | Contract-dependent | Advanced features draw from **shared contracted credit pool**, with group/user spend controls | **No fixed Work/Codex window by default** | Credits can exhaust; no fixed rate limit does *not* mean unlimited budget. |
| **Enterprise, token-based USD pricing** | Contract-dependent | Charges in **USD per model-token/feature** rather than workspace credits | Contract-dependent; flexible PAYG rather than the Plus-style window | **Instant may also be billable**, unlike current credit-based Enterprise Instant chat. |
| **OpenAI API key** | Usage-based | Metered API tokens and applicable service charges | **Not the ChatGPT five-hour window** | Separate API billing, API rate limits, and reduced ChatGPT cloud-product integration. |

Sources: [S1], [S2], [S3], [S4], [S5], [S6], [S12], [S13]. Business versus Plus is **not** simply "same product plus $5": Business offers workspace administration and different data-governance terms. Business data is excluded from training by default, whereas personal accounts can opt out of training. [S20]

### Ordinary ChatGPT conversations are a different allowance

The five-hour figures below are for **ChatGPT Work and Codex**, **not a universal message cap in the normal ChatGPT chat tab**. Business offers virtually unlimited **Instant** chat subject to abuse guardrails, while reasoning, Pro, image, research and agentic experiences have separate allowances. In October 2026, **Business Standard includes 15 GPT-6 Pro chat messages/month** and **Premium includes 50/week**; these are separate from Work/Codex. Credit-based Enterprise currently lists Instant as unlimited (subject to guardrails), GPT-6 thinking as **10 credits per message**, and GPT-6 Pro as **50 credits per message**. New *USD-token-based* Enterprise billing treats Instant differently. [S2], [S5], [S6]

## 2. The five-hour window and the weekly cap

OpenAI currently publishes the following **estimated local messages within one five-hour window**. Real consumption depends on context, output, model, reasoning, tools, subagents, cache and task complexity; these are **not guaranteed message counts**. [S1], [S13]

| Work/Codex model | Plus | Business Standard |
|---|---:|---:|
| GPT-6 Astra | 5-45 | 5-45 |
| GPT-6.1 Sol | 15-160 | 15-160 |
| GPT-6 Sol | 15-150 | 15-150 |
| GPT-6 Luna | 350-3,000 | 350-3,000 |

**How the controls interact:**

1. The **five-hour period** begins with a first eligible Work/Codex request after the previous window closes; it does not mean five hours of continuous computing. The meter can be exhausted in minutes by a large task. [S1]
2. The **weekly limit is another independent cap**. Even if the five-hour limit resets, running out of the weekly allowance may block further included use until its reset. Both Work and Codex share an allowance, often alongside other agentic products. [S1], [S13]
3. **The identical five-hour table does not prove identical weekly pools** for Plus and Business Standard. Treat any transfer of measured Plus **monthly** capacity to Business as a **proxy** to verify with actual Business usage data.
4. **Pro and Business Premium remove the five-hour Work/Codex cap**, **not all limits**. [S1], [S2], [S4]
5. **Credits are a paid overage mechanism**: Plus/Pro and Business Standard use their *included allowance first*. Enterprise with a contracted credit pool is a different billing model; the pool generally pays for advanced usage from the start. [S5], [S12], [S14]

## 3. Value of one Enterprise/Business credit

### Publicly verifiable exchange: 25 credits ≈ $1 of standard-rate Work/Codex tokens

OpenAI offered **2,500 workspace credits as a $100 promotion** for eligible Business Premium seats: `100 / 2500 = $0.04 per credit`. Independently, the **credit-based** and **USD-token-based** rate cards agree for standard GPT-6 Work/Codex token pricing. For example, GPT-6.1 Sol fresh input costs **50 credits per million** or **$2/million**; 50 × $0.04 = $2. [S5], [S6], [S7]

| Work/Codex model, standard speed | Credit-based: fresh / cached / output per **1M tokens** | Equivalent USD list-rate: fresh / cached / output per **1M tokens** |
|---|---|---|
| GPT-6.1 Sol | 50 / 2.5 / 250 | **$2 / $0.10 / $10** |
| GPT-6 Sol | 50 / 5 / 250 | **$2 / $0.20 / $10** |
| GPT-6 Astra | 250 / 25 / 1,250 | **$10 / $1 / $50** |
| GPT-6 Luna | 2.5 / 0.25 / 12.5 | **$0.10 / $0.01 / $0.50** |

**Formula for a standard token-metered task:**

```text
credits = (fresh_input_tokens  × model_fresh_credit_rate
         + cached_input_tokens × model_cached_credit_rate
         + output_tokens       × model_output_credit_rate) / 1_000_000

USD_list_equivalent ≈ credits × 0.04
```

This equivalence applies to **comparable token categories at standard rates**, not every ChatGPT feature or contract:

- Chat messages and features can be **charged by message, generated image, minute or task**, rather than actual tokens, on credit-based plans. [S5]
- **Fast** mode consumes purchased credits at **2×** the standard token rate, **Ultrafast** at **6×** where available; included **subscription allowances** burn at **2.5×** and **8×** respectively. These are *usage multipliers*, not speed promises. [S13]
- Long contexts, tool use, additional agents, image/voice activity, regional processing, cache-writing rules and contract discounts may affect a like-for-like API comparison. [S5], [S6], [S15]
- For **Enterprise billed directly in USD**, different provisions apply and Instant chat can be metered. For **Enterprise credit-based agreements**, an actual purchase rate, discounts, expiry and overage terms are governed by the contract. [S6], [S14]
- **"API-equivalent value" is not OpenAI's true inference expense**. It uses OpenAI's selling price on the API, which includes unknown margins and different service economics.

Useful conversions at the standard analytic rate:

| Credits | Standard token-metered list equivalent |
|---:|---:|
| 500 | $20 |
| **625** | **$25** |
| 1,000 | $40 |
| 2,500 | $100 |
| **3,000** | **$120** |
| 5,000 | $200 |
| 7,125 | $285 |
| 7,500 | $300 |

**Important:** Paying **$25 for a Business Standard seat does not grant 625 credits**. The 625 is merely what a separate $25 of standard-priced **metered token usage** would represent.

## 4. Independent measurements: how much is a $20 Plus allowance worth?

### Evidence table (method and degree of certainty)

| Source, snapshot | What was directly measured | Reported/extrapolated Plus capacity | Business applicability |
|---|---|---|---|
| **FinOps LLM**, updated **10 Oct 2026** [S8] | **27 Plus weekly-window observations** over multiple months; recent median full weekly window **$67 API-list equivalent**, seven recent windows in **$61-81/week** band | **~$290/month** from $67 × 52/12 (roughly **7,250 credit-equivalents**) | **Proxy**, not measured Business; date/model mix affect USD value. |
| **InventiveHQ**, published **4 Oct 2026** [S9] | Several clean **Pro $100/$200** windows from local Codex session logs; only **one near-clean Plus window** | **~$66/week = ~$285/month** for Plus (**~7,125 credits**), **projected using plan multipliers**, not a multi-window Plus study | **Proxy** only; author warns Plus five-hour cap may obstruct complete weekly use. |
| **r/codex user experiment**, updated **12 Oct 2026** [S10] | Fresh **Plus five-hour window**, token-level pricing; GPT-6.1 Sol measured **$7.5-7.8 per five hours** earlier, **$11 per five hours** in the **12 Oct update** | Older **~$200/month**, **newer ~$283/month**, using assumption of **6 fully consumed windows/week** and ~30 days/month | **Proxy** only; monthly value is not directly measured. |
| **SemiAnalysis**, **5 Oct 2026** [S11] | Controlled tests isolating fresh input, cache reads/writes and output against usage-meter movement | Public article argues **~12× list-value/fee broadly** across OpenAI plans, with workload dependence. **Exact Plus $211/month mentioned in earlier research could not be verified in the accessible article.** | Independent methodological support, **not** direct public confirmation of any one Business seat's dollar quota. |
| **CodePick**, updated **30 Sep 2026** [S16] | Official-pricing cross-check and analysis | **No independently measured $285 Plus sample** | Secondary context, not an independent quota experiment. |
| **UsageBox**, read **Oct 2026** [S17] | Official-documentation synthesis | Lists message ranges, token credit rates and pricing | Secondary verification of rules; **not** an independent subscription-value benchmark. |

### Interpretation and recommended teaching range

The **defensible high-utilization, Sol-class benchmark is approximately $200-300/month of API-list-equivalent Work/Codex activity for Plus**. The most recent independently developed calculations cluster around **$283-290**; a single source's exact number should not be treated as guaranteed. Business Standard has **matching published five-hour ranges**, so its presumed dollar value is **roughly the same only if its weekly limits and workload are comparable**. [S1], [S8], [S9], [S10]

**Do not call this "$200-300 of compute cost to OpenAI."** It is the **retail/API list price for comparable measured or projected tokens**. Models, cache rates, provider quota weights, price reductions and subscription changes can all shift the dollar equivalent. A cheaper API price can reduce the headline dollar value *without any reduction in useful tokens/tasks*. [S8], [S9], [S11]

**Realized value varies with utilization.** If a user consumes only a quarter of the hypothetically usable allowance, they realize only about a quarter of its token-list equivalent (for a similar workload), not the full $200-300:

| Illustrative use of benchmark capacity | Approx. token-list equivalent realized |
|---:|---:|
| 10% | $20-30/month |
| 25% | $50-75/month |
| 50% | $100-150/month |
| 100% | **$200-300/month** |

These are **scenarios**, not a survey of how much typical subscribers actually use. There is **no verified population-average spending or GPU-cost number** in the cited material.

### Why benchmark estimates conflict

- **Plus 5-hour vs weekly cap:** a single five-hour experiment multiplied by six windows per week can overstate monthly value if the weekly cap is smaller or the user does not run continuously. [S10]
- **Different models/caching:** cheap Luna and GPT-6.1 Sol have different API prices and may not move subscription meters in strict proportion to USD price. [S8], [S9], [S11]
- **Different account tiers:** Pro measurements cannot automatically be divided by a marketing "5×" to obtain a verified Plus allowance. FinOps LLM separately observed a **~$175/week Pro $100** median in a recent test, only **~2.6×** its own observed Plus median of $67. InventiveHQ inferred a larger Pro $100 window (~$330-380/week). These incompatible estimates show why workload, model selection and methodology matter. [S9], [S18]
- **Pricing and limit changes:** on **12 October**, the r/codex author updated GPT-6.1 Sol's five-hour value from **$7.8 to $11**, moving their extrapolated month from **~$200 to ~$283**. [S10]
- **Sparse Business measurements:** all three quantitative benchmarks above are based on personal Plus and/or Pro accounts. They cannot establish an official Business monthly-credit figure.

## 5. Generic comparison for a $25 seat (the useful procurement benchmark)

**Question:** If I pay $25 for one Business Standard seat, how many *credit-equivalents* of Work/Codex activity can its included allowance potentially deliver versus spending the same $25 as metered credits?

| Spending/allowance scenario, per person | Amount paid or list-value | Credit-equivalents at $0.04 | Ratio to a **$25 Business seat fee** | Status |
|---|---:|---:|---:|---|
| **$25 of separately metered credit usage** | $25 | **625 credits** | **1×** | Mathematical conversion; not a Business seat grant |
| Business Standard **low benchmark**, fully used | ~$200 API-list value | **5,000** | **8×** | **Plus-derived proxy** |
| Business Standard **mid benchmark**, fully used | ~$250 API-list value | **6,250** | **10×** | **Plus-derived proxy** |
| Business Standard **recent cluster**, fully used | ~$283-290 API-list value | **7,075-7,250** | **11.3-11.6×** | **Plus-derived proxy** |
| Business Standard **high benchmark**, fully used | ~$300 API-list value | **7,500** | **12×** | **Plus-derived proxy** |

**The same included Work/Codex capacity on $20 personal Plus** would imply **10-15× its $20 price** (using the $200-300 scenario). This does **not mean personal users receive more Work/Codex tasks than Standard Business users** - OpenAI publishes the **same five-hour ranges**. The Plus ratio is simply **larger because the personal subscription costs $20 instead of $25 month-to-month**. [S1], [S3]

At $20/user/month **billed annually** for Business Standard, its value/fee arithmetic is also **10-15×**; the billing commitment and **two-seat minimum** differ from personal Plus. [S3]

> [!important] Correct meaning of "subsidization" in a course
> Explain it as a **subscription discount relative to API list rates at a given utilization**, not a verified subsidy to OpenAI's physical inference costs or an indicator of operating losses. Business/Enterprise add compliance and organizational value that a pure token-dollar table cannot quantify.

## 6. Illustration: a 3,000-credit Enterprise budget

A commonly useful **hypothetical training scenario** is **3,000 credits allocated per employee**. This is **not** an official OpenAI standard allowance. First establish whether those credits are **monthly, quarterly, annual, total committed pool ÷ staff, or merely an individual spending-control ceiling**. The actual Enterprise resource is a **shared workspace pool**, and an individual cap does not mint new credits. [S12], [S14]

- `3,000 × $0.04 = $120` of standard **Work/Codex metered token-list equivalent**.
- **Against a full monthly Business/Plus-style $200-300 benchmark**, this is **1.67-2.5× less token-list equivalent** than the maximally utilized subscription proxy.
- **If 3,000 credits are yearly**, that is `$120/year`, or **$10/month** on an even allocation - not comparable to a $25/month seat's recurring monthly included usage.
- **If 3,000 credits are monthly**, it is **$120/month** of notional credit-metered activity, separate from whatever Enterprise subscription/seat fees and contract discounts apply.

### What 3,000 credits can do if devoted to just one feature

These **credit-based Enterprise Chat** rates are not a way to calculate the number of Work/Codex local messages. [S5]

| Activity in credit-based Enterprise | Published charge | 3,000-credit maximum at that rate |
|---|---:|---:|
| GPT-6 Sol medium/high/extra-high **Chat** | 10 credits/message | **300 chat messages** |
| GPT-6 Pro **Chat** | 50 credits/message | **60 chat messages** |
| Agent mode | 30 credits/message | **100 agent messages** |
| Deep Research | 50 credits/task | **60 tasks** |
| Images | 5 credits/generation | **600 generations** |
| Voice in ChatGPT | 1.25 credits/minute | **2,400 minutes** (40 h) |
| **GPT-6.1 Sol Work/Codex** | OpenAI estimate: **2-15 credits/typical task** | **~200-1,500 tasks**, highly variable |

For a reproducible **GPT-6.1 Sol Work/Codex** token example:

```text
One illustrative agentic task:
  fresh input   = 30,000 tokens × 50 credits/1M      = 1.500 credits
  cached input  = 70,000 tokens × 2.5 credits/1M     = 0.175 credits
  output        = 10,000 tokens × 250 credits/1M    = 2.500 credits
  ---------------------------------------------------------------
  total                                                4.175 credits
  standard API list equivalent                         $0.167
  tasks under 3,000 credits                            floor(3000/4.175) = 718
```

This is a **constructed task shape**, not a claim that real tasks average 4.175 credits; additional agents, larger contexts, speed modes and other billable features change it. [S5], [S6]

### Procurement comparison: where Enterprise may be preferable

**Business Standard** can make financial sense for frequent usage because its **included allowance can have much higher API-list-value than the seat price**; it also imposes rolling **five-hour + weekly** controls. **Credit-based Enterprise** offers a centrally managed pool, adjustable group budgets, governance and flexibility to burst **without the same fixed five-hour window**, but the budget is finite and a team can exhaust it. Different Enterprise **USD-token-based contracts** should be compared with the *contracted dollar rate card*, not forcibly converted into credits. [S5], [S6], [S12], [S14]

One firsthand account from **September 23, 2026** described switching from Business to Enterprise, receiving a **500-credit/month** user limit, and occasionally exhausting it in **under two hours** of Work/Codex activity. The user's dashboard displayed **1,000 credits ≈ $40** after a limit increase. That supports the **non-equivalence of a $20 Business seat and $20 Enterprise credits**, but does not establish a universal Enterprise allotment or actual typical usage. [S19]

A different organization's buyer reported **staying on Business** after struggling to forecast pooled Enterprise credit spending. This is a procurement anecdote, not a measured usage limit. [S21]

## 7. Validation of the claims in Grok's separate research

| Grok research claim | Assessment as of 12 Oct 2026 | Explanation / primary or independent evidence |
|---|---|---|
| "1 credit = $0.04" | **Supported for list-rate Work/Codex comparison** | OpenAI promo and rate-card arithmetic agree; contract purchase/discount terms still matter. [S5], [S6], [S7] |
| "3,000 credits = exactly $120 of API-priced usage" | **Correct with scope** | Works at the **standard token-based rate-card equivalent**; not all ChatGPT feature pricing, not cash and not provider compute cost. [S5], [S6] |
| "$20-25 Business matches Plus for Work/Codex" | **Confirmed for published five-hour ranges; unproven for weekly limits** | The OpenAI table is identical for five hours, but no explicit public weekly parity statement. [S1] |
| "Subscription capacity $200-300+ per month when maxed" | **Plausible benchmark range, not a guarantee** | FinOps, InventiveHQ and r/codex methods broadly converge for select Sol workloads; all have caveats. [S8], [S9], [S10] |
| "InventiveHQ Plus $66/week or ~$285/month was measured" | **Partially overstated** | The authors directly measured **Pro** windows; **Plus $285/month is a projection** supported by a single near-clean Plus window. [S9] |
| "FinOps LLM $67/week" | **Verified** | Reports **27 Plus weekly windows** and recent $67 median; annualizing a full weekly allowance is a separate calculation. [S8] |
| "r/codex GPT-6.1 Sol $7.8/5h ≈ $200/mo" | **Historically true, superseded** | Same experiment was **updated 12 Oct** to **$11/5h ≈ $283/month** (assuming six full windows/week). [S10] |
| "Astra always means more subscription dollar value" | **Not established** | A more expensive model may simply consume a quota faster; model-specific weighting matters. [S9], [S11] |
| "OpenAI estimates typical Codex developer spend at $100-200/mo" | **Documented, but about costs, not subscription grants** | Published in the credit rate card; a broad typical developer *cost* estimate, not a seat entitlement. [S5] |
| "3,000 credits are an extra buffer on top of the Enterprise included baseline" | **Usually misleading** | **Business:** included usage first, credits for overage. **Enterprise credit pool:** advanced usage draws from shared credits, absent specific contrary contract terms. [S5], [S12] |
| "Credits equal OpenAI's actual compute cost" | **Incorrect** | The calculation is at **API list rates**, not disclosed infrastructure/energy/GPU cost. [S6] |
| "Switch to API key after allowance ends rather than buy credits" | **Conditionally reasonable, not universal** | Standard token pricing is broadly at parity; API may offer speed but WorkOS's speed result is from GPT-5.6 in August, not a universal October guarantee. See next section. [S15], [S13] |

## 8. Does WorkOS's advice - "use an API key instead of credits" - still hold?

**Source:** WorkOS, ["When your Codex allowance runs out, use an API key instead of credits"], [S15], published **4 September 2026**.

**WorkOS's evidence:** For an agentic TypeScript task under **GPT-5.6 Sol**, they compared **10 runs per arm**. They reported similar blind-rated task quality, and median completion times of **1,296 seconds via API** vs **1,971 seconds through the Codex subscription/credits route** - approximately **1.52× slower** for the latter on their setup. An additional four-run weekday probe showed a similar direction. They also found **credit top-ups priced at the same standard model token list rate as API**, so extra credits offered no token-price discount *in that comparison*. [S15]

**What still holds on 12 October 2026:**

1. **Token-list price parity at standard speed:** The current GPT-6.1 Sol credit rate of **50 / 2.5 / 250 credits per million** maps to **$2 / $0.10 / $10** standard USD token prices. If you have **not yet bought extra credits** and are only doing supported **local CLI/SDK/IDE work**, a separately billed API key is a reasonable alternative to test. [S5], [S6], [S13]
2. **Cache-write and other charge differences:** OpenAI says **Codex credit billing has no separate cache-write charge**; the API pricing page separately lists cache-write prices (for current GPT-6.1 Sol: **$2.50/million at Standard short context**). Therefore, total API spend can exceed a simple three-column token-equivalent estimate for write-heavy activity. [S13], [S22]
3. **Product/operations trade-off:** API-key Codex supports **CLI, SDK and IDE**, but lacks some **subscription-linked cloud experiences**, such as GitHub code review and Slack integration. API billing, quota/limits, keys, policies and access are separate from ChatGPT seat billing. [S13]
4. **No automatic advantage for prepaid Enterprise credits:** If the organization **already purchased a contract credit pool**, abandoning it may create a *new API bill* while leaving committed credits unused. The marginal procurement decision differs from a consumer considering a **new** credit top-up. [S12], [S14]
5. **Speed result not proved for October's models:** WorkOS tested **one task family, one region/account and GPT-5.6** in August, prior to GPT-6.1 Sol and revised rates. A **1.5× API speedup is a test result**, not a service-level guarantee. To revalidate, rerun matched experiments with the **same October model, effort, caching, parallelism and region**. [S15]
6. **Fast-mode multipliers changed / vary by billing lane:** The current documented rate is **2× for purchased credits**, **2.5× for included subscription usage**, and **2× standard API list rate for supported Fast processing**. Do **not** transplant WorkOS's older credit-lane speed/cost examples unchanged to GPT-6.1. [S5], [S6], [S13]

**Decision rule:** **Use the included allowance first** (already covered by the fixed fee). When exhausted: **try an API key for local Codex** if all required features work, new metered spending is authorized, and your own paired tests show acceptable latency/price; **use workspace credits** when cloud/managed features, existing credit commitments, or enterprise governance justify them. There is **no safe universal "API key always wins" rule**.

## 9. How to measure your own plan reproducibly

> [!tip] This is the most defensible demonstration for an AI training course.
> Select a controlled task and show the *actual* Work/Codex meter change and token count side by side. No need to claim that "Business gives 7,000 credits"; instead, show what the **same work** would cost under a credit meter.

1. **Identify the contract:** Plus, Business Standard, Business Premium, Pro, Enterprise-credit, or Enterprise-USD; note billing period and permitted models.
2. **Fix the workload:** same repo/task, model (e.g. GPT-6.1 Sol), reasoning effort, speed (Standard), tooling, region and cache state. Do not mix multiple agent runs unintentionally.
3. **For a subscription**, note the **five-hour and weekly allowance percentages** before/after (where they exist), with precise reset timestamps. Read `Settings -> Usage` and use Codex CLI `/status` where supported. [S1], [S13]
4. **Capture token categories:** fresh input, cached input and output (including reasoning/output tokens). Codex local sessions are stored in `~/.codex/sessions/`; make sure the measurement includes **every machine and cloud task** counted against the meter, otherwise you underestimate actual spend. [S9], [S18]
5. **Price the same work** at the applicable **current API list rate**, noting **cache writes, context multipliers and paid-speed modes** if relevant. [S6], [S22]
6. **For a credit-billed Enterprise workspace**, read the actual credit charge from admin analytics / usage reporting. For a Standard Business account, track **meter consumption**, not a fictitious credit withdrawal within the included tier.
7. **Estimate a full weekly window** only where the weekly meter's consumed fraction is reliable:

```text
API_list_value_of_observed_work =
    (fresh_tokens / 1_000_000 × API_fresh_price)
  + (cached_tokens / 1_000_000 × API_cached_price)
  + (output_tokens / 1_000_000 × API_output_price)
  + any applicable extra charges

estimated_full_week_API_value = API_list_value_of_observed_work
                              / (weekly_allowance_percentage_used / 100)

estimated_full_month_API_value = estimated_full_week_API_value × (52 / 12)
analytical_credit_equivalents  = estimated_full_month_API_value / 0.04
```

8. **Repeat over multiple weeks and model mixes**, checking the impact of five-hour limits on attainable weekly utilization. Track **median, range and confidence**, not one precise-looking number. If a session ends due to a five-hour cap while substantial weekly allowance remains, **a fully used weekly value is not necessarily achievable**.

## 10. A ready-to-use teaching slide / speaking notes

**Headline:** "A $25 ChatGPT Business seat is not the same as $25 worth of Enterprise credits."

**Evidence:** OpenAI lists matching **five-hour Work/Codex** usage ranges for Plus and Standard Business, while outside observers estimate roughly **$200-300/month of equivalent API-token usage** for heavily utilized Plus. At **$0.04/credit**, that is about **5,000-7,500 credit-equivalents**; **$25 of metered credits buys only 625 credits**. This is **8-12× greater list-rate capacity than the same $25 spent on credits**, **not** proof that OpenAI subsidizes infrastructure cost by 8-12×. **Business weekly equivalence is not confirmed**, so frame its dollar value as a proxy. [S1], [S5], [S8], [S9], [S10]

**Illustration:** A credit-based Enterprise spending budget of **3,000 credits per employee per month** corresponds to **$120 of standard token-metered list value**. It may offer much less total heavily used agentic capacity than a self-serve seat **but greater governance, pooling and freedom from five-hour interruption**. [S5], [S12]

**Three questions for students:** What exactly resets? Which meter is being consumed? Is the number a **subscription fee**, **credit-list-equivalent**, **API invoice**, or **actual inference cost**?

## 11. Sources, validation status and snapshot dates

**Primary OpenAI documentation:**

- **[S1]** [Managing usage with GPT-6 Astra in Work and Codex](https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex)  -  official two-window explanation and equal **five-hour** Plus/Standard Business ranges. *Checked 2026-10-12.*
- **[S2]** [ChatGPT Business models and limits](https://help.openai.com/en/articles/12003714-chatgpt-business-models-and-limits)  -  Standard/Premium model separation, agentic limits, Pro chat messages. *Checked 2026-10-12.*
- **[S3]** [Managing billing and seats in ChatGPT Business](https://help.openai.com/en/articles/8792536-managing-billing-and-seats-in-chatgpt-business)  -  $25/$20 Standard and $125/$100 Premium, two-seat minimum. *Checked 2026-10-12.*
- **[S4]** [ChatGPT Business general FAQ](https://help.openai.com/en/articles/8542115-chatgpt-business-general-faq)  -  Premium roughly 5× included agentic usage, no five-hour restriction, included usage vs credits. *Checked 2026-10-12.*
- **[S5]** [ChatGPT Rate Card  -  credit-based Business / Enterprise / Edu](https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing)  -  authoritative credit rates, features, Work/Codex rates and 2-15-credit task estimate. *Checked 2026-10-12.*
- **[S6]** [ChatGPT Rate Card  -  Enterprise USD token-based pricing](https://help.openai.com/en/articles/20001415-chatgpt-rate-card-enterprise-token-based-pricing)  -  authoritative USD rate and contract-model distinctions. *Checked 2026-10-12.*
- **[S7]** [OpenAI announcement  -  Premium seats are coming to ChatGPT Business](https://openai.com/index/premium-seats-chatgpt-business/)  -  $100 = 2,500-credit promotion. Historical promotion, **not a current seat's included credit grant**. *2026 announcement; checked 2026-10-12.*
- **[S12]** [Flexible pricing for Enterprise, Edu and Business](https://help.openai.com/en/articles/11487671-flexible-pricing-for-the-enterprise-edu-and-business-plans)  -  when shared credits are used and Enterprise pool behavior. *Checked 2026-10-12.*
- **[S13]** [OpenAI Codex / Work pricing and usage](https://learn.chatgpt.com/docs/pricing)  -  five-hour and weekly controls, API-key support, speed multipliers, available features. *Checked 2026-10-12.*
- **[S14]** [Manage Enterprise/Edu usage limits and overages](https://help.openai.com/en/articles/20001001-manage-usage-limits-and-overages-in-chatgpt-enterprise-and-edu)  -  shared credit pool, group controls, contract-specific charges and USD budgets. *Checked 2026-10-12.*
- **[S20]** [OpenAI  -  Business data privacy](https://openai.com/business-data/) and [personal data controls](https://help.openai.com/en/articles/8983130-how-does-chatgpt-use-my-data)  -  governance differences; not included in token-dollar arithmetic. *Checked 2026-10-12.*
- **[S22]** [OpenAI API pricing](https://developers.openai.com/api/docs/pricing)  -  current standard token and cache-write rates. *Checked 2026-10-12.*

**Independent measurements / analyses:**

- **[S8]** [FinOps LLM  -  How much Codex does ChatGPT Pro include?](https://finopsllm.com/research/codex-usage-limits-chatgpt-pro)  -  **27 Plus weekly-window observations**, recent **$67/week median**. *Updated 2026-10-10.* **Measured Plus**, monthly extrapolated.
- **[S9]** [InventiveHQ  -  How Much Codex Does a ChatGPT Plan Buy? I Measured It](https://inventivehq.com/blog/codex-subscription-usage-measured)  -  strong session-log methodology; **Pro windows measured**, **Plus $285/month projected**, one near-clean Plus sample. *Published 2026-10-04.*
- **[S10]** [r/codex  -  GPT-6.1 Sol usage measurement and updates](https://www.reddit.com/r/codex/comments/1wtlkg6/gpt_61_brought_another_nerf_to_usage_table_update/) and [original five-hour comparison](https://www.reddit.com/r/codex/comments/1wp0v6x/allowance_for_gpt_6_luna_sol_and_astra_measured/)  -  firsthand **five-hour** experiment, plus *assumed* monthly projection; **2026-10-12 changed $7.8 to $11 per five-hour Sol window**. Not a controlled company-wide study.
- **[S11]** [SemiAnalysis  -  Anthropic Subscriptions Offer 5x+ More Value Than OpenAI](https://newsletter.semianalysis.com/p/anthropic-subscriptions-offer-5x)  -  controlled per-token-category methodology and broad economic framing; detailed tables/dashboard are **partly paywalled**; specific $211 Plus claim **not publicly verifiable from the page**. *2026-10-05.*
- **[S15]** [WorkOS  -  When your Codex allowance runs out, use an API key instead of credits](https://workos.com/blog/codex-allowance-runs-out-use-api-key-not-credits)  -  firsthand A/B speed test **on older GPT-5.6**; conclusion is conditional for Oct 2026. *2026-09-04.*
- **[S16]** [CodePick  -  Codex plan value analysis](https://codepick.dev/en/guides/codex-plan-value-analysis/)  -  secondary official-source cross-check with explicit caveats. *Updated 2026-09-30.*
- **[S17]** [UsageBox  -  Codex pricing and usage limits 2026](https://usagebox.com/articles/openai-codex-pricing-usage-limits-2026)  -  secondary documentation summary. *Oct 2026.*
- **[S18]** [FinOps LLM  -  We got eight Pro $100 weekly windows in 12 days](https://finopsllm.com/research/codex-pro-100-heavy-user-resets-log)  -  firsthand **Pro** logs with **~$175/week median**, special/banked resets. *2026-10-09.*
- **[S19]** [V2EX  -  Business to Enterprise credit exhaustion discussion](https://www.v2ex.com/t/1244246)  -  firsthand *anecdote* of 500 credits/month and perceived worse capacity; not representative. *2026-09-23.*
- **[S21]** [Reddit  -  ChatGPT Business vs Enterprise credit model](https://www.reddit.com/r/OpenAI/comments/1rk5opt/chatgpt_business_vs_enterprise_credit_model/)  -  qualitative buyer discussion; no quota measurement. *2026-03 to 2026-07.*

**Review/update checklist:** Before teaching from this note, confirm **pricing, latest model names, credit rates, 5-hour/weekly controls, promotions, availability of Premium seats, Enterprise contract type and experiment dates**. Quota changes can invalidate monthly extrapolations even when the subscription price is unchanged.

<!-- Obsidian/CommonMark reference links: [S#] citations above open the cited source. -->
[S1]: https://help.openai.com/en/articles/20001516-managing-usage-with-gpt-6-astra-in-work-and-codex
[S2]: https://help.openai.com/en/articles/12003714-chatgpt-business-models-and-limits
[S3]: https://help.openai.com/en/articles/8792536-managing-billing-and-seats-in-chatgpt-business
[S4]: https://help.openai.com/en/articles/8542115-chatgpt-business-general-faq
[S5]: https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu-credit-based-pricing
[S6]: https://help.openai.com/en/articles/20001415-chatgpt-rate-card-enterprise-token-based-pricing
[S7]: https://openai.com/index/premium-seats-chatgpt-business/
[S8]: https://finopsllm.com/research/codex-usage-limits-chatgpt-pro
[S9]: https://inventivehq.com/blog/codex-subscription-usage-measured
[S10]: https://www.reddit.com/r/codex/comments/1wtlkg6/gpt_61_brought_another_nerf_to_usage_table_update/
[S11]: https://newsletter.semianalysis.com/p/anthropic-subscriptions-offer-5x
[S12]: https://help.openai.com/en/articles/11487671-flexible-pricing-for-the-enterprise-edu-and-business-plans
[S13]: https://learn.chatgpt.com/docs/pricing
[S14]: https://help.openai.com/en/articles/20001001-manage-usage-limits-and-overages-in-chatgpt-enterprise-and-edu
[S15]: https://workos.com/blog/codex-allowance-runs-out-use-api-key-not-credits
[S16]: https://codepick.dev/en/guides/codex-plan-value-analysis/
[S17]: https://usagebox.com/articles/openai-codex-pricing-usage-limits-2026
[S18]: https://finopsllm.com/research/codex-pro-100-heavy-user-resets-log
[S19]: https://www.v2ex.com/t/1244246
[S20]: https://openai.com/business-data/
[S21]: https://www.reddit.com/r/OpenAI/comments/1rk5opt/chatgpt_business_vs_enterprise_credit_model/
[S22]: https://developers.openai.com/api/docs/pricing
