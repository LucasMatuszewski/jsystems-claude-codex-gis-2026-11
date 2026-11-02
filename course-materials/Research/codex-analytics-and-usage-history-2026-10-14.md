# Codex analytics and usage history

Research date: 2026-10-14. Verified locally against `codex-cli 0.162.1`; source links are pinned to its release commit, `092d3acd6bec3e3a14bdc7e7a2810ab628ab759d`. The Windows app version `26.1007.2314.0` and bundled CLI `0.162.0-alpha.17.2` were reference versions for this research, not independently verified here. Desktop UI availability and backend deployment are not established by reading CLI source.

## First correction: open /usage, not /analytics

In 0.162.1, type `/usage`, then select **View analytics**. `/usage daily`, `/usage weekly`, and `/usage cumulative` open the Overview token-activity view directly. The slash-command registry contains `Usage` and no `Analytics` command. The experimental feature's description still mentions `/analytics`; that text is not evidence that the command exists. [Command registry][A1], [dispatch][A2], [usage menu][A3], [feature definition][A4].

The account analytics dashboard first shipped in stable **0.156.0 on 2026-09-22**. Its release notes name the `/usage` dashboard and include the Summary, top-chat, and experimental plan-history changes, including PRs #45764, #45766, #45768, #45769, and #45772. The preceding 0.155.0 and 0.155.1 tags do not contain `codex-rs/tui/src/analytics.rs`. There is no verified first release of a separate `/analytics` command. [0.156.0 release][A5].

## What the dashboard actually displays

Internal section names differ from the labels on screen: `Summary` is **Overview**, workspace `Usage` is **Tokens**, and `Activity` is **Messages**. Tasks are represented within consumer **Chats**, rather than a separate Tasks tab. There is no generic Tools tab in this version. [Tab labels][A6], [section selection][A7].

| Visible tab | Contents and origin | Availability |
| --- | --- | --- |
| Overview | Backend account profile and statistics, including lifetime tokens, peak daily tokens, longest chat, streaks, and token activity with daily, weekly, or cumulative presentation. | All resolved account families; unknown plans expose only this section. [Profile loading][A8], [summary rendering][A9], [section selection][A7]. |
| Usage | Consumer daily relative usage, with supported groupings such as model, surface, feature, and turn start. Feature/turn attribution falls back to surface when backend attribution is incomplete. | Consumer accounts. [Client routing and fallback][A10], [group names][A11]. |
| Plan | Historical five-hour and weekly allowance periods, their boundaries and used percentages, accounting completeness, and optional model, surface, thread-source, or turn-trigger breakdowns. | Consumer accounts with `analytics_plan_history` enabled and a deployed, accessible endpoint. [Plan model][A12], [plan UI][A13], [endpoint][A14]. |
| Credits | Workspace credit consumption, with account-dependent product/surface, model, speed, and sometimes reasoning breakdowns. | Workspace account families; do not confuse credits with tokens. [Client routing][A10], [group eligibility][A15]. |
| Tokens | Workspace token activity grouped by token type or model, with a model filter. | Workspace account families. [Client loading][A10], [controls][A16]. |
| Messages | Daily message activity grouped by surface or model. | Consumer layout. [Section selection][A7], [endpoint routing][A17], [group options][A18]. |
| Plugins and Skills | Backend daily plugin and skill activity with top-item breakdowns. These are not a ledger of every shell command, file read, or MCP tool call. | Consumer and workspace layouts. [Section selection][A7], [backend contracts][A17]. |
| Chats | Consumer task usage, including available weekly %, five-hour %, and balance-credit metrics; or supported workspace chat credit estimates. Discovery uses local recent root threads, while amounts come from backend usage queries. | Consumers; workspace chat estimates are restricted to specific plan identifiers listed below. [Consumer queries][A19], [task metrics][A20], [workspace queries][A21]. |

