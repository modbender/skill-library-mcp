---
name: auto-reply
description: "Instagram DM auto-reply system. DM monitoring, reading, replying, security check (injection rejection). Use when checking Instagram DMs, reading unread messages, replying to DMs, setting up DM monitoring cron jobs, or handling DM auto-reply workflows. Triggers on: Instagram DM, DM check, DM reply, DM auto-reply, dm-alert."
author: 무펭이 🐧
---

# Instagram DM Auto-Reply 🐧

v2.js (Internal API) based. 0 browser snapshots, CDP cookie extraction → Instagram REST API direct calls.

## Prerequisites

- OpenClaw browser running (port 18800)
- Instagram tab open and logged in
- `ws` npm package (`npm i -g ws` or local)

## Script List

| Script | Purpose |
|--------|---------|
| `scripts/v2.js` | DM CLI (inbox, unread, check, read, reply) |
| `scripts/auto-reply.js` | Read dm-alert.json, security check, return reply metadata |
| `scripts/check-notify.js` | Check new DM notifications (for cron, state file based) |
| `scripts/dm-watcher.js` | Real-time DM detection daemon (15s polling) |

## Core Workflows

### 1. Check DMs

```bash
node scripts/v2.js check        # unread count (lightest)
node scripts/v2.js unread       # unread DM list
node scripts/v2.js inbox        # full DM list
```

### 2. Read Messages

```bash
node scripts/v2.js read "<username>" -l 5
```

### 3. Reply

```bash
node scripts/v2.js reply "<username>" "message content"
```

On API failure, returns JSON with `method: "use_browser"` + `threadUrl` → fallback to browser tool.

### 4. Notification Check (cron integration)

```bash
node scripts/check-notify.js
```
- If new DMs: outputs `📩 새 DM N건: ...`
- If none: outputs `no_new`
- Uses state file `dm-state.json` to prevent duplicates

### 5. Auto-Reply Flow

```bash
node scripts/auto-reply.js
```

1. Read `dm-alert.json` (created by dm-watcher)
2. Run security check on each DM
3. Return results: `needs_reply` / `security_alert` / `skipped`
4. AI generates replies for `needs_reply` DMs → send via `v2.js reply`

### 6. Real-time Detection Daemon

```bash
node scripts/dm-watcher.js              # detection only
node scripts/dm-watcher.js --auto-reply  # includes Discord notification
```

Polls `v2.js check` every 15s. On new DM detection, writes `dm-alert.json` + Discord DM notification.

## Security Check (Injection Rejection)

`auto-reply.js`'s `SECURITY_PATTERNS` detects:

- **Prompt Injection**: "ignore previous", "system prompt", "you are now", "act as", "pretend"
- **Jailbreak Attempts**: "override", "jailbreak", "DAN mode", "bypass"
- **Sensitive Info Requests**: "secret key", "private key", "seed phrase", "wallet address"
- **Code Execution Attempts**: "execute command", "run script", "eval(", "rm -rf", "sudo"
- **Social Engineering**: "simulation mode", zero-width characters

On threat detection → don't reply, return `security_alert`. Separate notification sent.

## Cron Setup Example

```yaml
# Check DMs every 5 minutes
- schedule: "*/5 * * * *"
  command: "node /path/to/scripts/check-notify.js"
  systemEvent: true

# Or dm-watcher daemon for continuous monitoring
- schedule: "@reboot"
  command: "node /path/to/scripts/dm-watcher.js --auto-reply"
  background: true
```

## Token Efficiency

- inbox/check: exec 1 call (~500 tokens)
- reply: exec 1 call (~200 tokens)
- browser snapshots: 0

---
> 🐧 Built by **무펭이** — [Mupengism](https://github.com/mupeng) ecosystem skill
