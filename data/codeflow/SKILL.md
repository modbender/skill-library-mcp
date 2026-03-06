---
version: 1.0.0
name: codeflow
description: Codeflow streams coding agent sessions (Claude Code, Codex, Gemini CLI, etc.) to Discord or Telegram in real-time. Use when invoking coding agents and wanting transparent, observable dev sessions — no black box. Parses Claude Code's stream-json output into clean formatted messages showing tool calls, file writes, bash commands, and results with zero AI token burn. Use when asked to "stream to Discord", "stream to Telegram", "relay agent output", or "make dev sessions visible".
user-invocable: true
metadata: {"openclaw":{"emoji":"🎬","requires":{"anyBins":["unbuffer","python3"]}}}
---

# Codeflow

Live-stream coding agent sessions to Discord or Telegram. Zero AI tokens burned.

Breaking note:
- Command name: `/codeflow`
- Env var prefix: `CODEFLOW_*`

## Setup

First-time setup: see [references/setup.md](references/setup.md) for webhook creation, unbuffer install, bot token, and smoke test.

## Developer Checks (optional)

Run a local sanity check bundle (Python syntax compile + unit tests + `bash -n`):

```bash
bash {baseDir}/scripts/codeflow check
```

## `/codeflow` command contract (session-scoped)

When user invokes `/codeflow`, treat it as a **session-scoped declaration**:

1. For the **current OpenClaw session**, all coding, development, or review tasks (code/architecture/security/product review) — including any direct Codex or Claude Code invocations — must be executed via **Codeflow relay + local Codex/Claude Code** (not direct edits unless explicitly requested).
2. Follow Codeflow output conventions (including compact Telegram behavior when applicable).
3. If user asks for direct non-code tasks, handle normally; this contract applies to coding, development, and review tasks.
4. The contract lasts for the current session context. If user resets/new session, require re-invocation.

Acknowledge activation in one short sentence, then execute coding tasks under this contract.

After `/codeflow` activation, immediately run a guard activation command (same chat/topic context):

```bash
# Telegram example (preferred in Telegram topics):
exec command:"{baseDir}/scripts/codeflow guard activate -P telegram --tg-chat <chat_id> --tg-thread <thread_id_optional>"

# Generic auto mode:
exec command:"{baseDir}/scripts/codeflow guard activate -P auto"
```

Guard enforcement (hard constraint in script):
- All execution modes that can post/run work (`run`, `resume`, `review`, `parallel`) are guard-protected by default because they route through `dev-relay.sh`.
- Guard management commands (`codeflow guard activate|deactivate|status`) bypass the precheck.
- Guard is bound to chat/topic context (and session key when available).
- Every allow/deny decision is appended to `${XDG_STATE_HOME:-$HOME/.local/state}/codeflow/guard-audit.jsonl` (stores `commandHint` only — redacted + truncated; never the full command).
- If blocked, instruct user to re-run `/codeflow` in the same chat/topic.

Default inference rules (do not ask unless ambiguous):
- Task content: ask user for this when missing.
- Workdir: infer from recent chat/context/task history (not blindly current workspace). If unclear, ask user to re-declare workdir.
- Platform: infer from current channel (Telegram/Discord).
- Target chat/thread: infer from inbound metadata (current chat/thread).

Codex session policy under `/codeflow`:
- Reuse the prior Codex session associated with the same `-w <workdir>` when available (keyed by `realpath(workdir)`).
- If no prior session is found, create a new session when the task is dispatched.
- Only force new session when user explicitly requests it.

Under `/codeflow`, avoid asking for workdir/platform/chat if derivable from context.

## Invocation

Launch with `exec background:true`. Background exec sessions survive agent turns. Exit notifications (e.g. `notifyOnExit`) are provided by the host runtime (OpenClaw), not by Codeflow itself.

```bash
exec background:true command:"{baseDir}/scripts/codeflow run -w ~/projects/myapp -- claude -p --dangerously-skip-permissions --output-format stream-json --verbose 'Your task here'"
```

Note the session ID from the response — use it to monitor via `process`.

### CLI (stable)

Public entrypoint (do not call `_internal/` scripts directly):

```bash
bash {baseDir}/scripts/codeflow <command> [...]
```

