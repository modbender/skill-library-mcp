# Waste Reminder Skill

A flexible, token-efficient skill for automated waste container collection reminders.

## Overview

This skill helps automate waste collection reminders based on user-defined schedules. It uses simple JSON configuration for maximum flexibility and minimal token usage.

**How it works:**
The skill reads your config and schedule, determines which reminders need to be sent, and outputs them in a format that your AI assistant can process. The AI then sends the actual messages to the specified channels.

Output format:
```
SEND_TO:recipient_id
CHANNEL:whatsapp
Your message here
---
```

This approach keeps your configuration simple and token-efficient - the skill doesn't need API keys or direct network access.

## Features

- Multiple container types
- Custom reminder schedules (up to 4 times per pickup)
- Flexible targeting (group, personal, escalation)
- Multi-channel support (WhatsApp, Telegram, Discord, Email) - messages sent by your AI
- Confirmation system (stops further reminders)
- Single schedule file
- Token-efficient - generates reminders without using AI tokens

## Installation

```bash
clawhub install waste-reminder
```

## Setup for Users

When you install this skill, the AI assistant will send you a config template. Reply in any language - the AI will understand and convert it to the correct format!

### Example Template (Complete example with all options)

```
I want to set up waste reminders!

My containers:
- blue: Paper (🔵)
- gray: Residual (⚫)
- orange: Plastic (🟠)
- green: Garden (🟢)

Reminder times:
- 18:00: to group_whatsapp (day before, group notification)
- 22:00: to group_whatsapp (evening reminder to group)
- 06:30: to partner_whatsapp (morning, specific person)
- 09:30: to me_telegram (escalation, different channel)

My contacts:
- group_whatsapp: 123456789@g.us
- partner_whatsapp: +31600000001
- me_telegram: 222222222

Upcoming pickups:
- 2026-02-24: orange
- 2026-02-25: gray
- 2026-03-02: blue
```

The AI will convert this to the correct JSON format and set everything up.

## Configuration

The skill stores configuration in:
`/data/.openclaw/workspace/data/waste-reminder/`

### Files

```
waste-reminder/
├── config.json      # Your containers, reminder times, targets
└── schedule.json   # Your pickup dates and status
```

### Complete config.json Example (all options shown)

```json
{
  "config_version": "1.0",
  "containers": {
    "blue": {"name": "Paper", "color": "blue", "emoji": "🔵"},
    "gray": {"name": "Residual", "color": "gray", "emoji": "⚫"},
    "orange": {"name": "Plastic", "color": "orange", "emoji": "🟠"},
    "green": {"name": "Garden", "color": "green", "emoji": "🟢"}
  },
  "reminder_times": {
    "18:00": {
      "type": "group",
      "template": "Tomorrow: {container_emoji} {container_name} will be collected!",
      "target": "group_whatsapp"
    },
    "22:00": {
      "type": "group",
      "template": "Not confirmed yet - {container_emoji} needs to go out by 7am!",
      "target": "group_whatsapp"
    },
    "06:30": {
      "type": "personal",
      "template": "⚠️ {container_emoji} put out NOW!",
      "target": "partner_whatsapp"
    },
    "09:30": {
      "type": "escalation",
      "template": "Container still not outside!",
      "target": "me_telegram"
    }
  },
  "targets": {
    "group_whatsapp": {"id": "123456789@g.us", "channel": "whatsapp"},
    "partner_whatsapp": {"id": "+31600000001", "channel": "whatsapp"},
    "partner_telegram": {"id": "111111111", "channel": "telegram"},
    "me_whatsapp": {"id": "+31600000002", "channel": "whatsapp"},
    "me_telegram": {"id": "222222222", "channel": "telegram"},
    "me_discord": {"id": "https://discord.com/api/webhooks/...", "channel": "discord"}
  }
}
```

### Complete schedule.json Example

```json
{
  "2026-02-24": {
    "orange": {
      "confirmed": false,
      "reminded_18:00": false,
      "reminded_22:00": false,
      "reminded_06:30": false,
      "reminded_09:30": false
    }
  },
  "2026-02-25": {
    "gray": {
      "confirmed": false,
      "reminded_18:00": false,
      "reminded_22:00": false,
      "reminded_06:30": false,
      "reminded_09:30": false
    }
  }
}
```

## Cron Job

Add ONE cron job that runs every 15 minutes:
- Name: "Waste Reminder Check"
- Schedule: every 15 minutes
- Script: `/data/.openclaw/workspace/skills/waste-reminder/waste_cron.py`

The cron script checks if any reminders need to be sent and outputs them. Your AI assistant (triggered by the cron job) reads this output and sends the actual messages to the appropriate channels.

## User Commands

- Confirm: "container is out"
- View: "waste schedule" or "waste status"
- Add: "waste add [date] [container]"
- Remove: "waste remove [date] [container]"

## Files

```
waste-reminder/
├── SKILL.md           # This file
├── waste_reminder.py # CLI tool (manual commands)
└── waste_cron.py      # Cron script (every 15 min)
```

## Template Placeholders

- `{container_emoji}` - The emoji
- `{container_name}` - The name
- `{date}` - The date

## Channel Support

Supported channels:
- `whatsapp` - Use phone number or group ID as ID
- `telegram` - Use chat ID
- `discord` - Use webhook URL
- `email` - Use email address

Each target must specify both `id` and `channel`.

## Target Naming Convention

Targets should be named with channel suffix:
- `group_whatsapp`, `group_telegram`, `group_discord`
- `me_whatsapp`, `me_telegram`, `me_discord`
- `partner_whatsapp`, `partner_telegram`, `partner_discord`

The channel is extracted from the target name automatically.

## License

MIT License
