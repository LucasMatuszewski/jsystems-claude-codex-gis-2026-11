# Continuing Codex work between CLI, desktop, Windows, and WSL

Research date: 2026-10-14. CLI behavior was checked with local `codex-cli 0.162.1` and the matching source commit `092d3acd6bec3e3a14bdc7e7a2810ab628ab759d`. Reference app versions for this research were Windows app `26.1007.2314.0` and bundled Codex `0.162.0-alpha.17.2`; they were not independently verified through a running GUI. Official documentation currently uses the name ChatGPT desktop app; distinguish Codex workflows from ordinary ChatGPT chats. [Official Windows app documentation][D1].

## Practical answer

Add the existing repository to the desktop app using **Add new project** or **Ctrl+O**, then select the actual folder. For a WSL repository, enter `\\wsl$\` in the folder picker, select the distribution, and select the repository. To run the agent in WSL rather than Windows, open **Settings**, change the agent selector from Windows native to WSL, and **restart the app**. Selecting WSL as the integrated terminal is a separate setting and does not select the agent backend. [Windows app, WSL section][D1].

Adding the folder establishes the app's project context; it is not a verified import of every CLI thread. To continue an existing local chat, the app must reach the store containing that chat and use compatible source, directory, and archive filters. The public server supports listing CLI-originated threads, so CLI origin alone does not make a thread inaccessible. **UNCONFIRMED:** whether adding a folder alone immediately lists all matching CLI threads in Windows app `26.1007.2314.0`; its exact frontend query was not inspected. [Thread-list contract][D2], [source filtering][D3].

## Native Windows performance alternative: Dev Drive

Added and checked 2026-10-16. For native Windows development, consider a trusted **Windows Dev Drive**, rather than treating WSL as the only filesystem-performance option. The inspected Codex main implements doctor check `git.worktree.dev_drive` and a warning also observed with Windows CLI 0.162.1: moving a worktree to a trusted Dev Drive can significantly improve repository/filesystem performance. The Windows check was source-verified, not executed from this WSL session. [Doctor implementation](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/cli/src/doctor/windows_dev_drive.rs).

Microsoft's requirements and caveats:

- Windows 11 22H2 build `22621.2338` or later; all SKUs. Minimum 8 GB RAM, 16 GB recommended.
- ReFS-based volume, at least 50 GB, with local administrator permissions to create it. Existing volumes cannot be converted in place. Enterprise policy may require administrator enablement.
- A trusted drive plus enabled Defender real-time protection allows Defender performance mode. Untrusted drives use ordinary real-time scanning. Do not disable antivirus to pursue performance.
- Store source and development data there; keep installed developer tools on the system drive. A Dev Drive is storage, not a Linux runtime or a sandbox.

Source: [Microsoft Dev Drive documentation](https://learn.microsoft.com/en-us/windows/dev-drive/), checked 2026-10-16.

Runtime recommendation: keep the WSL agent with Linux-side storage when the project uses Linux tools or needs the Linux sandbox. For native Windows tools, evaluate Dev Drive first. UNVERIFIED: comparative timings on the workshop machines; no universal claim that WSL outperforms Dev Drive is justified. Runtime selection and thread-store separation described below still apply.

## What selects projects and threads

The CLI uses its starting directory, or `-C` / `--cd`, as the chat's project context. The desktop app has saved local projects connected to folders; newer documentation also describes ChatGPT projects and multiple attached folders, with a primary folder controlling the default cwd. These concepts should not be treated as an identical project-registration mechanism in all surfaces. [Official projects documentation][D4].

The app-server `thread/list` contract establishes the following filtering behavior; it does not establish which options the proprietary desktop frontend sends. [Protocol fields][D2], [request implementation][D5].

| Filter or state | Verified behavior | Troubleshooting consequence |
| --- | --- | --- |
| Store/backend | The local thread list is obtained through the server's configured thread store. | Check the agent host and effective local state location before treating a missing thread as deleted. [Request implementation][D5]. |
| `cwd` | A supplied path, or any path in an array, must exactly match the recorded session cwd after server-side path handling. | A sibling checkout, repository subdirectory, Windows path, and Linux path are not automatically the same filter value. [Protocol][D2], [cwd normalization][D6]. |
| `sourceKinds` | Omitted or empty means interactive sources, not all sources. Explicit values can request `cli`, `vscode`, `exec`, `appServer`, or subagent variants. | A non-interactive `codex exec` task may be absent from a normal chat list. [Source kinds][D7], [filter implementation][D3]. |
| Interactive defaults | Core defaults include CLI, VS Code, and custom `atlas` / `chatgpt` sources. | A client using defaults can see interactive CLI history in the same store; it need not request only app-created chats. [Core source list][D8]. |
| `archived` | Omitted, null, or false returns non-archived threads; true returns only archived threads. | Search the archive separately. [Protocol][D2]. |
| Provider, title, section, project | Provider and title filters exist, as do section and experimental project-ID filters. Local stores can reject unsupported project-ID filtering. | Do not assume a broad-looking app view is an unfiltered inventory. [Protocol][D2], [implementation][D5]. |
| Pagination and database repair | Responses are paginated. `useStateDbOnly=true` avoids rollout scanning and metadata repair; its default is false. | A stale index or a client that has not loaded another page can affect discovery; do not start by deleting the database. [Protocol][D2], [implementation][D5]. |

The server's tests explicitly verify that an empty source-kind filter excludes an exec-originated thread and retains an interactive CLI thread. This is evidence for a real source-filter distinction, not a theory that CLI and desktop have intrinsically incompatible thread formats. [Thread-list test][D9].

## Continue a CLI thread in the app

On a native Windows or macOS CLI, `/app` opens the current saved chat in the desktop app. The source first requires a thread ID, then emits an open-desktop-thread event. The slash command is compiled as available only for Windows and macOS; do not promise it in the native Linux CLI running inside WSL. [Official command documentation][D10], [dispatch][D11], [platform gate][D12].

For a WSL CLI chat, first set the app's intended agent runtime and restart if it changed, add the exact WSL folder, and look for the chat in that project or **Search chats**. Check **Settings > Archived chats** if necessary. This is a discovery procedure, not a promise of automatic Windows-to-WSL history migration. **UNCONFIRMED:** a supported arbitrary-thread-ID entry field or deep-link format for opening an existing WSL thread in this specific Windows app build. [Windows runtime selection][D1], [search and archive UI][D4].

Stop submitting turns in the original surface before continuing elsewhere. The official 0.154.0 release notes describe a read-only transcript and retry behavior when a conversation is already open in another app. Treat handoff as continuing the same chat sequentially, rather than assuming both clients can independently write to it. [Official 0.154.0 release notes][D13].

## Continue an app thread in the CLI

Run the CLI in the runtime and state environment that can see the saved thread. `codex resume` opens the picker. `--all` removes its cwd filtering and shows a cwd column; it does not search other Windows users, WSL distributions, remote hosts, or arbitrary homes. `--include-non-interactive` separately widens picker and `--last` selection to non-interactive sessions. [CLI resume arguments][D14], [state-location documentation][D15].

```bash
codex resume
```

```bash
codex resume --all
```

```bash
codex resume --last
```

```bash
codex resume --last --all
```

```bash
codex resume --all --include-non-interactive
```

To continue a known saved chat directly, replace the illustrative UUID below with its actual ID. Resume also accepts an exact session name; a valid UUID takes precedence. An ID is an address within reachable history, not a portable transcript. [CLI resume arguments][D14].

```bash
codex resume 00000000-0000-0000-0000-000000000000
```

Use `codex fork` to branch a saved conversation into a new chat rather than continue the original. The picker, `--all`, `--last`, and direct session-ID forms are available. These commands do not themselves transfer repository files or discover an unrelated state directory. Commands below do not request a Git worktree. [Official resume/fork documentation][D10], [local help verification below].

```bash
codex fork --all
```

```bash
codex fork --last
```

```bash
codex fork 00000000-0000-0000-0000-000000000000
```

For app-originated local interactive history in the same reachable store, choose the chat in the CLI picker. If it is absent, investigate runtime/store and filters before trying transcript copying. **UNCONFIRMED:** an end-to-end app-to-CLI resume in Windows app `26.1007.2314.0`; no live app thread was opened or altered in this research. [Core interactive sources][D8], [resume arguments][D14].

## Windows and WSL state locations

Codex's default state directory is the current runtime user's `~/.codex`, overridden by `CODEX_HOME`. On native Windows this normally resolves under `%USERPROFILE%\.codex`; an independently launched WSL CLI normally uses the Linux user's `~/.codex`. `sqlite_home` can separately relocate SQLite state. Therefore matching the repo and login is insufficient if the two processes use different state locations. [State-location documentation][D15], [configuration reference][D16].

| Surface | What is established |
| --- | --- |
| Native Windows CLI | Uses its effective Windows user/home and overrides; do not infer the WSL home from it. [State-location documentation][D15]. |
| Independently launched WSL CLI | Uses its effective Linux user/home and overrides; verify the distribution and user. [State-location documentation][D15]. |
| Windows desktop with Windows-native agent | The app's agent executes commands in PowerShell by default. Its exact launch environment and state overrides remain app implementation details. [Windows documentation][D1]. |
| Windows desktop with WSL agent | Agent execution changes to WSL/Linux sandboxing after restart; projects should remain registered. **UNCONFIRMED:** whether this build uses Linux `~/.codex`, a Windows-backed location, an injected `CODEX_HOME`, or a migration/shared-state mechanism. The public Windows documentation does not specify that contract. [Windows documentation][D1]. |
| Desktop integrated terminal | Its selected shell is independent of the agent runtime. A WSL terminal is not proof that the current agent or thread store is WSL-based. [Windows documentation][D1]. |

Do not teach the unsupported shortcut "switch the app to WSL and it will necessarily use the same `~/.codex` as my shell". Instead compare the app's effective runtime diagnostics with the CLI's diagnostics and configuration paths. Switching execution OS, registering folders, sharing source files, and locating conversation state are four separate checks. [Windows runtime documentation][D1], [state locations][D15], [thread-list cwd contract][D2].

## Local example and evidence boundary

Names-only inspection confirmed both the Windows `%USERPROFILE%\.codex\` and the WSL `~/.codex/` exist, each containing `config.toml`, `sessions`, `archived_sessions`, `state_5.sqlite`, and associated `-wal` / `-shm` files. The Windows directory also contains `.codex-global-state.json` and `external_agent_session_imports.json`; those files' contents were not opened. The WSL shell had no `CODEX_HOME` environment override. These are local observations on 2026-10-14, not portable product guarantees.

The permitted Windows `config.toml` inspection parsed only app/WSL/project-related structure and emitted no credential values. It found 24 configured project entries but no explicit WSL agent-selector key through that narrow inspection. Project trust entries are not proof of the desktop sidebar's saved-project list. A supplied WSL-agent setting does not establish which store the running app actually selected; that store remains **UNCONFIRMED**. No auth files, private session bodies, or app-global-state contents were inspected.

`codex doctor --json` completed with exit 0 on the WSL CLI. Only report structure and safe execution metadata were emitted; individual diagnostic statuses were not retained, so this does not establish a clean installation or prove the app's backend location. The CLI also emitted a nonfatal sandbox warning that PATH aliases could not be created on a read-only filesystem.

## Safe ways to move work

**Same machine, same runtime/store:** add the actual local folder and use the saved-thread picker, `/app` where supported, or `codex resume`. This is the preferred first investigation because it preserves the recorded chat rather than attempting an undocumented migration. Discovery still depends on filters. [Official commands][D10], [thread-list protocol][D2].

**Across Windows/WSL or different machines:** use Git to transfer repository changes and checked-in requirements/decisions, then start a new chat with a concise handover describing the objective, current branch/commit, completed checks, and remaining work. This is a course recommendation: Git transfers project artifacts; it should not be presented as a Codex thread-sync feature. Conversation sync and local-folder access are explicitly separate in current project documentation. [Projects and file access][D4].

**Read the WSL repository from the Windows app:** use the documented `\\wsl$\<distribution>\home\<user>\...` picker route. Prefer a WSL agent for the course's Linux checkout and toolchain. The official docs separately recommend Windows-hosted project folders when staying with the Windows-native agent. A UNC folder selection alone does not establish that the old Linux conversation store is reachable. [Windows/WSL guidance][D1].

**Human-readable handover:** `/export` writes a Markdown conversation export, and `/copy` supports copying session information. A new chat can consume a reviewed summary/export as context. No supported Codex-to-Codex round-trip thread import was established here; do not promise restoration of thread identity, approvals, tool state, or lineage from Markdown. [Export/copy registry][D12], [export dispatch][D11].

**Other-agent imports:** `external_agent_session_imports.json` is an import ledger containing source-path/hash and imported-thread tracking. It is not evidence of automatic CLI-to-desktop or Windows-to-WSL Codex history synchronization. The documented import flow targets Claude Code, Claude Cowork, and Cursor, with supported agents varying by surface. [Ledger source][D17], [official import documentation][D18].

**Connected-host handoff:** current docs also describe app-managed transfer to a matching project on an SSH host through the chat footer's run location, destination selection, and **Hand off** action. That workflow can transfer chat and Git state and creates or reuses a destination worktree. It is a separate managed feature, not a documented arbitrary Windows/WSL JSONL import. **UNCONFIRMED:** availability in this workshop's app build and whether the local Windows/WSL switch is a supported destination. Do not run it in this repository without its required worktree authorization. [Remote-connections documentation][D19].

## What not to do

Do not manually point a native Windows process and a Linux process at one shared `CODEX_HOME` over `/mnt/c` or `\\wsl$` as a workshop synchronization fix. This is an engineering recommendation, not a claim that the app's own supported WSL implementation is broken. Codex state uses SQLite WAL mode; SQLite requires coordinated locking/shared memory and excludes network filesystems for WAL. Compatibility of mixed Windows/WSL access was not established, and a common path does not prove compatible locking or path metadata. [Codex SQLite initialization][D20], [SQLite WAL documentation][D21].

Do not copy a live `state_5.sqlite` alone, overwrite one home with the other, edit rollout `cwd` values, copy authentication files, or delete the state database to make a picker refresh. Such operations are outside the verified continuation workflow; a live WAL can contain committed data absent from the main database file. Use diagnostics first and keep repository transfer separate from state migration. [SQLite WAL][D21], [Codex state location][D15], [thread-list repair contract][D2].

## Thread not visible in the app: checklist

1. **Runtime:** open Settings, check Windows native versus WSL agent, and restart after changing it. Check the WSL distribution/user; the terminal shell alone is insufficient. [Windows documentation][D1].
2. **Folder:** use Add new project / Ctrl+O and select the exact checkout. For Linux use the WSL picker path. Compare the recorded cwd with the actual project directory, including subdirectories and alternate checkouts. [Windows documentation][D1], [cwd filter][D2].
3. **History location:** in the originating runtime run `codex resume --all`. Check effective `CODEX_HOME`, any `sqlite_home` override, and safe `codex doctor` diagnostics. Seeing the chat there establishes its presence in that runtime, not its presence in the app's store. [Resume arguments][D14], [state configuration][D15], [configuration reference][D16].
4. **Filters:** check Search chats and Settings > Archived chats. For an exec-originated task, try `codex resume --all --include-non-interactive` in the originating runtime; this widens the CLI picker, not the app's filters. [App search/archive][D4], [CLI arguments][D14].
5. **Continue:** use `/app` from a supported native CLI or pick the existing chat when the stores align. If the boundary remains unresolved, transfer the code through Git and use a reviewed handover in a new chat; record that the original thread was not migrated. [Platform gate][D12], [official continuation commands][D10].

## Verification and remaining questions

Verified read-only commands: `codex --version`, `codex --help`, `codex resume --help`, `codex fork --help`, `codex doctor --help`, `codex features list`, and a filtered `codex doctor --json` run. No resume/fork command actually continued a conversation, and no desktop settings or repositories were changed. Folder registration and runtime instructions come from fetched official docs; source filtering is pinned to 0.162.1.

**UNCONFIRMED:** the exact frontend `thread/list` request in app 26.1007, actual post-WSL-switch state location, automatic history migration, arbitrary thread-ID opening in the app, round-trip Codex thread import, and connected-host handoff support in that build. A future manual check should use one synthetic chat and compare the app's runtime/state diagnostics before and after a controlled switch; this research did not perform that switch.

## Sources

[D1]: https://learn.chatgpt.com/docs/windows/windows-app#windows-subsystem-for-linux-wsl
[D2]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/app-server-protocol/src/protocol/v2/thread.rs#L1394-L1465
[D3]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/app-server/src/filters.rs#L6-L82
[D4]: https://learn.chatgpt.com/docs/projects
[D5]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/app-server/src/request_processors/thread_processor.rs#L2524-L2652
[D6]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/app-server/src/request_processors/thread_processor.rs#L250-L284
[D7]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/app-server-protocol/src/protocol/v2/thread.rs#L1498-L1523
[D8]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/rollout/src/lib.rs#L86-L95
[D9]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/app-server/tests/suite/v2/thread_list.rs#L1265-L1307
[D10]: https://learn.chatgpt.com/docs/developer-commands?surface=cli
[D11]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/chatwidget/slash_dispatch.rs#L318-L827
[D12]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/tui/src/slash_command.rs#L89-L312
[D13]: https://github.com/openai/codex/releases/tag/rust-v0.154.0
[D14]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/cli/src/main.rs#L353-L376
[D15]: https://learn.chatgpt.com/docs/config-file/config-advanced#config-and-state-locations
[D16]: https://learn.chatgpt.com/docs/config-file/config-reference
[D17]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/external-agent-migration/src/sessions/ledger.rs#L16-L62
[D18]: https://learn.chatgpt.com/docs/import
[D19]: https://learn.chatgpt.com/docs/remote-connections#hand-off-a-chat-between-hosts
[D20]: https://github.com/openai/codex/blob/092d3acd6bec3e3a14bdc7e7a2810ab628ab759d/codex-rs/state/src/sqlite.rs#L375-L402
[D21]: https://sqlite.org/wal.html
