# Cerebro Setup Guide

This guide walks you through setting up **Project Cerebro** — an autonomous AI brain control center.

## Prerequisites

1. **OpenClaw** installed and running (`openclaw status`)
2. **Node.js** v18+ (`node --version`)
3. **A messaging channel in OpenClaw** (Discord/Telegram/Signal/etc.)
4. Optional: **Google Calendar access** via `gog` CLI (for calendar-based planning)

## Installation

### 1. Clone & Install

```bash
git clone https://github.com/YOUR_USERNAME/project-cerebro.git
cd project-cerebro
npm install
cd frontend && npm install && npm run build && cd ..
```

### 2. Configure Environment

Copy the example `.env` file:

```bash
cp .env.example .env
```

Edit `.env` and set:

**Required:**
```bash
OPENCLAW_GATEWAY_URL=ws://127.0.0.1:18789
OPENCLAW_TOKEN=YOUR_GATEWAY_TOKEN  # Get from: openclaw devices list
# Messaging is handled by OpenClaw. Ensure your desired channel plugin is configured in OpenClaw.
```

**Optional (calendar integration / merged schedule context):**

Cerebro can optionally inject a merged calendar view into certain planning/report tasks.
This uses the `gog` CLI under the hood (Google Calendar via your OpenClaw environment).

1) Ensure `gog` is authenticated for the account you want to use.
2) Set these env vars:

```bash
# Which Google account gog should use (email address)
GOG_ACCOUNT=you@example.com

# Comma-separated calendar IDs to merge.
# "primary" is your main calendar; additional calendars are long IDs from Google Calendar settings.
CEREBRO_CALENDAR_IDS=primary,OTHER_CALENDAR_ID

# Optional friendly names (same order as IDs). Only used for display.
CEREBRO_CALENDAR_NAMES=Primary,Classes

# Optional override (otherwise uses TZ)
CEREBRO_TIMEZONE=America/Chicago
```

Notes:
- No calendar IDs are shipped in the repo; you provide them locally via `.env`.
- If you don’t set these, Cerebro still works; you just won’t get schedule context injected.

### 3. Configure Brains & Channels

Copy template config files:

```bash
cp config/brains.template.json config/brains.json
cp config/brain_targets.template.json config/brain_targets.json

# Optional (Job module only)
# If you want the Job Applications tracker + Job Profile page, opt in by:
# 1) Adding the Job brain to config/brains.json (see config/brains.jobs.addon.template.json)
# 2) Adding a job destination to config/brain_targets.json
# 3) Creating a local job profile file:
cp data/job_profile.template.json data/job_profile.json
```

Edit `config/brain_targets.json` to choose where each brain sends notifications.
Example (Discord):

```json
{
  "brains": {
    "nexus":   { "channel": "discord", "target": "YOUR_GENERAL_CHANNEL_ID" },
    "personal":{ "channel": "discord", "target": "YOUR_PERSONAL_CHANNEL_ID" }
  }
}
```

Example (Telegram):

```json
{
  "brains": {
    "nexus":   { "channel": "telegram", "target": "@your_chat_or_channel" }
  }
}
```

You can customize brain definitions in `config/brains.json` (name, description, openClawAgentId), but the defaults work out of the box.

### 4. Build & Run

```bash
npm run build

# Optional: seed example tasks/recurring tasks (safe: skips if DB already has data)
npm run seed

npm start
```

Or run as a systemd service (see `project-cerebro.service`).

## Dashboard

Navigate to: `http://localhost:3030`

## Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `PORT` | No | `3030` | Dashboard HTTP port |
| `DB_PATH` | No | `./cerebro.db` | SQLite database path |
| `OPENCLAW_GATEWAY_URL` | **Yes** | — | OpenClaw Gateway WebSocket URL |
| `OPENCLAW_TOKEN` | **Yes** | — | OpenClaw Gateway auth token |
| (messaging) | — | — | Configure your messaging channels in OpenClaw |
| `TZ` | No | `America/Chicago` | Timezone for scheduling (fallback for calendar merge) |
| `CEREBRO_TIMEZONE` | No | — | Explicit timezone for merged calendar context |
| `GOG_ACCOUNT` | No | — | Google account for calendar access (via `gog` CLI) |
| `CEREBRO_CALENDAR_IDS` | No | `primary` | Comma-separated calendar IDs to merge |
| `CEREBRO_CALENDAR_NAMES` | No | — | Optional: calendar display names (matches IDs order) |
| `CEREBRO_MANAGE_SYSTEM_RECURRING` | No | `false` | Enable backend auto-creation of report/planning tasks |
| `CORS_ORIGINS` | No | — | Comma-separated allowed browser origins for API CORS |
| `CEREBRO_MODELS_JSON` | No | — | Optional JSON array of model aliases for `/api/config/models` |

## Security Notes

- **Never commit** `.env`, `config/brains.json`, or `config/brain_targets.json` with real values.
- Keep `cerebro.db` local (gitignored by default).
- Restrict Control UI access (bind to `127.0.0.1` or use auth).
- For Discord: use per-guild/channel allowlists (see OpenClaw docs).

## Troubleshooting

- **"Required environment variable X is not set"**: Check `.env`.
- **"Brains config file not found"**: Run `cp config/brains.template.json config/brains.json`.
- **Calendar scripts fail**: Ensure `GOG_ACCOUNT` is set and `gog` CLI is configured. Calendar/account values are validated and executed without shell interpolation.
- **CORS blocked in browser**: set `CORS_ORIGINS` to your frontend origin(s), comma-separated.

## License

[Include your license here]
