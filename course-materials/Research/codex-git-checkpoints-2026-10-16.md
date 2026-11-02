# Codex Git checkpoints, turn diffs, and rewind

Checked: 2026-10-16. Local CLI: `codex-cli 0.162.1`. Source reviewed: main commit `6b991972c5b539198dcea9bac4fc14e57559c3af`, dated 2026-10-15. This main snapshot is not proof of the installed release's exact internals.

## What observed checkpoint refs establish

`refs/codex/turn-diffs/checkpoints/` is an observed Codex integration namespace, not a normal branch or tag. A separate first-hand report in the upstream repository documents it with the VS Code extension, including a nested checkpoint-key/turn-ID/timestamp/UUID layout and Windows path-length failures. Thus it is **not exclusive to the desktop app**. [Upstream report #37559](https://github.com/openai/codex/issues/37559).

Inference: the name and integration report associate these refs with turn-diff snapshot bookkeeping. A Git ref preserves reachability of its target object; if that object is a commit, its tree can represent a filesystem snapshot independently of the branch history. Inspect the actual object type before assuming its content. UNVERIFIED: the precise writer, retention policy, snapshot coverage and restoration contract in the observed desktop build. No desktop bundle or private session store was inspected, and no maintainer specification for this namespace was found.

## What the open-source CLI actually contains

The full checked-out source was searched for `refs/codex` and the exact checkpoint prefix. The only literal `refs/codex` namespace found was `refs/codex/curated-sync`, a plugin-fetch ref, unrelated to per-turn recovery. No writer of `refs/codex/turn-diffs/checkpoints/` was found. [Plugin startup sync](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/core-plugins/src/startup_sync.rs).

Three similarly named mechanisms need separating:

- **Legacy ghost commits / undo:** main retains `Feature::GhostCommit` only as a removed, disabled compatibility flag named `undo`. It is explicitly a no-op. The protocol also tests that historical `ghost_snapshot` records deserialize as `Other`. These remnants are not an active checkpoint writer. [Features](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/features/src/lib.rs), [legacy protocol compatibility](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/protocol/src/models.rs).
- **Turn diffs:** `TurnDiffTracker` computes net text diffs from committed `apply_patch` mutations in memory. That is not evidence of repository-wide Git snapshots or coverage of arbitrary shell edits. [Tracker](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/core/src/turn_diff_tracker.rs).
- **Conversation revert:** main's app-server documentation says `thread/rollback` was removed in favor of `thread/revert` for paginated threads. Transcript operations must not be described as guaranteed filesystem recovery. The TUI slash-command enum has no `/undo` or `/rewind`. [App-server](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/app-server/README.md#thread-rollback), [TUI commands](https://github.com/openai/codex/blob/6b991972c5b539198dcea9bac4fc14e57559c3af/codex-rs/tui/src/slash_command.rs).

The [official app features](https://developers.openai.com/codex/app/features/) and [changelog](https://developers.openai.com/codex/changelog/) were also checked. They do not establish the exact namespace's retention/deletion contract. Generic changelog references to checkpoints, including approval-review recovery, are not evidence of this Git mechanism.

## Comparison

| Surface | Verified recovery behavior |
|---|---|
| Codex integration checkpoint refs | Observed Git refs associated with turn diffs; do not promise a supported CLI rewind command or full backup coverage. |
| GitHub Copilot CLI | `/undo` or `/rewind` opens a picker for conversation-only or conversation-and-files recovery. Current docs say Git is not required and later user edits are skipped. Its context-compaction checkpoints are another mechanism. [Rewind](https://docs.github.com/en/copilot/how-tos/copilot-cli/use-copilot-cli/roll-back-changes), [context checkpoints](https://docs.github.com/en/copilot/concepts/agents/copilot-cli/context-management) |
| VS Code Copilot | Restore Checkpoint is a UI feature for chat edits. Do not infer that its implementation uses the Codex namespace. [Review edits](https://code.visualstudio.com/docs/agents/run/review-code-edits) |
| Claude Code | `/rewind` or double Esc offers code/conversation restoration and summarization. Checkpointing complements Git; it does not reverse external side effects. [Checkpointing](https://code.claude.com/docs/en/checkpointing) |

## Inspecting, pushing, and deleting

List refs without changing anything:

```bash
git for-each-ref --format='%(refname) %(objecttype) %(objectname)' refs/codex
```

After copying one full ref name into a local variable `checkpoint_ref`, inspect metadata and filenames before opening potentially sensitive contents:

```bash
git cat-file -t "$checkpoint_ref"
```

```bash
git show --no-patch --format=fuller "$checkpoint_ref"
```

```bash
git ls-tree -r --name-only "$checkpoint_ref"
```

Ordinary branch pushes and `git push --all` do not push this custom ref namespace. **`git push --mirror` or an explicit matching refspec can publish it and its reachable objects.** Do not treat these snapshots as private if you mirror the entire repository. [Git push](https://git-scm.com/docs/git-push).

Deletion is not an unconditional safe-cleanup recommendation. Stop all clients using the checkout, save wanted work independently, and inspect/archive any needed snapshot first. Removing a ref does not itself change checked-out files or branch tips, but can lose a turn-diff/recovery baseline; the app may recreate it. Objects can remain until garbage collection, so ref deletion is not secure erasure. Exact app behavior after deletion is UNVERIFIED.

For an individually reviewed, obsolete ref, Git's supported deletion mechanism is `git update-ref -d <full-ref-name> <expected-object-id>`, using the OID previously inspected. Prefer this to removing loose files: refs may be packed. No refs were deleted, no garbage collection was run, and no push was performed in this research. [Git update-ref](https://git-scm.com/docs/git-update-ref).
