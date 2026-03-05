# What Discord Sees

## Claude Code (stream-json)
- ⚙️ Model info and permission mode
- 📝 File writes with line count and smart content preview
- ✏️ File edits
- 🖥️ Bash commands
- 📤 Bash command output (truncated to 800 chars)
- 👁️ File reads (hide with `--skip-reads`)
- 🔍 Web searches
- 💬 Assistant messages
- ✅/❌ Completion summary with turns, duration, cost, and session stats

## Codex (--json)
- ⚙️ Session thread ID
- 🖥️ Command executions
- 📤 Command output (truncated)
- 📝 File creates / ✏️ File modifications
- 🧠 Reasoning traces
- 🔍 Web searches / 🔧 MCP tool calls / 📋 Plan updates
- 💬 Agent messages
- 📊 Token usage per turn
- ✅ Session summary with cost and stats

## Other agents (raw mode)
- Output in code blocks with ANSI stripping
- Hang detection warnings
- Completion/error status

## End Summary
Every session ends with: files created/edited, bash commands run, tool usage breakdown, total cost.

## Architecture

```
scripts/
├── dev-relay.sh          # Shell entry point, process management
├── parse-stream.py       # Multi-agent JSON stream parser
├── review-pr.sh          # PR review mode (--review)
├── parallel-tasks.sh     # Parallel worktree tasks (--parallel)
├── discord-bridge.py     # Discord → stdin bridge
├── codecast-watch.sh     # PID watcher for completion detection
├── test-smoke.sh         # Pre-flight validation
├── .webhook-url          # Discord webhook URL (gitignored)
└── platforms/
    ├── __init__.py       # Platform adapter loader
    └── discord.py        # Discord webhook + thread support
```

## Environment Variables

| Variable | Description | Default |
|----------|------------|---------|
| `CODECAST_BOT_TOKEN` | Discord bot token for --thread and bridge | `.bot-token` file |
| `CODECAST_RATE_LIMIT` | Max posts per 60s | `25` |
| `BRIDGE_CHANNEL_ID` | Channel for bridge to watch | All |
| `BRIDGE_ALLOWED_USERS` | User IDs for bridge | All |

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Garbled/empty output | Missing PTY | Ensure `unbuffer` installed |
| Agent hangs | Idle beyond threshold | Increase with `-h <sec>` |
| Webhook rate limited | Too many posts | Auto-batched; lower with `-r 15` |
| No Discord messages | Bad webhook URL | Run `test-smoke.sh` |