Most daily-report views switch between 7 and 30 days, using UTC dates. Plan history requests seven days of allowance snapshots; Overview uses a separate profile report. These are different reporting periods, not interchangeable measures. Daily aggregates do not provide a general hour-of-day heat map. Use Plan period boundaries, where present, and separately recorded session timestamps for timing investigations. [Report ranges][A7], [UTC request contract][A17], [plan endpoint][A14], [profile loading][A8].

## Data provenance and account access

The dashboard is not a local JSONL token scanner. `AnalyticsSession` loads the local ChatGPT sign-in, fetches the selected account's plan through `get_accounts_check()`, and checks both account and user identity before accepting data. Report requests go to the configured ChatGPT/Codex backend, under `wham/...` or `api/codex/...`. An API-key-only login cannot satisfy this analytics authentication path. [Authentication and plan discovery][A22], [report endpoints][A17].

| Account type | Tabs selected by 0.162.1 source |
| --- | --- |
| Known consumer plans, including Plus and Pro | Overview, Usage, Messages, Plugins, Skills, Chats; Plan only when its feature is enabled. Source eligibility does not guarantee populated backend reports. [Account classification][A15], [section selection][A7]. |
| Team and self-serve Business variants | Overview, Credits, Tokens, Plugins, Skills. These identifiers are classified as the internal Business family. [Plan predicates][A23], [classification][A15], [section selection][A7]. |
| `business`, `enterprise_cbp_usage_based`, `enterprise_cbp_automation` | Overview, Credits, Tokens, Plugins, Skills, Chats. These exact identifiers pass `thread_usage_supported`; the marketing term Business alone is insufficient to infer the SKU. [Chat eligibility][A15], [section selection][A7]. |
| Other workspace plans, including Enterprise and Edu/EduPlus/EduPro | Overview, Credits, Tokens, Plugins, Skills; no consumer Plan tab and no Chats unless the exact identifier passes the predicate above. [Plan predicates][A23], [section selection][A7]. |
| Unknown server plan | Overview only in the section selector; failed plan discovery may prevent loading. [Section selection][A7], [plan discovery][A22]. |
| API-key-only login | No authenticated account analytics through this path. Use the API provider's usage accounting separately. [Authentication gate][A22]. |

The authenticated reports describe the selected user/account scope, not automatically the whole organization's activity. Activity requests explicitly ask for workspace-user scope. Organization reporting is a separate surface with its own permissions, such as **Admin Console > Analytics > Insights**. [Endpoint parameters][A17], [official Usage Insights documentation][A24].

Chats combine two sources: app-server `thread/list` discovers non-archived, non-ephemeral root chats updated within the past 30 days, without a cwd restriction; backend `usage/thread_usage/query` or `usage/thread_usage/query_v2` supplies amounts. Consumer discovery is capped at 100 recent roots and gathers descendants, including archived descendants. Therefore Chats is not guaranteed to enumerate every chat on every device, even when account totals cover broader activity. [Root discovery][A21], [consumer discovery][A19], [workspace endpoint][A25], [consumer endpoint][A26].

An unavailable report is not zero usage. The client distinguishes loading, unavailable, and errors; plan data preserves missing percentages, incomplete coverage, and approximation metadata. A 404 on the experimental plan-history endpoint returns no report. Other requests have distinct sign-in, access-denied, and endpoint-unavailable messages. **UNCONFIRMED:** whether a given account currently has this backend endpoint and complete historical data. No live billing endpoint was called during this research. [Load states][A11], [plan parsing][A12], [plan endpoint][A14], [error handling][A10].

## Enable the experimental Plan tab

These are participant instructions, not actions performed by this research. The flag defaults to false and gates the Plan section, not the whole analytics dashboard. [Feature definition][A4], [view initialization][A18], [section selection][A7].

For one launch without changing persistent configuration:

```bash
codex --enable analytics_plan_history
```

For persistent enablement, use the documented feature command, then restart the TUI:

```bash
codex features enable analytics_plan_history
```

