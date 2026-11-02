# Codex voice, `codex queue` and ChatGPT Enterprise chat credits

*Research date: 30 October 2026. Questions raised by participants during the course. Web research by an agent (Gemini via Antigravity), checked by the trainer against the official pages cited below and against Codex CLI 0.165-0.166 on Linux. Pricing and limits change often; check the linked Help Center pages before relying on a number.*

## Summary

- **Enterprise chat and credits:** on credit-based ChatGPT Enterprise, **Instant** chat costs 0 credits. **Thinking** costs **10 credits per message** whatever the reasoning effort (Medium, High and Extra High cost the same), **Pro** 50, image generation 5 and deep research 50, and they are taken from the shared workspace pool from the first message. On token-based Enterprise every request is billed in USD per token. Business, Plus and Pro use included per-seat allowances first.
- **What participants heard was almost right:** "simple chat is free, reasoning costs credits even in chat" matches the rate card. The free tier is Instant, not a "low" reasoning level, and a higher effort does not raise the per-message price on credit-based plans.
- **Chat and Work:** the new ChatGPT desktop app (28.10.2026) puts Chat, Work and Codex in one app, but billing stays separate: Work is metered like Codex, Chat keeps chat rates. A merge of Chat and Work limits is not rolling out; a notice suggesting it was published by mistake.
- **Voice in Codex CLI:** the old hold-Space dictation (`voice_transcription`) was removed in 0.118.0 (April 2026). In 0.165-0.166 the CLI has a **voice conversation** that you start and stop (toggle, not push-to-talk), with a separate microphone mute. Dictation into the composer is in the ChatGPT/Codex desktop app.
- **`codex queue`:** works in 0.165-0.166. A message queued with `Tab` in the TUI is lost when you quit Codex; it is not saved with the session. It adds a message to an existing session from another terminal or script; `--resume` (0.166) also wakes a session that is not loaded. In the TUI, `Tab` queues a follow-up for the next turn and `Enter` steers the running turn.

## 1. Does ordinary chat use credits on ChatGPT Enterprise?

It depends on the contract and the model, not on the Chat/Work tab alone.

| Chat mode | Credit-based Enterprise (per message) |
|---|---|
| Instant | 0 credits (unlimited, abuse guardrails) |
| Thinking, GPT-6 (Medium, High, Extra High) | 10 credits |
| Pro (GPT-6 Pro) | 50 credits |
| Image generation | 5 credits |
| Agent mode in chat | 30 credits |
| Deep research | 50 credits per task |

- The rate card FAQ states that a higher reasoning effort does not change the per-message rate: the model sets the price.
- **Credit-based Enterprise** has no per-seat allowance in front of the pool, so every Thinking, Pro, image or deep research message is paid from the workspace credits. Admins limit this with model/tool access and group spend controls.
- **Token-based Enterprise** (USD pricing) has no credit pool. Chat, Work and Codex are billed per million tokens; a higher effort produces more tokens and so costs more.
- **Business, Plus and Pro:** Instant is effectively unlimited, and Thinking/Pro/deep research first use the seat's included allowance. Business credits are optional overflow after a seat runs out.
- ChatGPT Work and Codex are not billed per message: on credit-based plans they use credits per token.

