---
name: calendar
description: >
  Check availability and create calendar entries. Used during calls to
  book appointments and check schedule conflicts. Use when the user or
  a caller needs to schedule something or check availability.
---

# Calendar

Query and manage the operator's calendar during or outside of calls.

## MCP Tools

### calendar_query
Look up or create calendar events.
- `action` (string, required): "lookup" or "create"
- `query` (string, required for lookup): Natural language query (e.g., "am I free Tuesday at 3pm?")
- `title` (string, required for create): Event title
- `start` (string, required for create): Start time (ISO 8601)
- `end` (string, required for create): End time (ISO 8601)
- `calendar` (string): Which calendar to use (defaults to operator's primary)
- `location` (string): Event location
- `notes` (string): Event notes

## Guidelines

- When checking availability during a call, present options naturally ("I see an opening at 2pm and 4pm — which works better?")
- Always confirm the final date, time, and details before creating an event
- Include relevant context from the call in the event notes (who requested it, purpose)
