---
name: feishu-calendar-advanced
description: Feishu calendar management via feishu-agent. View calendars, list events, create and delete events with conflict detection.
compatibility: darwin,linux
metadata:
  version: 1.0.0
  requires:
    bins:
      - bun
---

# Feishu Calendar Advanced

Manage your Feishu (Lark) calendar using the feishu-agent CLI tool.

## Dependencies

| Dependency | Required | Description |
|------------|----------|-------------|
| `bun` | Yes | Bun runtime (for running bunx commands) |
| `@teamclaw/feishu-agent` | Yes | Installed automatically via bunx |

### Check Dependencies

```bash
# Check bun availability
bun --version
```

## Setup

### First Time Setup

1. **Install and configure feishu-agent**:

```bash
# Interactive setup wizard (recommended)
bunx @teamclaw/feishu-agent setup

# Or manual configuration
bunx @teamclaw/feishu-agent config set appId <your_app_id>
bunx @teamclaw/feishu-agent config set appSecret <your_app_secret>
```

2. **OAuth Authorization**:

```bash
bunx @teamclaw/feishu-agent auth
```

3. **Verify setup**:

```bash
bunx @teamclaw/feishu-agent whoami
```

## Usage

```bash
/feishu-calendar-advanced [command] [options]
```

## Commands

| Command | Description |
|---------|-------------|
| `calendars` | List all calendars (primary, subscribed) |
| `events` | List events in primary calendar |
| `create --summary "Meeting" --start "2026-03-05 14:00" --end "2026-03-05 15:00"` | Create a new event |
| `create --summary "Meeting" --start "..." --end "..." --attendee user_id` | Create event with attendees |
| `delete --event-id <event_id>` | Delete an event by ID |

## Options

| Option | Description |
|--------|-------------|
| `--summary` | Event title/summary (required for create) |
| `--start` | Start time in format "YYYY-MM-DD HH:MM" (required for create) |
| `--end` | End time in format "YYYY-MM-DD HH:MM" (required for create) |
| `--attendee` | Add attendee by user_id (can be used multiple times) |
| `--event-id` | Event ID (required for delete) |

## Examples

```bash
# List all calendars
/feishu-calendar-advanced calendars

# List events in primary calendar
/feishu-calendar-advanced events

# Create a simple event
/feishu-calendar-advanced create --summary "Team Standup" --start "2026-03-05 10:00" --end "2026-03-05 10:30"

# Create event with attendees
/feishu-calendar-advanced create --summary "Project Review" --start "2026-03-05 14:00" --end "2026-03-05 15:00" --attendee user_id_1 --attendee user_id_2

# Delete an event
/feishu-calendar-advanced delete --event-id evt_xxxxxxxxxxxxx
```

## Troubleshooting

**"User authorization required"**
- Run `bunx @teamclaw/feishu-agent auth` to authorize

**"Token expired"**
- Run `bunx @teamclaw/feishu-agent auth` again to refresh

**"Time conflict detected"**
- The requested time slot is already busy
- Choose a different time or check your calendar with `bunx @teamclaw/feishu-agent calendar events`

**"Permission denied"**
- Check app permissions in Feishu Developer Console
- Required: `calendar:calendar`, `calendar:event`
