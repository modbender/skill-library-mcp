# HeySummon Provider Skill

Receive and respond to help requests from AI agents via the [HeySummon](https://heysummon.ai) platform.

## What is this?

When an AI agent gets stuck, it can send a help request through HeySummon. As a **provider**, you receive these requests as notifications and can respond directly from your messaging app (e.g. Telegram).

## Architecture

```
AI Agent → HeySummon Platform → SSE Event Stream → Provider Watcher → Notification (Telegram/etc)
      ←       Platform API       ←  Reply Script  ←  Your response
```

All communication flows through the HeySummon platform. The watcher connects to the platform's SSE endpoint (`/api/v1/events/stream`) — never directly to any internal message bus.

## Setup

### 1. Create `.env`

Copy `.env.example` and fill in your values:

```bash
cp .env.example .env
```

| Variable | Required | Description |
|---|---|---|
| `HEYSUMMON_BASE_URL` | ✅ | Platform URL (e.g. `https://cloud.heysummon.ai`) |
| `HEYSUMMON_API_KEY` | ✅ | Your provider key (`hs_prov_...`) from the dashboard |
| `HEYSUMMON_NOTIFY_TARGET` | ✅ | Chat ID for notifications (e.g. Telegram chat ID) |

### 2. Start the watcher

```bash
bash scripts/setup.sh
```

This starts a persistent SSE listener (via pm2 or nohup) that sends you a notification whenever an AI agent requests help.

### 3. Stop the watcher

```bash
bash scripts/teardown.sh
```

## Scripts

| Script | Description |
|---|---|
| `scripts/setup.sh` | Start the event watcher (pm2 or nohup) |
| `scripts/teardown.sh` | Stop the event watcher |
| `scripts/mercure-watcher.sh` | SSE listener — connects to platform, sends notifications via OpenClaw |
| `scripts/reply-handler.sh` | Reply to a request by refCode: `reply-handler.sh HS-XXXX "your answer"` |
| `scripts/respond.sh` | Reply by request ID: `respond.sh <requestId> "your answer"` |

## How replies work

When you receive a 🦞 notification, reply directly to it. Your AI assistant (e.g. OpenClaw) will parse the refCode from the quoted message and call `reply-handler.sh` automatically.

Manual reply:
```bash
bash scripts/reply-handler.sh "HS-XXXX" "Here's the answer to your question"
```

## Security

- **No keys in code** — all credentials are in `.env` (gitignored)
- **No direct infrastructure access** — all communication via platform API
- **Provider key validation** — scripts reject non-provider keys
- **Encryption** — handled server-side by the platform
- **IP binding** — the platform auto-binds client keys to their first IP
- **Event deduplication** — watcher tracks seen events to prevent duplicate notifications

## Files (gitignored)

These files are created at runtime and excluded from version control:

| File | Purpose |
|---|---|
| `.env` | Your credentials |
| `providers.json` | Cached provider names (auto-populated) |
| `seen-events.txt` | Deduplication tracking for the watcher |
| `*.jsonl` | Event logs |

## Requirements

- Node.js (for JSON parsing in scripts)
- `curl`, `jq`
- pm2 (recommended) or nohup
- OpenClaw (for notification delivery)
