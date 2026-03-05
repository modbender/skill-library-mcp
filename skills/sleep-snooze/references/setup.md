# Sleep Snooze — Setup Guide

## Prerequisites

- OpenClaw installed and connected to at least one provider (Telegram, WhatsApp, etc.)
- Node.js v18+ on your machine
- `better-sqlite3` and `node-cron` (auto-installed by OpenClaw via skill metadata)

## Installation via ClawHub

```bash
clawhub install sleep-snooze
```

Or manually copy this skill folder to `~/.openclaw/skills/sleep-snooze/`.

## First-Time Setup

Start a conversation with your OpenClaw bot and type:

```
/snooze-setup
```

OpenClaw will ask you three questions:
1. **Sleep start time** — e.g., `10:00 PM` or `22:00`
2. **Wake time** — e.g., `6:00 AM` or `06:00`
3. **Timezone** — e.g., `Asia/Kolkata`, `America/New_York`, `Europe/London`

It will then configure cron jobs on your machine to automatically activate sleep mode and deliver your digest.

## Manual Configuration

If you prefer to configure manually, create `~/.openclaw/skills/sleep-snooze/data/state.json`:

```json
{
  "sleepStart": "22:00",
  "wakeTime": "06:00",
  "timezone": "Asia/Kolkata",
  "manualOverride": false,
  "isSleeping": false,
  "lastDigestAt": null
}
```

Then run:

```bash
node ~/.openclaw/skills/sleep-snooze/scripts/sleep-init.js \
  --sleep-start 22:00 \
  --wake-time 06:00 \
  --timezone Asia/Kolkata
```

## Environment Variables (Alternative Config)

You can also configure via environment variables in `~/.openclaw/openclaw.json`:

```json5
{
  skills: {
    entries: {
      "sleep-snooze": {
        enabled: true,
        env: {
          SLEEP_START: "22:00",
          WAKE_TIME: "06:00",
          TIMEZONE: "Asia/Kolkata"
        }
      }
    }
  }
}
```

## Adding VIP Contacts

VIP contacts bypass sleep mode and are delivered immediately. Edit:

```
~/.openclaw/skills/sleep-snooze/data/vip-contacts.json
```

```json
{
  "contacts": ["telegram:123456789", "whatsapp:+1234567890"]
}
```

Format: `provider:id` where `id` is the sender's platform-specific ID.

## Slash Commands

| Command | Description |
|---------|-------------|
| `/snooze-setup` | Interactive first-time configuration |
| `/sleep` | Manually activate sleep mode now |
| `/wake` | Manually deactivate + deliver digest now |
| `/snooze-status` | Check status and queued message count |
| `/snooze-history` | View past 7 days of digest summaries |

## How the Digest Looks

```
🌅 Good morning! Here's what arrived while you slept:

📬 3 messages from Alex
  • "Hey are you free tomorrow?"
  • "Also wanted to share this article..."
  • "Never mind, talk later!"

📬 1 message from GitHub Notifications
  • PR #42 was merged into main

💬 4 total messages from 2 senders.
```

## Data Storage

All data is stored locally on your machine:

```
~/.openclaw/skills/sleep-snooze/
  data/
    state.json          — sleep schedule and current mode
    queue.db            — SQLite message queue
    vip-contacts.json   — contacts that bypass snooze
```

Nothing is sent to any external service. Your messages stay on your machine.

## Troubleshooting

**Digest not arriving in the morning?**
- Check that cron is running: `crontab -l | grep sleep-snooze`
- Verify Node.js is on your cron PATH: `which node`
- Check the queue manually: `node ~/.openclaw/skills/sleep-snooze/scripts/status.js`

**Messages not being queued?**
- Make sure the skill is enabled: `openclaw skills list --eligible`
- Check state: `cat ~/.openclaw/skills/sleep-snooze/data/state.json`

**Reset everything:**
```bash
rm -rf ~/.openclaw/skills/sleep-snooze/data/
node ~/.openclaw/skills/sleep-snooze/scripts/sleep-init.js
```
