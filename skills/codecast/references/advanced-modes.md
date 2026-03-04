# Advanced Modes

## PR Review Mode

Review a pull request with a coding agent and stream the review to Discord:

```bash
bash {baseDir}/scripts/dev-relay.sh --review https://github.com/owner/repo/pull/123
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
bash {baseDir}/scripts/dev-relay.sh --review https://github.com/owner/repo/pull/123

# Review with Codex, post comment, in a thread
bash {baseDir}/scripts/dev-relay.sh --thread --review https://github.com/owner/repo/pull/123 -- -a codex -c

# Custom review prompt
bash {baseDir}/scripts/dev-relay.sh --review https://github.com/owner/repo/pull/123 -- -p "Focus on security vulnerabilities"
```

## Parallel Tasks Mode

Run multiple codecast sessions concurrently:

```bash
bash {baseDir}/scripts/dev-relay.sh --parallel tasks.txt
```

**Tasks file format** (one task per line: `directory | prompt`):
```
~/projects/api | Build user authentication endpoint
~/projects/web | Add dark mode toggle to settings page
```

Each task gets its own Discord thread, relay directory, and session.

**Options:**

| Flag | Description | Default |
|------|------------|---------|
| `-a <agent>` | Agent (claude, codex) | claude |
| `--worktree` | Use git worktrees | Off |
| `-r <n>` | Rate limit per task | 25 |
| `-t <sec>` | Timeout per task | 1800 |

## Discord Bridge (Interactive)

Run a companion process that forwards Discord messages to active agent sessions:

```bash
python3 {baseDir}/scripts/discord-bridge.py --channel CHANNEL_ID --users USER_ID1,USER_ID2
```

**Commands from Discord:**

| Command | Description |
|---------|------------|
| `!status` | Show active sessions |
| `!kill <PID>` | Kill a session |
| `!log [PID]` | Show recent output |
| `!send [PID] <msg>` | Forward to agent stdin |
| *(plain text)* | Auto-forwarded if one session active |

**Requires:** `websocket-client` (`pip install websocket-client`) and a Discord bot token.

## Session Resume

Replay a previous session's events:
```bash
bash {baseDir}/scripts/dev-relay.sh --resume /tmp/dev-relay.XXXXXX
```

## Codex Structured Output

Codex CLI supports `--json` for JSONL events. Auto-detected by parse-stream.py:
```bash
bash {baseDir}/scripts/dev-relay.sh -w ~/projects/myapp -- codex exec --json --full-auto 'Fix test failures'
```
