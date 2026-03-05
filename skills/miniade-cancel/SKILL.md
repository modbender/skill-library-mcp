---
name: cancel
description: Cancel an active interactive dispatch run by run-id from slash command cancel. Use when user wants to stop a dispatchi or ralph-loop task immediately.
---

Run `{baseDir}/scripts/run_cancel.sh` with user args.

## Contract

- Format: `/cancel <run-id>`
- Also supports: `/cancel <project>/<run-id>`

## Local config

- optional env file: `${OPENCLAW_DISPATCH_ENV:-<workspace>/skills/dispatch.env.local}`
- supports OpenClaw `skills.entries.cancel.env` injection
- script is self-contained

## Security disclosure

- Reads only allowlisted env keys from `dispatch.env.local` using key=value parsing (no `source`).
- Sends tmux keystrokes only to the run session resolved from local metadata.
- Updates local run metadata (`status=cancelled`, `exit_code=130`).

## Behavior

1. Resolve run-id to exactly one result directory.
2. Send `/ralph-loop:cancel-ralph` to that tmux session.
3. Perform hard-cancel by requesting `/exit` and killing tmux session.
4. Return success or precise error.