Alternatively, set `analytics_plan_history = true` inside the existing `[features]` table in the effective user `config.toml`; do not create a duplicate table. The TUI `/experimental` picker exposes **Analytics plan history**. Feature commands, `--enable`, and feature configuration are documented; the source registers this feature as experimental. [Official command reference][A27], [feature definition][A4].

After enabling, open `/usage` -> **View analytics**, then select **Plan**. On a Business/Enterprise/Edu account, enabling the flag does not override the consumer-account check. [Section selection][A7], [consumer-only request gate][A10].

## /status, /usage, and the desktop app

`/status` reports the current session's configuration and token usage; the official pricing documentation also recommends it for current remaining limits. `/usage` opens account usage actions and analytics; its daily/weekly/cumulative arguments select Overview aggregation. These are useful together: the current session snapshot and the account's historical reports answer different questions. [Official command reference][A27], [pricing and usage dashboard][A28], [argument dispatch][A2].

The documented browser usage dashboard is [Codex usage settings](https://chatgpt.com/codex/settings/usage). Workspace administrators also have the separate Admin Console analytics surface. **UNCONFIRMED:** an exact desktop-app menu and complete tab-for-tab equivalent to this CLI dashboard in Windows app `26.1007.2314.0`. Do not teach a guessed **Settings > Analytics** path. The public CLI source alone cannot establish the proprietary app's UI. [Official usage-dashboard guidance][A28], [workspace Insights][A24].

A five-hour-limit report must not become a claim that every plan has both limits. The current pricing page says Pro plans have no five-hour limit and describes different Enterprise/Edu arrangements. Have each participant inspect their actual dashboard rather than infer limits from the account's display name. This is current documentation, not a reconstruction of every participant's contract. [Official pricing][A28].

## How to use it in the course

1. Run `codex --version` and confirm the commands supported by that installation. Start with `/status`; record the model, remaining limits/reset times when shown, and session identifier. Run `/usage` and select **View analytics**. [Local verification](#verification-and-limits-of-this-research), [status and usage reference][A27].
2. Check the selected account identity. Use **Overview** for the longer trend, then inspect **Usage** or **Tokens** over a selected date range. Use the model grouping where available. Keep token counts, relative allowance, and credits labeled separately. [Account identity checks][A22], [group options][A18], [units][A15].
3. For a consumer account, optionally enable the experiment as above, then inspect **Plan** and **Chats**. Select a high-usage chat and compare available weekly/five-hour percentages; keep unavailable values unknown. For workspace users with Chats, use the displayed credit estimates. [Task metrics][A20], [workspace chats][A21], [plan metadata][A12].
4. Use **Plugins** and **Skills** to find heavily used integrations, then inspect the actual chat/tool evidence before blaming a tool. These reports describe activity; activity counts alone do not measure allowance cost or the usefulness of completed work. [Report contracts][A17], [official Insights interpretation][A24].
5. Repeat a small synthetic exercise with narrower source scope and a suitable model; compare the reported consumption after accounting updates. Recommended actions are precise prompts, relevant files only, shorter required output, compact repository instructions, and disabling unnecessary MCP servers. No fixed savings percentage or token-to-allowance conversion is established here. [Official efficiency advice][A28].

## Keep more evidence from a session

| Evidence | What to retain | Limitation |
| --- | --- | --- |
| `$CODEX_HOME/sessions` and `archived_sessions` | Local rollout records and session metadata, including recorded events; the default home is `~/.codex`. | Treat transcripts as sensitive; they can include prompts and tool output. They are local history, not authoritative account billing. [Rollout storage][A29], [recorder][A30], [state locations][A31]. |
| `codex doctor` or `codex doctor --json` | Installation/config/runtime diagnostics, rollout counts and total/average bytes, and rollout/state inventory checks. | Bytes and file counts are storage diagnostics, not token totals or five-hour-limit history. [Rollout statistics][A32], [inventory checker][A33]. |
| `codex exec --json` | Newline-delimited machine-readable run events; capture stdout into a suitable local artifact for a synthetic exercise. | This runs a task; it does not export an old interactive thread. JSON output can contain task content. This research did not start a model run. [Exec CLI][A34], [official command reference][A27]. |
| OpenTelemetry, when configured | Exported request/stream/tool events and relevant token metadata for future runs. | Opt-in export; prompt logging is separately controlled and defaults off. Configure an approved collector before the session; it does not recover past unexported events. [Official OTel configuration][A31]. |
| `/status`, `/copy`, `/export` | Session snapshots and a human-readable Markdown conversation export. | A Markdown export is not a lossless thread import or account billing record. [Command registry][A1], [export dispatch][A2], [official commands][A27]. |

## Verification and limits of this research

Read-only checks: `codex --version`, `codex --help`, `codex doctor --help`, `codex resume --help`, `codex fork --help`, and `codex features list`. Version was `0.162.1`; `analytics_plan_history` was `experimental false`. `codex doctor --json` exited 0 and produced a JSON report; exit 0 is not a claim that every diagnostic check passed. The sandbox printed `WARNING: proceeding, even though we could not create PATH aliases: Read-only file system (os error 30)`. No configuration was changed, no model prompt was submitted, and no live analytics/account responses or private rollout bodies were inspected.

Official developer documentation URLs now redirect to ChatGPT Learn; those fetched pages are cited below. The former `developers.openai.com/codex/changelog.md` returned 404, so the version finding uses the official GitHub release and tagged source. **UNCONFIRMED:** actual backend availability per account, app parity, and results on bundled alpha `0.162.0-alpha.17.2`. This is a source-and-documentation investigation, not a live desktop acceptance test.

## Sources

All GitHub source references below use the 0.162.1 release commit unless the link explicitly names another release.

[A1]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/slash_command.rs#L13-L122
[A2]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/chatwidget/slash_dispatch.rs#L498-L827
[A3]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/chatwidget/usage.rs#L32-L68
[A4]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/features/src/lib.rs#L980-L990
[A5]: https://github.com/openai/codex/releases/tag/rust-v0.156.0
[A6]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/chrome.rs#L11-L22
[A7]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/sections.rs#L138-L289
[A8]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/summary.rs#L12-L48
[A9]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/summary_panel.rs#L59-L159
[A10]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/client.rs#L109-L269
[A11]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/data.rs#L11-L47
[A12]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/plan.rs#L9-L81
[A13]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/plan_panel.rs#L67-L118
[A14]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/backend-client/src/client/plan_history.rs#L10-L83
[A15]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/models.rs#L5-L79
[A16]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/controls.rs#L29-L100
[A17]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/backend-client/src/client/analytics.rs#L8-L125
[A18]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics.rs#L141-L261
[A19]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/tasks.rs#L35-L243
[A20]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/task_panel.rs#L21-L135
[A21]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/analytics/chats.rs#L39-L189
[A22]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/backend-client/src/analytics_session.rs#L30-L117
[A23]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/protocol/src/account.rs#L7-L89
[A24]: https://learn.chatgpt.com/docs/enterprise/usage-insights
[A25]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/backend-client/src/client/thread_usage.rs#L89-L129
[A26]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/backend-client/src/client/task_usage.rs#L80-L116
[A27]: https://learn.chatgpt.com/docs/developer-commands?surface=cli
[A28]: https://learn.chatgpt.com/docs/pricing
[A29]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/rollout/src/lib.rs#L86-L95
[A30]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/rollout/src/recorder.rs#L77-L102
[A31]: https://learn.chatgpt.com/docs/config-file/config-advanced
[A32]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/cli/src/doctor.rs#L2200-L2285
[A33]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/cli/src/doctor/thread_inventory.rs#L1-L24
[A34]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/exec/src/cli.rs#L52-L70
