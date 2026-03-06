---
name: claude-relay
description: Relay operator for Claude Code via tmux across multiple projects. Use when the user wants to start/continue a Claude Code terminal session, send prompts, read output, or manage background Claude sessions by project name/path.
metadata: {"openclaw":{"emoji":"🔄","requires":{"bins":["tmux","claude"]}}}
---

# Claude Relay

Operate Claude Code as a persistent terminal copilot through tmux.

## Script

All actions go through `scripts/relay.sh`. Run with no args for usage help.

```bash
scripts/relay.sh <action> [project] [args...]
```

**Actions**: `start`, `send`, `tail`, `stop`, `status`, `session`

## Workflow

1. Start session: `scripts/relay.sh start <project>`
2. Send instruction: `scripts/relay.sh send <project> "<text>"`
3. Read output: `scripts/relay.sh tail <project> [lines]`
4. Repeat send/tail as needed.
5. Stop when done: `scripts/relay.sh stop <project>`

## Project resolution

The script resolves `<project>` in order:

1. Absolute path (if directory exists)
2. Alias from `projects.map` (`name=/abs/path`)
3. `$CLAUDE_RELAY_ROOT/<name>` exact match
4. Find under `$CLAUDE_RELAY_ROOT` (maxdepth=2) by folder name
5. If omitted, re-use last project

Multiple matches → script exits with candidates; ask user to clarify.

## Session naming

Deterministic: `cc_<basename_sanitized>`. One project = one tmux session.

## Error handling

- **tmux not installed**: script exits with code 2 and "missing dependency" message.
- **Claude binary not found**: same exit code 2. Verify `CLAUDE_BIN` env or default path.
- **Session not running** (send/tail on stopped session): exits code 6. Start first.
- **Project not found**: exits code 4. Check `projects.map` or project path.
- **Claude process hung**: `tail` still works — check output. If stuck, `stop` and `start` fresh.

## Environment variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAUDE_RELAY_ROOT` | `$HOME/projects` | Root directory for project discovery |
| `CLAUDE_RELAY_MAP` | `<skill-dir>/projects.map` | Path to project alias map file |
| `CLAUDE_BIN` | `claude` (from PATH) | Path to Claude Code CLI binary |
| `RELAY_WAIT` | `6` | Seconds to wait after send before tailing output |

## Setup

1. Install this skill
2. Create a `projects.map` file in the skill directory (see `projects.map.example`)
3. Ensure `tmux` and `claude` are installed and in your PATH

## Notes

- Transport-focused skill (relay/orchestration), not deep code reasoning.
