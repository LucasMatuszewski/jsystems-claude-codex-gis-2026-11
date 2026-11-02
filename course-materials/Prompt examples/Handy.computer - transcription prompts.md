# Handy.computer - transcription prompts

https://handy.computer/

## Enable post-processing (Handy v0.9.8, verified in source 14.10.2026)

1. **Advanced** (PL: **Zaawansowane**) > group **App** (**Aplikacja**) > turn on **Experimental Features** (**Funkcje Eksperymentalne**).
2. A new group **Experimental** (**Eksperymentalne**) appears lower on the same page > turn on **Post Processing** (**Postprocess**).
3. A new sidebar page **Post Process** (**Postproces**) appears. Set **Provider** (OpenAI-compatible, Anthropic-compatible, a custom base URL such as a local Ollama endpoint, or Apple Intelligence on Apple Silicon with macOS 26), **API Key** and **Model**.
4. Under **Prompt**, choose **Create New Prompt**, paste one of the prompts below and keep `${output}` where the transcript should go. Select the prompt you want to use.
5. Optional: set a dedicated **Post-Processing Hotkey** on the same page, so one shortcut gives a raw transcript and the other an AI-processed one.

Post-processing sends the transcript to the selected model provider. Use a local model or an approved company provider for work content.

---

## Translate to English

```
Translate the transcript provided below from Polish to English.

Rules:
1. Translate faithfully with proper English grammar, punctuation, and natural interpretation, but keep the meaning strictly the same.
2. Preserve the exact meaning and (as much as reasonably possible) the word order. Do not paraphrase or add/remove information.
3. Keep names, brands, product names, and technical terms exactly as written (do not translate them).
4. If something is unclear in Polish, choose the most likely interpretation, but do not invent details.
5. Use safe plain punctuation for dictation: straight apostrophe ', straight quote ", hyphen -, and three dots ... . Never use curly quotes, smart apostrophes, typographic dashes, bullets, emoji, tabs, control characters, or line breaks.
6. Return one single line of text unless the transcript explicitly asks for multiple lines.
7. Return ONLY the English translation (no notes, no explanations, no extra text).

Names/terms that may appear and must be preserved exactly (or be corrected if misspelled):
ChatGPT, OpenClaw, Encore, PayloadCMS, Claude Code, Claude Cowork, Codex, Tailwind, TailwindCSS, Playwright, OpenAI, AGENTS.md, React.js, Qwen, LoRA

Polish transcript to translate:
${output}
```

---

## Improve Transcriptions

```
Clean the transcript provided below:
1. Fix spelling, capitalization, and punctuation errors
2. Convert number words to digits (twenty-five: 25, ten percent: 10%, five dollars: $5)
3. Replace spoken punctuation with symbols (period: ., comma: ,, question mark: ?)
4. Use safe plain punctuation for dictation: straight apostrophe ', straight quote ", hyphen -, and three dots ... . Never use curly quotes, smart apostrophes, typographic dashes, bullets, emoji, tabs, control characters, or line breaks
5. Return one single line of text unless the transcript explicitly asks for multiple lines
6. Remove filler words (um, uh, eee, like as filler)
7. Do NOT make translations! Keep the original language of transcription (if it was Polish, keep it in Polish!)
8. Correct obvious grammar errors, make it more clear, correct, and nice to read
9. Correct probable transcription errors based on the context of the sentence to make it more clear. If something feels odd or is not clear assume transcription error and try to correct it based on context
10. When cleaning a transcript, prioritize understanding the intended meaning based on the context of the sentence. Correct probable transcription errors, misspellings, or unclear references by using contextual knowledge. For example, if the context suggests technical terms (like IDE, themes, or specific product names), infer the most likely correct term rather than sticking to a literal transcription if it makes no sense. Use your general knowledge regarding software development tools and popular terms

Names and words that may apear in the transcript and be misspelled, so you should correct them if you see something similar:
ChatGPT, OpenClaw, Encore, Coolify, PayloadCMS, Claude Code, Claude Cowork, Codex, Tailwind, TailwindCSS, Playwright, OpenAI, AGENTS.md, React.js, Qwen, LoRA, theme (often misspeled as "team" - check the context of sentence)

Preserve exact meaning of the sentences and word order. Do not paraphrase or reorder content. But correct errors and probable mistakes in transcription.

Return only the cleaned transcript.

Transcript:
${output}
```


---

## Recommended Base STT Models (Speech-to-Text)

For detailed benchmark comparisons, Word Error Rate (WER) metrics across Polish and English datasets, and hardware considerations for Handy, see the full research report:
- **Research reference:** [`../Research/speech-to-text-models-polish-handy.md`](../Research/speech-to-text-models-polish-handy.md)

### Quick model recommendations for Handy:
- **Polish Dictation (Fast & Zero Hallucination):** `Parakeet TDT 0.6B v3` (`Q8_0`) - 7.31% FLEURS WER, non-autoregressive transducer avoids pause loops.
- **Polish Accuracy & Low WER:** `Canary 1B v2` (`Q5_K_M`) - **6.64% FLEURS WER** (beats Parakeet v3). In Handy catalog, speed score is **81** (slightly faster than Parakeet at 79). Features native Polish <-> English translation (`translate: true`) and excellent capitalization.
- **Polish Literary / Punctuation-rich:** `Whisper Large v3 Turbo` (`Q8_0`) - ~6.2% FLEURS WER with rich syntax and diacritics at 3.5x legacy Whisper speed.
- **English Dictation (Handy Recommended #1):** `Parakeet Unified EN 0.6B` (`Q8_0`) - ~1.6% clean WER, sub-200ms latency.
- **Highest Accuracy English Benchmark:** `IBM Granite Speech 4.1 2B NAR` or `Cohere Transcribe (03-2026)` (1.25% clean WER).
- **Translation Note:** Use **direct Polish transcription + the LLM post-processing prompt below**. This two-stage pipeline preserves developer jargon (Tailwind, PayloadCMS, Encore) and proper names far better than native single-step speech translation.