Sources: [Flexible pricing for Enterprise, Edu and Business](https://help.openai.com/en/articles/10427845-flexible-pricing-for-the-enterprise-edu-and-business-plans), [ChatGPT rate card (Business, Enterprise/Edu)](https://help.openai.com/en/articles/11481834-chatgpt-rate-card-business-enterpriseedu), earlier course research [ChatGPT subscriptions vs Enterprise credits](chatgpt-subscription-vs-enterprise-credits-2026-10-12.md).

## 2. Are Chat and Work being merged?

- **Done:** on 28.10.2026 the Codex desktop app became the new ChatGPT desktop app with Chat, Work and Codex. Chat and Work share Recents and Projects and are switched with a toggle; Codex keeps its own view. Source: [Moving to the new ChatGPT desktop app](https://help.openai.com/en/articles/20001276-moving-to-the-new-chatgpt-desktop-app).
- **Not happening yet:** a shared limit for Chat and Work. A checkout notice suggesting it appeared by mistake; the head of ChatGPT and Codex said the merge is not rolling out (tech press reports, no official Help Center page).
- **Billing today:** Work uses the same usage and billing structure as Codex; Chat keeps chat rates (section 1). On 29.10.2026 Work/Codex allowances were doubled for Pro and Business Premium.

## 3. Voice in Codex

| Where | What it does | How |
|---|---|---|
| Codex CLI 0.165-0.166 | Spoken conversation with the agent (audio in and out) | Toggle: start/stop a voice conversation, separate microphone mute. Both are key actions you can bind in `config.toml` (`tui.keymap.chat.toggle_voice`, `tui.keymap.chat.toggle_voice_mute`). Feature flag `in_app_voice` (stable, on by default). Best with ChatGPT login. |
| Codex CLI before 0.118 | Hold Space to dictate text into the prompt | Removed in 0.118.0 (April 2026). There is no built-in dictation in the CLI now. |
| ChatGPT/Codex desktop app (Windows, macOS) | Dictation into the composer and voice chat | Microphone button, shortcut and toggle or hold-to-talk in Settings → Voice. ChatGPT login. |
| Codex extension in VS Code / IntelliJ | No own voice button | Use the IDE or system dictation (Windows `Win+H`, VS Code Speech `Ctrl+Alt+V` / `Ctrl+Shift+Space` depending on version). |

Checked locally: `codex features list` on 0.166.0 shows `in_app_voice` and `in_app_dictation` as stable; the binary describes the key action as "Start or stop a voice conversation". Hold-to-talk for the CLI is an open feature request in `openai/codex`. Sources: [Codex app](https://developers.openai.com/codex/app), [Codex CLI reference](https://developers.openai.com/codex/cli/reference), [openai/codex releases](https://github.com/openai/codex/releases).

## 4. `codex queue` and follow-up messages

- **From another terminal or a script:**

  ```bash
  codex queue --thread "<session-id-or-name>" --message "Run the integration tests next"
  ```

  With `--resume` (added in 0.166.0) Codex also tries to resume a session that is not loaded. If the session was interrupted mid-turn, the message is stored but not sent until you resume the session yourself.
- **In the TUI while a turn is running:** `Tab` queues the text as the next turn, `Enter` steers the current turn at the next safe point, `Shift+Left` edits the last queued message.
- **Continue an earlier session:** `codex resume` (picker), `codex resume --last "next prompt"`, or non-interactively `codex exec resume --last "next prompt"`.

Checked locally with `codex queue --help` on 0.165.0 (`--thread`, `--message`, `--resume`, `--remote`). Source: [openai/codex releases, rust-v0.166.0](https://github.com/openai/codex/releases).

### Does a message queued with Tab survive leaving the session?

**No.** Scenario from the course: during a running turn you type a message and press `Tab`, so it is queued instead of steering; you switch to another agent view and back, then quit Codex and later `codex resume` the session. The queued message is gone.

- In the TUI source (`codex-rs/tui/src/chatwidget/user_messages.rs`, `ThreadInputState.queued_user_messages`, commit `2546265` of 30.10.2026) the queue is kept **only in the memory of the running TUI**. When you switch between agent views, the TUI saves it per thread in memory and restores it, so navigation alone does not drop it. Nothing writes it to the session file, so quitting Codex loses it and `codex resume` cannot bring it back.
- The desktop app has the same reported problem: [openai/codex#32715](https://github.com/openai/codex/issues/32715) "Codex Desktop silently loses queued follow-up messages after restart" (open).
- `codex queue --thread ... --message ...` is different: it adds the message through the app server, so it is stored with the thread and survives the TUI closing; `--resume` then wakes the thread.

How not to lose a follow-up: wait until the turn finishes before quitting, use `Enter` to steer the running turn instead of queueing, or copy the queued text before you quit. For work you hand over to a later session, use `codex queue`.