Commands:

- `codeflow run [run-flags] -- <agent command>` — start a relay session
- `codeflow guard activate|deactivate|status [run-flags]` — manage the session-scoped guard
- `codeflow resume [run-flags] <relay_dir>` — replay a previous session from `stream.jsonl`
- `codeflow review [...] <pr_url>` — PR review mode
- `codeflow parallel [...] <tasks_file>` — parallel tasks mode
- `codeflow bridge [...]` — Discord gateway bridge
- `codeflow check` — local checks (syntax + unit tests)
- `codeflow smoke` — config/prereq smoke test

See `bash {baseDir}/scripts/codeflow --help` for the canonical CLI.

### Run flags (`codeflow run`)

| Flag | Description | Default |
|------|------------|---------|
| `-w <dir>` | Working directory | Current dir |
| `-t <sec>` | Timeout | 1800 |
| `-h <sec>` | Hang threshold | 120 |
| `-i <sec>` | Post interval (raw mode only) | 10 |
| `-n <name>` | Agent display name | Auto-detected |
| `-P <platform>` | `discord`, `telegram`, `auto` (inferred) | discord |
| `--thread` | Post into a Discord thread | Off |
| `--tg-chat <id>` | Telegram chat id (when `-P telegram`) | — |
| `--tg-thread <id>` | Telegram thread/topic id (optional) | — |
| `--skip-reads` | Hide Read tool events | Off |
| `--new-session` | For Codex exec: force a new Codex session | auto policy |
| `--reuse-session` | For Codex exec: require and reuse previous session | auto policy |

Rate limiting note (Telegram hardening): parse-stream now routes all delivery through an in-process **delivery governor** with strict 429 handling:
- Telegram 429 backoff: `next_allowed_at = now + retry_after + 1s` (strictly follows Telegram `retry_after`; adds +1s to avoid immediately hitting 429 again)
- do not send any request before `next_allowed_at`
- queue priority: `final` > `event` > `state`
- compact `state` cards (thinking/cmd) are strict snapshot overwrite (latest-wins); during 429 windows updates are merged in memory and only the latest snapshot is applied once the window opens

If you still need to reduce output volume, use `CODEFLOW_OUTPUT_MODE` (see below) plus existing knobs (`--skip-reads`, `CODEFLOW_SAFE_MODE=true`, `CODEFLOW_COMPACT`).

For PR review, parallel tasks, Discord bridge, and Codex structured output: see [references/advanced-modes.md](references/advanced-modes.md).

## Agent Launch Checklist

1. **Start background session** → note session ID from the `exec` response
2. `codeflow run` posts the session header and streams events to the target channel automatically
3. **Monitor** via `process log` / `process poll`; stop via `process kill`

## Completion Detection

Completion notifications are runtime-dependent (OpenClaw). Codeflow itself simply exits when the inner agent command exits.

**Backup:** Append this to the inner agent's prompt for an additional signal:
```
When completely finished, run: openclaw system event --text "Done: <brief summary>" --mode now
```

## Monitoring

```
process poll sessionId:<id>        # Check status
process log sessionId:<id>         # View recent output
process kill sessionId:<id>        # Stop session
```

### Safe mode (optional)

If you stream relay output into a shared channel, enable:

- `CODEFLOW_SAFE_MODE=true`

Effects:
- Suppress file-content previews (Claude `Write`)
- Suppress command output bodies (Claude Bash output, Codex `command_execution` output, raw mode output)
- Apply stricter redaction to high-risk fields

### Output mode

Control how verbose channel posts are via env:

- `CODEFLOW_OUTPUT_MODE=minimal|balanced|verbose` (default: `balanced`)
  - `minimal`: only `warning/error/final`
  - `balanced`: key progress + `warning/error/final`
  - `verbose`: near-full (debug; Telegram is more likely to hit 429)

Telegram compact state cards (strict snapshot overwrite):
- thinking/cmd cards always `edit` the same anchor (no extra posts)
- each `edit` replaces the full snapshot (no accumulated log); during 429 windows updates are merged in memory (latest-wins) and only the latest snapshot is applied once the window opens
- only when the message exceeds platform limits do we truncate/compress and mark `…(truncated)`; otherwise we do not fold/hide content

