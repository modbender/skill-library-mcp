---
name: dispatch
description: Launch non-blocking Claude Code headless tasks from slash command dispatch. Use when user requests async coding jobs and does not require slash-only Claude plugins.
---

Run `{baseDir}/scripts/run_dispatch.sh` with user args.

## Contract

- Format: `/dispatch <project> <task-name> <prompt...>`
- Workdir mapping: `${REPOS_ROOT:-/home/miniade/repos}/<project>`
- Agent Teams policy: on-demand (enabled only if prompt contains Agent Team signals)
- Safety: headless runs enforce timeout via `DISPATCH_TIMEOUT_SEC` (default 7200s)

## Local config

- optional env file: `${OPENCLAW_DISPATCH_ENV:-<workspace>/skills/dispatch.env.local}`
- supports OpenClaw `skills.entries.dispatch.env` injection
- script is self-contained (bundled `dispatch.sh` + `claude_code_run.py`)

## Security disclosure

- Reads only allowlisted env keys from `dispatch.env.local` using key=value parsing (no `source`).
- Starts a background local process (`nohup`) and writes logs/results under configured paths.
- Network callback is **disabled by default**; enable only with `ENABLE_CALLBACK=1` and explicit group settings.
- Does not download remote code at runtime.

## Behavior

1. Validate args and return usage if incomplete.
2. Start task in background (non-blocking).
3. Return one-line launch summary with run-id and log path.
4. Do not run extra validation unless requested.
