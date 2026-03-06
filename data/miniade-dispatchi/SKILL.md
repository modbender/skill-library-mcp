---
name: dispatchi
description: Launch non-blocking interactive Claude Code tasks for slash-only plugins like ralph-loop. Use when a task needs interactive slash commands and completion callback routing.
---

Run `{baseDir}/scripts/run_dispatchi.sh` with user args.

## Contract

- Format: `/dispatchi <project> <task-name> <prompt...>`
- Workdir mapping: `${REPOS_ROOT:-/home/miniade/repos}/<project>`
- Defaults: `max-iterations=20`, `completion-promise=COMPLETE`
- Auto-exit: when completion promise appears on its own line, wrapper requests `/exit` and closes tmux session.

## Local config

- optional env file: `${OPENCLAW_DISPATCH_ENV:-<workspace>/skills/dispatch.env.local}`
- supports OpenClaw `skills.entries.dispatchi.env` injection
- script is self-contained (bundled `claude_code_run.py`)

## Security disclosure

- Reads only allowlisted env keys from `dispatch.env.local` using key=value parsing (no `source`).
- Launches local tmux session and local Claude process; writes output to configured result paths.
- Network callback is **disabled by default**; enable only with `ENABLE_CALLBACK=1` and explicit group settings.
- No runtime download of external code.

## Behavior

1. Validate args and return usage if incomplete.
2. Start interactive dispatch in background (non-blocking).
3. Verify tmux session exists before returning started.
4. Use `/cancel <run-id>` to stop a running loop.