### Telegram anti-spam mode (default)

When `-P telegram` is used, Codex sessions run in compact mode by default:
- per turn, one rolling "thinking" message (edited in place)
- per turn, one rolling "commands/results" message (edited in place)
- one separate turn-complete output message (full text; paginated if oversized)

Next turn starts a fresh pair of rolling messages.

Override with env:
- `CODEFLOW_COMPACT=true|false` (default `auto`, where Telegram => true)

Telegram 429 / anchor stability (compact mode):
- edit failures do not "post a new anchor immediately" (no anchor explosion); state cards preserve single-anchor edit semantics
- on 429, Codeflow sleeps for `retry_after + 1s` (not a fixed 10s); when the window opens, it flushes by priority (final > event > state)

Telegram adapter memory guard (oversized message edit groups):
- `CODEFLOW_TELEGRAM_EDIT_GROUPS_MAX=<n>`: max tracked groups (LRU, default `64`; set `0` to disable tracking)
- `CODEFLOW_TELEGRAM_TRACK_EDIT_GROUPS=true|false`: enable/disable tracking (default `true`)

Notes:
- This only affects multi-message editing via `platforms/telegram.py` `edit()`; compact mode uses `edit_single` and is unaffected.
- Disabling tracking means `edit()` cannot delete/overwrite prior tail messages for already-split posts.

### Codex session reuse policy (hard workflow constraint)

For `codex exec ...`, Codeflow enforces a session policy in code (not just docs):
- default `auto`: reuse previous Codex session for the same workdir when available
- if prompt contains `/new` under `auto`: force a new session for that run
- `--new-session`: force new session
- `--reuse-session`: require previous session and force resume (error if missing)

Optional env overrides:
- `CODEFLOW_CODEX_SESSION_MODE=auto|new|reuse` (default `auto`)
- `CODEFLOW_CODEX_SESSION_MAP=/tmp/dev-relay-codex-sessions.json` (session map path)

## Agent Support

| Agent | Output Mode | Status |
|-------|------------|--------|
| Claude Code | stream-json | Full support |
| Codex | --json JSONL | Full support |
| Any CLI | Raw ANSI | Basic support |

## Session Tracking

- **Active sessions:** `/tmp/dev-relay-sessions/<PID>.json` (auto-removed on end)
- **Event logs:** `/tmp/dev-relay.XXXXXX/stream.jsonl` (7-day auto-cleanup)
- Stream log policy: `CODEFLOW_STREAM_LOG=full|redacted|off` (default: `full`; if `CODEFLOW_SAFE_MODE=true` and `CODEFLOW_STREAM_LOG` is unset, default becomes `redacted`). `off` writes minimal metadata only (resume/debug is limited).
- Delivery anomaly events: appended into `stream.jsonl` as `codeflow.delivery.*` (exceptions only; no message bodies/tokens/URLs).
- Delivery stats (local): `/tmp/dev-relay.XXXXXX/delivery-summary.json` (single-file summary; includes rate-limit counts, drops, etc).
- **Guard state:** `${XDG_STATE_HOME:-$HOME/.local/state}/codeflow/guard.json` (stores `commandHint` only — redacted + truncated)
- **Guard audit log:** `${XDG_STATE_HOME:-$HOME/.local/state}/codeflow/guard-audit.jsonl` (JSONL)
- **Interactive input:** `process submit sessionId:<id> data:"message"`
  - If the XDG state dir is not writable, guard/state/audit fall back to dotfiles under `{baseDir}/scripts/` (see `codeflow/scripts/_internal/bin/lib.sh`).
- Telegram/Discord delivery no longer spawns `curl`; tokens/webhooks do not appear in child process argv (avoids `ps` leakage).
- `/tmp/dev-relay-sessions/<PID>.json` is written atomically (tmp + rename, best-effort fsync) and minimized (does not persist full command/context).

## Reference Docs

- [Setup guide](references/setup.md) — first-time install, webhook, bot token
- [Advanced modes](references/advanced-modes.md) — PR review, parallel tasks, Discord bridge, Codex
- [Discord output](references/discord-output.md) — message formats, architecture, env vars, troubleshooting
