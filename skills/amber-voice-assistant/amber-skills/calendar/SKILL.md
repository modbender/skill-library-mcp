---
name: calendar
version: 1.2.0
description: "Query and manage the operator's calendar — check availability and create new entries"
metadata: {"amber": {"capabilities": ["read", "act"], "confirmation_required": false, "timeout_ms": 5000, "permissions": {"local_binaries": ["ical-query"], "telegram": false, "openclaw_action": false, "network": false}, "function_schema": {"name": "calendar_query", "description": "Check the operator's calendar availability or create a new entry. PRIVACY RULE: When reporting availability to callers, NEVER disclose event titles, names, locations, or any details about what the operator is doing. Only share whether they are free or busy at a given time (e.g. 'free from 2pm to 4pm', 'busy until 3pm'). Treat all calendar event details as private and confidential.", "parameters": {"type": "object", "properties": {"action": {"type": "string", "enum": ["lookup", "create"], "description": "Whether to look up availability or create a new event"}, "range": {"type": "string", "description": "For lookup: today, tomorrow, week, or a specific date like 2026-02-23", "pattern": "^(today|tomorrow|week|\\d{4}-\\d{2}-\\d{2})$"}, "title": {"type": "string", "description": "For create: the event title", "maxLength": 200}, "start": {"type": "string", "description": "For create: start date-time like 2026-02-23T15:00", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}$"}, "end": {"type": "string", "description": "For create: end date-time like 2026-02-23T16:00", "pattern": "^\\d{4}-\\d{2}-\\d{2}T\\d{2}:\\d{2}$"}, "calendar": {"type": "string", "description": "Optional: specific calendar name", "maxLength": 100}, "notes": {"type": "string", "description": "For create: event notes", "maxLength": 500}, "location": {"type": "string", "description": "For create: event location", "maxLength": 200}}, "required": ["action"]}}}}
---

# Calendar Skill

Query the operator's calendar for availability and create new entries via `ical-query`.

## Capabilities

- **read**: Check free/busy availability for today, tomorrow, this week, or a specific date
- **act**: Create new calendar entries

## Privacy Rule

**Event details are never disclosed to callers.** This is enforced at two levels:

1. **Handler level** — the handler strips all event titles, names, locations, and notes from ical-query output before returning results. Only busy time slots (start/end times) are returned.
2. **Model level** — the function description instructs Amber to only communicate availability ("free from 2pm to 4pm") and never reveal what the events are.

Amber should say things like:
- ✅ "The operator is free between 2 and 4 this afternoon"
- ✅ "They're busy until 3pm, then free for the rest of the day"
- ❌ "They have a meeting with John at 2pm" ← never
- ❌ "They're at the dentist from 10 to 11" ← never

## Security — Three Layers

Input validation is enforced at three independent levels:

1. **Schema level** — `range` is constrained by `pattern: ^(today|tomorrow|week|\d{4}-\d{2}-\d{2})$`; `start`/`end` by `pattern: ^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$`; freetext fields have `maxLength` caps. The LLM cannot produce out-of-spec values without violating the schema.
2. **Handler level** — explicit validation before any exec call; rejects values that don't match expected formats even if schema is bypassed.
3. **Exec level** — `context.exec()` takes a `string[]` and uses `execFileSync` (no shell spawned); arguments are passed as discrete tokens, not a shell-interpolated string.

## Notes

- Uses `/usr/local/bin/ical-query` — no network access, no gateway round-trip
- Fast: direct local binary call (~100ms)
- Calendar name optional — defaults to operator's primary calendar
