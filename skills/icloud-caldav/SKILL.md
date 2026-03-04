---
name: icloud-caldav
description: Direct iCloud Calendar integration via CalDAV protocol. Create, read, update, and delete calendar events without third-party services. Use when the user wants to manage their iCloud Calendar, check schedule, create events, or find free time. Requires Apple ID and app-specific password.
---

# iCloud CalDAV — Direct Calendar Access

Manage iCloud Calendar directly via CalDAV protocol. No third-party services, no data leaves your machine except to Apple's servers.

## When to Use

**Activate when the user wants to:**
- Check their calendar or upcoming events
- Create new calendar events
- Delete existing events
- List available calendars

**Do NOT use for:**
- Reminders (use `apple-reminders` skill if available)
- Contacts (CalDAV is calendar-only)
- Non-iCloud calendars (Google, Outlook, etc.)

## Prerequisites

**Required credentials:**
- `APPLE_ID` — Your Apple ID email address
- `APPLE_APP_PASSWORD` — An [app-specific password](https://appleid.apple.com) (NOT your regular Apple ID password)

**To generate app-specific password:**
1. Go to [appleid.apple.com](https://appleid.apple.com)
2. Sign in → Sign-In and Security → App-Specific Passwords
3. Generate a new password
4. Use this password (not your regular one)

## Quick Start

```bash
# Set credentials
export APPLE_ID="your.email@icloud.com"
export APPLE_APP_PASSWORD="xxxx-xxxx-xxxx-xxxx"

# List calendars
./scripts/caldav.py list-calendars

# List events for next 7 days
./scripts/caldav.py list-events --days 7

# Create an event
./scripts/caldav.py create-event \
  --title "Team Meeting" \
  --start "2025-07-23T14:00:00" \
  --duration 60 \
  --calendar "Work"
```

## Available Operations

| Operation | Command | Description |
|-----------|---------|-------------|
| List calendars | `list-calendars` | Show all iCloud calendars |
| List events | `list-events` | Events in a date range |
| Create event | `create-event` | Add new calendar event |
| Delete event | `delete-event` | Remove event by filename or UID |

## Workflow Patterns

### Creating Events

```bash
# Basic event
./scripts/caldav.py create-event \
  --title "Dentist Appointment" \
  --start "2025-07-25T09:30:00" \
  --duration 30

# With location and description
./scripts/caldav.py create-event \
  --title "Project Review" \
  --start "2025-07-26T14:00:00" \
  --duration 60 \
  --location "Conference Room B" \
  --description "Q3 planning review" \
  --calendar "Work"

# All-day event
./scripts/caldav.py create-event \
  --title "Vacation" \
  --start "2025-08-01" \
  --all-day
```

### Batch Operations

**Note:** CalDAV does not support native batch operations. To create multiple events, run the script multiple times:

```bash
# Create multiple events by running the command multiple times
./scripts/caldav.py create-event --title "Meeting 1" --start "2025-07-26T10:00:00" --duration 60
./scripts/caldav.py create-event --title "Meeting 2" --start "2025-07-26T14:00:00" --duration 60
./scripts/caldav.py create-event --title "Meeting 3" --start "2025-07-27T09:00:00" --duration 60
```

iCloud handles rapid sequential requests well, but there is no single API call for creating multiple events.

### Deleting Events

```bash
# Delete by filename
./scripts/caldav.py delete-event \
  --file "event-name.ics" \
  --calendar "Calendar"

# Delete by UID (searches calendar for matching event)
./scripts/caldav.py delete-event \
  --uid "openclaw-xxx@openclaw.local" \
  --calendar "Calendar"
```

**Warning:** Deletions are permanent. iCloud may have its own backup, but standard CalDAV DELETE immediately removes the event.

## Date/Time Formats

- **ISO 8601**: `2025-07-23T14:00:00` (assumes local timezone if none specified)
- **With timezone**: `2025-07-23T14:00:00+08:00`
- **All-day**: `2025-07-23` (date only)

## Security Notes

- Credentials are read from environment variables only
- No credentials are logged or stored
- All communication is HTTPS to `caldav.icloud.com`
- App-specific passwords can be revoked anytime at appleid.apple.com

## Error Handling

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Bad credentials | Check APPLE_ID and APPLE_APP_PASSWORD |
| 404 Not Found | Calendar/event doesn't exist | List calendars/events first |
| 403 Forbidden | Read-only calendar | Try a different calendar |
| Timeout | Network issue | Retry the request |

## References

- See `references/caldav-protocol.md` for CalDAV implementation details
- See `references/icloud-endpoints.md` for iCloud-specific endpoints