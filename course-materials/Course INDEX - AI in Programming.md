# AI in Programming - Course INDEX

Reference notes from earlier AI programming courses.

Trener: Łukasz Matuszewski · [LinkedIn](https://www.linkedin.com/in/lukaszmatuszewski/) · [X](https://x.com/mrLumatic)

## PYTANIA NA START:
- Jak do tej pory używasz AI w pracy? Jakich narzędzi i w jaki sposób? (poziom autonomii)
- Jakie są Twoje doświadczenia? Pomaga? Przyspiesza? Spowalnia?
  - Czy używasz AGENTS.md, Rules?
- Największe problemy jakie masz z AI
- Co sądzisz o AI i przyszłości programowania?

---

## Trends 2025–2026 and what to expect next

- Knowledge base on latest trends: [NotebookLM](https://notebooklm.google.com/notebook/5a69e473-2453-4ee7-bcb6-866af29ba553)
- **Vibe Codding vs Vibe Engineering**
  - Linus Torvalds, DHH, and Node.js creator use automated code generation, e.g.:
    - "[the era of humans writing code is over.](https://x.com/kimmonismus/status/2013524952553492933)" (Node.js creator on AI generating code)
  - Microsoft named their new Power Apps platform Vibe - we prompt to build apps: [Vibe - Power Apps](https://vibe.powerapps.com/) (only in US right now) | Docs: [Omówienie nowego środowiska usługi Power Apps - Power Apps | Microsoft Learn](https://learn.microsoft.com/pl-pl/power-apps/vibe/overview)
  - Vibe Coding definition: [X.com](https://x.com/karpathy/status/1886192184808149383?lang=en)
- **Context rot & Context engineering**
- **Async Codding Agents in Cloud & on Mobile**
- CLI tools, Automation (Auto Review, Auto Mode, Schedules/Rutines, Loops), YOLO in container/cloud or local device (e.g. mac mini, Nvidia DGX Spark, AMD Strix Halo)
- Huge jump in quality of **Opus 4.5+**, GPT 5.4 and Gemini 3
- **Open Source LLMs** are very close to top models:
  - GLM-5.3 and GLM-5.3-Flash (z.ai), Kimi K3 (Moonshot), MiMo 1.6 (Xiaomi - great and very cheap), Minimax M3, DeepSeek v4 Pro - best OSS models are all from China (updated 02.10.2026)
  - Best OSS for consumer hardware: Google [Gemma 4](https://ollama.com/library/gemma4), [Qwen 3.6](https://ollama.com/library/qwen3.6)
  - could be used also with Claude Code: [Ollama](https://docs.ollama.com/integrations/claude-code), [vLLM](https://docs.vllm.ai/en/latest/serving/integrations/claude_code/) (good concurrency for scaling), [LocalAI](https://localai.io/integrations/index.html#claude-code)
  - **Local backend protocols (checked 2026-10-16):** Claude Code uses Anthropic Messages; Codex requires OpenAI Responses (`wire_api = "chat"` was removed). Native endpoints and translation through Ollama, vLLM, LiteLLM, claude-code-router, OpenRouter or LM Studio, with private-inference caveats and agent configs: [routing research](Research/local-llm-routing-messages-vs-responses-2026-10-16.md).
  - **Tiny and local models as agent workers** (verified 2026-10-01): LFM2.5-350M (219 MB) handles extraction and simple tool calls; 8 GB laptop = `gemma4:e2b` or LFM2.5-350M, 16 GB = `gemma4:e4b` / `gemma4:12b` / `lfm2.5:8b`; run them as workers with `ollama launch claude` or `codex --oss` - sizes, benchmarks, configs: [local-models-as-agent-workers.md](Research/local-models-as-agent-workers.md)
  - **"Luna" as a subagent model = GPT-6 Luna (OpenAI)**: cheap high-volume tier (350-3,000 local messages per 5h on Plus), `codex -m gpt-6-luna` - details and Codex lineup: [token-optimization-limits-resets.md](Research/token-optimization-limits-resets.md#gpt-6-luna-as-a-subagent-model)
- **Decision models (System 1)** - a new model category for fast, calibrated typed decisions (routing, triage, classification) instead of a full LLM call: [System One and Jev](https://typesafe.ai/blog/introducing-system-one-models-and-jev), leaderboard [Benchmark Heaven: Jev models](https://benchmarkheaven.com/jev-models)
  - Polish model [Basal Omni 1.0 Ultra](https://huggingface.co/Remek/basal-omni-1.0-ultra) by Remek, co-creator of the Polish LLM Bielik, briefly took first place on the Jev leaderboard (October 2026)
- **Source control redesigned for agents:** Anthropic grew from about 2,500 to 30,000 merges a day and replaced Git-based workflows with an in-house version control system in five months: [Redesigning source control at Anthropic](https://www.anthropic.com/research/redesigning-source-control), [discussion on Reddit](https://www.reddit.com/r/ClaudeCode/comments/1x5phqp/anthropic_went_from_2500_to_30000_merges_a_day/)
- **Screenshots** as a better way to provide context for vision models (less tokens thanks to compression, more information thanks to formatting, colors, images, etc.)
  - [DeepSeek OCR research paper on context compression](https://arxiv.org/abs/2510.18234)
  - [Andrej Karpathy on X.com](https://x.com/karpathy/status/1980397031542989305?lang=en) "whether pixels are better inputs to LLMs than text. Maybe it makes more sense that all inputs to LLMs should only ever be images"
- **Agents in the Cloud**
  - Delegating work to agents running 24/7 in the cloud, on VPS, or Codex/Claude/GH Environments
  - Case: [Levelsio runs agents on PROD VPS for >12 months](https://x.com/levelsio/status/2071162399864889705) + Theo's T3 thoughts about this
- **HTML replacing Markdown** - as more readable and interactive documents get easier to generate
  - You can start PRD, ADR or Plan with Markdown draft and ask agent to convert it to HTML
  - Example on feature branch in `/docs/PRD-Product-Requirements-Document.html`
- **AI disappointment**, broken promises, productivity drop, less fun and joy, frustration:
  - [AI Coding Sucks - YouTube](https://www.youtube.com/watch?v=0ZUkQF6boNg)
  - undeterministic nature of LLMs,
  - hallucinations,
  - crazy pace of changes in AI tools,
  - skill degradation, vanishing muscle memory
    - AI detox

### Stages of AI-Assisted Programming (0 → 5):

| Stage | Name | Description | Who manages |
|-------|------|-------------|-------------|
| **0** | Manual | No AI — pure hand-written code | Developer writes everything |
| **1** | Autocomplete | AI tab completion (Copilot-style) | Developer drives, AI suggests |
| **2** | Chat | AI chat assistant — ask, copy-paste | Developer + AI pair |
| **3** | Agent | Full file edits, tools, AGENTS.md, MCP | Developer oversees one agent |
| **4** | Multi-Agent | Parallel agents, async cloud, CI/CD | Developer orchestrates a fleet |
| **5** | **Dark Factory** | Fully autonomous; humans manage specs, not code | Human defines *what*, agents decide *how* and *when* |

> **Dark Factory** (term borrowed from manufacturing — a factory floor that runs lights-out because no humans need to be present): applied to software, agents ship features 24/7, humans set direction, review specs, and handle escalations only.

### 3 New IT Roles in the Agentic Era:

1. **Orchestrators** — Manage fleets of agents, define tasks, review and steer output. Write less code and more context: AGENTS.md, PRDs, rules. The "new tech lead".
2. **System/Infrastructure Builders** — Build the scaffolding: CI/CD pipelines, MCP servers, agent sandboxes, observability, cost controls. Deep technical role that requires architecture thinking.
3. **Domain Experts as Programmers** — Subject-matter experts (lawyers, analysts, operations staff, doctors) who use natural language in Claude Code, Cursor or similar tools to produce working software. **They don't know they've become programmers** — they describe what they want in English and get working software. The most disruptive shift: an entirely new supply of "programmers" who never wrote a line of code.

### Future of work research (2026):

How AI changes developer careers - key insights from the 2026 future-of-work research (full report: [AI, przyszlosc pracy i nowy profil specjalisty - Research/ai_future_of_work_t_m_comb_shaped_report_2026.md](Research/ai_future_of_work_t_m_comb_shaped_report_2026.md)):

- **From T-shaped to M- and comb-shaped.** A T-shaped expert has one deep domain and a narrow strip of general skills. Working with agents widens several strips at once (M shape) and ties deep areas together with AI leverage (comb shape).
- **43,5%** of tasks performed with AI assistance traditionally belonged to a different occupation than the user's - specialization boundaries blur.
- **PwC, "rise of the generalist":** "AI can enable specialists to do so much they become generalists." What pays: judgment, prioritization, decision making, integration, ownership of the outcome.
- **Integrative generalist:** broad context + several real competences + AI leverage + judgment + ownership.
- **Microsoft Agent Boss loop:** define the goal -> break the problem down -> delegate to agents -> control -> integrate -> decide -> own the result.
- The three new roles above (Orchestrators, System/Infrastructure Builders, Domain Experts) are the career paths this research describes.

### Research data on AI Coding:

- Knowledge base with research data: [NotebookLM](https://notebooklm.google.com/notebook/ae14d724-0256-482a-85b8-95fca9ba1c11)
- **Stanford** research on ROI of AI code (from 07.2025):
  - YT talk 12.2025 [Can you prove AI ROI in Software Eng? (Stanford 120k Devs Study) – Yegor Denisov-Blanch, Stanford - YouTube](https://www.youtube.com/watch?v=JvosMkuNxF8)
  - Insights on [X.com](https://x.com/dexhorthy/status/1992266735970652447)
  - Slides: [Yegor Denisov-Blanch - The AI Conference](https://aiconference.com/speakers/yegor-denisov-blanch/)
  - Original talk from 07.2025 on YT: [Does AI Actually Boost Developer Productivity? (100k Devs Study) - Yegor Denisov-Blanch, Stanford - YouTube](https://www.youtube.com/watch?v=tbDDYKRFjhk)
- US, 12.2025: [Beyond Productivity: Evaluating the Hidden Costs of Generative AI in Software Development by Edward Anderson, Geoffrey Parker, Burcu Tan :: SSRN](https://papers.ssrn.com/sol3/papers.cfm?abstract_id=5842302)
- METR, US, 07.2025: [Measuring the Impact of Early-2025 AI on Experienced Open-Source Developer Productivity - METR](https://metr.org/blog/2025-07-10-early-2025-ai-experienced-os-dev-study/)
- India 09.2025: [\[2509.19708\] Intuition to Evidence: Measuring AI's True Impact on Developer Productivity](https://arxiv.org/abs/2509.19708)
- Meta: [Measuring the Impact of AI on Developer Productivity at Meta - YouTube](https://www.youtube.com/watch?v=1OzxYK2-qsI)
- **QUESTION:**
  - **Do you measure velocity / ROI / time estimations / Quality?** e.g.
  - Velocity in Jira with story points,
  - number of comments on CR,
  - number of issues/bugs/tickets,
  - it helps to measure AI impact on their work
- **The Productivity J-Curve** - productivity drops for 1-2 months when you learn

### Case Studies:

- **Microsoft: Galen Hunt's original ambition:** eliminate **every line of C/C++ from Microsoft by 2030**, using AI and algorithms to rewrite Microsoft's largest codebases in **Rust**. North Star: **1 engineer, 1 month, 1 million lines of code**; a scalable code graph guides agents making mass modifications. Hunt later clarified in the same post that this is a research project enabling language migration, not an announced AI rewrite of Windows.
  - Linkedin post from [Galen Hunt - Principal Software Engineer (CoreAI)](https://www.linkedin.com/posts/galenh_principal-software-engineer-coreai-microsoft-activity-7407863239289729024-WTzf)
  - [Code graphs, hybrid migration and the distinction from Code Mode](Research/code-mode-and-algorithmic-code-migration-2026-10-13.md#microsoft-research-ambition): research ambition, not an achieved throughput benchmark.
   My goal is to eliminate every line of C and C++ from Microsoft by 2030. Our strategy is to combine AI *and* Algorithms to rewrite Microsoft's largest codebases. Our North Star is "1 engineer, 1 month, 1 million lines of code".   To accomplish this previously unimaginable task, we've built a powerful code processing infrastructure. Our algorithmic infrastructure creates a scalable graph over source code at scale. Our AI processing infrastructure then enables us to apply AI agents, guided by algorithms, to make code modifications at scale. The core of this infrastructure is already operating at scale on problems such as code understanding.

- **OpenClaw** — fastest-growing GitHub project in history (launched late Nov 2025)
  - **220k+ Stars, 790 contributors, 4,300+ open PRs** — [github.com/openclaw/openclaw](https://github.com/openclaw/openclaw)
  - Created by **Peter Steinberger** ([@steipete](https://github.com/steipete)), who joined **OpenAI in Feb 2026** to help build autonomous agents at scale. OpenClaw transitions to an OpenAI-backed open-source foundation.
  - **50+ parallel Codex agents for PR triage:** Peter spins up 50 Codex instances simultaneously, each outputs a JSON report (vision match, intent, risk signals). All 50 reports ingested in one session to query/deduplicate/auto-close/merge — no vector DB needed: [X post](https://x.com/steipete/status/2025591780595429385)
  - **GitHub activity at agent scale:** on **May 9, 2026**, Peter recorded **6,747 contributions**, including **1,089 commit contributions**. The approximate record is **6,700 GitHub activities**; contributions also include pull requests and other activity. Peter runs many agents across multiple projects. [Dated GitHub result and reproducible GraphQL query](Research/steipete-github-activity-2026-05-09.json) | [GitHub profile and contribution calendar](https://github.com/steipete) | [Earlier workflow post](https://x.com/steipete/status/2024524946114814414)
  - Peter's articles on his workflow:
    - My [NotebookLM knowledge base](https://notebooklm.google.com/notebook/3e4c8c3c-d617-4060-998c-c684d124d762) with his articles and videos about how he works
    - [Essential Reading Aug 2025](https://steipete.me/posts/2025/essential-reading-august-2025)
    - [Optimal AI Dev Workflow (Aug 2025)](https://steipete.me/posts/2025/optimal-ai-development-workflow)
    - [Live Coding Session (Sep 2025)](https://steipete.me/posts/2025/live-coding-session-building-arena)
    - [Just Talk To It (Oct 2025)](https://steipete.me/posts/just-talk-to-it) — shorter prompts work when models are smarter + voice input; good AGENTS.md handles all context
    - [Shipping at Inference Speed (Dec 2025)](https://steipete.me/posts/2025/shipping-at-inference-speed) — multi-project parallel workflow; no worktrees, no RAG, commit straight to main
  - 🦞 **YCombinator** (world's top startup accelerator) leadership dressed as "Claws" (red lobsters), talking OpenClaw and the AI Agent Economy: [YouTube](https://www.youtube.com/watch?v=Q8wVMdwhlh4) — signals this is a social phenomenon, not just a dev tool. First time thousands of *non-technical* people started using autonomous agents.
  - My 10-day experience report with exact token/cost/productivity numbers + notes on Opus 4.6 and GLM-4.7 (now GLM-5): [10 dni z OpenClaw](https://edukey.ai/pl/blog/10-dni-z-openclaw-i-claude-opus-46-ai-rozwija-sie-szybciej-niz-twoj-zespol)

- **AI token budget: Jensen Huang (NVIDIA CEO), All-In Podcast, 19 March 2026.** For a software engineer or AI researcher earning **$500,000/year**, Huang expects **at least $250,000/year in tokens**, an additional company-funded AI budget equivalent to half the salary. This is an expectation/thought experiment, not verified actual expenditure or an ROI result. NVIDIA benefits commercially from AI infrastructure demand; this signals big-tech ambitions rather than a ready-made budget for a Polish company.
  - Huang compares working without AI to a chip designer declining CAD tools:

    > I'm just going to use paper and pencil, I don't think I'm going to need any CAD tools.

  - Primary publisher's [video clip and transcript](https://www.linkedin.com/videos/allinpod_jensen-huang-if-that-500000-engineer-activity-7440742599600230400-drTE); [full All-In interview](https://www.youtube.com/watch?v=gwW8GKwHB3I).

### AI real impact we already see in Dev/IT:
- TailwindCSS financial issues
  - people stopped visiting Docs = less sales of their products = how to maintain OSS Projects???
  - [The Tailwind drama - YouTube](https://www.youtube.com/watch?v=luhgjBrRulk)
  - PR comment: [feat: add llms.txt endpoint for LLM-optimized documentation by quantizor · Pull Request #2388 · tailwindlabs/tailwindcss.com · GitHub](https://github.com/tailwindlabs/tailwindcss.com/pull/2388#issuecomment-3717222957)
  - Adam Wathan on X: [morning walk talk](https://x.com/adamwathan/status/2008909129591443925)
- StackOverflow is dying [Prepare your goodbyes - YouTube - Primagen](https://www.youtube.com/watch?v=Gy0fp4Pab0g)
- All Publishers see huge decline in Traffic because of AI search tools - "The Great Decoupling" (people search more, but traffic goes down - 60% of Google searches without clicks!)
- Long Video Courses are dying - people stop to use Udemy and similar platforms
  - [Why I stopped making coding tutorials - YouTube](https://www.youtube.com/watch?v=WCGTQBCE3FA)

### People and accounts to follow in AI

#### 📺 YouTube

- [Theo T3](https://www.youtube.com/@t3dotgg) — from TS, Web App and startup perspective
- [Nate B Jones](https://www.youtube.com/@NateBJones) — Deep thoughts on AI architecture, insights, deep dives
- [Silicon Valley Girl](https://www.youtube.com/@SiliconValleyGirl) — from startup and woman perspective, interviews
- [Alex Ziskind](https://www.youtube.com/@AZisk) — from Hardware perspective, testing GPUs, Local AI Models, Benchmarks
- [AI Code King](https://www.youtube.com/@AICodeKing) — Open Source, Coding Tools, alternative perspective
- [Matthew Berman](https://www.youtube.com/@matthew_berman) — from business and investor perspective, general AI news
- [Matt Pocock](https://www.youtube.com/@mattpocockuk) — AI Coding tools tips, skills, techniques
- [Rob Walling](https://www.youtube.com/@RobWalling) — AI in Startups, SaaS, Solo Devs, Bootstrap
- [YCombinator](https://www.youtube.com/@ycombinator) — AI from Startups and Investors perspective
- [Claude](https://www.youtube.com/@claude) — official
- [OpenAI](https://www.youtube.com/@OpenAI) — official
- [Fireship](https://www.youtube.com/@Fireship) — general AI news
- [Wes Roth](https://www.youtube.com/@WesRoth) — general AI news
- [Maximilian Schwarzmüller](https://www.youtube.com/@maximilian-schwarzmueller) — from TS, Web Dev perspective
- [Traversy Media](https://www.youtube.com/@TraversyMedia) — Web Dev perspective, provocative and honest
- [Greg Isenberg](https://www.youtube.com/@GregIsenberg) — General AI news and tips

#### 🐦 X.com

- [Andrej Karpathy](https://x.com/karpathy) — ex-OpenAI, Data Science
- [Paul Rohan](https://x.com/rohanpaul_ai) — Data science, AI deep dive, news
- [Tibo](https://x.com/thsottiaux) — OpenAI, Codex team; announces Codex rate-limit resets a few hours ahead ("Saint Tibo the token giver")
- [Petter Steinberger](https://x.com/steipete) — OpenClaw founder
- [Pliny Deliberator](https://x.com/elder_plinius) — Jail Breaking in AI
- [Boris Cherny](https://x.com/bcherny) — Claude Code creator, Anthropic
- [Matt Pocock](https://x.com/mattpocockuk) — AI tips in programming
- [Pieter Levels](https://x.com/levelsio) — famous Solo Dev, Startup founder, AI & bootstrap
- [Wes Bos](https://x.com/wesbos) — Syntax, AI in Web Dev

#### 🇵🇱 Po polsku

- [Mateusz Chrobok](https://www.youtube.com/@MateuszChrobok) — często o AI i bezpieczeństwie, w ciekawy sposób
- [This is IT](https://www.youtube.com/@MK_ThisIsIT) — wywiady, często o AI
  - [Polacy w OpenAI z jednego liceum — Wychował geniuszy ChatGPT](https://www.youtube.com/watch?v=w20lk3OyLMI&t=2s)
  - [Andrzej Dragan vs Krzysztof Zaręba (OpenAI)](https://www.youtube.com/watch?v=Y4SjbbZ5qoA)
  - [Krzysztof Zaręba z OpenAI (wywiad)](https://www.youtube.com/watch?v=6QhGUQ5iTdk)
- [Ania Kubów](https://www.youtube.com/@aniakubow) — po angielsku, ale Polka z Google, Amazon i Microsoft — często wrzuca coś o AI
- [Przeprogramowani](https://www.youtube.com/@Przeprogramowani) — rzadko wrzucają (i nie zawsze się z nimi zgadzam), ale są newsy AI
- [Michał Sadowski (Brand24)](https://www.youtube.com/@Michal.Sadowski) — biznes, SaaS, AI, startupy, rzadko wrzuca | [X.com](https://x.com/sadek)
- [Tomasz Karwatka](https://x.com/tomik99) — często o AI i biznesie, eCommerce (X.com)
- [Maciej Dobrodziej](https://www.linkedin.com/in/maciejdobrodziej/) — AI w Wideo (bardzo dobre jakościowo) (LinkedIn)
  - [Smok Wawelski](https://www.linkedin.com/feed/update/urn:li:activity:7337045944347037696)
  - [Bitwa pod Grunwaldem](https://www.linkedin.com/feed/update/urn:li:activity:7335560375406329856)

---

## AI Fundamentals

- **Knowledge Cutoff** - AI doesn't know latest versions & features of Tools/Languages
  - Better use **Java 21 (2023)** than 25 (07.2025)
  - Add context, docs for latest features
  - Overfitting - LLM may still struggle, ignore context and follow old path
- **Hallucinations**
  - RAG / Context / Browser helps to solve this issue, but not 100%
  - [AA-Omniscience Index](https://artificialanalysis.ai/evaluations/omniscience) (Benchmark for Hallucination level)
  - [LogProbs parameter](https://developers.openai.com/cookbook/examples/using_logprobs/) (log probabilities of each output token)
- **Context Window**
  - Temporary "working memory" of LLM,
  - Attention (uwaga, skupienie),
  - Context Rot,
  - Lost in the Middle
- **Tokens**, Tokenizer, Embedding (osadzanie), Vector DB, etc.
  - Tokens are numeric IDs for pieces of text/data; an embedding lookup maps them to learned vectors. An ID is not itself a vector.
  - Approximate word averages (tokenizer-dependent): **Polish around 2.4 tokens/word, English around 1.3; comparable Polish prose can use 60-80% more tokens**. Use English when practical to conserve context and token budget; Polish prompts can also lead to Polish reasoning traces. Quality effects depend on model/task, not a universal rule. [OpenAI Tokenizer](https://platform.openai.com/tokenizer) | [Do Multilingual LLMs Think In English?](https://arxiv.org/abs/2502.15603)
  - **Session context view (2026-10-06):** Claude Code and Copilot CLI show a detailed breakdown with `/context`. Codex CLI `/status` shows remaining context capacity and session/token usage; `/usage` provides account-wide analytics. Codex has no equivalent per-component session breakdown. **ChatGPT Desktop app, Codex mode** (Codex merged into the ChatGPT app): **Settings > General > Composer > Show context window usage**; availability has been unstable; the post-merge report includes an October 2026 reproduction even with the setting enabled. This indicator describes the current Codex session. [OpenAI merger announcement](https://openai.com/index/chatgpt-for-your-most-ambitious-work/) | [Indicator regression report, October 1 reproduction](https://github.com/openai/codex/issues/32104#issuecomment-5935357072). [Copilot context management](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management) | [Codex commands](https://learn.chatgpt.com/docs/developer-commands?surface=cli)

- **Autoregression**
  - model predicts future values in a sequence by using a linear combination of its own past values
  - one mistake may lead to cascade / domino effect of mistakes (better to start again - branching in ChatGPT, Cursor can also revert with back icon next to our prompts in history)
- What LLM needs to support to use it as **AI Agent**:
  - **Structured Output** / Json schema:
    - [OpenAI Structured Outputs Guide (JavaScript)](https://developers.openai.com/api/docs/guides/structured-outputs/?lang=javascript)
    - [OpenAI Java SDK Examples (structured output at the end of the list)](https://github.com/openai/openai-java/tree/332e1a18b4a11469e528f0359c997ae2beecd04a/openai-java-example/src/main/java/com/openai/example)
    - [Spring AI – OpenAI Structured Outputs](https://docs.spring.io/spring-ai/reference/api/chat/openai-chat.html#_structured_outputs)
  - **Function Calling** / Tool usage
- **RAG** - architecture / concept of augmenting context / input with real data
  - Retrieval-Augmented Generation (creator regrets this name ;)
  - Semantic search in vector space, Vector DB, Graph DB, Hybrid
  - Reranking
    - [Vercel AI SDK – Reranking](https://ai-sdk.dev/docs/ai-sdk-core/reranking)
  - Local Vector DBs:
    - [SQLite Vector Extension](https://www.sqlite.ai/sqlite-vector)
    - [Chroma – Open-source Embedding Database](https://github.com/chroma-core/chroma)
- **Cache** - cost optimization, caching calculated weights for same input tokens
- **Reasoning**, Reinforced Learning & R1:
  - [How was DeepSeek-R1 built; For dummies : r/LLMDevs](https://www.reddit.com/r/LLMDevs/comments/1ibhpqw/how_was_deepseekr1_built_for_dummies/)
  - It changed a lot in AI, enabled Vibe Coding, Autonomus Agents
  - Should we always use reasoning models??? :)
- **System 1 models (Jev)** - new model class between big LLMs and classic ML classifiers: fast, cheap, calibrated typed judgments (routing, triage, classification) instead of a full LLM call; TypeSafe launched Jev 15.09.2026 - details, trade-offs, JevBench: [system-1-models-jev.md](Research/system-1-models-jev.md)
- **Types of AI Assistance** in programming (quick history):
  - **autocomplete** (starting from [Tabnine](https://www.tabnine.com/), GH Copilot, now Cursor Tab [based on Supermaven](https://supermaven.com/blog/cursor-announcement))
  - Chat / Research / Talk about your code
  - Inline Generation
  - Code Generation, planning, TODOs, Tools, MCPs, etc.
  - **Agentic workflows**, local task automation, loops, goals (not only codding):
    - Local Agents for Business:
      - Claude Cowork: [Introducing Cowork | Claude](https://claude.com/blog/cowork-research-preview)
      - Codex for Everyday work mode:
        - Settings > General > Work Mode > For coding | For everyday work
        - Removes Git, code diff and features dedicated for developers
        - [Codex for Work](https://chatgpt.com/codex/for-work/)
        - [Codex Academy: How to Use Codex for Everyday Work](https://openai.com/academy/how-to-use-codex-for-everyday-work/)
    - Batching / Scripting - run dozens to hundreds of sub-agents in parallel:
      - Claude Workflow scripts: [Dynamic Workflows](https://code.claude.com/docs/en/workflows)
      - Codex CSV file batching: [Codex CSV Batch with Subagents](https://developers.openai.com/codex/subagents#process-csv-batches-with-subagents-experimental)
        - **UPDATE**: spawn CSV agents was REMOVED in July 2026 and replaced by Multi Agent v2 Mode - here is why: [ChatGPT Research on CSV Agent Spawning](https://chatgpt.com/s/t_6abe712058a48191835314697f61d570)
    - Hooks - trigger actions in deterministic way on events:
      - [Claude - Hooks](https://code.claude.com/docs/en/hooks-guide)
      - [Codex - Hooks](https://developers.openai.com/codex/hooks)
    - Goals / Loops:
      - [Claude - Goals](https://code.claude.com/docs/en/goal)
      - [Codex - Goals](https://developers.openai.com/codex/use-cases/follow-goals)
    - Schedules / Cron jobs:
      - [Claude - Scheduled Tasks](https://code.claude.com/docs/en/scheduled-tasks)
      - [Codex - Automations](https://developers.openai.com/codex/app/automations)
    - [Goose Recipes](https://goose-docs.ai/docs/guides/recipes/)
  - **Cloud Automation**, CI/CD, delegation from mobile:
    - Remote Environments
    - [Routines](https://code.claude.com/docs/en/routines)
    - Remote control of local agent
      - [Claude Dispatch](https://claude.com/blog/dispatch-and-computer-use)
      - [Claude Remote](https://code.claude.com/docs/en/remote-control)
      - [Codex Mobile](https://chatgpt.com/codex/mobile/)
- **Prompting**
  - Polish language in prompting: [AI mówi po polsku – nasz język zdeklasował angielski w najnowszym rankingu (cryps.pl)](https://cryps.pl/sztuczna-inteligencja-mowi-po-polsku-nasz-jezyk-zdeklasowal-angielski-w-najnowszym-rankingu/)
  - Context vs Prompt Engineering: [Effective Context Engineering for AI Agents – Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  - [Prompting Techniques](https://www.promptingguide.ai/techniques) data base
  - My slides from other course: [Promting - Generative AI szkolenie – DevPowers (slajd 8)](https://devpowers.com/szkolenia/generative-ai-08-12-2025/#slide-8)
  - Testowanie promptów: [Promptfoo – Open-source Prompt Testing](https://www.promptfoo.dev/)
  - Smart Prompt generator: [Prompt Cowboy – AI Prompt Generator](https://www.promptcowboy.ai/)

## LLM benchmarks, best models

- LMArena (agent vs agent fights based on [Elo rating system](https://en.wikipedia.org/wiki/Elo_rating_system)):
  - [Agent Leaderboard](https://arena.ai/leaderboard/agent)
  - [WebDev Leaderboard](https://arena.ai/leaderboard/code/webdev)
  - [Search Leaderboard](https://arena.ai/leaderboard/search)
- Design Arena Elo (agent vs agent fights in UI, Game Dev, etc.): [Design Arena](https://www.designarena.ai/leaderboard)
- Software Engineering Benchmarks:
  - **DeepSWE Bench** (Datacurve, v1 2026-05-26, v1.1 2026-06-14, leaderboard refreshed 2026-09-22): [DeepSWE Bench](https://deepswe.datacurve.ai/), [intro post](https://deepswe.datacurve.ai/blog/deepswe), [v1.1 changes](https://deepswe.datacurve.ai/blog/deepswe-v1-1)
    - contamination-free long-horizon tasks, all models in one harness (mini-swe-agent); top v1.1: gpt-6-astra, gemini-3.8-flash, claude-opus-5 at 74% - details: [benchmarks-deepswe-harness-vs-model.md](Research/benchmarks-deepswe-harness-vs-model.md#deepswe-bench)
  - SWE Bench: [SWE-bench Leaderboards](https://www.swebench.com/)
- **Harness vs model - you buy a harness + model, not just a model** (same model scores differently in different harnesses):
  - e.g. one harness config change moved SWE-bench Verified from 28% to 49% with unchanged weights; Terminal-Bench ranks model + agent pairs - evidence and papers: [benchmarks-deepswe-harness-vs-model.md](Research/benchmarks-deepswe-harness-vs-model.md#harness-vs-model)
- Terminal Bench: [Terminal-Bench](https://www.tbench.ai/leaderboard/terminal-bench/2.0)
- Tool Calling: [Berkeley Function Calling Leaderboard (BFCL) V4](https://gorilla.cs.berkeley.edu/leaderboard.html)
- AIME (High School Math Exam): [AIME 2025 Benchmark Leaderboard | Artificial Analysis](https://artificialanalysis.ai/evaluations/aime-2025)
- Market Share - Open Router: [LLM Rankings | OpenRouter](https://openrouter.ai/rankings)
- Cost vs Intelligence Index [Artificial Analysis](https://artificialanalysis.ai/evaluations/artificial-analysis-intelligence-index?eval-cost=intelligence-vs-total-cost#eval-cost-tabs)
- **Price of intelligence over time (research 14.10.2026):** the cheapest model at a fixed quality level gets 9x-900x cheaper per year (median 50x, Epoch AI; GPT-3.5 level fell from $20 to $0.07 per 1M tokens in 23 months), but flagship prices stay high (GPT-6 Astra $10 / $50) and agents use far more tokens per task. Data and sources: [price-of-intelligence-2026-10-14.md](Research/price-of-intelligence-2026-10-14.md) Related per-task chart: [Artificial Analysis Trends](https://artificialanalysis.ai/trends#efficiency).

---

## Best AI Codding Tools
- Gartner: [Best AI Code Assistants Reviews 2026 | Gartner Peer Insights](https://www.gartner.com/reviews/market/ai-code-assistants)
- YT comparison: [Best AI Coding Tools for Developers in 2026 - YouTube](https://www.youtube.com/watch?v=pvMGRSZJ4Jw&t=330s)
- **IDE & plugins:**
  - Zed [Zed — Love your editor again](https://zed.dev/) (Open Source)
    - [Should You Use Zed In 2026? - YouTube](https://www.youtube.com/watch?v=lRrElGM23h4)
    - Windows users: [Zed in WSL](https://zed.dev/docs/remote-development#wsl-support)
    - Native Windows alternative: keep source on a trusted [Windows Dev Drive](https://learn.microsoft.com/en-us/windows/dev-drive/) for filesystem performance. Prefer WSL with Linux-side storage for Linux toolchains and the Linux sandbox; do not assume one runtime is universally faster. [Requirements and Codex doctor finding](Research/codex-cli-desktop-projects-wsl-2026-10-14.md#native-windows-performance-alternative-dev-drive).
    - Offline / air-gapped env: [Agents/LLMs](https://zed.dev/docs/ai/use-a-local-model), [Zeta](https://zed.dev/docs/ai/edit-prediction#local-and-self-hosted-models) (edit prediction), [LSP](https://zed.dev/docs/configuring-languages#possible-configuration-options) (language servers from PATH)
  - Cursor [Cursor](https://cursor.com/)
  - GitHub Copilot: [GitHub Copilot · Plans & pricing · GitHub](https://github.com/features/copilot/plans)
    - Not only GPT, Claude Opus in all plans: [Claude Opus 4.5 is now generally available in GitHub Copilot - GitHub Changelog](https://github.blog/changelog/2025-12-18-claude-opus-4-5-is-now-generally-available-in-github-copilot/)
    - VS Code harnesses: **Local** (Extension Host, default chat) vs **Agent Host** (separate process running Copilot SDK, Claude and Codex harnesses; needed for Assisted permissions, shared sessions, remote hosts). Connected to WSL/SSH, the agent runs inside that environment: [Agent Host](https://code.visualstudio.com/docs/agents/concepts/agent-host), [Agent harnesses](https://code.visualstudio.com/docs/agents/run/agent-harnesses)
    - For a Windows-native Agent Host, a trusted Dev Drive is the storage alternative to WSL; it improves the Windows filesystem path, while WSL provides a Linux runtime. [Dev Drive details](Research/codex-cli-desktop-projects-wsl-2026-10-14.md#native-windows-performance-alternative-dev-drive).
    - Session history synced to your GitHub account: enable from the Copilot status bar icon (bottom right) > `Session Sync: Enable`: [Session history](https://code.visualstudio.com/docs/agents/run/sessions/session-history)
    - Answers to participants' Copilot questions (rewind, permissions, Autopilot, skills in JetBrains, nested AGENTS.md, hooks, CI/CD): [Copilot Q&A page](https://devpowers.com/szkolenia/COURSE-SITE/pytania.html)
  - [Google Antigravity IDE](https://antigravity.google/product/antigravity-ide)
  - [Junie | IntelliJ IDEA Documentation](https://www.jetbrains.com/help/idea/junie.html)
  - [Cline - AI Coding, Open Source and Uncompromised](https://cline.bot/)
  - [Augment Code - The Software Agent Company](https://www.augmentcode.com/)
  - [Kilo - Move at Kilo Speed](https://kilo.ai/)
  - [Tabnine AI Code Assistant | Smarter AI Coding Agents. Total Enterprise Control.](https://www.tabnine.com/)
  - ~~Continue~~ (acquired by Cursor): https://www.continue.dev/
  - ~~Windsurf / Codeium~~ (founders joined Google, team joined Cognition, it's Devin Desktop now): https://devin.ai/desktop/ (VSCode Clone)
  - ... list can go on...
- **Desktop apps:**
  - [Claude Desktop](https://code.claude.com/docs/en/desktop-quickstart)
    - [Linux - Claude Desktop Debian](https://github.com/aaddrick/claude-desktop-debian) (unofficial re-packaged Electron app - works well)
  - [Codex App](https://developers.openai.com/codex/app)
    - Linux [Codex Desktop Linux](https://github.com/ilysenko/codex-desktop-linux), [Codex App Linux](https://github.com/better-slop/codex-app-linux) (both unofficial, re-packaged from source = build is required)
  - [Google Antigravity 2.0](https://antigravity.google/product/antigravity-2)
  - [OpenCode](https://opencode.ai/download) (Open Source)
    - WebUI mode in the browser - [supports Offline / air-gapped env](https://github.com/anomalyco/opencode/issues/18492#issuecomment-4135581838) 
  - [Goose](https://block.github.io/goose/) (Open Source)
- **CLI tools:**
  - Knowledge Base with comparisons: [NotebookLM](https://notebooklm.google.com/notebook/44128edb-6841-4315-909c-4402b2d13bd1)
  - [Claude Code - AI coding agent for terminal & IDE | Claude](https://claude.com/product/claude-code)
  - [Codex CLI](https://developers.openai.com/codex/cli/)
  - ~~Gemini CLI~~ (open source, killed by Google... replaced by closed source Antigravity CLI): [Google Gemini CLI](https://geminicli.com/)
  - [Google Antigravity CLI](https://antigravity.google/product/antigravity-cli) (rewritten in Go, based on Crush and Bubblewrap)
  - [Crush](https://github.com/charmbracelet/crush) (Open Source, works on FreeBSD!)
  - [Goose](https://block.github.io/goose/) (Open Source)
  - [OpenCode](https://opencode.ai/) (Open Source)
  - [Aider](https://aider.chat/) (Open Source, pair programming)
  - [GitHub Copilot CLI](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/agents/about-copilot-cli)
  - [Droid by Factory](https://factory.ai/)
  - Letta Code (MemGPT): [Quickstart | Letta Docs](https://docs.letta.com/letta-code/quickstart) (Open Source)
  - AIChat for Terminal commands help: [GitHub - aichat - Shell Assistant, Chat-REPL, RAG, AI Agent](https://github.com/sigoden/aichat) (Open Source)
  - ... many more....

### Codex - official plugin from OpenAI for VSCode "family":
- [https://developers.openai.com/codex/ide/](https://developers.openai.com/codex/ide/)
- VSCode / Cursor / Antigravity / Windsurf: [https://open-vsx.org/extension/openai/chatgpt#review-details](https://open-vsx.org/extension/openai/chatgpt#review-details)

### Claude Code extension for VSCode "family":
[https://open-vsx.org/extension/Anthropic/claude-code#review-details](https://open-vsx.org/extension/Anthropic/claude-code#review-details)

### Copilot in VS Code - Autopilot, Assisted Permissions, Subagents (group questions, verified 2026-10-01)

- **Autopilot / Allow all**: `chat.tools.global.autoApprove` (renamed in v1.104 from `chat.tools.autoApprove`, no migration); Autopilot (Preview) auto-approves tools and keeps working until done - skips confirmation for destructive actions and consumes AI credits
- **Assisted permissions** (experimental, `chat.assistedPermissions.enabled`): an LLM judge rates the risk of each tool call, Agent Host sessions only; in Copilot CLI: `/permissions assisted`
- **Copilot CLI subagents**: `/tasks` (tree of subagents, teleport into one), `/subagents` (model per agent), `/fleet` (parallel execution)
- **Can everything from the course run in VS Code?** Almost: Claude Code in VS Code is the same CLI; Copilot has agent modes + `runSubagent`; headless CI, worktree fleets with a multiplexer and Beads stay in the terminal
- All setting IDs, limits and the full answers (partly in Polish): [copilot-vscode-autopilot-permissions-subagents.md](Research/copilot-vscode-autopilot-permissions-subagents.md)

---

## Pricing - rate limits

[NotebookLM](https://notebooklm.google.com/notebook/8a4739c4-f9b3-41a2-aaf0-612daa0750ce) on pricing of main AI Coding tools
[NotebookLM](https://notebooklm.google.com/notebook/ddbe409f-832b-4d19-ac7d-aed2e059d2c2) on pricing & quality of OpenSource Models (GLM/ M2) vs big providers

- **Google Gemini AI Pro** plan with CLI / Code Assist / Antigravity:
  - on Pro: 120 requests/m, 1500 r/day - [Quotas and limits  |  Gemini Code Assist ](https://developers.google.com/gemini-code-assist/resources/quotas)
  - Antigravity on Pro "high generous quota refreshed every 5h": [Google Antigravity Quota](https://antigravity.google/docs/plans)
- **JetBrains** AI Assistant has only 10 credits for $10 = around 100 requests/month
  - [Licensing and subscriptions | AI Assistant Documentation](https://www.jetbrains.com/help/ai-assistant/licensing-and-subscriptions.html#individual-use)
- **Claude Code Pro** ($17-20/m) & Max ($100 5x, $200 20x Pro) plans:
  - [Pricing | Claude](https://claude.com/pricing)
- **GitHub Copilot** 
  - Free: 50 premium requests/m + 2000 completions (NO: CLI, PRs, issue assign,  code reviews)
  - Pro for $10/m - unlimited GPT-5.4 mini, 300 premium requests (also Opus 4.5+)
  - Pro+ for $39/m - 1500 premium requests
  - [GitHub Copilot · Plans & pricing · GitHub](https://github.com/features/copilot/plans)
  - [Plans for GitHub Copilot - GitHub Docs](https://docs.github.com/en/copilot/get-started/plans) (detailed docs)
- **Cursor Pro** for $20/m provides best autocomplete
  - [Pricing · Cursor](https://cursor.com/pricing)
- **ChatGPT Plus** for $20/m
  - provides access to **Codex** (both CLI and Cloud agents with GitHub integration)
- **GLM Codding Plan**
  - GLM-5.3 (and the faster GLM-5.3-Flash) is probably the best open source Coding LLM (some argue that M2.7 is better/faster)
  - Lite plan may be slow but costs only $3/m and offers 3x usage of Claude Code Pro!
  - Pro plan is for $12 for the first year, $30/m later (5x Lite plan = 15x Claude Code Pro)
    Video on GLM-5 and Minimax M2.7: [So close to Opus at 1/10th the price (GLM-4.7 and Minimax M2.1 showdown) - YouTube](https://www.youtube.com/watch?v=kEPLuEjVr_4)
  - Invite link with additional 10%: https://z.ai/subscribe?ic=IA5VBRGQV4
  - ⚠️ **UPDATE 01.10.2026**: z.ai restructured pricing around GLM-5.3 - docs now say "starting at 18 USD/mo" with a credits system (Lite 2,000/5h + 10,000 weekly, Pro 12,000/60,000, Max 28,000/140,000 credits), older GLM-5.2/5.1 auto-routed to GLM-5.3, off-peak = 50% credits: [z.ai devpack docs](https://docs.z.ai/devpack/overview). Re-check before quoting the $3/$12 prices above
- **MiniMax** - M2.1/M2.5 API $0.30/$1.20 per M tokens; Token Plan Plus $20/m, Max $50/m, Ultra $120/m; [M Plan](https://www.minimax.io/m-plan) annual from $220/yr with MiniMax Code agent included. Cheapest per-token coding workhorse, fast (M2.7): [YT showdown](https://www.youtube.com/watch?v=kEPLuEjVr_4) (verified 01.10.2026)
- **Kimi (Moonshot)** - K3 flagship (~$3/$15 per M via gateways), K2.7 Code better value for long coding sessions; Kimi Code membership tiers (Allegretto $39/m); K3 subscriptions sold out at one point due to demand - [pricing guide](https://felloai.com/kimi-pricing), [docs](https://www.kimi.com/code/docs/en). Top-tier agentic coder, watch availability (verified 01.10.2026)
- **DeepSeek** - official API pricing (01.10.2026): `deepseek-v4-pro` (1M ctx) $0.66-1.32 input / $1.98-3.96 output per M; `deepseek-flash` (V4.1-Flash, 1M ctx) $0.15-0.30 input / $0.60-1.20 output; off-peak half price - [pricing](https://api-docs.deepseek.com/quick_start/pricing). Cheapest flagship-tier API with 1M context; no flat-rate subscription, so no Claude Code-style plan - pay per token
- **Tetrate.ai** $15 for free (OpenRouter for Enterprise):
  - 1. Create account for $5 free: [Tetrate: Safe, Fast, and Profitable AI for the Enterprise](https://tetrate.io/)
  - 2. Use goose CLI to add Tetrate Agent Router for $10 more: [Quickstart | goose](https://block.github.io/goose/docs/quickstart/)

### TOKEN OPTIMIZATION - limits, resets, cheaper models (verified 01.10.2026)

- **Claude Pro/Max**: rolling 5-hour window + weekly limit at the same time; the 5h window starts on your first prompt, so the **6am trick** (scheduled throwaway prompt) works; check `/usage`
- **Banked resets are granted, not bought** (model releases, incidents; redeem within about a month): Codex, and Claude since the Opus 5.5 release (end of 09.2026); paid options = Claude usage credits, Codex paid instant reset
- **Strategy**: burn the weekly allowance to zero first, then apply the reset (effectively 2x for that week)
- **Cheaper models as workers**: GPT-6 Luna, local LFM2.5 / Gemma 4 / Qwen 3.6, Chinese APIs (MiniMax, Kimi, DeepSeek, MiMo)
- **Skills that cut tokens:** [ponytail](https://github.com/dietrichgebert/ponytail) (write as little code as possible) and [caveman](https://github.com/JuliusBrussee/caveman) ([SKILL.md](https://github.com/JuliusBrussee/caveman/blob/main/skills/caveman/SKILL.md), terse agent output)
- **Prompt caching** (cached input is much cheaper; keep stable instructions and context at the start of the prompt): [OpenAI](https://developers.openai.com/api/docs/guides/prompt-caching), [Anthropic](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)
- Full numbers (Codex 5h ranges per model), auto-continue, how to save the allowance, sources: [token-optimization-limits-resets.md](Research/token-optimization-limits-resets.md)
- **Subscription allowances vs credits and API prices (research snapshot 12.10.2026):** [Quantified comparison and measurement methods](Research/chatgpt-subscription-vs-enterprise-credits-2026-10-12.md). Independent Codex estimates put a heavily utilized $20 Plus subscription at roughly $200-300/month of API-list-equivalent usage, or **10-15x the subscription fee**. The $25 Business Standard comparison is an **8-12x Plus-derived proxy**; weekly equivalence is unconfirmed. Ratios depend on workload, caching and usable quota, and describe API list value, not the provider's actual inference cost.
- **Codex usage analytics (verified 14.10.2026, CLI 0.162.1):** `/status` for the current session; `/usage` -> **View analytics** for account activity, with tabs depending on account type (`/usage daily`, `/usage weekly`); historical 5h and weekly allowance periods where applicable in the **Plan** tab after enabling *Analytics plan history* in `/experimental` (`codex features enable analytics_plan_history`), consumer accounts (Plus, Pro) only. Details per tab and per account type: [codex-analytics-and-usage-history-2026-10-14.md](Research/codex-analytics-and-usage-history-2026-10-14.md)

## My Recommendations - tools to install/use:

- **Handy STT** (like SuperWhisper but Open Source MIT)
  - [Handy](https://handy.computer/)
  - architecture details (Tauri): [Code Wiki](https://codewiki.google/github.com/cjpais/handy)
  - **AI post-processing** (clean-up, PL->EN translation with an LLM after transcription; v0.9.8): **Advanced -> Experimental Features** on, then **Experimental -> Post Processing** on, then configure provider, model and prompt on the new **Post Process** page (optional separate hotkey). Steps and ready prompts: [Handy.computer - transcription prompts](Prompt%20examples/Handy.computer%20-%20transcription%20prompts.md)
- Claude Code - for multi-step tasks, leading in innovation, and access to best models on discounted prices (especially on Max plan)
  - Desktop & Mobile apps with Code Agent in the cloud! [Claude Desktop App](https://code.claude.com/docs/en/desktop)
  - ⚠️ **Anthropic API / Claude Code availability** — in the last months, uptime has sometimes dropped below 99% for 90 day window. When you see below API errors, check [status.claude.com](https://status.claude.com/):
    - `● API Error: 529 Overloaded` — server-side overload, usually temporary — try again in a moment
    - `● API Error: 500 Internal server error` — server-side issue, usually temporary — try again in a moment
    - If either persists, check https://status.claude.com
- Codex - for very high limits, best models for hard work (not as good as Opus in architecture, but great for development and more focused), good cloud agents with GitHub integration.
  - Outages and errors: check [status.openai.com](https://status.openai.com/) (and [status.claude.com](https://status.claude.com/) for Claude) before debugging your setup.
- Zed.ai - to use any AI tool/Provider you wont, Open Source, Rust (fast)
- Cursor - for best autocomplete and cloud agents, RAG on any docs
- GitHub Copilot - for integration with JetBrains IDEs, access to many models, good Cloud Agent (GH native), best Code Reviews online, and good price.
- Google AI Pro - not best for programming, but best value for money overall: Gemini App, Gmail, Docs + Gemini CLI + Antigravity + Code Assist + Veo + ...
  - NotebookLM for learning / knowledge base: [NotebookLM](https://notebooklm.google.com/)
- **Terminal / TUI helpers** for agent work in the terminal: [lazygit](https://github.com/jesseduffield/lazygit) + [delta](https://github.com/dandavison/delta) (review agent diffs and commits), [atuin](https://atuin.sh/) (searchable shell history), [eza](https://github.com/eza-community/eza) + [Nerd Fonts](https://www.nerdfonts.com/) (readable listings), [Fresh](https://getfresh.dev/) (terminal IDE), [micro](https://micro-editor.github.io/) set as `$EDITOR` (agents and Git open a simple editor instead of vim)
- [OpenRouter](https://openrouter.ai/) for control, observability and 1 API Key for all tools
- [Goose](https://block.github.io/goose/) Agent for programming, PC control & automation workflows
  - Advent of AI: [Advent of AI](https://adventofai.dev/) (by Goose)
  - based on: [Advent of Code 2025](https://adventofcode.com/)

---

## AI Agents Tool-belt:

### Rules

- custom prompts/instructions per folder / type of file (with regex):
  - Cursor, GitHub Copilot & Claude Code has path based targeting e.g. `"src/api/**/*.ts"`
  - in Cluade Code: [Path Specific Rules](https://code.claude.com/docs/en/memory#path-specific-rules)
  - in Cursor: [Rules | Cursor Docs](https://cursor.com/docs/context/rules)
  - in OpenCode: [Rules | OpenCode](https://opencode.ai/docs/rules/)
  - in Codex CLI: [Rules](https://developers.openai.com/codex/rules)
  - examples:
    - [payload/templates/website/.cursor/rules at main · payloadcms/payload · GitHub](https://github.com/payloadcms/payload/tree/main/templates/website/.cursor/rules)

### Config files & Permissions (Claude Code, Codex, Copilot - verified 2026-10-01)

- **Claude Code**: `permissions` block in `settings.json` with `allow` / `ask` / `deny`, evaluated deny > ask > allow (an allow can't punch a hole in a deny); files: managed > `--settings` > `.claude/settings.local.json` > `.claude/settings.json` > `~/.claude/settings.json`
- **Codex**: `default_permissions` selects a named filesystem/network profile in `config.toml`, with `approval_policy` + `approvals_reviewer` controlling approval; legacy setups use `sandbox_mode`. Allow/prompt/forbid specific commands with Starlark **rules** in `~/.codex/rules/` or `<repo>/.codex/rules/` (most restrictive wins)
- **Copilot CLI**: saved approvals in `~/.copilot/permissions-config.json` (allow only); deny with `--deny-tool` flags (deny always wins) and `deniedUrls`
- **Course push policy**: feature-branch pushes and PRs are permitted, subject to each tool's approval settings; deny `main`/`master`/`prod` and covered force-push forms with Claude `Bash(git push * main)`/`Bash(git push *:main)` globs, OpenCode `permission.bash` deny globs, Copilot `shell(git push origin main:*)` prefixes and Codex `prefix_rule` argv prefixes (with option variants); bare `git push` can escape these branch rules, and token prefixes miss `HEAD:main` refspecs, so GitHub/Bitbucket branch protection is the real guard.
- Full syntax, examples and sources: [config-files-and-permissions.md](Research/config-files-and-permissions.md)
- Example files in this repo:
  - Claude Code: [project `.claude/settings.json`](../.claude/settings.json) (allow/deny + pom.xml security hook), [`agent-configs/claude/settings.json`](agent-configs/claude/settings.json), commented version with the reasoning behind each rule: [`agent-configs/claude/settings.jsonc`](agent-configs/claude/settings.jsonc)
  - Codex: [project `.codex/config.toml`](../.codex/config.toml) (`approval_policy`, `sandbox_mode`, network), Java/Spring variant: [`agent-configs/codex/config.toml`](agent-configs/codex/config.toml)
  - Copilot CLI: `--allow-tool` / `--deny-tool` flags in [`agent-configs/copilot/start-copilot.sh`](agent-configs/copilot/start-copilot.sh) and [`start-copilot.ps1`](agent-configs/copilot/start-copilot.ps1)
  - Hooks that block secrets in all three tools: [`hooks-example/`](hooks-example/)

### AGENTS.md

Custom project file (or many nested files) with instructions and description of application or it's parts:
  - Growing standard: [AGENTS.md](https://agents.md/)
  - CLAUDE.md [CLAUDE.MD files: Customizing Claude Code for your codebase | Claude](https://claude.com/blog/using-claude-md-files)
  - GEMINI.md [Provide context with GEMINI.md files | Gemini CLI](https://geminicli.com/docs/cli/gemini-md/)
  - **Claude Code reads AGENTS.md natively (v2.1.277+, 2026)**: [How Claude remembers your project](https://code.claude.com/docs/en/memory)
    - **Precedence when both exist**: CLAUDE.md (also `.claude/CLAUDE.md`, `CLAUDE.local.md`) in the working dir or any parent **wins by default**; AGENTS.md is read only when none of those exist
    - Change in `/config` -> **Project instructions**: `claude-md-or-agents-md` (default) | `claude-md-and-agents-md` (both, CLAUDE.md first) | `claude-md` | `managed-only` (org instructions only)
    - Portable trick: one-line `CLAUDE.md` containing `@AGENTS.md` imports it for Claude AND other tools read the AGENTS.md directly
    - Verify what was loaded: `/memory` (AGENTS.md appears in the list); `/context` shows its token cost
    - Files over 200 lines "consume more context and may reduce adherence"; hard cap 4 MiB; use `.claude/rules/` path-scoped rules instead of one giant file
  - Discussions / Sources:
    - X.com thread: [Matt Pocock](https://x.com/mattpocockuk/status/2012906065856270504)
    - Article & Prompt to fix AGENTS.md: [A Complete Guide To AGENTS.md](https://www.aihero.dev/a-complete-guide-to-agents-md)
  - Examples:
    - [mcp-for-beginners/AGENTS.md at main · microsoft/mcp-for-beginners · GitHub](https://github.com/microsoft/mcp-for-beginners/blob/main/AGENTS.md) (includes Java Spring Boot)
    - [payload/templates/website/AGENTS.md at main · payloadcms/payload · GitHub](https://github.com/payloadcms/payload/blob/main/templates/website/AGENTS.md)

### Claude Code: enterprise (managed) settings vs your config

- Org-wide `managed-settings.json` (highest precedence, users can't override) can enforce permission rules, models, hooks, MCP servers and block bypass mode
- Your CLAUDE.md/AGENTS.md can't be blocked by default; only an explicit org setting (`instructionFiles: "managed-only"`) leaves them out
- Paths per OS, full key list, how to check what applied: [config-files-and-permissions.md](Research/config-files-and-permissions.md#claude-code-enterprise-managed-settings-vs-your-config)

### SKILLS.md

- What are Skills:
  - [GitHub - agentskills/agentskills: Specification and documentation for Agent Skills](https://github.com/agentskills/agentskills)
  - [Overview - Agent Skills](https://agentskills.io/home)
- **skills.sh** - Library of Skills & "skill manager" tool from Vercel: [The Agent Skills Directory](https://skills.sh/)
  - Check a skill before installing it: the skills.sh security scanners and [ESET AI Skills Checker](https://www.eset.com/us/home/ai-skills-checker/)
  - **Does skills.sh install plugins? NO (verified 01.10.2026)** - the `skills` CLI ([vercel-labs/skills](https://github.com/vercel-labs/skills)) installs **skills only** (SKILL.md instruction files): `add`, `use`, `list`, `find`, `remove`, `update`, `init`; ~80 agents supported. Partial plugin compatibility: if a repo has `.claude-plugin/marketplace.json` or `.claude-plugin/plugin.json`, the **skills declared in those manifests** are discovered and installable - but the plugin itself (commands, agents, hooks, MCP config) is not. Full plugin install stays with the agents' own mechanisms (e.g. Claude Code `claude plugin`, Codex `codex plugin marketplace add`)
- **NEW TREND: Skills over MCP** - an MCP server serves skills and the agent loads them on demand, so they are always up to date (no `skills update` in every repo). Official MCP extension `io.modelcontextprotocol/skills`, [SEP-2640](https://modelcontextprotocol.io/seps/2640-skills-extension) final since 13 Sep 2026; client support is still rolling out: [Skills over MCP Working Group](https://modelcontextprotocol.io/community/working-groups/skills-over-mcp), [spec & implementations](https://github.com/modelcontextprotocol/ext-skills)
- Our public skills (PRD, ADR, design system, code review responses): [EdukeyTeam/agent-toolbox](https://github.com/EdukeyTeam/agent-toolbox) - install with `npx skills add EdukeyTeam/agent-toolbox --skill write-prd`
- Skills in popular tools (docs):
  - in Copilot: [About Agent Skills - GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
  - in Claude Code: [Agent Skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
  - in Gemini CLI: [Agent Skills | Gemini CLI](https://geminicli.com/docs/cli/skills/)
  - in Cursor: [Agent Skills | Cursor Docs](https://cursor.com/docs/context/skills)
  - in OpenCode: [Agent Skills | OpenCode](https://opencode.ai/docs/skills/)
  - in Codex CLI: [Agent Skills](https://developers.openai.com/codex/skills)
- **Most Popular Skills & skill libraries**
  - Engineering Skills from [Matt Pocock](https://github.com/mattpocock/skills/tree/main) (e.g. Grill Me, PRD, TDD, Triage)
  - Superpowers by [Obra](https://github.com/obra/superpowers) (e.g. TDD, Writing Plans, Executing Plans, Code Review, Debugging)
  - Microsoft [Azure Skills](https://github.com/microsoft/azure-skills)
  - [Anthropic](https://github.com/anthropics/skills) (not only for Claude, e.g. PDF, **MS Office** skills for Excel, Word, PowerPoint)
  - Reduce context window and token usage with [Caveman](https://github.com/JuliusBrussee/caveman/tree/main/skills/caveman)
  - Marketing Skills by [Corey Haines](https://github.com/coreyhaines31/marketingskills)
  - Extract [Design System](https://github.com/arvindrk/extract-design-system)
  - [Awesome Copilot](https://github.com/github/awesome-copilot) (library from GitHub with various skills, e.g. [SQL Optimization](https://www.skills.sh/github/awesome-copilot/sql-optimization), but also with Sub-Agents)
  - Vercel's [Next.js](https://github.com/vercel-labs/next-skills)
  - SQL / DB [Database Skills](https://github.com/planetscale/database-skills) | [DB Skills](https://db-skills.com/) from Planetscale
  - Convex (AI first Reactivity platform for rapid Web development) [Convex](https://github.com/get-convex/agent-skills)
  - Supabase & [PostgreSQL](https://github.com/supabase/agent-skills)
- **Skills for Java**
  - [java-testing – pluginagentmarketplace/custom-plugin-java](https://skills.sh/pluginagentmarketplace/custom-plugin-java/java-testing)
  - [java-spring-boot – pluginagentmarketplace/custom-plugin-java](https://skills.sh/pluginagentmarketplace/custom-plugin-java/java-spring-boot)
  - [java-maven – pluginagentmarketplace/custom-plugin-java](https://skills.sh/pluginagentmarketplace/custom-plugin-java/java-maven)
  - [java-architect – jeffallan/claude-skills](https://skills.sh/jeffallan/claude-skills/java-architect)
  - [java-coding-standards – affaan-m/everything-claude-code](https://skills.sh/affaan-m/everything-claude-code/java-coding-standards)
  - [android-java – alinaqi/claude-bootstrap](https://skills.sh/alinaqi/claude-bootstrap/android-java)
  - [custom-plugin-java/skills – full skills collection on GitHub](https://github.com/pluginagentmarketplace/custom-plugin-java/tree/main/skills)
  - [agent-browser SKILL.md – vercel-labs/agent-browser (example skill structure)](https://github.com/vercel-labs/agent-browser/blob/2fe7394dbeb89efb00e56899dd71f32db5ec1dee/skills/agent-browser/SKILL.md)
  - [spring-ai - Spring AI framework skill](https://skills.sh/teachingai/full-stack-skills/spring-ai)
  - [spring-ai-mcp-server-patterns - Spring AI MCP server patterns](https://skills.sh/giuseppe-trisciuoglio/developer-kit/spring-ai-mcp-server-patterns)
  - [langchain4j-spring-boot-integration - LangChain for Java with Spring Boot integration](https://skills.sh/giuseppe-trisciuoglio/developer-kit/langchain4j-spring-boot-integration)

### Custom Slash Commands / Prompts

**Claude Code custom slash commands** are reusable Markdown prompts invoked with `/command-name`. Codex's legacy **Custom Prompts** use `~/.codex/prompts/` and `/prompts:name`; they are deprecated in favor of skills invoked with `$name`. The inspected Codex main also has `/presets` for numbered saved inputs, not a `.codex/commands/` directory. Release availability and migration: [Codex commands vs Claude](Research/codex-custom-commands-vs-claude-2026-10-16.md).

- **What they are:** Markdown files stored in `.claude/commands/` (Claude Code CLI, Claude Code Desktop app, or Agent SDK). Each file becomes a `/`-command. You can optionally pass `$ARGUMENTS` to inject a custom message at invocation time.
- **When to use Commands vs Skills:**
  - Use **Custom Commands** for *simpler, reusable prompts* you want to trigger *explicitly* (e.g. a commit-message generator, a code-review checklist, a fixed prompt template). Lower overhead, no triggering heuristics.
  - Use **Skills** when the agent should *auto-detect* context and pull instructions in (via the `description` field), when you need to split knowledge/instructions in multiple files, or when you want bundled assets or scripts.
- **Grouping (optional):** Placing commands in a subfolder creates a `group:name` namespace. E.g. `.claude/commands/git/commit.md` is invoked as `/git:commit`.
- Docs in Claude Agent SDK (same mechanism for Claude Code CLI & Desktop app): [Creating custom slash commands](https://code.claude.com/docs/en/agent-sdk/slash-commands#creating-custom-slash-commands)
- Docs in Codex (DEPRECATED, use skills instead): [Custom Prompts](https://developers.openai.com/codex/custom-prompts)
- Example commands in this repo: [`/.claude/commands/`](../.claude/commands/) — grouped under [`git/`](../.claude/commands/git):
  - [`git/commit.md`](../.claude/commands/git/commit.md) → invoked as `/git:commit`
  - [`git/diff.md`](../.claude/commands/git/diff.md) → invoked as `/git:diff`

### Hooks

Scripts the agent harness runs on lifecycle events (session start, before/after a tool call, prompt submit, stop). A `PreToolUse` hook gets the planned tool call as JSON and can **deny** it (exit code `2`), rewrite its arguments or log it. Narrow a hook with a `matcher` (tool name regex), in Claude Code also with `if` (permission-rule syntax, e.g. `Bash(git commit *)`), or inside the script (check the file path / command).

- Copilot (CLI, cloud agent, VS Code preview): `.github/hooks/*.json` - [Hooks](https://docs.github.com/en/copilot/concepts/agents/hooks), [reference](https://docs.github.com/en/copilot/reference/hooks-reference), [VS Code hooks](https://code.visualstudio.com/docs/copilot/customization/hooks)
- Claude Code: `.claude/settings.json` - [Hooks guide](https://code.claude.com/docs/en/hooks-guide)
- Codex: `.codex/hooks.json` (trust once with `/hooks`) - [Hooks](https://developers.openai.com/codex/hooks)
- Examples in this repo: [secret-file blocking](hooks-example/README.md#sprawdź-czy-działa) for all three tools, plus [optional Codex and Claude Code guards](hooks-example/README.md#cztery-przykłady-dla-codexa-i-claude-code) for shell commands, written content, an opt-in Java check and session context. Merge only the chosen entries; direct script tests do not establish agent installation or enforcement.

### Statusline (Claude Code)

- Custom status line under the prompt: `statusLine` in settings.json runs your script after each turn with session JSON on stdin, no API tokens: [Statusline docs](https://code.claude.com/docs/en/statusline)
- Easiest: type `/statusline show model name and context percentage` and Claude Code writes the script for you
- Full example in this repo (git branch, context bar, cost, Pro/Max 5h + weekly usage): [`agent-configs/claude/statusline.sh`](agent-configs/claude/statusline.sh), wired in [`agent-configs/claude/settings.json`](agent-configs/claude/settings.json)
- Minimal manual setup and stdin JSON fields: [config-files-and-permissions.md](Research/config-files-and-permissions.md#statusline-claude-code)

### Tools

- built-in Agent tools (provided by IDE / CLI you use):
  - Terminal
  - Browse / Search
  - Docs (RAG) lub Contex7 MCP jeśli nie ma docs wbudowanych
  - Codebase index / semantic search (RAG over your repo): Cursor and Copilot (`#codebase`; remote index for GitHub/Azure DevOps repos, local index elsewhere, off by default for org accounts): [Copilot semantic search](https://code.visualstudio.com/docs/agents/reference/workspace-context#_semantic-search). Less critical than a year ago: agents find code well with plain grep/ripgrep
  - Code-graph MCP servers vs repo maps (research 14.10.2026): Aider repo map and Repomix give static snapshots; [codebase-memory-mcp](https://github.com/DeusData/codebase-memory-mcp) (MIT, local, tree-sitter + LSP incl. Java) and [Graphify](https://github.com/Graphify-Labs/graphify) (Apache-2.0) give queryable graphs for callers, impact and dead code. Start with `rg` + AGENTS.md, add a graph only when multi-file dependencies are the bottleneck; GitNexus is non-commercial. [code-graph-tools-vs-repo-maps-2026-10-14.md](Research/code-graph-tools-vs-repo-maps-2026-10-14.md)
  - GIT
  - TODO list
  - Browser integration (e.g. in Cursor) / Chrome-devtools-mcp
  - + Custom Tools
- **LSP** (Language Server Protocol)
  - allows agent to use diagnostic tools and understand syntax, linting errors

### Code Mode and algorithmic transformations (research 13.10.2026)

- **Code Mode / programmatic tool calling:** the agent writes a program that composes tool calls, filters intermediate results and returns compact evidence. OpenCode v2 defaults MCP tools to Code Mode; Codex availability depends on the harness, model metadata and configuration. [Research: mechanisms, defaults and measured results](Research/code-mode-and-algorithmic-code-migration-2026-10-13.md).
- **Algorithmic refactoring is a separate mechanism:** use a tested AST/type-aware recipe for repeatable edits; use the LLM for interpretation and difficult cases. Code Mode can orchestrate that recipe and its validation. The research compares OpenRewrite, C2Rust, Airbnb, Google and RustMap, with a qualified Microsoft example.
- **Benefits are workload-dependent:** fewer model round trips and less intermediate context can save tokens and time. Preserve failure evidence and compare behavioral correctness; a generated program can still encode a wrong condition or unsafe sequence. [Case studies and limitations](Research/code-mode-and-algorithmic-code-migration-2026-10-13.md#7-migration-cases-production-evidence-and-research-ambitions).

### MCP - Tools & Servers

- MCP (Model Context Protocol)
  - open standard for anybody to build tools for agents
  - best suited for accessing external services (as MCP Servers, or **Connectors**)
  - but there are also local MCP tools available (e.g. Playwright)
  - Anthropic's Skill to build own MCP Tools: [MCP Builder](https://www.skills.sh/anthropics/skills/mcp-builder)
- Problems:
  - Context bloating = Context rot,
    - partially fixed by [Tool Discovery](https://modelcontextprotocol.info/docs/concepts/tools/#tool-discovery-and-updates) = 1 tool to rule them all
  - Too many choices for agent (max 5x MCP servers / 50 tools in total used at once!)
  - Slower than just Bash scripts, terminal commands (Agent also can use them!)
  - Sometimes CLI tool is better (with optional skill how to use it), e.g.
    - [Sentry CLI](https://cli.sentry.dev/)
    - [GitHub CLI](https://docs.github.com/en/github-cli/github-cli/quickstart)
    - [Playwright CLI](https://github.com/microsoft/playwright-cli) + [Skill](https://www.skills.sh/microsoft/playwright-cli/playwright-cli)
- History of the Standard
  - Introduced by Anthropic in 2024: [Introducing the Model Context Protocol \\ Anthropic](https://www.anthropic.com/news/model-context-protocol)
  - Donated to Linux Foundation subsidiary: [Donating the MCP and the Agentic AI Foundation](https://www.anthropic.com/news/donating-the-model-context-protocol-and-establishing-of-the-agentic-ai-foundation)
  - Open Standard: [What is the Model Context Protocol (MCP)? - Model Context Protocol](https://modelcontextprotocol.io/docs/getting-started/intro)
  - Why MCP moved from SSE to Streamable HTTP: [SSE vs. Streamable HTTP - which will be the standard for remote servers? : r/mcp](https://www.reddit.com/r/mcp/comments/1kdyse2/sse_vs_streamable_http_which_will_be_the_standard/)
- **NEW TREND: WebMCP** - a web page declares its own tools for agents (annotated HTML forms or `navigator.modelContext.registerTool()` in JS). Instead of slow, token-hungry DOM traversal and clicking, the agent does complex actions with a few tool calls. Chrome 149 origin trial, locally via `chrome://flags/#enable-webmcp-testing`: [WebMCP in Chrome](https://developer.chrome.com/docs/ai/webmcp)
  - Example: [Stack Underflow](https://devpost.com/software/stack-underflow-your-ai-agent-plays-in-the-office) (my OpenAI WebMCP Challenge game, the browser agent plays as an office coworker) - [play it](https://play.devpowers.com)
- **Installation** instructions for Agents:
  - in Claude Code: [Connect Claude Code to tools via MCP - Claude Code Docs](https://code.claude.com/docs/en/mcp)
  - in Zed: [Redirecting... | Zed Code Editor Documentation](https://zed.dev/docs/assistant/model-context-protocol)
  - in Cursor: [Model Context Protocol (MCP) | Cursor Docs](https://cursor.com/docs/context/mcp)
  - in OpenCode: [MCP servers | OpenCode](https://opencode.ai/docs/mcp-servers/)
- **Most Popular MCPs**:
  - Context7 - documentation: [Context7 - Up-to-date documentation for AI](https://context7.com/)
    - deep dive: [Research/context7-research.md](Research/context7-research.md) - how it works, setup commands (Claude Code, Codex, Copilot CLI, Cursor), ctx7 CLI, pricing and limits
    - quick setup in Claude Code: `claude mcp add --scope user --transport http context7 https://mcp.context7.com/mcp`
    - or one command for any tool: `npx ctx7 setup`
  - Chrome DevTools: [GitHub - Chrome DevTools for coding agents](https://github.com/ChromeDevTools/chrome-devtools-mcp)
  - Playwright: [Microsoft Playwright MCP](https://github.com/microsoft/playwright-mcp)
    - Claude: `claude mcp add playwright npx @playwright/mcp@latest`
    - Codex: `codex mcp add playwright npx "@playwright/mcp@latest"`
  - Browser Use: [MCP Server - Browser Use](https://docs.browser-use.com/customize/integrations/mcp-server)
  - IntelliJ IDEA: [MCP Server | IntelliJ IDEA Documentation](https://www.jetbrains.com/help/idea/mcp-server.html)
  - GitHub: [MCP GitHub · GitHub](https://github.com/mcp/io.github.github/github-mcp-server)
  - Jenkins: [MCP server for Jenkins build tasks](https://github.com/jasonkylelol/jenkins-mcp-server)
  - Linear, GitLab, Atlassian, Azure DevOps
  - Notion, PostHog, Postman, Sentry, ...
  - PostgreSQL, MongoDB, ...
  - Figma
  - Blender
- **Example Java MCP Servers:**
  - Create own MCP server in Java: [modelcontextprotocol/java-sdk – The official Java SDK for MCP servers and clients, maintained with Spring AI](https://github.com/modelcontextprotocol/java-sdk)
  - [tangcent/maven-indexer-mcp](https://github.com/tangcent/maven-indexer-mcp)
  - [OpenLinkSoftware/mcp-jdbc-server – Java based MCP Server for JDBC](https://github.com/OpenLinkSoftware/mcp-jdbc-server)
  - [quarkiverse/quarkus-mcp-servers – Model Context Protocol Servers in Quarkus](https://github.com/quarkiverse/quarkus-mcp-servers)
  - [quarkiverse/quarkus-mcp-server – Extension for implementing MCP server features in Quarkus](https://github.com/quarkiverse/quarkus-mcp-server)
  - [hpalma/springinitializr-mcp – MCP server for Spring Initializr](https://github.com/hpalma/springinitializr-mcp)
  - [vishalmysore/a2ajava – Pure Java implementation of Google A2A protocol with Spring Boot; agents also exposed as MCP tools](https://github.com/vishalmysore/a2ajava)
  - [ECF/MCPToolGroups – Tool Groups Support for the Model Context Protocol](https://github.com/ECF/MCPToolGroups)
  - [arvindand/maven-tools-mcp – MCP server for Maven Central dependency intelligence for Maven, Gradle, SBT, Mill](https://github.com/arvindand/maven-tools-mcp)
  - [idachev/mcp-javadc](https://github.com/idachev/mcp-javadc)
  - [studykit/mcp-jar-indexer](https://github.com/studykit/mcp-jar-indexer)

Example MCP Config (it's standard, similar for all MCPs):

```json
{
  "mcpServers": {
    "maven-indexer": {
      "command": "npx.cmd",
      "args": [
        "-y",
        "maven-indexer-mcp@latest"
      ]
    },
    
  }
}
```

### ACP (Agent Client Protocol)

- use CLI Agents in other tools / IDEs
  - Created by Zed IDE to use Claude Code in Zed (now also for Codex, Gemini, OpenCode)
  - in ZED [Zed — Agent Client Protocol](https://zed.dev/acp)
  - in JetBrains IDEs: [Agent Client Protocol | JetBrains](https://www.jetbrains.com/help/ai-assistant/acp.html#install-agent-from-registry)
  - in OpenCode: [ACP Support | OpenCode](https://opencode.ai/docs/acp/)
  - in Goose: [Using goose in ACP Clients | goose](https://block.github.io/goose/docs/guides/acp-clients)

### Sub-Agents

Main agent can delegate tasks to sub-agents (often specialized), to focus on orchestration, minimize context window bloat and work in parallel (often faster).

- In most popular tools:
  - Claude Code: [Create custom subagents - Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
    - [Agent Teams (experimental feature) vs Sub-Agents](https://code.claude.com/docs/en/agent-teams)
    - [Blog: Subagents in Claude Code](https://claude.com/blog/subagents-in-claude-code)
  - Codex CLI [Multi-agents](https://developers.openai.com/codex/multi-agent/) - the user-facing command is **`/subagents`** (see the supervision layers below)
  - Google Antigravity [Subagents](https://antigravity.google/docs/subagents)
  - Cursor: [Subagents | Cursor Docs](https://cursor.com/docs/context/subagents)
  - Copilot: [About custom agents - GitHub Docs](https://docs.github.com/en/copilot/concepts/agents/coding-agent/about-custom-agents)
  - OpenCode: [Agents | OpenCode](https://opencode.ai/docs/agents/)
  - Goose: [Subagents | goose](https://block.github.io/goose/docs/guides/subagents/)
- Nested Sub-Agents (sub-agents spawned by sub-agents):
  - [Claude Code - Nested Sub-Agents](https://code.claude.com/docs/en/sub-agents#spawn-nested-subagents) (max depth is 5, not configurable)
  - [Codex Subagent settings](https://developers.openai.com/codex/subagents#global-settings) - `agent.max_threads` is now a **legacy alias** of `agents.max_concurrent_threads_per_session` (default **4** as of CLI 0.159.3, was 6) & `agent.max_depth` (default: 1 - only main agent can spawn sub-agents, set to 2+ to allow nested sub-agents)
- **Codex CLI: two layers of multi-agent supervision** (verified 2026-10-01, CLI 0.159.3):
  - **Agent Command Center** (shipped 0.149.0, 2026-08-20): open with **`codex agents`** from the shell or **`/agents`** in a session - a dashboard over **top-level sessions/tasks**: search, start, open, rename, stop, filter, archive/delete, plus **Git worktree** management: [release notes](https://github.com/openai/codex/releases/tag/rust-v0.149.0), [docs](https://learn.chatgpt.com/docs/agent-configuration/subagents)
    - same release added **`codex queue`** - send a message to an existing local or remote Codex session (even when it is not in the foreground)
  - **`/subagents`** - the Subagents picker **inside the current session**: switch between and inspect the agent threads the current root agent spawned (internally named `MultiAgents` in source - the old docs name "Multi-agents" maps to the user-facing command **`/subagents`**; current docs say `/agent` singular, docs slightly ahead of stable - UNCONFIRMED)
  - Mental model for teaching: **Agent Command Center manages jobs, `/subagents` inspects the workers inside a job**
- **Git Worktrees** for Parallel Agents in same repository:
  - Default: split tasks by files/folders and record dependencies in one checkout. Use a worktree only when agents must change the same files in parallel.
  - Put a no-default-worktrees rule in AGENTS.md: dependency installs consume disk and CPU, and agents often forget cleanup.
  - Only the coordinator changes Git branch/index state or commits; workers edit only their assigned files. Worktrees do not eliminate same-file merge conflicts.
  - What is a Git Worktree? [Git Worktree Docs](https://git-scm.com/docs/git-worktree)
  - Claude: [Run parallel Claude code sessions with Git worktrees | Claude Docs](https://code.claude.com/docs/en/common-workflows#run-parallel-claude-code-sessions-with-git-worktrees)
  - Codex: [Worktrees | OpenAI Codex Docs](https://developers.openai.com/codex/app/worktrees/)
  - Cursor: [Parallel Agents | Cursor Docs](https://cursor.com/docs/configuration/worktrees)
  - Avoid a full `node_modules` install per worktree: pnpm global virtual store (`virtualStoreType: global` in `pnpm-workspace.yaml`), each worktree only links into one shared store: [pnpm + git worktrees](https://pnpm.io/git-worktrees)
- Library of Sub-Agent definitions from GitHub: [Awesome Copilot Agents](https://github.com/github/awesome-copilot/tree/main/agents)

### Agent managers / multiplexers - work with many agents at once (links verified 01.10.2026)

- **[Herdr](https://herdr.dev)** - open-source terminal multiplexer for agents: vendor-neutral, tracks agent state (idle/working/blocked/done), survives lost SSH
- **[Beads](https://github.com/gastownhall/beads)** - git-backed issue tracker as shared memory for agents (Steve Yegge)
- **[Paseo](https://paseo.sh)**, **[Orca](https://www.onorca.dev)**, **[T3 Code](https://t3.codes)**, **[Conductor](https://conductor.build)**, **[Vibe Kanban](https://www.vibekanban.com)** - orchestrators / control planes for parallel agents; **[Codex App](https://developers.openai.com/codex/app)** - OpenAI's single-vendor desktop app
- **Herdr vs Codex App**: vendor-neutral runtime on your own machines vs zero-ops, OpenAI-only app with cloud tasks - they combine well
- **Native Windows storage (checked 2026-10-16):** Codex doctor recommends a trusted Windows Dev Drive for repository performance. Requirements, Defender performance mode and when to prefer WSL: [Dev Drive](Research/codex-cli-desktop-projects-wsl-2026-10-14.md#native-windows-performance-alternative-dev-drive).
- **Codex aliases and profiles (CLI 0.162.1):** copy the chosen profile files to `~/.codex/`, then use the documented [Bash shortcuts](agent-configs/.bashrc-agents) or [PowerShell equivalents](agent-configs/codex-aliases.ps1), dot-sourced from `$PROFILE`. Provider/mode names and warnings: [Codex profiles](agent-configs/README.md#codex-profiles).
- **Codex checkpoint refs (checked 2026-10-16):** `refs/codex/turn-diffs/checkpoints/` is also reported in the VS Code integration; it is not a verified CLI `/rewind` feature. Inspection, deletion risks, push behavior and comparison with Copilot/Claude: [checkpoint research](Research/codex-git-checkpoints-2026-10-16.md).
- **Remote agents**: `herdr --machine <label>` over SSH, Codex cloud tasks, `codex exec`, `codex agents` + `codex queue`
- **Codex CLI <-> Codex app, Windows <-> WSL (verified 14.10.2026):** add the exact project folder in the app (**Add new project** / `Ctrl+O`; WSL repos via `\\wsl$\`), restart the app after switching the agent between Windows and WSL, find old sessions with `codex resume --all` in the environment that created them, and use `/app` from a native Windows/macOS CLI to continue its saved chat in the app. Independently launched Windows and WSL CLIs normally keep separate state; confirm the app's effective store rather than assuming a WSL agent shares the shell's history. Never manually share one `.codex` across runtimes. Checklist: [codex-cli-desktop-projects-wsl-2026-10-14.md](Research/codex-cli-desktop-projects-wsl-2026-10-14.md)
- Details, comparison and remote setup: [agent-managers-and-remote-agents.md](Research/agent-managers-and-remote-agents.md)

### Claude Code Plugins vs MCP/Skills

- https://code.claude.com/docs/en/plugins
- https://github.com/luongnv89/claude-howto/blob/main/claude_concepts_guide.md#plugins
- **Sharing skills across many projects:** keep one source repository with `skills/` and MCP config and distribute it as a plugin: Codex `codex plugin marketplace add org/repo` + `codex plugin add plugin@marketplace`, Copilot CLI `copilot plugin install org/repo`, Claude Code `claude plugin marketplace add org/repo`. Plugins do not deploy project rules or settings: AGENTS.md, `.codex/config.toml` and rules stay in each project. Pin a tag or commit. Worked example with all three: [Edukey Agent Toolbox](https://github.com/EdukeyTeam/agent-toolbox)

## Security

- **Codex on Windows:** [sandbox setup, permissions and troubleshooting](Research/codex-windows-sandbox-troubleshooting-2026-10-15.md).
- Validate skills, MCPs and any scripts before installing and using them.
  - Skill scanners: skills.sh security checks and [ESET AI Skills Checker](https://www.eset.com/us/home/ai-skills-checker/)
- **What can go wrong:** the agent incident at Hugging Face - [OpenAI's statement and next steps](https://openai.com/pl-PL/index/hugging-face-incident-and-the-road-ahead/) and the Netflix documentary [Instadocs: AI Gone Wild](https://www.netflix.com/tudum/articles/instadocs-ai-gone-wild-release-date-news)
- Check the license for skills, hooks and agents you copy from internet (e.g. Anthropic skills are not permissive) - license can be found on GitHub repo or inside skill folder.
- YOLO MODE requires good sandboxing or phisical 2nd device without sensitive credentials.
- https://code.claude.com/docs/en/best-practices#safe-autonomous-mode
- https://code.claude.com/docs/en/sandboxing

### Evals, Tests & Observability

- [PromptFoo](https://www.promptfoo.dev/) (open source) -prompt x model testing framework
- [LangFuse](https://langfuse.com/) (open source) - advanced OSS framework and application for tracing, evals, prompt management, metrics and debugging of LLL-based app! 
- OpenAI Evals:
  - https://developers.openai.com/api/docs/guides/evals/
  - https://developers.openai.com/api/docs/guides/evaluation-getting-started
- Google Vertex: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/models/evaluation-overview
- Microsoft Foundry Evals: https://learn.microsoft.com/en-us/azure/ai-foundry/how-to/evaluate-generative-ai-app?view=foundry-classic


## Best Practices / Methodologies for Agentic Codding:

- Plan & Solve
- Plan-Execute-Test-Commit loop
- Good AGENTS.md and rules for better understanding of the project
- Make AI Agent ask you questions instead of acting immediately (Custom agent or in AGENTS.md)
  - With better initial prompt and info Agent will not interrupt you so often and work longer
  - **Codex: interactive questions OUTSIDE plan mode** (verified 2026-10-01, CLI 0.159.3):
    - The interactive questions UI (clickable options) is **plan mode only**: [Plan mode](https://developers.openai.com/codex/plan-mode) - toggle with `/plan` or **Shift+Tab**; "Plan mode lets Codex gather context, ask clarifying questions, and build a stronger plan"
    - Outside plan mode: **no built-in "ask user" tool** yet - open feature request: [GitHub issue #30150](https://github.com/openai/codex/issues/30150) (since 2026-06-26)
  - **Plan mode is expected to go away** in Claude Code and Codex (announced on X, October 2026: [thread by Thariq from Anthropic](https://x.com/trq212/status/2102813194196758746), agreed by the head of Codex): plan with a prompt, a PRD and a written plan instead of relying on a special mode.
    - Workaround 1 - prompting: ask Codex to **interview you** before acting (official suggestion in [Best practices](https://learn.chatgpt.com/guides/best-practices)), or add one line to AGENTS.md like "Before implementing, ask me clarifying questions until requirements are unambiguous" - questions arrive as plain text, not the structured UI: [r/codex thread](https://www.reddit.com/r/codex/comments/1vdo16g/adding_this_one_line_allows_your_codex_to_ask/)
    - Workaround 2 (official, structured): **MCP elicitation** - an MCP server can ask the user structured questions mid-tool-call (`mcpServer/elicitation/request`); enable with `approval_policy.granular.mcp_elicitations = true` in config.toml: [Config reference](https://developers.openai.com/codex/config-reference), [MCP app-server docs](https://developers.openai.com/codex/app-server)
- Product Requirement Document (PRD): 
  - [GitHub - snarktank/ai-dev-tasks: A simple task management system for managing AI dev agents](https://github.com/snarktank/ai-dev-tasks)
  - [Legal agent income up-cert PRD creation - Amp](https://ampcode.com/threads/T-019b98b9-3fe1-77ea-9d43-235c62200559)
- **Spec-Driven Development (SDD)** - specification first, then plan, then code: [GitHub Spec Kit](https://github.com/github/spec-kit), [specs.md](https://specs.md/); skills: [spec](https://www.skills.sh/?q=spec), [plan](https://www.skills.sh/?q=plan), [PRD](https://www.skills.sh/?q=prd)
- Architecture Decision Records (ADR): **give the agent links to the libraries and APIs you consider.** Without them it often misses new options and falls back to outdated patterns from training data. Adding [Chat SDK](https://chat-sdk.dev/), [OpenRouter Responses API](https://openrouter.ai/docs/api_reference/responses/overview) and [OpenRouter + Vercel AI SDK](https://openrouter.ai/docs/guides/community/vercel-ai-sdk) changed our ADR a lot: [example prompt](Prompt%20examples/ADR-generation-typescript-vercel-ai-sdk.md)
- TODO List / Task list / Progress tracking
  -  Not needed with Opus 4.5? [TODOs Are Done - Amp](https://ampcode.com/news/todos-are-done)
- **System 2 Thinking**
  - refers to a **slow, deliberate** approach to software development that prioritizes logic and architecture over intuitive, rapid generation.
  - This philosophy has emerged as a rigorous defense against "slop"—the influx of unmaintainable or hallucinated code that often results from **"System 1"** thinking (**fast, intuitive** = "vibe coding")
  - Terms borrowed from [Daniel Kohneman - Thinking, Fast and Slow](https://www.goodreads.com/en/book/show/11468377-thinking-fast-and-slow) book
- Tips for OpenCode: [Don't sign up the yearly plan, it's a trap : r/ZaiGLM](https://www.reddit.com/r/ZaiGLM/comments/1q2oqhx/comment/nxf1idh/)
  - Agent RPI-V8 [Claudette coding agent](https://gist.github.com/bizzkoot/bdf957cd745de8c788df3ca7f353daad#file-rpi-v8-opencode-agent-md)
  - Skill **Superpowers** [GitHub - obra/superpowers: An agentic skills framework & software development methodology that works.](https://github.com/obra/superpowers/tree/main)
  - MCP sequential-thinking
- Clavix - templates for better prompts. PRDs
  - [GitHub - ClavixDev/Clavix: Transform vague ideas into production-ready prompts. Analyze gaps, generate PRDs, and supercharge your AI coding workflow with the CLEAR framework.](https://github.com/ClavixDev/Clavix)

### Ralph Wiggum Bash loop:

- Knowledge Base: [NotebookLM](https://notebooklm.google.com/notebook/c92dbf13-8174-42eb-9f1d-15be3f7c842d)
- original post from Geoffrey Huntley: [Ralph Wiggum as a "software engineer"](https://ghuntley.com/ralph/)
- repo that Geoffrey supports: [GitHub - ghuntley - The Ralph Wiggum Technique—the AI development methodology that reduces software costs to less than a fast food worker's wage.](https://github.com/ghuntley/how-to-ralph-wiggum)
- Video where G.H. explains Ralph: [Ralph Wiggum (and why Claude Code's implementation isn't it) with Geoffrey Huntley and Dexter Horthy - YouTube](https://www.youtube.com/watch?v=O2bBWDoxO4s)
- Ryan Carson version: [GitHub - snarktank/ralph: Ralph is an autonomous AI agent loop that runs repeatedly until all PRD items are complete.](https://github.com/snarktank/ralph) / on [X.com](https://x.com/ryancarson/status/2008548371712135632)
  - G.H. wrote "it isn't it" on [X.com](https://x.com/GeoffreyHuntley/status/2008731415312236984)
- Ralph meme coin and technique explanation: [$RALPH - The Memecoin That's Helping AI Ship Code While You Sleep](https://ralphcoin.org/#technique)
- Ralph Wiggum from 1st principles: [The Ralph Wiggum Loop from 1st principles (by the creator of Ralph) - YouTube](https://www.youtube.com/watch?v=4Nna09dG_c0)
- Claude Code Ralph plugin (official, but not fixing context rot): [claude-code/plugins/ralph-wiggum at main · anthropics/claude-code · GitHub](https://github.com/anthropics/claude-code/tree/main/plugins/ralph-wiggum)
- Goose with Ralph loop: [Ralph Loop | goose](https://block.github.io/goose/docs/tutorials/ralph-loop)
- Detailed technical video: ["Ralph Wiggum" AI Agent will 10x Claude Code/Amp - YouTube](https://www.youtube.com/watch?v=RpvQH0r0ecM)

---

## Cloud Agents / Containerization / VM - Security

- OpenAI Codex Web
  - [Codex Web](https://chatgpt.com/codex)
  - NEW! (macOS only now) [Codex App](https://openai.com/codex/)
  - [Docs Codex Web](https://developers.openai.com/codex/cloud/)
  - Blog [Introducing Codex Web](https://openai.com/pl-PL/index/introducing-codex/)
- [Claude Code Web](https://claude.ai/code) (also in mobile app!)
- Cursor Cloud Agents [Cursor Agents](https://cursor.com/agents)
- Copilot Agents: [GitHub Copilot Agents](https://github.com/copilot/agents)
  - Docs: [About GitHub Copilot coding agent - GitHub Enterprise Cloud Docs](https://docs.github.com/en/enterprise-cloud@latest/copilot/concepts/agents/coding-agent/about-coding-agent)
  - Also in mobile GitHub app!
- Goose in Docker: [Building goose in Docker | goose](https://block.github.io/goose/docs/tutorials/goose-in-docker)

### Headless agents in CI/CD

- Code review and security review of every PR with Copilot, Claude Code, Codex or OpenCode, posted as a PR comment and to Jira; pipelines for Azure, GitLab and Bitbucket: [`cicd-headless/agent-review/`](cicd-headless/agent-review/)
- **Full research on AI-assisted PRs and code review across platforms (checked 02.10.2026):** [AI-assisted pull requests and code reviews handbook](Research/ai-assisted-pull-requests-course-handbook.md) - PR lifecycle, community PR-Agent, AI Review, Kodus, Danger JS/reviewdog, GitLab, Bitbucket Cloud/Server/DC, Azure DevOps, Jenkins, security, reruns and review-quality evaluation.
- **GitHub review with Azure OpenAI:** [participant/fork setup instructions](cicd-headless/github-actions/README.md) and [Azure workflow](cicd-headless/github-actions/pr-agent-azure-review.yml) - resource endpoint as a variable, API key as a secret, deployment/model variables, and fail-fast checks before model calls.
- **Community PR-Agent 0.47.0:** ready-made review/describe/improve workflows, with a [ready exercise and examples for GitHub, GitLab, Bitbucket, Azure DevOps, Jenkins, Bamboo, Gitea and a local run](cicd-headless/PR-Agent-Qodo/README.md); Git hosting and CI runner are separate choices. Pipeline execution publishes comments; slash commands need a comment-event listener/webhook.
- **Codex directly in Bitbucket + Jira:** [headless pipeline and custom REST adapter](cicd-headless/codex-bitbucket/README.md) - fetch PR diff and ticket details, request a schema-validated review, then update bot comments in both systems. Separate context, model and publication stages; no Qodo/PR-Agent dependency. This example targets Cloud APIs; Server/DC needs a different adapter.
- Headless commands: `copilot -p`, `claude -p`, `codex exec`, `opencode run` (also `agy -p`, `grok -p`)
  - deep dive (validated 01.10.2026): [Research/Headless agents - CLI automation, JSON streaming, subscriptions and CI-CD](Research/Headless%20agents%20-%20CLI%20automation,%20JSON%20streaming,%20subscriptions%20and%20CI-CD.md) - JSON event streams, JSON Schema output, subscription vs API billing per tool, CI/CD patterns, security rules
  - **JSON event streams** (newline-delimited): `claude -p --output-format stream-json` | `codex exec --json` | `agy -p --output-format stream-json` | `grok -p --output-format streaming-json` (different spelling!) | `copilot -p --output-format json` | `opencode run --format json`
  - **JSON Schema final output** (validated, not just "please respond with JSON"): Claude `--json-schema`, Codex `--output-schema <file>`, Antigravity `--json-schema`; Grok/Copilot CLI expose events only (validate yourself, e.g. Zod); OpenCode via SDK `json_schema`
  - **Claude `--bare`**: skips hooks, skills, MCP, plugins, CLAUDE.md discovery = deterministic CI mode (recommended by Anthropic for scripts/SDK), but does NOT use subscription OAuth - needs `ANTHROPIC_API_KEY`; also the safe choice in untrusted repos (`-p` loads project config without showing the trust dialog)
  - **Env trap**: `ANTHROPIC_API_KEY` set in the environment overrides the subscription even in `-p` mode - `unset ANTHROPIC_API_KEY` to go back to subscription billing
  - Budgets/limits: `copilot -p --max-ai-credits 50` (1 credit = $0.01, soft cap), `grok --max-turns`, plus your own orchestrator timeouts
- One `OPENROUTER_API_KEY` can drive all four (Copilot CLI BYOK via `COPILOT_PROVIDER_BASE_URL`); Copilot on its own account needs a user-owned fine-grained PAT with **Copilot Requests**: [Copilot CLI programmatically](https://docs.github.com/en/copilot/how-tos/copilot-cli/automate-copilot-cli/run-cli-programmatically), [Codex non-interactive](https://developers.openai.com/codex/noninteractive), [Claude Code headless](https://code.claude.com/docs/en/headless)
- CI image: Debian slim, not Alpine (agent CLIs expect glibc). Bitbucket app passwords stopped working in July 2026, use access/API tokens

## Other AI Tools and Ecosystem

 - **Design / UX / FE with AI:**
   - Google: [Stitch - Design with AI](https://stitch.withgoogle.com/?pli=1)
   - Figma AI plugins
     - Figma MCP: [Guide to the Figma MCP server – Figma Learn - Help Center](https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server)
   - Lovable
   - v0 from Vercel
   - GitHub Spark [GitHub Spark · Dream it. See it. Ship it. · GitHub](https://github.com/features/spark)
   - Tailwind & Shadcn popularity
 - **Code Reviews, GitHub integrations**
   - **Qodo** - [commercial AI code review platform](https://www.qodo.ai/), separate from the community open-source project. Qodo [announced the PR-Agent handover on 23 April 2026](https://www.qodo.ai/blog/qodo-is-handing-pr-agent-over-to-the-community/).
   - **Community PR-Agent** - [The-PR-Agent/pr-agent](https://github.com/The-PR-Agent/pr-agent), MIT, community-owned and maintained independently of Qodo; latest release checked 02.10.2026: [v0.47.0](https://github.com/The-PR-Agent/pr-agent/releases/tag/v0.47.0). Use [community docs](https://docs.pr-agent.ai/), rather than assuming commercial Qodo features exist in OSS.
     - Supports GitHub, GitLab, Bitbucket Cloud/Server/DC, Azure DevOps and Gitea; tool and inline-comment support vary by provider: [platform matrix](https://docs.pr-agent.ai/overview/supported_platforms/).
     - [`qodo-pr-agent-review.yml`](cicd-headless/github-actions/qodo-pr-agent-review.yml) retains its historical filename but now uses the community runtime; manual dispatch accepts a PR number and calls the CLI. [Multi-platform examples](cicd-headless/PR-Agent-Qodo/README.md).
     - For full comparison and implementation details: [AI-assisted pull requests and code reviews handbook](Research/ai-assisted-pull-requests-course-handbook.md).
   - CodeRabbit [AI Code Reviews | CodeRabbit | Try for Free](https://www.coderabbit.ai/)
     - GitLab Sef-Managed: [CodeRabbit GitLab](https://docs.coderabbit.ai/platforms/self-hosted-gitlab)
   - Gemini Code Assist: [Review GitHub code using Gemini Code Assist](https://developers.google.com/gemini-code-assist/docs/review-github-code)
     - Consumer - config files: [Customize Gemini Code Assist behavior in GitHub  |  Google for Developers](https://developers.google.com/gemini-code-assist/docs/customize-gemini-behavior-github#consumer)
     - Enterprise - Cloud Console: [Customize Gemini Code Assist behavior in GitHub  |  Google for Developers](https://developers.google.com/gemini-code-assist/docs/customize-gemini-behavior-github#enterprise)
  - Gemini CLI w CI/CD:
    - Google Course: [Sprawdzanie kodu i analiza bezpieczeństwa za pomocą interfejsu wiersza poleceń Gemini](https://codelabs.developers.google.com/gemini-cli-code-analysis?hl=pl#0)
    - GitLab MR Article: [Building an automated GitLab Merge Request Review Agent with Gemini CLI  | Medium](https://medium.com/google-cloud/building-an-automated-gitlab-merge-request-review-agent-with-gemini-cli-35855d53bec1)
  - GitHub Copilot:
    - [Configuring automatic code review by GitHub Copilot - GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/configure-automatic-review)
    - [Using GitHub Copilot code review - GitHub Docs](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review)
   - OpenAI Codex [Use Codex in GitHub](https://developers.openai.com/codex/integrations/github/)
   - Cursor Bugbot: [Bugbot | Cursor Docs](https://cursor.com/docs/bugbot)
   - Cursor CLI in GH Actions: [Code Review with Cursor CLI | Cursor Docs](https://cursor.com/docs/cli/cookbook/code-review)
 - **Debugging, Security, Docs**
   - Sentry Seer: [Seer: AI debugging agent that works for you. | Sentry](https://sentry.io/product/seer/)
   - [Jam | Build a bug-free product.](https://jam.dev/)
   - [Mend.io - AI Powered Application Security](https://www.mend.io/)
   - [Mintlify - The Intelligent Documentation Platform](https://www.mintlify.com/)
   - Snyk: [Snyk AI-powered Developer Security Platform | AI-powered AppSec Tool & Security Platform | Snyk](https://snyk.io/)
   - Snyk Evo: [Security for Agentic AI Applications and Tools | Evo by Snyk | Evo](https://evo.ai.snyk.io/)
   - Snyk vs Mend: [Mend.io vs Snyk 2026 | Gartner Peer Insights](https://www.gartner.com/reviews/market/application-security-testing/compare/mend-io-vs-snyk)
   - **Markdown** is best for AI Docs, and supports many additional features, eg.
     - Diagrams with Mermaid [Mermaid | Diagramming and charting tool](https://mermaid.js.org/)
     - Slides with [Marp: Markdown Presentation Ecosystem](https://marp.app/)
     - **Confluence** synchronization in GH Action: [confluence-markdown-sync · Actions · GitHub Marketplace · GitHub](https://github.com/marketplace/actions/confluence-markdown-sync)
       - [GitHub - andygolubev/github-to-confluence-publisher](https://github.com/andygolubev/github-to-confluence-publisher)
       - [GitHub - mihaeu/cosmere: Sync your markdown files to Confluence](https://github.com/mihaeu/cosmere)

---
 
## Frameworks & Tools to Build Agents:

- **JAVA & AI**
  - [Spring AI](https://docs.spring.io/spring-ai/reference/index.html)
  - Implementation of official [OpenAI Java SDK](https://docs.spring.io/spring-ai/reference/api/chat/openai-sdk-chat.html)
  - [OpenAI Chat](https://docs.spring.io/spring-ai/reference/api/chat/openai-chat.html)
  - Official OpenAI Java SDK:
    - [GitHub - openai/openai-java: The official Java library for the OpenAI API](https://github.com/openai/openai-java)
    - [Libraries | OpenAI API](https://platform.openai.com/docs/libraries?language=java&desktop-os=windows)
  - Microsoft [Semantic Kernel for Java](https://github.com/microsoft/semantic-kernel-java/tree/main)
- **UI Libraries**:
  - Vercel AI SDK UI [AI SDK UI: Overview](https://ai-sdk.dev/docs/ai-sdk-ui/overview)
  - assistant-ui [GitHub - assistant-ui/assistant-ui: Typescript/React Library for AI Chat💬🚀](https://github.com/assistant-ui/assistant-ui)
  - Protocol giving Agents ability to generate UI on the fly [AG-UI](https://github.com/ag-ui-protocol/ag-ui)
  - UI Components for AI tools, with full support of AG-UI [CopilotKit](https://github.com/CopilotKit/CopilotKit)
- **AI & Agentic Frameworks**:
  - Biggest Node.js framework [AI SDK by Vercel](https://ai-sdk.dev/docs/introduction)
  - Fastest growing Node.js AI Framework [Mastra AI](https://workos.com/blog/mastra-ai-quick-start)
  - Most Popular Framework (JS & Python)
    - RAG, Chat and Tools [LangChain](https://www.langchain.com/)
    - Multi-agent framework [LangGraph](https://www.langchain.com/langgraph)
  - Python Multi-agent framework [CrewAI Multi-Agent Platform](https://www.crewai.com/)
  - Microsoft's .Net & Python Framework [AutoGen](https://microsoft.github.io/autogen/stable/)
    - UI Low-Code [AutoGen Studio](https://microsoft.github.io/autogen/stable/)
  - Rust [GitHub - 0xPlaygrounds/rig: ⚙️🦀 Build modular and scalable LLM Applications in Rust](https://github.com/0xPlaygrounds/rig)
  - Tools for RAG / knowladge base [LlamaIndex](https://www.llamaindex.ai/)
  - Protocol for Agent to Agent communication [A2A Protocol](https://a2a-protocol.org/latest/)
    - Created by Google, now as open standard: [Google blog post announcing A2A](https://developers.googleblog.com/en/a2a-a-new-era-of-agent-interoperability/)
- **Platform-specific**
  - Google [Agent Development Kit](https://google.github.io/adk-docs/)
  - OpenAI
    - [Agents SDK](https://developers.openai.com/api/docs/guides/agents-sdk/)
    - [AgentKit]()
  - Microsoft
    - [Agent Framework](https://learn.microsoft.com/en-us/agent-framework/overview/?pivots=programming-language-csharp)
    - [Semantic Kernel](https://github.com/microsoft/semantic-kernel) (.Net, Python & Java)
    - [365 Agent SDK](https://github.com/microsoft/Agents/tree/main)
- **No-Code Tools**
  - Flowise, OpenSource Apache (based on LangChain and LangGraph = many agents working together) [Flowise - Build AI Agents, Visually](https://flowiseai.com/)
  - n8n for business automation & simple AI Agents [AI Workflow Automation Platform & Tools - n8n](https://n8n.io/)
  - MS 365 + Power Automate + [Microsoft Copilot Studio](https://www.microsoft.com/en-us/microsoft-365-copilot/microsoft-copilot-studio)
  - Google [Workspace Studio](https://workspace.google.com/studio/)

---

### JetBrains AI Ecostystem
 
 - Article: [Best Software Composition Analysis Tools - Qodana Blog](https://blog.jetbrains.com/qodana/2025/09/best-software-composition-analysis-tools/) 
   (Qodana, Mend, Snyk, OWASP, Black Duck, FOSSA)
 - **MCP Server:** [MCP Server | IntelliJ IDEA Documentation](https://www.jetbrains.com/help/idea/mcp-server.html)
 - **AI Assistant** - [AI Assistant in JetBrains IDEs](https://www.jetbrains.com/help/idea/ai-assistant-in-jetbrains-ides.html?utm_source=product&utm_medium=link&utm_campaign=IU&utm_content=2025.3)
   - **low quota** - only 10 credits in Pro for $10 (~10 agent requests): [Licensing and subscriptions | AI Assistant Documentation](https://www.jetbrains.com/help/ai-assistant/licensing-and-subscriptions.html#ai-quota)
   - **Junie** AI Agent (unified in Chat now): [Junie, the AI coding agent by JetBrains - IntelliJ IDEs Plugin | Marketplace](https://plugins.jetbrains.com/plugin/26104-junie-the-ai-coding-agent-by-jetbrains)
   - **Other CLI Agents** in JetBrains IDEs with ACP - [Agent Client Protocol Registry | JetBrains](https://www.jetbrains.com/help/ai-assistant/acp.html#install-agent-from-registry)
 - **GH Copilot** - higher quota, also on free tier (GPT-5 mini, Haiku 4.5)
   - [GitHub Copilot - Your AI Pair Programmer - IntelliJ IDEs Plugin | Marketplace](https://plugins.jetbrains.com/plugin/17718-github-copilot--your-ai-pair-programmer)
   - [GitHub Copilot app modernization - IntelliJ IDEs Plugin | Marketplace](https://plugins.jetbrains.com/plugin/28791-github-copilot-app-modernization) (legacy code, refactors)
 - **AI Unit Testing**: [Diffblue Cover - AI Agent for unit testing - IntelliJ IDEs Plugin | Marketplace](https://plugins.jetbrains.com/plugin/14946-diffblue-cover--ai-agent-for-unit-testing)
   - Does NOT use LLM. Own small RL model that generates tests automatically!
   - has mixed reviews, probably LLM based agent can write better tests nowadays
   - Specialized in Java, JUnit and TestNG
 - **SonarQube** static analysis (to control better AI generated code):
   - [SonarQube for IDE - IntelliJ IDEs Plugin | Marketplace](https://plugins.jetbrains.com/plugin/7973-sonarqube-for-ide)
   - [SonarQube Plans & Pricing | Static Code Analysis Tool | Sonar](https://www.sonarsource.com/plans-and-pricing/)
 - **Qodana** Static Analysis & CI/CD:
   - [Qodana: Static Code Analysis Tool by JetBrains](https://www.jetbrains.com/qodana/)


## Planning, delegation and token budget

Use the [planning prompt with a dependency matrix](Prompt%20examples/Plan-SubAgents-matrix-dependency-map.md) for one approved vertical slice. Save plans under docs/plans, link the PRD/ADR sources and prefer ad hoc workers for one-off tasks. After reviewing a plan, turn the reusable procedure into a planning skill with the group and test it on another feature. The [public planning-skill proposal](https://github.com/EdukeyTeam/agent-toolbox/pull/28) is an optional example pending review.

[Agents, permissions and token budget](Research/agent-workflows-and-token-budget-2026-10-24.md) covers /config, concise output, the statusline with jq, usage views, optional token-saving skills, headless delegation and the documented login-code fallback. Short output does not replace tests or review. [Polish dictation findings](Research/speech-to-text-models-polish-handy.md) distinguish model-card measurements from local observations and explain how to compare recordings.


## Copilot configuration and test evidence

Use [Copilot: configuration, tests and cloud task](exercises/copilot-testing-and-cloud.md) to connect repository instructions, path rules, prompt files, skills, custom agents and hooks with one observable application criterion. The test-engineer and test-evidence examples stay inactive until reviewed and deliberately enabled. Cloud assignment and model spending require the actual account/organization authorization; completing a task does not authorize merge.
