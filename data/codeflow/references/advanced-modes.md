# Advanced Modes

## PR Review Mode

Review a pull request with a coding agent and stream the review to Discord:

```bash
bash {baseDir}/scripts/codeflow review https://github.com/owner/repo/pull/123
```

This will:
1. Clone the repo to a temp directory
2. Checkout the PR branch
3. Run a coding agent with a review prompt
4. Stream the review to Discord as usual
5. Optionally post the review as a `gh pr comment`

**Options:**

| Flag | Description | Default |
|------|------------|---------|
| `-a <agent>` | Agent to use (claude, codex) | claude |
| `-p <prompt>` | Custom review prompt | Standard code review |
| `-c` | Post review as `gh pr comment` | Off |

**Examples:**
```bash
# Review with default Claude Code agent
bash {baseDir}/scripts/codeflow review https://github.com/owner/repo/pull/123

# Review with Codex, post comment, in a thread
bash {baseDir}/scripts/codeflow review --thread -a codex -c https://github.com/owner/repo/pull/123

# Custom review prompt
bash {baseDir}/scripts/codeflow review -p "Focus on security vulnerabilities" https://github.com/owner/repo/pull/123
```

## Parallel Tasks Mode

Run multiple Codeflow sessions concurrently:

```bash
bash {baseDir}/scripts/codeflow parallel tasks.txt
```

**Tasks file format** (one task per line: `directory | prompt`):
```
~/projects/api | Build user authentication endpoint
~/projects/web | Add dark mode toggle to settings page
```

Notes:
- Lines starting with `#` (after optional leading whitespace) are ignored.
- Empty lines are ignored.
- Fields support surrounding single/double quotes to preserve spaces (quotes are stripped).

Each task gets its own Discord thread, relay directory, and session.

**Options:**

| Flag | Description | Default |
|------|------------|---------|
| `-a <agent>` | Agent (claude, codex) | claude |
| `--worktree` | Use git worktrees | Off |
| `-t <sec>` | Timeout per task | 1800 |

Note: structured relay delivery is scheduled by an in-process delivery governor (Telegram: 429 backoff `next_allowed_at = now + retry_after + 1s`, priority queue; compact state cards are strict snapshot overwrite and coalesce in memory during 429 windows). Raw mode remains best-effort; if you still hit platform rate limits, reduce event volume (`CODEFLOW_OUTPUT_MODE`, `--skip-reads`, `CODEFLOW_SAFE_MODE=true`, Telegram `CODEFLOW_COMPACT`).

## Discord Bridge (Read-only)

Run a companion process that connects to the Discord gateway and exposes lightweight **read-only** session introspection commands.

```bash
bash {baseDir}/scripts/codeflow bridge --channel CHANNEL_ID --users USER_ID1,USER_ID2
```

**Commands from Discord:**

| Command | Description |
|---------|------------|
| `!status` | Show active sessions |
| `!log [PID]` | Show recent stream event types |

**Notes:**
- This bridge does **not** forward messages to agent stdin and does **not** implement remote `!kill` (by design).
- Fail-closed by default: if `--channel`/`--users` (or env) are not both configured, commands are refused.
- Always scope it to a channel + allowlist (`--channel` + `--users`) to avoid exposing session metadata broadly.
- `CODEFLOW_SAFE_MODE=true` enables stricter redaction across Codeflow.

**Requires:** `websocket-client` (`pip install websocket-client`) and a Discord bot token.

## Session Resume

Replay a previous session's events:
```bash
bash {baseDir}/scripts/codeflow resume /tmp/dev-relay.XXXXXX
```

Notes:
- Resume uses `stream.jsonl`.
- If `CODEFLOW_SAFE_MODE=true` and `CODEFLOW_STREAM_LOG` is unset, the stream log defaults to `redacted` (replay works, but sensitive fields are redacted).
- If `CODEFLOW_STREAM_LOG=off`, the log contains minimal metadata only (limited replay detail).

## Codex Structured Output

Codex CLI supports `--json` for JSONL events. Auto-detected by parse-stream.py:
```bash
bash {baseDir}/scripts/codeflow run -w ~/projects/myapp -- codex exec --json --full-auto 'Fix test failures'
```

Notes:
- Resume/replay uses `stream.jsonl`. Delivery stats are written to `delivery-summary.json`. No additional log files are written by the relay.

## Guard Audit Privacy

Guard audit records (default: `${XDG_STATE_HOME:-$HOME/.local/state}/codeflow/guard-audit.jsonl`) store `commandHint` only (redacted + truncated). Full command lines are never persisted.
