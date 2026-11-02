# The price of intelligence over time (research 14.10.2026)

Research date: 14 October 2026. Source data for explaining the price of intelligence over time: cheapest API price for a fixed capability level over time (log scale), plus the counterpoint that frontier prices fell less and agents consume far more tokens per task. Web research delegated to OpenCode/GLM-5.3. Re-checked directly on 14.10.2026: the Epoch AI series for MMLU 64.8 and MMLU 86 (all dated points), Epoch's method (3:1 weighted input/output price, reasoning models excluded, decline 9x-900x per year, median 50x), the OpenAI API prices of o1, GPT-5, GPT-6 Astra, GPT-6 Sol, GPT-6.1 Sol and GPT-6 Luna, and Epoch's OpenAI coding-agent spending insight (median $601/day in the week ending 15 Aug 2026; self-reported by OpenAI, list prices, interactive use only). Other rows keep the source labels below; treat aggregator and Wikipedia-sourced dates as secondary.

**Verification key:** every price is labeled with `source_type`: `official` (provider pricing page / official docs, fetched today or via Wayback snapshot of the official page), `official-launch` (provider announcement, price verified only through a dated third-party record - flagged), or `aggregator` / `research` (Epoch AI, Artificial Analysis, press). Anything I could not verify is marked **UNCONFIRMED** with an empty cell.

---

## 1. Published analyses with numbers

### 1.1 Stanford HAI AI Index 2025 - CONFIRMED (headline), details via its data source (Epoch AI)

- **Claim:** "Driven by increasingly capable small models, the inference cost for a system performing at the level of GPT-3.5 dropped over 280-fold between November 2022 and October 2024."
- **Metric:** cost of the cheapest system whose performance matches GPT-3.5 level, defined as **MMLU 64.8**; price per 1M tokens (the underlying figure is a blended price - see Epoch entry below; the AI Index figure is based on Epoch AI data).
- **Period:** November 2022 -> October 2024.
- **Exact endpoints (from the Epoch AI table the AI Index figure is built on):** GPT-3.5 (release 2022-11-30) **$20.00 per 1M tokens (blended)** -> Gemini-1.5-Flash-8B (release 2024-10-03) **$0.07**. 20.00 / 0.07 ~ 286x, i.e. "over 280-fold". Models and dates confirmed; the dollar endpoints themselves are stated in Epoch's published table, not on the HAI landing page.
- Source: https://hai.stanford.edu/ai-index/2025-ai-index-report ; data: https://epoch.ai/data-insights/llm-inference-price-trends

### 1.2 Epoch AI, "LLM inference prices have fallen rapidly but unequally across tasks" (12 Mar 2025) - CONFIRMED

