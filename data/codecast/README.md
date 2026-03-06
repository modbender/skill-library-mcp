# Dev Session Relay

Streams coding agent (Claude Code, Codex, Gemini CLI, etc.) sessions to Discord #dev-session, enabling interactive pair programming.

## Phase 1: Nexus-Orchestrated (Current)

Nexus spawns the coding agent via `exec pty:true background:true`, polls output via `process:log`, and relays to #dev-session via `message` tool. Allan's messages in #dev-session are forwarded to the agent via `process:submit`.

### Protocol

1. **Start:** Nexus posts session header to #dev-session (command, workdir, agent)
2. **Stream:** Poll `process:log` every ~10s, post new output chunks (batched, ANSI stripped)
3. **Input:** Allan's messages in #dev-session during active session → `process:submit`
4. **Hang detection:** No output for 120s → post warning
5. **Completion:** Post exit code + summary
6. **Kill:** Allan says `!kill` → `process:kill`

### Commands (Allan types in #dev-session)

- Any text → forwarded to agent stdin
- `!kill` → kill the agent process
- `!status` → show session status (runtime, last output)
- `!log` or `!log 50` → show last N lines of output

## Phase 2: Standalone (Future)

Requires Discord webhook URL. Script spawns agent, tails output, posts via webhook, listens for input via Discord gateway.

## Location

- Protocol docs: this file + TOOLS.md
- Helper: `relay.sh` (ANSI stripping, output batching)
- Project: `~/projects/dev-session-relay/`
