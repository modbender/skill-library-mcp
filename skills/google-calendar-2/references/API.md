# Google Calendar API v3 — Quick Reference

Full docs: https://developers.google.com/workspace/calendar/api/v3/reference

## Contents

- Event Resource Fields
- Events.list Parameters
- Recurring Events
- Colors
- Attendees & Invitations
- Move Event to Another Calendar
- OAuth Scopes Used

## Event Resource Fields

Key fields when creating or updating events:

| Field | Type | Description |
|-------|------|-------------|
| `summary` | string | Event title |
| `description` | string | Event description (supports HTML) |
| `location` | string | Free-text location |
| `start` | object | `{ dateTime: "RFC3339" }` or `{ date: "YYYY-MM-DD" }` for all-day |
| `end` | object | Same format as `start` |
| `attendees` | array | `[{ email: "..." }]` |
| `recurrence` | array | RRULE strings, e.g. `["RRULE:FREQ=WEEKLY;COUNT=10"]` |
| `reminders` | object | `{ useDefault: false, overrides: [{ method: "popup", minutes: 10 }] }` |
| `colorId` | string | `"1"` through `"11"` — see Colors API |
| `status` | string | `confirmed`, `tentative`, `cancelled` |
| `visibility` | string | `default`, `public`, `private`, `confidential` |
| `transparency` | string | `opaque` (busy) or `transparent` (free) |

## Events.list Parameters

| Parameter | Description |
|-----------|-------------|
| `timeMin` | RFC3339 lower bound (exclusive) |
| `timeMax` | RFC3339 upper bound (exclusive) |
| `maxResults` | Max events returned (default 250) |
| `singleEvents` | `true` to expand recurring events |
| `orderBy` | `startTime` (requires singleEvents=true) or `updated` |
| `q` | Free text search across event fields |
| `showDeleted` | Include cancelled events |
| `updatedMin` | Only events updated after this time |

## Recurring Events

Create with `recurrence` field using RRULE:

```json
{
  "summary": "Weekly standup",
  "start": { "dateTime": "2026-02-09T10:00:00-08:00" },
  "end": { "dateTime": "2026-02-09T10:30:00-08:00" },
  "recurrence": ["RRULE:FREQ=WEEKLY;BYDAY=MO;COUNT=20"]
}
```

List instances of a recurring event:
```
GET /calendars/{calendarId}/events/{eventId}/instances
```

## Colors

Get available color definitions:
```
GET /colors
```

Event color IDs: `"1"` (lavender) through `"11"` (tomato).

## Attendees & Invitations

```json
{
  "attendees": [
    { "email": "alice@example.com" },
    { "email": "bob@example.com", "optional": true }
  ],
  "sendUpdates": "all"
}
```

`sendUpdates` on create/update/delete: `"all"`, `"externalOnly"`, or `"none"`.

## Move Event to Another Calendar

```
POST /calendars/{calendarId}/events/{eventId}/move?destination={destinationCalendarId}
```

## OAuth Scopes Used

| Scope | Access |
|-------|--------|
| `calendar` | Full read/write to all calendars |
| `calendar.events` | Read/write events on all calendars |
| `calendar.readonly` | Read-only access to calendars |
| `calendar.events.readonly` | Read-only access to events |

The skill requests `calendar` + `calendar.events` by default for full read/write.
