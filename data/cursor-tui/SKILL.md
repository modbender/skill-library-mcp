---
name: cursor-tui
description: Spawn and relay Cursor Agent's CLI (`agent` binary) as an interactive passthrough. Use when the user wants to run Cursor Agent in a directory, ask it questions, or send follow-up prompts — acting as a transparent bridge between the user and the agent session.
metadata: {"openclaw":{"requires":{"bins":["cursor","cursor-agent"]}}}
---

# Cursor CLI Passthrough

Spawn Cursor's `agent` in a PTY background session and relay its output and the user's inputs as a silent passthrough.

## Spawning

```json
{ "tool": "exec", "command": "agent", "pty": true, "background": true, "workdir": "<project-dir>", "yieldMs": 3000 }
```

- Always set `workdir` to the project directory the user wants to work in (not the OpenClaw workspace).
- If the user doesn't specify a directory, ask before spawning.
- Note: `agent` requires workspace trust on first run in a directory — relay the trust prompt and send the user's choice (e.g. `a`, `w`, or `q`) via `process send-keys`.

## Relaying output

After spawning or sending input, poll for output:

```json
{ "tool": "process", "action": "poll", "sessionId": "<id>", "timeout": 15000 }
```

- Strip ANSI escape codes mentally, but relay the **content** faithfully and verbatim.
- Do **not** wrap output in code blocks or quote formatting.
- Do **not** add preamble, postamble, interpretation, or commentary — relay exactly what Cursor outputs.
- If you need to add context or a note, prefix that line with your name in brackets (e.g. `[YourName]`) so it's clearly distinguished from Cursor's output.
- **Permission prompts**: When Cursor shows a "Run this command?" or any approval dialog, relay it verbatim to the user and wait for their response. **Never approve or deny on the user's behalf.**
- After relaying the agent's response, append a single prompt line: `cursor @ <workdir>` — use `~` in place of the user's home directory (e.g. `~/repos/myproject` not `/home/username/repos/myproject`).

## Sending user input

For single-line prompts:

```json
{ "tool": "process", "action": "submit", "sessionId": "<id>", "data": "<text>" }
```

For multi-line prompts:

```json
{ "tool": "process", "action": "paste", "sessionId": "<id>", "text": "<text>" }
```

Then submit with Enter:

```json
{ "tool": "process", "action": "send-keys", "sessionId": "<id>", "keys": ["Enter"] }
```

For other special keys (arrow keys, Escape, etc.):

```json
{ "tool": "process", "action": "send-keys", "sessionId": "<id>", "keys": ["ArrowUp"] }
```

Use `@filename` or `@directory/` in interactive prompts to add more context.

## Ending the session

Send `/quit` or `Ctrl+D` (double-press):

```json
{ "tool": "process", "action": "submit", "sessionId": "<id>", "data": "/quit" }
```

## Notes

- `agent` is Cursor's CLI binary. `cursor-agent` is a backward-compatible alias.
- The binary must be on `PATH`. If not found, check `TOOLS.md` for custom binary paths.
- One session at a time is typical; use `process list` to check for orphaned sessions.
