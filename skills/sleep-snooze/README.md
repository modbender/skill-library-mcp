# 🌙 sleep-snooze

> An OpenClaw skill that snoozes notifications during your sleep hours and delivers a morning digest when you wake up.

## What it does

- **Buffers** all incoming messages (Telegram, WhatsApp, Discord, Slack…) during your sleep window
- **Bypasses** urgent messages and VIP contacts immediately
- **Delivers** a grouped morning digest at your wake time
- **Works across all providers** OpenClaw is connected to — configure once, works everywhere

## Install

```bash
clawhub install sleep-snooze
```

Then set it up in chat:
```
/snooze-setup
```

## Quick example

```
You: /snooze-setup
OpenClaw: What time do you usually go to bed?
You: 10 PM
OpenClaw: What time do you wake up?
You: 6 AM
OpenClaw: What's your timezone?
You: Asia/Kolkata
OpenClaw: ✅ Sleep snooze is set: 🌙 10:00 PM → ☀️ 6:00 AM (IST).
          I'll queue notifications overnight and send your digest at 6:00 AM.
```

At 6:00 AM, you receive:
```
🌅 Good morning! Here's what arrived while you slept:

📬 2 messages from Alex
  • "You around?"
  • "Talk tomorrow!"

📬 1 message from Server Monitor
  • Disk usage at 82% — check when available
```

## Commands

| Command | Action |
|---------|--------|
| `/snooze-setup` | First-time configuration |
| `/sleep` | Manually start sleep mode |
| `/wake` | Manually end sleep mode + get digest now |
| `/snooze-status` | Check queue size and current mode |

## Configuration

See [references/setup.md](references/setup.md) for full configuration options including VIP contacts, manual config, and troubleshooting.

## Privacy

All data (message queue, schedule, contacts) is stored **locally on your machine** in `~/.openclaw/skills/sleep-snooze/data/`. Nothing is sent to external servers.

## Requirements

- OpenClaw with at least one provider connected
- Node.js v18+
- `better-sqlite3` (auto-installed)

## License

MIT
