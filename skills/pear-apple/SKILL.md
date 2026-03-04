---
name: pear-apple
description: iCloud Calendar, Reminders & Contacts via Pear. Manage events, reminders, contacts, daily briefings, and AI scheduling. 27 tools for Apple iCloud via CalDAV/CardDAV.
homepage: https://pearmcp.com
metadata:
  openclaw:
    emoji: "🍐"
    primaryEnv: PEAR_API_KEY
    requires:
      env:
        - PEAR_API_KEY
      network:
        - pearmcp.com
---

# Pear — iCloud Integration

Pear provides read/write access to iCloud Calendar, Reminders, and Contacts through 27 MCP tools. All tools are prefixed with `pear_` and communicate with iCloud via CalDAV/CardDAV protocols.

## When to Use

**Activate this skill when the user wants to:**
- Check their schedule, upcoming events, or daily agenda
- Create, update, or delete calendar events
- Manage reminders or to-do lists
- Look up, create, or update contacts
- Find free time slots or schedule meetings
- Get a daily briefing of events and tasks
- Check availability for a specific time
- Work with contact groups
- Perform bulk operations on events, reminders, or contacts

**Activation triggers:**
- "What's on my calendar", "my schedule", "upcoming events"
- "Remind me to", "add a reminder", "my tasks", "to-do"
- "Find contact", "add a contact", "phone number for"
- "Schedule a meeting", "find a time", "when am I free"
- "Daily briefing", "what's today look like"
- "Birthday", "anniversaries"

**Do NOT activate for:**
- Apple Notes (not supported — CalDAV only)
- Apple Mail or iMessage
- iCloud Drive or file storage
- Apple Music, Photos, or other non-PIM services
- Local macOS Calendar.app scripting (Pear works cross-platform via API)

## Prerequisites