- **Claim:** "The inference price of LLMs has fallen dramatically... the price to achieve GPT-4's performance on a set of PhD-level science questions [GPQA Diamond] fell by 40x per year. The rate of decline varies dramatically depending on the performance milestone, ranging from **9x to 900x per year**." In the methodology: "prices declining between 9x per year and 900x per year, with a **median of 50x per year**"; removing pre-2024 data raises the median to 200x/year; the fastest trends (900x/yr) start after January 2024. The 9x/900x endpoints are **not** attributed to specific benchmarks in the article.
- **Metric:** cheapest price at fixed benchmark thresholds across MMLU (43.9 / 64.8 / 68.0 / 86.0 / 87.0), GPQA Diamond (33 / 50 / 53 / 56), MATH-500, MATH 5, HumanEval, LMSys Chatbot Arena ELO. Price = **3:1 blended input:output weighted average** ("All prices were a 3:1 weighted average of input and output token prices"), first-party API price where available, else median across providers. **Reasoning models were excluded** from the per-token price analysis. Price changes are recorded as new observations (a model's price is matched to the price current at the recorded date).
- **Period:** 2021-2025 (six benchmarks, three years).
- **Useful dated rows (MMLU 64.8 = "GPT-3.5 level"):** GPT-3.5 $20.00 (2022-11-30) -> GPT-3.5 Turbo $2.00 (2023-03-06) -> GPT-3.5-Turbo-2023-11 $0.75 (2023-11-06) -> Claude-3-Haiku $0.50 (2024-03-04) -> Gemini-1.5-Flash $0.13 (2024-05-10) -> Llama-3.1-8B $0.10 (2024-07-23) -> **Gemini-1.5-Flash-8B $0.07 (2024-10-03)**.
- **MMLU 86 ("GPT-4 level"):** GPT-4-0314 $37.50 (2023-03-14) -> GPT-4 Turbo $15.00 (2023-11-06) -> GPT-4o $7.50 (2024-05-13) -> Gemini-1.5-Pro $2.19 (2024-05-23) -> Gemini 2.0 Flash $0.18 (2025-02-05).
- **Arena ELO >=1186 (GPT-4-0314 level):** GPT-4-0314 $37.50 (2023-03-14) -> GPT-4 Turbo $15.00 -> Claude-3-Sonnet $6.00 (2024-03-04) -> Llama-3-70B $0.89 (2024-04-18) -> Gemini-1.5-Flash $0.13 (2024-05-10) -> Gemini-1.5-Flash-8B $0.07 (2024-10-03).
- Source: https://epoch.ai/data-insights/llm-inference-price-trends

### 1.3 a16z, "Welcome to LLMflation" (12 Nov 2024, Guido Appenzeller) - CONFIRMED

- **Claim:** "For an LLM of equivalent performance, the cost is decreasing by **10x every year**." Concrete anchors: cheapest model at MMLU >=42 went from **GPT-3 at $60/M tokens (Nov 2021)** to **Llama 3.2 3B on Together.ai at $0.06/M (Nov 2024)** - 1,000x in 3 years; at MMLU >=83, price fell ~62x since GPT-4 (Mar 2023).
- **Metric:** cheapest monthly price of any model meeting a fixed MMLU score (42 and 83); **simple average of input and output price**; models from OpenAI, Anthropic and Meta Llama (incl. third-party inference providers); historical prices from the Internet Archive.
- **Frontier observation quoted (for Q3):** "OpenAI's leading model today, o1, has the same cost per output token as GPT-3 had at launch ($60 per million)."
- Source: https://a16z.com/llmflation-llm-inference-cost/

### 1.4 Sam Altman, "Three Observations" (Feb 2025) - CONFIRMED

- **Claim:** "The cost to use a given level of AI falls about **10x every 12 months**, and lower prices lead to much more use. You can see this in the token cost from GPT-4 in early 2023 to GPT-4o in mid-2024, where the price per token dropped about **150x** in that time period."
- **Metric:** unspecified "price per token" for a given level of AI (GPT-4 $30/$60 Mar 2023 -> GPT-4o $5/$15 May 2024 is 6-4x on list price; the 150x figure refers to price for *equivalent capability*, consistent with the LLMflation framing, not to GPT-4o's own list price).
- Source: https://blog.samaltman.com/three-observations

### 1.5 Artificial Analysis - cost to run its Intelligence Index - CONFIRMED (point-in-time and cross-model; a long time series is not published as one chart)

- **Metric:** since **Intelligence Index v4.1 (15 June 2026)**, AA publishes **Cost per Task, Time per Task, and Tokens per Task** - "the total cost, total time, and total output tokens for a model to run the Intelligence Index... divided by the number of tasks", including cached-input-token effects. (Index weights: GDPval-AA v2 20%, Terminal-Bench 2.1 16%, tau3-Bench Banking 14%, HLE 12%, GPQA 6%, etc. - an agentic-heavy composite.)
- **Key numbers (v4.1, June 2026):** Claude Fable 5 (AAII 60) **$3.25/task** (highest, then unavailable); Claude Opus 4.8 max (56) **$1.78/task**; GPT-5.5 xhigh (55) **$0.99/task**; **DeepSeek V4 Pro max (44) $0.04/task** - "other leading proprietary models costing 20x to 45x more". Time per task 1.5 min (Grok 4.3) to 13.5 min (Claude Sonnet 4.6, which "uses more output tokens... than Claude Opus 4.8").
- **September 2026 update (v4.3.x era, via AA article "claude-fable-5-1" reported by FourWeekMBA, 2 Sep 2026):** Claude Fable 5.1 **AAII 66** (highest AA has ever recorded) at **~$3.7/task** ($3.76 in AA's article vs $3.69 on the live model page - flagged discrepancy); Fable 5 ~$3.1/task (AAII 62); Claude Opus 5 $2.34/task (AAII 63); GPT-5.6 "Sol" 61 and Grok 4.6 61 (costs not quoted). Fable 5.1 uses **~1.7x the output tokens** of Fable 5 despite unchanged list prices - capability and cost per task rising together.
- **Takeaway for the slide:** per-token price of the frontier is flat-ish, but cost *per unit of benchmark work* at the top is ~90x the efficient frontier ($0.04 vs $3.7) and rose ~20% generation-over-generation.
- Sources: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-1 ; https://artificialanalysis.ai/articles/claude-fable-5-1 ; summary: https://fourweekmba.com/ai-claude-fable-5-1-artificial-analysis-cost-benchmark/

### 1.5b Artificial Analysis cost per task over time

The [Artificial Analysis Trends efficiency chart](https://artificialanalysis.ai/trends#efficiency) tracks cost per Intelligence Index task at six thresholds (>= 10, 20, 30, 40, 50, 60). This complements fixed-capability price-per-token series by including the tokens used for the task. Checked 2026-10-16 against the primary page: the current chart uses Intelligence Index v4.3.2; data points were not exported or independently recalculated. Do not substitute per-token prices for this per-task metric.

### 1.6 2026 updates of these analyses

- **AI Index 2026 exists** (published 2026; chapter PDFs at hai.stanford.edu). I checked the landing page and the public highlights of the Economy and Technical Performance chapters: **no updated inference-cost-decline figure appears in the public web highlights**. Whether the full 2026 PDF refreshes the 2025 GPT-3.5-level cost analysis is **UNCONFIRMED** (the chapter PDF exceeded fetch limits; the 2025 figure above remains the citable one). The 2026 report's adjacent findings: benchmark reliability problems (invalid-question rates up to 42% on GSM8K, 2-42% across nine benchmarks), frontier performance convergence, and compute spend by OpenAI/Anthropic reaching $16.3B/$6.8B in 2025.
- Source: https://hai.stanford.edu/ai-index/2026-ai-index-report
- **Epoch AI 2026 update (adjacent, not a re-run of the price insight):** "Coding-agent spending by OpenAI researchers is doubling roughly every month" (5 Oct 2026) - see section 4.
- a16z has not published a follow-up LLMflation update that I could find (UNCONFIRMED whether one exists).

---

## 2. Dated data table of price/capability points (2023 - Oct 2026)

Notes: prices per **1M tokens, list, Standard tier, USD**. "Blended 3:1" = 0.75*input + 0.25*output (Epoch/AA convention) - useful for single-number comparisons. Empty cells = UNCONFIRMED (not invented). Launch months are the model's release month; for price rows taken from Epoch the "date" is Epoch's recorded observation date.

| Date | Model | Provider | Input $/1M | Output $/1M | Blended 3:1 | Capability anchor | Source |
|---|---|---|---|---|---|---|---|
| 2023-03 | GPT-4 (8K, 0314/0613) | OpenAI | 30.00 | 60.00 | 37.50 | MMLU 86.0; GPQA-D 33.0; Arena 1186 (Epoch) | OpenAI pricing (official); Epoch (research) |
| 2023-03 | GPT-3.5 Turbo | OpenAI | UNCONFIRMED (~2.00 in ~ out) | UNCONFIRMED | 2.00 | MMLU 68.0 (Epoch) | Epoch |
| 2023-11 | GPT-4 Turbo (preview) | OpenAI | 10.00 | 30.00 | 15.00 | MMLU 87.0; GPQA-D 50.0 (Epoch) | OpenAI pricing lists gpt-4-turbo-2024-04-09 $10/$30 (official); Epoch dated 2023-11-06 |
| 2023-11 | GPT-3.5 Turbo (1106) | OpenAI | 1.00 | 2.00 | 0.75 (Epoch obs.; later price cut - see caveat) | MMLU 68.0 (Epoch) | OpenAI pricing (official, current); Epoch |
| 2024-03 | Claude 3 Haiku | Anthropic | UNCONFIRMED (widely reported $0.25) | UNCONFIRMED (widely reported $1.25) | 0.50 | MMLU 71; GPQA-D 33; HumanEval 77; Arena 1179 (Epoch) | Epoch |
| 2024-05 | GPT-4o (2024-05-13) | OpenAI | 5.00 | 15.00 | 7.50 | MMLU 87.0; GPQA-D 53.0 (Epoch) | OpenAI pricing (official launch price kept for the dated snapshot) |
| 2024-05 | Gemini 1.5 Flash | Google | UNCONFIRMED (launch announcement not retrieved) | UNCONFIRMED | 0.13 (Epoch observation) | MMLU 79; GPQA-D 39; Arena 1227 (Epoch) | Epoch |
| 2024-07 | GPT-4o mini | OpenAI | 0.15 | 0.60 | 0.26 | MATH-500 79 (Epoch) | OpenAI pricing (official) |
| 2024-10 | Gemini 1.5 Flash-8B | Google | UNCONFIRMED (widely reported $0.0375) | UNCONFIRMED (widely reported $0.15) | 0.07 | MMLU 75; Arena 1211 (Epoch) | Epoch |
| 2024-12 | DeepSeek-V3 | DeepSeek | 0.27 (cache miss; 0.07 cache hit) | 1.10 | 0.48 | GPQA-D 57 (Epoch); blended $0.48 | DeepSeek API docs via Wayback 2025-01-31 (official) |
| 2024-12 | o1 | OpenAI | 15.00 | 60.00 | 26.25 | (reasoning model; Epoch excluded reasoning - no score) | OpenAI pricing (official); date Dec 2024 widely documented |
| 2025-01 | DeepSeek-R1 | DeepSeek | 0.55 | 2.19 | 0.96 | reasoning model | DeepSeek API docs via Wayback 2025-01-31 (official) |
| 2025-02 | Gemini 2.0 Flash | Google | UNCONFIRMED (page retired; widely reported $0.10) | UNCONFIRMED (widely reported $0.40) | 0.18 | MMLU 88; GPQA-D 62 (Epoch) | Epoch |
| 2025-03 | Gemini 2.5 Pro | Google | 1.25 (<=200K) | 10.00 (<=200K) | 3.44 | - | Gemini API pricing via Wayback 2026-10-01 (official) |
| 2025-04 | o3-mini | OpenAI | 1.10 | 4.40 | 1.93 | - | OpenAI pricing (official) |
| 2025-05 | Gemini 2.5 Flash | Google | 0.30 | 2.50 | 0.85 | - | Gemini API pricing via Wayback 2026-10-01 (official) |
| 2025-08 | GPT-5 | OpenAI | 1.25 | 10.00 | 3.44 | - | OpenAI pricing (official); launch Aug 2025 widely documented |
| 2025-08 | GPT-5 mini | OpenAI | 0.25 | 2.00 | 0.69 | - | OpenAI pricing (official) |
| 2025-08 | GPT-5 Pro | OpenAI | 15.00 | 120.00 | 41.25 | - | OpenAI pricing (official) |
| 2025-11 | Claude Opus 4.5 | Anthropic | 5.00 | 25.00 | 10.00 | - | Anthropic pricing (official, legacy list); date 2025-11-24 (Wikipedia) |
| 2025-11 | Gemini 3 Pro | Google | UNCONFIRMED (no longer listed; successor 3.1 Pro is $2/$12) | UNCONFIRMED | - | - | UNCONFIRMED |
| 2025-12 | Gemini 3 Flash (preview) | Google | 0.50 | 3.00 | 1.13 | - | Gemini API pricing via Wayback 2026-10-01 (official); date 2025-12-17 (Wikipedia) |
| 2026-02 | Gemini 3.1 Pro (preview) | Google | 2.00 (<=200K) | 12.00 (<=200K) | 4.50 | AAII 46 (AA, June 2026) | Gemini API pricing via Wayback (official); date 2026-02-19 (Wikipedia) |
| 2026-06 | Claude Fable 5 | Anthropic | 10.00 | 50.00 | 20.00 | AAII 60 (v4.1) / 62 (v4.3 era); $3.25->~$3.1 per AA task | Anthropic pricing (official); date 2026-06-09 (Wikipedia); AA |
| 2026-06 | DeepSeek V4 Pro | DeepSeek | 0.66 (off-peak; 1.32 peak) | 1.98 (off-peak; 3.96 peak) | 0.99 (off-peak) | AAII 44; **$0.04 per AA task** | DeepSeek pricing (official, V4-Pro-0813); AA (June 2026); exact V4 launch date UNCONFIRMED (V4 Pro cited by AA on 2026-06-15) |
| 2026-07 | Claude Opus 5 | Anthropic | 5.00 | 25.00 | 10.00 | AAII 63; $2.34 per AA task | Anthropic pricing (official, legacy list); date 2026-07-24 (Wikipedia); AA |
| 2026-08 | GPT-5.6 Sol | OpenAI | 4.00 (promo; >= through 2026-11-21) | 20.00 | 8.00 | AAII 61 (v4.3 era) | OpenAI pricing (official); month per promo/aggregator reports |
| 2026-09 | GPT-6 Astra | OpenAI | 10.00 | 50.00 | 20.00 | flagship; AAII UNCONFIRMED | OpenAI pricing (official); released 2026-09-03/04 (Wikipedia) |
| 2026-09 | Claude Fable 5.1 | Anthropic | 10.00 | 50.00 | 20.00 | AAII 66; ~$3.7 per AA task | Anthropic pricing (official); date 2026-09-01 (Wikipedia); AA |
| 2026-09 | Claude Opus 5.5 | Anthropic | 4.00 | 20.00 | 8.00 | - | Anthropic pricing (official); date 2026-09-22 (Wikipedia) |
| 2026-09 | Claude Sonnet 5.5 | Anthropic | 2.00 | 10.00 | 4.00 | - | Anthropic pricing (official); date 2026-09-28 (Wikipedia) |
| 2026-09 | GPT-6 Sol | OpenAI | 2.00 | 10.00 | 4.00 | - | OpenAI pricing (official); released 2026-09-22 (Wikipedia) |
| 2026-09 | GPT-6 Luna | OpenAI | 0.10 | 0.50 | 0.20 | - | OpenAI pricing (official); released 2026-09-22 (Wikipedia) |
| 2026-09 | GPT-6.1 Sol | OpenAI | 2.00 | 10.00 | 4.00 | - | OpenAI pricing (official); date 2026-09-29 (aggregator benchlm.ai) |
| 2026-09 | Gemini 3.8 Flash | Google | 0.75 (intro pricing through 2026-12-31; 1.50 from 2027-01-01) | 3.75 (intro; 7.50 from 2027) | 1.50 | - | Gemini API pricing via Wayback (official); released 2026-09-02 (Wikipedia) |
| 2026-07 | Gemini 3.5 Flash-Lite | Google | 0.30 | 2.50 | 0.85 | - | Gemini API pricing via Wayback (official); released 2026-07-21 (Wikipedia) |
| 2026-10 | Claude Haiku 5.5 | Anthropic | 0.10 (<=100K prompts) | 0.50 (<=100K) | 0.20 | - | Anthropic pricing (official); date 2026-10-07 (Wikipedia) |
| 2026-10 | DeepSeek V4.1 Flash (`deepseek-flash`) | DeepSeek | 0.30 (peak; 0.15 off-peak) | 1.20 (peak; 0.60 off-peak) | 0.53 (peak) | - | DeepSeek pricing (official, current) |
| 2026-10 | Gemini 4 Argon | Google | UNCONFIRMED (GA 2026-10-13; not yet on the fetched pricing snapshot of 2026-10-01) | UNCONFIRMED | - | - | UNCONFIRMED |
| 2026-10 | Claude Mythos 5.1 | Anthropic | UNCONFIRMED (trusted-access program only) | UNCONFIRMED | - | - | UNCONFIRMED |

**Source URLs for the table:** OpenAI: https://developers.openai.com/api/docs/pricing (openai.com/api/pricing returns 403 to bots; the developers' docs page is the official price list). Anthropic: https://www.anthropic.com/pricing . Google: https://ai.google.dev/gemini-api/docs/pricing (verified via Wayback snapshot 2026-10-01; live page blocked fetches). DeepSeek current: https://api-docs.deepseek.com/quick_start/pricing ; DeepSeek V3/R1 (Jan 2025): https://web.archive.org/web/20250131222749/https://api-docs.deepseek.com/quick_start/pricing . Epoch dated series: https://epoch.ai/data-insights/llm-inference-price-trends . Launch dates: https://en.wikipedia.org/wiki/GPT-6 , https://en.wikipedia.org/wiki/Claude_(language_model) , https://en.wikipedia.org/wiki/Gemini_(language_model) . AA scores/costs: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-1 , https://artificialanalysis.ai/articles/claude-fable-5-1 .

### CSV

```csv
date,model,provider,input_usd_per_m,output_usd_per_m,capability_metric,capability_score,source_url,source_type
2023-03,GPT-4 (8K),OpenAI,30.00,60.00,MMLU (Epoch),86.0,https://developers.openai.com/api/docs/pricing,official
2023-03,GPT-3.5 Turbo,OpenAI,UNCONFIRMED,UNCONFIRMED,MMLU (Epoch blended $2.00),68.0,https://epoch.ai/data-insights/llm-inference-price-trends,research
2023-11,GPT-4 Turbo,OpenAI,10.00,30.00,MMLU (Epoch),87.0,https://developers.openai.com/api/docs/pricing,official
2023-11,GPT-3.5 Turbo 1106,OpenAI,1.00,2.00,MMLU (Epoch),68.0,https://developers.openai.com/api/docs/pricing,official
2024-03,Claude 3 Haiku,Anthropic,UNCONFIRMED,UNCONFIRMED,MMLU (Epoch blended $0.50),71.0,https://epoch.ai/data-insights/llm-inference-price-trends,research
2024-05,GPT-4o (2024-05-13),OpenAI,5.00,15.00,MMLU (Epoch),87.0,https://developers.openai.com/api/docs/pricing,official
2024-05,Gemini 1.5 Flash,Google,UNCONFIRMED,UNCONFIRMED,MMLU (Epoch blended $0.13),79.0,https://epoch.ai/data-insights/llm-inference-price-trends,research
2024-07,GPT-4o mini,OpenAI,0.15,0.60,MATH-500 (Epoch),79.0,https://developers.openai.com/api/docs/pricing,official
2024-10,Gemini 1.5 Flash-8B,Google,UNCONFIRMED,UNCONFIRMED,MMLU (Epoch blended $0.07),75.0,https://epoch.ai/data-insights/llm-inference-price-trends,research
2024-12,DeepSeek-V3,DeepSeek,0.27,1.10,GPQA Diamond (Epoch),57.0,https://web.archive.org/web/20250131222749/https://api-docs.deepseek.com/quick_start/pricing,official
2024-12,o1,OpenAI,15.00,60.00,,UNCONFIRMED,https://developers.openai.com/api/docs/pricing,official
2025-01,DeepSeek-R1,DeepSeek,0.55,2.19,,UNCONFIRMED,https://web.archive.org/web/20250131222749/https://api-docs.deepseek.com/quick_start/pricing,official
2025-02,Gemini 2.0 Flash,Google,UNCONFIRMED,UNCONFIRMED,MMLU (Epoch blended $0.18),88.0,https://epoch.ai/data-insights/llm-inference-price-trends,research
2025-03,Gemini 2.5 Pro,Google,1.25,10.00,,UNCONFIRMED,https://ai.google.dev/gemini-api/docs/pricing,official
2025-04,o3-mini,OpenAI,1.10,4.40,,UNCONFIRMED,https://developers.openai.com/api/docs/pricing,official
2025-05,Gemini 2.5 Flash,Google,0.30,2.50,,UNCONFIRMED,https://ai.google.dev/gemini-api/docs/pricing,official
2025-08,GPT-5,OpenAI,1.25,10.00,,UNCONFIRMED,https://developers.openai.com/api/docs/pricing,official
2025-08,GPT-5 mini,OpenAI,0.25,2.00,,UNCONFIRMED,https://developers.openai.com/api/docs/pricing,official
2025-08,GPT-5 Pro,OpenAI,15.00,120.00,,UNCONFIRMED,https://developers.openai.com/api/docs/pricing,official
2025-11,Claude Opus 4.5,Anthropic,5.00,25.00,,UNCONFIRMED,https://www.anthropic.com/pricing,official
2025-11,Gemini 3 Pro,Google,UNCONFIRMED,UNCONFIRMED,,UNCONFIRMED,https://ai.google.dev/gemini-api/docs/pricing,UNCONFIRMED
2025-12,Gemini 3 Flash preview,Google,0.50,3.00,,UNCONFIRMED,https://ai.google.dev/gemini-api/docs/pricing,official
2026-02,Gemini 3.1 Pro,Google,2.00,12.00,AA Intelligence Index (v4.1),46,https://ai.google.dev/gemini-api/docs/pricing,official
2026-06,Claude Fable 5,Anthropic,10.00,50.00,AA Intelligence Index (v4.1 / v4.3 era),60 / 62,https://www.anthropic.com/pricing,official
2026-06,DeepSeek V4 Pro,DeepSeek,0.66,1.98,AA Intelligence Index (v4.1),44,https://api-docs.deepseek.com/quick_start/pricing,official
2026-07,Claude Opus 5,Anthropic,5.00,25.00,AA Intelligence Index (v4.3 era),63,https://www.anthropic.com/pricing,official
2026-08,GPT-5.6 Sol,OpenAI,4.00,20.00,AA Intelligence Index (v4.3 era),61,https://developers.openai.com/api/docs/pricing,official
2026-09,GPT-6 Astra,OpenAI,10.00,50.00,,UNCONFIRMED,https://developers.openai.com/api/docs/pricing,official
2026-09,Claude Fable 5.1,Anthropic,10.00,50.00,AA Intelligence Index (v4.3 era); $/task ~3.7,66,https://www.anthropic.com/pricing,official
2026-09,Claude Opus 5.5,Anthropic,4.00,20.00,,UNCONFIRMED,https://www.anthropic.com/pricing,official
2026-09,Claude Sonnet 5.5,Anthropic,2.00,10.00,,UNCONFIRMED,https://www.anthropic.com/pricing,official
2026-09,GPT-6 Sol,OpenAI,2.00,10.00,,UNCONFIRMED,https://developers.openai.com/api/docs/pricing,official
2026-09,GPT-6 Luna,OpenAI,0.10,0.50,,UNCONFIRMED,https://developers.openai.com/api/docs/pricing,official
2026-09,GPT-6.1 Sol,OpenAI,2.00,10.00,,UNCONFIRMED,https://developers.openai.com/api/docs/pricing,official
2026-09,Gemini 3.8 Flash,Google,0.75,3.75,,UNCONFIRMED,https://ai.google.dev/gemini-api/docs/pricing,official
2026-07,Gemini 3.5 Flash-Lite,Google,0.30,2.50,,UNCONFIRMED,https://ai.google.dev/gemini-api/docs/pricing,official
2026-10,Claude Haiku 5.5,Anthropic,0.10,0.50,,UNCONFIRMED,https://www.anthropic.com/pricing,official
2026-10,DeepSeek V4.1 Flash,DeepSeek,0.30,1.20,,UNCONFIRMED,https://api-docs.deepseek.com/quick_start/pricing,official
2026-10,Gemini 4 Argon,Google,UNCONFIRMED,UNCONFIRMED,,UNCONFIRMED,https://ai.google.dev/gemini-api/docs/pricing,UNCONFIRMED
2026-10,Claude Mythos 5.1,Anthropic,UNCONFIRMED,UNCONFIRMED,,UNCONFIRMED,https://www.anthropic.com/pricing,UNCONFIRMED
```

---

## 3. Frontier price trend (most capable model per provider at launch)

**Direct answer: the top list price first fell (2023->mid-2025, as flagships got cheaper per token), then stopped falling and in 2026 rose outright at OpenAI and Anthropic, while Google kept its top tier cheap and DeepSeek raised prices slightly.** The cheap end (small models) collapsed 2022-2024 and then hit a floor around $0.10-0.30 input / $0.50-1.20 output where it has stayed.

| Date | Provider's most capable model | Input/Output $/1M | Evidence |
|---|---|---|---|
| 2023-03 | OpenAI: GPT-4 | 30 / 60 | OpenAI pricing (gpt-4-0613), official |
| 2023-11 | OpenAI: GPT-4 Turbo | 10 / 30 | OpenAI pricing; Epoch |
| 2024-03 | Anthropic: Claude 3 Opus | UNCONFIRMED (widely reported 15 / 75; not verified from an official page in this research) | UNCONFIRMED |
| 2024-05 | OpenAI: GPT-4o | 5 / 15 | OpenAI pricing (dated snapshot), official |
| 2024-12 | OpenAI: o1 | 15 / 60 | OpenAI pricing, official; a16z: "same cost per output token as GPT-3 at launch ($60)" |
| 2025-04 | OpenAI: o1-pro | 150 / 600 | OpenAI pricing, official |
| 2025-08 | OpenAI: GPT-5 / GPT-5 Pro | 1.25 / 10 and 15 / 120 | OpenAI pricing, official |
| 2025-11 | Anthropic: Claude Opus 4.5 | 5 / 25 (down from Opus 4.1's widely reported 15 / 75 - UNCONFIRMED) | Anthropic pricing, official (current legacy list) |
| 2025-11 | Google: Gemini 3 Pro | UNCONFIRMED (successor 3.1 Pro listed at 2 / 12) | UNCONFIRMED |
| 2026-06 | Anthropic: Claude Fable 5 (new Mythos tier above Opus) | **10 / 50** - up 2x/2x vs Opus 4.5-5 | Anthropic pricing, official |
| 2026-08->09 | OpenAI: GPT-5.5 Pro -> **GPT-6 Astra (2026-09-03)** | 30 / 180 -> **10 / 50** (Astra "Ultrafast" tier: 60 / 300) | OpenAI pricing, official |
| 2026-09 | Anthropic: Claude Fable 5.1 (2026-09-01) | 10 / 50 (per-token unchanged; cache-read cut $1.00->$0.25) | Anthropic pricing, official |
| 2026-10 | Google: Gemini 4 Argon (GA 2026-10-13) | UNCONFIRMED | UNCONFIRMED |
| 2026-10 | DeepSeek: V4 Pro | 0.66 / 1.98 off-peak (1.32 / 3.96 peak) - up from V3's 0.27 / 1.10 | DeepSeek pricing, official |

Reading of the trend with sources: OpenAI's flagship output price went 60 -> 30 -> 15 (2023-2024), back up to 60 with o1 (Dec 2024), down to 10 for standard GPT-5 while the Pro tier opened at 120-180 (2025-2026), and GPT-6 Astra re-raised the flagship to 50 (300 Ultrafast). Anthropic's top model dropped to 5/25 with Opus 4.5 and then the new Fable tier doubled it to 10/50. Net: **frontier list prices in Oct 2026 are at or above their 2024 level, not below.** Sources: https://developers.openai.com/api/docs/pricing , https://www.anthropic.com/pricing , https://ai.google.dev/gemini-api/docs/pricing (Wayback 2026-10-01), https://api-docs.deepseek.com/quick_start/pricing , https://a16z.com/llmflation-llm-inference-cost/ .

---

## 4. Tokens per task: reasoning models and agents consume many more tokens

1. **Artificial Analysis per-task metrics (primary, measured):** running the AA Intelligence Index costs **$0.04 (DeepSeek V4 Pro) to $3.25-3.78 (Claude Fable 5 / 5.1) per task** - a ~90x spread - and time per task of **1.5 to 13.5 minutes** of decoding for leading models; Claude Sonnet 4.6 takes *longer per task than Opus 4.8 because it uses more output tokens*; **Fable 5.1 uses ~1.7x the output tokens of Fable 5** at unchanged list prices. Cost per task at the frontier is *rising* (Fable 5.1 ~ +20% vs Fable 5) because capability gains are being delivered by spending more test-time tokens. Sources: https://artificialanalysis.ai/articles/artificial-analysis-intelligence-index-v4-1 ; https://artificialanalysis.ai/articles/claude-fable-5-1 ; https://fourweekmba.com/ai-claude-fable-5-1-artificial-analysis-cost-benchmark/
2. **Epoch AI on OpenAI's own coding agents (Oct 2026):** the median OpenAI researcher's daily coding-agent usage at API prices rose from **under $1/day (Jan 2026) to $601/day (mid-Aug 2026)**; the 90th-percentile researcher reached **$7,047/day** (~ **$2M/year**); recent doubling time ~ **1 month** (median 1.8x/month, p90 2.2x/month). Self-reported by OpenAI, priced at list, interactive usage only. Sources: https://epoch.ai/data-insights/openai-coding-agent-spending (data from https://openai.com/index/research-acceleration-view-inside-openai/ , accessed via Epoch).
3. **Epoch's price-trend methodology itself:** reasoning models were **excluded** from the 2025 per-token price analysis ("We excluded reasoning models from our analysis of per-token prices") - i.e., the famous 9x-900x/year curves measure non-thinking tokens and understate the cost of reasoning workloads, whose thinking tokens are billed as output. Source: https://epoch.ai/data-insights/llm-inference-price-trends
4. **Anthropic statements:** at Fable 5.1's launch Anthropic said typical token-billed workloads would cost ~25% less and **agentic workloads up to ~45% less** "due to increased efficiency" - implicitly confirming agentic workloads are the expensive ones; AA quantified the cache-read cut ($1.00->$0.25/MTok) as saving ~$1.40 per index task. Source: https://en.wikipedia.org/wiki/Claude_(language_model) (quoting Anthropic); https://artificialanalysis.ai/articles/claude-fable-5-1
5. **Concrete agent spend example:** Nicholas Carlini's 16-agent Claude Opus 4.6 experiment (writing a C compiler in Rust) cost **nearly $20,000** in API tokens (Feb 2026). Source: https://en.wikipedia.org/wiki/Claude_(language_model)
6. Aggregator (not independently verified): tokensperday.com models global daily token consumption from public disclosures - treat numbers as UNCONFIRMED. OpenRouter publishes per-model token-volume rankings (https://openrouter.ai/rankings) but the page was not retrievable in this session.

---

## 5. Recommended chart design

**Is the proposed chart misleading?** Only if shown alone. A per-token price chart at fixed capability is accurate for what it measures, but (a) the collapse mostly happened 2022-2024 and then hit a floor at the cheap end, (b) the frontier tier did not get cheaper in 2026, and (c) reasoning models/agents convert cheap tokens into expensive tasks. Show the decline honestly and pair it with the counterpoint.

**Design - one main panel, log-scale Y (USD per 1M tokens, blended 3:1 where the series comes from Epoch; label the metric), X = launch/observation month, 2023-01 -> 2026-10, three lines:**

- **Line A - "GPT-3.5 level" (MMLU 64.8; the AI Index 2025 anchor):** GPT-3.5 Turbo $2.00 (2023-03) -> GPT-3.5 Turbo $0.75 (2023-11) -> Claude 3 Haiku $0.50 (2024-03) -> Gemini 1.5 Flash $0.13 (2024-05) -> Gemini 1.5 Flash-8B $0.07 (2024-10) -> then flat at the floor: GPT-6 Luna ~ $0.20 blended (2026-09), DeepSeek V4.1 Flash ~ $0.26-0.53 (2026-10). Story: ~30x in 19 months, then flat - the cheap tier commoditized.
- **Line B - "GPT-4 level" (MMLU 86-87):** GPT-4 $37.50 (2023-03) -> GPT-4 Turbo $15.00 (2023-11) -> GPT-4o $7.50 (2024-05) -> Gemini 1.5 Pro $2.19 (2024-05) -> Gemini 2.0 Flash $0.18 (2025-02) -> 2026 equivalents: DeepSeek V4.1 Flash ~ $0.53, Gemini 3.8 Flash ~ $1.50 (promo). Story: ~50-200x over three years and still falling slowly.
- **Line C - "frontier reasoning level" (2024-25 frontier, e.g., GPQA >=50; today's AAII >= 55):** o1 $26.25 (2024-12) -> GPT-5 $3.44 (2025-08) -> GPT-6 Sol $4.00 / Gemini 3.8 Flash $1.50 (2026-09). Story: fell ~10x from o1, then flattened - and per *task* it went up (AA: $0.99-3.78/task at the top).

**Optional right-hand mini-panel (the honest counterpoint):** AA cost per Intelligence-Index task (DeepSeek V4 Pro $0.04 -> Opus 4.8 $1.78 -> Fable 5.1 ~ $3.7) next to Epoch/OpenAI agent spend (median researcher: <$1 -> $601/day in 7.5 months). This carries the message "price per token falls, spend per task rises".

**One-sentence takeaway (plain language):** *"Intelligence got dramatically cheaper per token - what cost $37.50 per million tokens in March 2023 (GPT-4) now costs well under a dollar - but the newest frontier models cost as much as ever, and agents burn tokens by the million, so total spend keeps climbing."*

**Caveats to print on the slide (footnote):**
1. **List price vs real cost:** Batch APIs are 50% off (OpenAI, Anthropic, Google); cached input is 10% of list on GPT-6, ~1/4 on Claude 5.5, 1/10 on Gemini 3.x; DeepSeek halves prices off-peak; intro promos distort 2026 points (Gemini 3.8 Flash 50% promo to 2026-12-31; GPT-5.6 Sol promo to 2026-11-21).
2. **Blended price convention:** Epoch/AA use a 3:1 input:output blend; your actual mix differs (agents are output/thinking-heavy, so blended figures *understate* agent costs).
3. **Reasoning tokens:** the classic price series excludes reasoning models' thinking tokens (billed as output); per-token declines overstate the cost drop for reasoning workloads.
4. **Benchmark validity:** MMLU is contaminated/saturated (AI Index 2026: invalid-question rates 2-42% across nine benchmarks); MMLU 64.8 "GPT-3.5 level" is a 2022 yardstick, not today's agentic capability; AA Intelligence Index versions (v4.1 vs v4.3) are not directly comparable across time.
5. **Date/price ambiguity:** providers cut prices post-launch (e.g., GPT-3.5 Turbo, o3); rows mix launch dates with last-known list prices where the launch price was unverifiable (marked UNCONFIRMED).

---

## Research log / limitations

- Fetched directly: HAI AI Index 2025 + 2026 (landing pages, Economy & Technical Performance chapter highlights), Epoch price insight + OpenAI agent-spending insight, a16z LLMflation, Sam Altman "Three Observations", AA Intelligence Index v4.1 article, OpenAI developer pricing docs (full table), Anthropic pricing (full, incl. legacy), DeepSeek pricing (current + Wayback Jan 2025), Google Gemini API pricing (Wayback snapshot 2026-10-01; live page and 2024 snapshots blocked), Wikipedia (GPT-6, Claude, Gemini) for launch dates.
- Not retrievable this session, hence UNCONFIRMED where relevant: OpenAI openai.com/api/pricing (403; developers.openai.com used instead), Gemini 3 Pro launch price, Gemini 4 Argon price, Claude Mythos pricing, official 2024 Gemini Flash launch input/output prices (Epoch blended used instead), Claude 3 Opus/Haiku official price pages (Wikipedia has none; Epoch blended used), AI Index 2026 full-PDF cost figure, OpenRouter rankings page, DuckDuckGo rate-limited partway through (switched to primary sources).
- All aggregator-reported figures are labeled as such; nothing was back-filled from memory without a fetched source except launch dates of GPT-5 (Aug 2025), o1 (Dec 2024) and o3-mini (Jan-Feb 2025), which are uncontested public record and flagged by date only.
