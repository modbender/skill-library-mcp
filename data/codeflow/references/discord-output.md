# What Output Channels See (Discord / Telegram)

## Claude Code (stream-json)
- ⚙️ Model info and permission mode
- 📝 File writes with line count + content preview (redacted; suppressed in safe mode)
- ✏️ File edits
- 🖥️ Bash commands
- 📤 Bash command output (redacted; suppressed in safe mode)
- 👁️ File reads (hide with `--skip-reads`)
- 🔍 Web searches
- 💬 Assistant messages
- Long messages are split safely to avoid silent truncation. For Discord, long code-fenced messages are split into self-contained fences (no unclosed ``` blocks).
- ✅/❌ Completion summary with turns, duration, cost, and session stats

## Codex (--json)
- ⚙️ Session thread ID
- 🖥️ Command executions
- 📤 Command output (redacted; suppressed in safe mode)
- ⚠️ Non-zero exit codes: only real failures emit warnings; probe-style commands that use `exit=1` for "no match/false" (e.g. `rg`/`grep`/`test`) are downgraded to debug (visible only with `CODEFLOW_OUTPUT_MODE=verbose`).
- 📝 File creates / ✏️ File modifications
- 🧠 Reasoning traces
- 🔍 Web searches / 🔧 MCP tool calls / 📋 Plan updates
- 💬 Agent messages
- 📊 Token usage per turn
- ✅ Session summary with cost and stats

## Other agents (raw mode)
- Output in code blocks with ANSI stripping (suppressed in safe mode)
- Hang detection warnings
- Completion/error status

## End Summary
Every session ends with: files created/edited, bash commands run, tool usage breakdown, total cost, and delivery counters (ok/fail/retries).

Local delivery stats summary is written to: `/tmp/dev-relay.XXXXXX/delivery-summary.json` (single file; updated incrementally on delivery anomalies and at end).

Delivery anomaly metadata (no message bodies/tokens/URLs) is appended into `stream.jsonl` as `codeflow.delivery.*` events. No additional log files are written by the relay.

## Architecture

```
scripts/
├── codeflow              # Single public entrypoint (router)
├── .webhook-url          # Discord webhook URL (ignored by .gitignore)
├── .bot-token            # Discord bot token (optional; ignored by .gitignore)
└── _internal/
    ├── bin/
    │   ├── dev-relay.sh          # Process management + guard enforcement
    │   ├── lib.sh                # Shared shell helpers (platform inference, state helpers)
    │   ├── review-pr.sh          # PR review mode (--review)
    │   ├── parallel-tasks.sh     # Parallel worktree tasks (--parallel)
    │   ├── check.sh              # Local sanity checks (py_compile + tests + bash -n)
    │   └── test-smoke.sh         # Pre-flight validation
    ├── py/
    │   ├── parse-stream.py       # Multi-agent JSON stream parser
    │   ├── delivery_governor.py  # Single-thread delivery scheduler (priority + strict 429)
    │   ├── delivery_errors.py    # Delivery exception types (rate limit, drop)
    │   ├── message_split.py      # Parser-layer message splitting helpers (Discord code fences)
    │   ├── redaction.py          # Minimal secret redaction helpers
    │   ├── py_compat.py          # Python >=3.10 guard + readable error
    │   ├── discord-bridge.py     # Discord gateway bridge (read-only: status/log)
    │   ├── codeflow-guard.py     # Session-scoped guard state + audit logger (commandHint only)
    │   ├── tests/                # Unit tests (unittest)
    │   └── platforms/
    │       ├── __init__.py       # Platform adapter loader
    │       ├── discord.py        # Discord webhook + thread support
    │       └── telegram.py       # Telegram Bot API sendMessage adapter
    └── (state) ${XDG_STATE_HOME:-$HOME/.local/state}/codeflow/
        ├── dev-relay-state.json    # Telegram chat/thread persistence (fallback: scripts/.codeflow-state.json)
        ├── guard.json              # Guard state (fallback: scripts/.codeflow-guard.json)
        └── guard-audit.jsonl       # Guard audit JSONL (fallback: scripts/.codeflow-audit.jsonl)
```

## Environment Variables

| Variable | Description | Default |
|----------|------------|---------|
| `CODEFLOW_BOT_TOKEN` | Discord bot token for --thread and bridge | `.bot-token` file |
| `CODEFLOW_TELEGRAM_CHAT_ID` | Telegram chat id for `-P telegram` | — |
| `CODEFLOW_TELEGRAM_THREAD_ID` | Telegram topic/thread id (optional) | — |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token (if not in OpenClaw config) | OpenClaw config |
| `CODEFLOW_COMPACT` | Codex compact Telegram updates (`auto|true|false`) | `auto` |
| `CODEFLOW_TELEGRAM_EDIT_GROUPS_MAX` | Telegram: max tracked oversized-message edit groups (LRU); set `0` to disable tracking | `64` |
| `CODEFLOW_TELEGRAM_TRACK_EDIT_GROUPS` | Telegram: enable tracking oversized-message edit groups for `edit()` | `true` |
| `CODEFLOW_SAFE_MODE` | Suppress file previews + command output bodies; stricter redaction | `false` |
| `CODEFLOW_OUTPUT_MODE` | Output verbosity: `minimal|balanced|verbose` | `balanced` |
| `CODEFLOW_STREAM_LOG` | Stream log policy: `full|redacted|off` (default `full`; if `CODEFLOW_SAFE_MODE=true` and unset, default is `redacted`) | `full` |
| `CODEFLOW_ENFORCE_GUARD` | Enforce Codeflow guard precheck in `dev-relay.sh` (`true|false`) | `true` |
| `CODEFLOW_PLATFORM` | Default platform hint for `-P auto` (`discord|telegram|auto`) | — |
| `CODEFLOW_DEFAULT_PLATFORM` | Like `CODEFLOW_PLATFORM`, but takes precedence when both are set | — |
| `CODEFLOW_STATE_FILE` | Override dev-relay state file path | XDG state dir |
| `CODEFLOW_GUARD_FILE` | Override guard state file path | XDG state dir |
| `CODEFLOW_AUDIT_FILE` | Override guard audit log path | XDG state dir |
| `CODEFLOW_DISCORD_ALLOW_MENTIONS` | Allow mentions/pings in Discord payloads (default is deny to prevent `@everyone` spam) | `false` |
| `CODEFLOW_TG_TYPING_ENABLED` | Telegram: send periodic chat actions (`typing`) from `dev-relay.sh` | `true` |
| `CODEFLOW_TG_TYPING_INTERVAL` | Telegram: typing action interval seconds | `4` |
| `TELEGRAM_SILENT` | Telegram: set `disable_notification=true` (`true|false`) | `false` |
| `BRIDGE_CHANNEL_ID` | Channel for bridge to watch (required; fail-closed if unset) | — |
| `BRIDGE_ALLOWED_USERS` | User IDs for bridge (required; fail-closed if unset) | — |

Rate limiting note: structured relay delivery is scheduled by a delivery governor (Telegram: 429 backoff `next_allowed_at = now + retry_after + 1s`, priority queue; compact state cards are strict snapshot overwrite and coalesce in memory during 429 windows). If you still hit rate limits, reduce event volume (`CODEFLOW_OUTPUT_MODE`, `--skip-reads`, `CODEFLOW_SAFE_MODE=true`, Telegram compact mode via `CODEFLOW_COMPACT`).

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Garbled/empty output | Missing PTY | Ensure `unbuffer` installed |
| Agent hangs | Idle beyond threshold | Increase with `-h <sec>` |
| Webhook rate limited | Too many posts | Reduce event volume: `--skip-reads`, `CODEFLOW_SAFE_MODE=true`, avoid huge outputs |
| No Discord messages | Bad webhook URL | Run `test-smoke.sh` |