**Required Environment Variable:**
- `PEAR_API_KEY` — Your Pear API key (format: `pear_sk_...`)
  - Sign up at [pearmcp.com](https://pearmcp.com)
  - Generate an API key from the dashboard
  - Connect your iCloud account (requires an [app-specific password](https://support.apple.com/en-us/102654))

**Optional:**
- `PEAR_MCP_URL` — Custom endpoint URL (defaults to `https://pearmcp.com/api/mcp`)

## Tool Reference

### Events (8 tools)

| Tool | Description |
|------|-------------|
| `pear_list_calendars` | List all iCloud calendars (including read-only subscriptions) |
| `pear_list_events` | List events in a time range, with pagination and calendar filtering |
| `pear_search_events` | Search events by title or description within a date range |
| `pear_create_event` | Create an event with optional recurrence, alarms, attendees, and location |
| `pear_update_event` | Update an existing event's properties |
| `pear_delete_event` | Delete an event by filename |
| `pear_find_free_slots` | Find available time slots of a given duration |
| `pear_check_availability` | Check if a specific time slot is free, returns conflicts |

### Reminders (4 tools)

| Tool | Description |
|------|-------------|
| `pear_list_reminders` | List reminders with optional list filtering, includes completed toggle |
| `pear_create_reminder` | Create a reminder with optional due date, priority (1=high, 5=med, 9=low), and notes |
| `pear_update_reminder` | Update a reminder's properties |
| `pear_complete_reminder` | Mark a reminder as completed |

### Contacts (9 tools)

| Tool | Description |
|------|-------------|
| `pear_list_contacts` | List all contacts with full vCard data (phones, emails, addresses, birthdays) |
| `pear_search_contacts` | Search by name, email, phone, or organization |
| `pear_create_contact` | Create a contact with full vCard support including photo |
| `pear_update_contact` | Update contact fields (merges with existing data) |
| `pear_delete_contact` | Delete a contact |
| `pear_list_contact_groups` | List all contact groups with member counts |
| `pear_create_contact_group` | Create a new contact group |
| `pear_add_contact_to_group` | Add a contact to a group by name or email |
| `pear_update_contact_photo` | Update a contact's photo (Base64, data URI, or external URL) |

### Briefing (1 tool)

| Tool | Description |
|------|-------------|
| `pear_get_daily_briefing` | Get today's events and pending reminders in one call. Enriches attendees with contact data. |

### Scheduling (1 tool)

| Tool | Description |
|------|-------------|
| `pear_find_best_time` | AI-scored optimal meeting slots. Considers work hours, time-of-day preference, day-of-week preference, buffer time, and reminder deadlines. |

### Batch Operations (4 tools)

| Tool | Description |
|------|-------------|
| `pear_create_events_batch` | Create up to 50 events in one call |
| `pear_create_reminders_batch` | Create up to 50 reminders in one call |
| `pear_create_contacts_batch` | Create up to 50 contacts in one call |
| `pear_delete_contacts_batch` | Delete up to 50 contacts in one call |

## Workflow Guidelines

### Dates and Times

- **Always use ISO 8601 format**: `2025-06-15T14:30:00Z` or `2025-06-15T14:30:00+10:00`
- **Timezone parameter**: Pass `timezone` (IANA format like `America/New_York` or `Australia/Sydney`) for user-friendly display times
- **All-day events**: Set `isAllDay: true` and use date-only format `2025-06-15`
- **Date ranges**: `pear_list_events` requires a `timeRange` object: `{ start: "...", end: "..." }`

### Creating Events

When creating events, follow this pattern:

1. If the user doesn't specify a calendar, omit `calendarName` — Pear auto-selects the default
2. For recurring events, use the `recurrence` object: `{ frequency: "WEEKLY", interval: 1, count: 10 }`
3. For attendees, you can pass names — Pear resolves them against the user's contacts automatically
4. Use `idempotencyKey` when retrying to prevent duplicate events
5. Alarms use minutes before: `{ action: "display", trigger: 15 }` for a 15-minute reminder

### Finding Meeting Times

For scheduling, prefer `pear_find_best_time` over `pear_find_free_slots`:

- `pear_find_best_time` returns AI-scored slots considering work hours, preferences, and existing commitments
- Pass `preferences` to customize: `{ timeOfDay: "morning", focusTime: true, workHoursStart: 9, workHoursEnd: 17 }`
- `pear_find_free_slots` is simpler — just returns raw available slots without scoring

### Reminders

- Reminders are accessed via CalDAV (VTODO protocol) — basic operations work well (title, due date, priority, notes, completion). Modern Apple Reminders features like subtasks, tags, smart lists, and location-based reminders are not available via CalDAV.
- Priority values: `1` = high, `5` = medium, `9` = low, `0` = none
- To list only incomplete reminders, use `includeCompleted: false` (default)
- Reminder lists are auto-created if they don't exist when using `listName`

### Contacts

- `pear_update_contact` merges fields — it won't erase data you don't include in the update
- Birthday format: `YYYY-MM-DD` for full date, `--MM-DD` for year-unknown
- Phone/email can be a single string or an array for multiple entries
- Contact photos accept Base64 or data URI format

### Virtual Birthdays

Pear generates all-day birthday events from contact birthday fields. These appear as events on a "Birthdays" calendar when listing events. This is a synthesized feature — Apple's native Birthdays calendar is not exposed via CalDAV.

### Daily Briefing

`pear_get_daily_briefing` is the most efficient way to give the user an overview:
- Returns today's events + pending reminders in a single call
- Automatically enriches event attendees with contact details (name, email, phone)
- Pass `timezone` for correct day boundaries
- Pass `date` to get a briefing for a different day

## Safety & Confirmation

### Actions Requiring Care

| Action | Risk | Guidance |
|--------|------|----------|
| `pear_delete_event` | Removes event permanently | Confirm event title and date with user before deleting |
| `pear_delete_contact` | Removes contact permanently | Always confirm — show contact name first |
| `pear_delete_contacts_batch` | Bulk delete up to 50 contacts | Require explicit user confirmation with count |
| `pear_update_event` | Overwrites event fields | Summarize changes before applying |
| `pear_complete_reminder` | Marks as done | Safe — can be undone by updating `completed: false` |
| Batch create operations | Creates up to 50 items | Confirm count and summarize before executing |

### Data Safety

- **Read operations are always safe** — listing, searching, and briefings have no side effects
- **Updates merge, not replace** — `pear_update_contact` preserves fields you don't mention
- **Batch operations are rate-limited** — chunks of 5 with 200ms delays, no need to throttle manually
- **Never expose the user's `PEAR_API_KEY`** — treat it as a secret

## Error Handling

| Error Code | Meaning | What to Do |
|------------|---------|------------|
| `-32001` | Missing or invalid API key | Check `PEAR_API_KEY` is set correctly |
| `-32602` | Invalid parameters | Check parameter names and types against tool reference |
| `-32603` | Server error | Retry once, then report to user |
| `404` on event/reminder | Item not found | The filename may have changed — re-list to get current filenames |
| Calendar is read-only | Cannot modify subscription calendars | List calendars first to check which are writable |

## Common Patterns

### Error Recovery (Idempotency)
```
Event creation failed mid-request or timed out:
→ Retry pear_create_event with the same idempotencyKey
→ Pear deduplicates — no double-booking even if the first request succeeded silently
```

### Morning Briefing
```
User: "What's on my plate today?"
→ Call pear_get_daily_briefing with timezone
→ Summarize events chronologically, then pending reminders
```

### Schedule a Meeting
```
User: "Find time for a 1-hour meeting this week"
→ Call pear_find_best_time with durationMinutes: 60 and this week's range
→ Present top 3 options with scores
→ On user selection, call pear_create_event
```

### Quick Reminder
```
User: "Remind me to call the dentist tomorrow"
→ Call pear_create_reminder with title and dueDate set to tomorrow
```

### Contact Lookup
```
User: "What's Sarah's phone number?"
→ Call pear_search_contacts with query: "Sarah"
→ Return matching contacts with phone numbers
```

### Bulk Event Creation
```
User: "Add these 5 meetings to my calendar"
→ Call pear_create_events_batch with all events in one request
→ Summarize results (created count, any failures)
```

## References

- [Pear Documentation](https://pearmcp.com/docs)
- [Apple App-Specific Passwords](https://support.apple.com/en-us/102654)
- [CalDAV Protocol (RFC 4791)](https://www.rfc-editor.org/rfc/rfc4791)
- [CardDAV Protocol (RFC 6352)](https://www.rfc-editor.org/rfc/rfc6352)
- [IANA Timezone Database](https://www.iana.org/time-zones)
