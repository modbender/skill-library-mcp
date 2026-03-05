---
name: pubblue
description: >-
  Publish files or generated content via the pubblue CLI, and go live for
  interactive P2P browser communication.
license: MIT
compatibility: Requires Node.js 18+ with npm/pnpm/npx.
metadata:
  author: pub.blue
  version: "5.0.0"
allowed-tools: Bash(pubblue:*) Bash(npx pubblue:*) Bash(node:*) Read Write
---

# pubblue

Use this skill when the user asks about `pubblue`, `pub.blue`, publishing content, or going live/canvas chat.

## Required CLI Version

Use **pubblue CLI 0.6.0+**.

```bash
pubblue --version
npm i -g pubblue@latest
```

## Setup

```bash
# One-time auth
pubblue configure --api-key pub_KEY
# or
echo "pub_KEY" | pubblue configure --api-key-stdin
```

Key source: <https://pub.blue/dashboard>
Config path: `~/.config/pubblue/config.json`
Env override: `PUBBLUE_API_KEY`

Optional OpenClaw bridge config (saved in CLI config):
```bash
pubblue configure --set bridge.mode=openclaw
pubblue configure --set openclaw.path=/app/dist/index.js
pubblue configure --set openclaw.sessionId=<session-id>
# or:
pubblue configure --set openclaw.threadId=<thread-id>
pubblue configure --set openclaw.canvasReminderEvery=10
pubblue configure --show
```

## Core Publish Commands

```bash
pubblue create page.html
pubblue create --slug demo --title "Demo" --public page.html
cat notes.md | pubblue create

pubblue get <slug>
pubblue get <slug> --content

pubblue update <slug> --file next.html
pubblue update <slug> --title "New title" --public

pubblue list
pubblue delete <slug>
```

Notes:
- Pubs are **private by default**.
- `create` supports `--public/--private`, `--title`, `--slug`, `--expires`.
- `update` supports `--file`, `--title`, `--public/--private`, `--slug`.
- Content is optional — a pub can be interactive-only.

## Going Live (Interactive Flow)

Live is browser-initiated. The daemon registers agent presence; the browser creates the WebRTC offer when the pub owner clicks "Go Live".

1. Start the agent daemon (registers presence, no slug needed):
```bash
pubblue start --agent-name "Oz"
```

Optional explicit bridge selector:
```bash
pubblue start --agent-name "Oz" --bridge openclaw
pubblue start --agent-name "Oz" --bridge none --foreground
```

`--agent-name` is the display name shown to the browser user (required).

Behavior:
- `start` runs a per-user daemon + managed bridge in background.
- `--foreground` keeps process attached to current shell (no managed bridge).
- The daemon polls for incoming live requests from any of the user's pubs.

2. Check daemon status:
```bash
pubblue status
```

3. Send content (slug resolved automatically via daemon):
```bash
pubblue write "Hello"
pubblue write -c canvas -f /tmp/view.html
```

4. Read incoming (manual/debug mode):
```bash
pubblue read --follow -c chat
pubblue read --all              # read from all channels
```

5. Stop the daemon:
```bash
pubblue stop
```

6. Validate live end-to-end (strict):
```bash
pubblue doctor
# optional handshake:
pubblue doctor --wait-pong --timeout 30
# skip specific channels:
pubblue doctor --skip-chat --skip-canvas
```

Important:
- `write` uses delivery confirmation; failures should be retried.
- `read` is consumptive. Do not run multiple `read --follow` consumers on the same channel.
- The browser initiates the live connection; the daemon responds automatically.

## Bridge Modes

`pubblue start` supports:
- `--bridge openclaw` (default): managed local bridge process (OpenClaw session delivery)
- `--bridge none`: no managed bridge; use manual polling or external integration

Useful env for `openclaw` mode:
- `OPENCLAW_SESSION_ID` or `OPENCLAW_THREAD_ID` (recommended for deterministic routing)
- `OPENCLAW_PATH` (explicit OpenClaw binary/index.js path, if auto-discovery fails)
- `OPENCLAW_DELIVER=1` (optional, enables OpenClaw `--deliver`)
- `OPENCLAW_DELIVER_CHANNEL`, `OPENCLAW_REPLY_TO` (optional channel routing)
- `OPENCLAW_DELIVER_TIMEOUT_MS` (optional dispatch timeout)
- `OPENCLAW_CANVAS_REMINDER_EVERY` (optional, default `10`)

## Telegram Mini App

pub.blue supports Telegram Mini App. When configured, `create`
automatically outputs `t.me` deep links. Check `pubblue configure --show` for status.

## Troubleshooting

- `Rate limit exceeded`:
  - Read and respect retry hints.
- `No browser connected`:
  - Ask user to open pub URL and click "Go Live", then wait for connection.
- `Agent offline`:
  - Make sure `pubblue start` is running. Check `pubblue status`.
- `Session not found or expired`:
  - Check `pubblue status` and daemon log path.
  - Restart with `pubblue stop && pubblue start`.
- Bridge errors:
  - Use `pubblue status` and inspect bridge state/log path.
