---
name: bullybuddy
description: >
  BullyBuddy — Claude Code session manager CLI wrapper. Spawn, list, send input,
  kill, and monitor multiple Claude Code sessions via /bullybuddy slash command.
  Reads auth token from ~/.bullybuddy/connection.json automatically.
user-invocable: true
command-dispatch: tool
command-tool: exec
command-arg-mode: raw
metadata:
  openclaw:
    emoji: "🦞"
    homepage: "https://github.com/ChenKuanSun/openclaw-bullybuddy"
    requires:
      bins:
        - bullybuddy
        - jq
        - curl
      config:
        - "~/.bullybuddy/connection.json"
    install:
      - id: node
        kind: node
        package: openclaw-bullybuddy
        bins:
          - bullybuddy
---

# BullyBuddy

Spawns and manages multiple Claude Code CLI sessions. Dual backend: **tmux** (default, sessions survive server restart) or **node-pty** (fallback). REST API, WebSocket streaming, web dashboard.

## Setup

1. Install the package globally:

```bash
npm install -g openclaw-bullybuddy
```

2. Start the server:

```bash
bullybuddy server
```

Connection info is auto-saved to `~/.bullybuddy/connection.json` on startup. The `/bullybuddy` command reads it automatically — no env vars needed.

For remote access, start with `bullybuddy server --tunnel`. The tunnel URL is available via `/bullybuddy url`.

## /bullybuddy Slash Command

```
/bullybuddy status          - Server status & session summary
/bullybuddy list            - List all sessions
/bullybuddy spawn [cwd] [task] [group] - Create new session
/bullybuddy send <id> <text> - Send input to session
/bullybuddy output <id> [lines] - Show session output/transcript
/bullybuddy kill <id>       - Terminate session
/bullybuddy url             - Show dashboard URL (local + tunnel)
/bullybuddy audit [limit]   - View audit log
/bullybuddy transcript <id> [limit] - View conversation transcript
/bullybuddy help            - Show help
```

## Security Notice

- The auth token grants **full control over all spawned Claude Code sessions**, including sending arbitrary input. Treat it as a secret.
- The `/bullybuddy url` command outputs the dashboard URL with the token embedded. Do not share or log this URL publicly.
- When using `--tunnel`, the dashboard and API are exposed to the internet via a Cloudflare temporary URL. Anyone with the token can access all sessions remotely.
- Spawned sessions run Claude Code with your local permissions. If `--dangerously-skip-permissions` is enabled, Claude can execute any command without confirmation.

## Authentication

A random token is generated on each server start and saved to `~/.bullybuddy/connection.json` (mode 0600). CLI and `/bullybuddy` auto-discover it. For the dashboard, the token is included in the URL printed on startup. The connection file is deleted on graceful shutdown.

## API Overview

All endpoints require the token via `Authorization: Bearer <token>` header or `?token=` query parameter. All responses follow `{ ok: boolean, data?: T, error?: string }`.

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/health` | Server status |
| `GET` | `/api/sessions` | List sessions (filter by group) |
| `POST` | `/api/sessions` | Spawn session |
| `GET` | `/api/sessions/:id` | Session detail with metrics |
| `DELETE` | `/api/sessions/:id` | Kill session |
| `POST` | `/api/sessions/:id/input` | Send input to PTY |
| `POST` | `/api/sessions/:id/resize` | Resize PTY |
| `POST` | `/api/sessions/:id/task` | Set task metadata |
| `POST` | `/api/sessions/:id/mute` | Mute notifications |
| `POST` | `/api/sessions/:id/unmute` | Unmute notifications |
| `GET` | `/api/groups` | Groups with session counts |
| `GET` | `/api/summary` | Aggregate state counts and groups |
| `GET` | `/api/browse` | Browse directories (disabled by default) |
| `GET` | `/api/audit` | Audit log |
| `GET` | `/api/sessions/:id/transcript` | Conversation transcript |

### Spawn Request Body

```json
{
  "name": "worker-1",
  "group": "myproject",
  "cwd": "/path/to/repo",
  "task": "Implement feature X",
  "args": ["--verbose"],
  "cols": 120,
  "rows": 40,
  "skipPermissions": false
}
```

All fields optional. When `task` is provided, it is automatically sent as input when Claude reaches the idle prompt.

**Note:** When sending input, terminate with `\r` (carriage return), not `\n`.

## WebSocket Protocol

Connect to `ws://<host>:<port>/ws?token=<token>`.

### Client Messages

| type | fields | description |
|------|--------|-------------|
| `subscribe` | `sessionId`, `cols?`, `rows?` | Receive output from session |
| `unsubscribe` | `sessionId` | Stop receiving output |
| `input` | `sessionId`, `data` | Send keystrokes to PTY |
| `resize` | `sessionId`, `cols`, `rows` | Resize PTY |

### Server Messages

| type | fields | description |
|------|--------|-------------|
| `sessions` | `sessions[]` | Full session list (on connect) |
| `output` | `sessionId`, `data` | Terminal output chunk |
| `scrollback` | `sessionId`, `data` | Buffered scrollback on subscribe |
| `session:created` | `session` | New session spawned |
| `session:exited` | `sessionId`, `exitCode` | Session terminated |
| `session:stateChanged` | `sessionId`, `detailedState` | State transition |
| `error` | `message` | Error (e.g. invalid message) |

## State Detection

BullyBuddy analyzes raw PTY output to detect Claude Code's state in real-time.

| `detailedState` | Meaning |
|-----------------|---------|
| `starting` | Session just spawned, Claude loading |
| `working` | Claude is thinking/editing (spinner visible) |
| `permission_needed` | Claude waiting for user approval |
| `idle` | Claude at prompt, ready for input |
| `compacting` | Compacting conversation history |
| `error` | Error detected in output |

State transitions are broadcast via WebSocket and reflected in `GET /api/summary`.

## OpenClaw Integration

Poll `GET /api/summary` on an interval to check fleet status. The `sessionsNeedingAttention` field contains IDs of sessions in `permission_needed` or `error` state.

## Remote Access

Start the server with `--tunnel` to create a Cloudflare temporary URL automatically:

```bash
bullybuddy server --tunnel
```

The tunnel URL is printed on startup and saved to `~/.bullybuddy/connection.json`. Use `bullybuddy url` or `/bullybuddy url` to retrieve it anytime.

## CLI Commands

```bash
bullybuddy server                          # Start server
bullybuddy server --tunnel                 # Start with Cloudflare tunnel
bullybuddy url                             # Show dashboard URL (local + tunnel)
bullybuddy spawn --name worker --group proj  # Spawn session
bullybuddy list --json                     # List sessions
bullybuddy send <id> "Fix the bug"         # Send input
bullybuddy attach <id>                     # Interactive terminal
bullybuddy kill <id>                       # Kill session
bullybuddy groups                          # List groups
bullybuddy open                            # Open dashboard
```

## Script

When invoked, run:
```bash
{baseDir}/scripts/bullybuddy.sh $ARGUMENTS
```
