---
name: donotify
description: Send immediate voice call reminders or schedule future calls via DoNotify.
version: 1.0.1
homepage: https://donotifys.com/openclaw
permissions:
  - network:outbound
requires:
  env:
    - DONOTIFY_API_TOKEN
    - DONOTIFY_URL
metadata: {"openclaw":{"requires":{"env":["DONOTIFY_API_TOKEN","DONOTIFY_URL"]},"primaryEnv":"DONOTIFY_API_TOKEN"}}
---

# DoNotify Skill

You can send immediate voice call reminders or schedule future calls through the DoNotify API.

## Authentication

All requests require:
- Header: `Authorization: Bearer $DONOTIFY_API_TOKEN`
- Header: `Accept: application/json`
- Base URL: `$DONOTIFY_URL` (default: `https://donotifys.com`)

## Endpoints

### Check Usage

Check the user's plan, remaining notifications, and phone number status.

```
GET $DONOTIFY_URL/api/usage
```

Response:
```json
{
  "plan": "starter",
  "notification_limit": 30,
  "used_this_month": 5,
  "remaining": 25,
  "phone_number_set": true
}
```

Before placing calls, check that `phone_number_set` is `true` and `remaining` is greater than 0. If the phone number is not set, tell the user to configure it in their DoNotify profile.

### Call Now

Place an immediate voice call to the user's phone.

```
POST $DONOTIFY_URL/api/call-now
Content-Type: application/json

{
  "title": "Pick up groceries",
  "description": "Milk, eggs, bread from Trader Joe's"
}
```

Parameters:
- `title` (required, string, max 255) — What the call is about. This is spoken aloud.
- `description` (optional, string, max 1000) — Additional details spoken after the title.

Success response:
```json
{
  "success": true,
  "reminder_id": 42,
  "call_uuid": "abc-123",
  "status": "completed"
}
```

Error response (422 if no phone number, 500 if call fails):
```json
{
  "success": false,
  "reminder_id": 42,
  "error": "Phone number not configured. Update your profile first.",
  "status": "failed"
}
```

### Schedule Reminder

Schedule a voice call for a future time.

```
POST $DONOTIFY_URL/api/reminders
Content-Type: application/json

{
  "title": "Team standup",
  "call_at": "2025-06-15T14:45:00Z",
  "description": "Prepare sprint update",
  "event_time": "2025-06-15T15:00:00Z"
}
```

Parameters:
- `title` (required, string, max 255) — Reminder title spoken in the call.
- `call_at` (required, ISO 8601 datetime, must be in the future) — When to place the call.
- `description` (optional, string, max 1000) — Extra details.
- `event_time` (optional, ISO 8601 datetime) — The actual event time, if different from call time.

Success response (201):
```json
{
  "success": true,
  "reminder": {
    "id": 43,
    "title": "Team standup",
    "description": "Prepare sprint update",
    "call_at": "2025-06-15T14:45:00+00:00",
    "event_time": "2025-06-15T15:00:00+00:00",
    "status": "pending"
  }
}
```

## Behavior Guidelines

- When the user says "call me now about X" or "remind me right now about X", use the **Call Now** endpoint.
- When the user says "remind me at [time] about X" or "call me at [time] for X", use the **Schedule Reminder** endpoint. Convert the user's natural language time to ISO 8601 for `call_at`.
- When the user asks "how many reminders do I have left" or "check my usage", use the **Usage** endpoint.
- Always check usage first if you're unsure whether the user has remaining notifications.
- If `phone_number_set` is `false`, tell the user to set their phone number at their DoNotify profile page before placing calls.
- Keep titles concise and descriptive — they are read aloud during the call.
