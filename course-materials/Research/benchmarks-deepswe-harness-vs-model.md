# DeepSWE Bench and harness vs model

> Moved from [Course INDEX - AI in Programming](../Course%20INDEX%20-%20AI%20in%20Programming.md) on 2026-10-02 to keep the notes short. Facts verified 2026-10-01; dates and sources are on each item.

## DeepSWE Bench

- **DeepSWE Bench** (Datacurve, v1 2026-05-26, v1.1 2026-06-14, leaderboard refreshed 2026-09-22): [DeepSWE Bench](https://deepswe.datacurve.ai/), [intro post](https://deepswe.datacurve.ai/blog/deepswe), [v1.1 changes](https://deepswe.datacurve.ai/blog/deepswe-v1-1)
  - 113 original tasks in 91 active OSS repos, 5 languages; tasks **written from scratch, never merged upstream** = contamination-free (SWE-bench tasks come from public GitHub issues models may have memorized)
  - Tasks are long-horizon: solutions ~668 lines vs ~120 in SWE-bench Pro, with half-length prompts; hand-written **verifiers test behavior** (public APIs), not implementation
  - Datacurve audit of SWE-bench Pro: **8.5% false positives, 24% false negatives**; ~13% of reviewed Claude Opus 4.6/4.7 rollouts CHEATED (read the gold fix via `git log --all`)
  - All models run in **one harness (mini-swe-agent)** to remove harness variance; scores span 5-74% vs ~30-point band on SWE-bench Pro
  - Top (v1.1, 2026-09-22): gpt-6-astra, gemini-3.8-flash, claude-opus-5 all 74%, gpt-5.6-sol 73%; Artificial Analysis swapped SWE-bench Pro for DeepSWE in [Coding Agent Index v1.5](https://artificialanalysis.ai/methodology/coding-agents-benchmarking), lifting Codex (GPT-5.5) above Claude Code

## Harness vs model

- **Harness vs model - you buy a harness + model, not just a model** (same model scores differently in different harnesses):
  - [Terminal-Bench](https://www.tbench.ai/leaderboard/terminal-bench/2.0) ranks **model + agent pairs** (separate AGENT column); Artificial Analysis also pins all models to mini-swe-agent on [Terminal-Bench 4.0](https://artificialanalysis.ai/evaluations/terminalbench-4-0)
  - DeepSWE pilot (2026-05): claude-opus-4.7 scored **50% on mini-swe-agent vs 40% on Claude Code** (same 10 SWE-bench Pro tasks): [DeepSWE intro](https://deepswe.datacurve.ai/blog/deepswe)
  - LangChain deepagents-cli (2026-02-17): same gpt-5.2-codex, harness engineering only: **52.8% -> 66.5%** on Terminal-Bench 2.0 (Top 30 -> Top 5); reasoning config alone: xhigh 53.9% vs high 63.6%: [Harness engineering](https://www.langchain.com/blog/improving-deep-agents-with-harness-engineering)
  - Paper "Same Model, Different Harness" (2026-08-26): one harness config change moved SWE-bench Verified pass from **28% to 49%** for unchanged weights: [arXiv:2608.26218](https://arxiv.org/abs/2608.26218)
  - Paper "Stop Comparing LLM Agents Without Disclosing the Harness" (2026-05-07): harness-induced variance can exceed model variance and reverse rankings; calls for harness disclosure: [arXiv:2605.23950](https://arxiv.org/abs/2605.23950)
  - Counterpoint (2026-09-08): on a private contamination-free 256-task suite the average harness effect was ~0 (Opus 4.8: 48.8% vs 50.0%), but up to 23.7 pp on task subsets and 1.2-1.6x cost per solved task: [arXiv:2609.11987](https://arxiv.org/abs/2609.11987)
