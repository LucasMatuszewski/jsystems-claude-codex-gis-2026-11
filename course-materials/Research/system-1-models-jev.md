# System 1 models (Jev) and JevBench

> Moved from [Course INDEX - AI in Programming](../Course%20INDEX%20-%20AI%20in%20Programming.md) on 2026-10-02 to keep the notes short. Facts verified 2026-10-01; dates and sources are on each item.

- **System 1 models (Jev)** - new model class BETWEEN big LLMs and classic ML classifiers (also called "decision models", from Kahneman's System 1 vs System 2):
  - **TypeSafe** (founder Diogo Almeida, ex-OpenAI) launched **Jev** 15.09.2026, the first "System One" model
  - Problem it solves: fast, cheap, repeatable **typed judgments** (routing, triage, classification, reranking, policy checks) where a full LLM call is overkill and hand-written rules are too brittle
  - Natural language + app **state** in -> typed answers with **calibrated probabilities** out (no text generation, no parsing): **Choice** (picks an option + distribution), **Score** (ordered levels), **Noul** (yes/no probability, from "Bernoulli"); many questions evaluated in parallel against the same state
  - vs **prompting an LLM per item**: no autoregression (parallel sampler, all outputs in one query), vendor claims 70-500 ms and "two orders of magnitude faster and more efficient" (09.2026); $0.042/MTok input, output free - cheaper than GPT-5 Nano ($0.05/MTok)
  - vs **classifiers trained with Google AutoML / Vertex AI AutoML**: zero-shot, no labeled training set - you describe options and criteria in natural language; trade-offs: not trained on your data (validate on your own cases), and even more black-box than an LLM (returns only a number, no justification - bias caution: [Simon Willison, 21.09.2026](https://simonwillison.net/2026/Sep/21/jev)); with labeled outcomes the judgments can also become features for classic ML
  - Not a smaller LLM: new architecture + training with **RLCD** (Reinforcement Learning for Calibrated Decisions), no chain-of-thought
  - Known limits (TypeSafe "jaggedness" notes, Jev 1.13): struggles with numbers, dates, adversarial content
  - **JevBench** - independent community benchmark (not affiliated with TypeSafe): intelligence + calibration + speed + cost; 534 decisions per system (v1.2); v1.4.2.2 (09.2026): 95 systems measured, Jev 1.13.0 ranked 4th (63.29) behind open-weight Imajev-4B (67.37); open Jev-clones (e.g. **Kev**, Qwen 3.5 based) already emerging
  - [Announcement](https://typesafe.ai/blog/introducing-system-one-models-and-jev) | [Docs - System One](https://docs.typesafe.ai/concepts/system-one) | [Review - Simon Willison](https://simonwillison.net/2026/Sep/21/jev) | [JevBench](https://github.com/fstandhartinger/jevbench) (links verified 01.10.2026)
