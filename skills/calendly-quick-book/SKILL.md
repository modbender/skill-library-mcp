---
name: calendly-quick-book
description: Book Calendly meetings instantly. Triggers on "book", "schedule calendly", "calendly book", or any request to book a meeting without sending a link.
user-invocable: true
metadata: {"openclaw": {"always": true, "emoji": "📅", "requires": {"env": ["CALENDLY_API_TOKEN"]}}}
---

# Calendly Quick Book

Book Calendly meetings via natural language. No tab switching, no link sending.

## Default Configuration

| Setting | Value |
|---------|-------|
| Default Calendly Link | https://calendly.com/YOUR_USERNAME |
| Calendly Username | YOUR_USERNAME |

**Note:** Update the values above with your own Calendly username after installation.

## Commands

| Input | Action |
|-------|--------|
| `book [name] [email] [timezone] [time]` | Book a meeting |
| `calendly book [name] [email] [timezone] [time]` | Book a meeting |

## Input Fields

| Field | Required | Example |
|-------|----------|---------|
| Name | Yes | John Smith |
| Email | Yes | john@acme.com |
| Timezone | Yes | EST, PST, UTC |
| Time | Yes | tomorrow 2pm |

## Timezone Mapping

| Input | IANA Format |
|-------|-------------|
| EST/EDT | America/New_York |
| CST/CDT | America/Chicago |
| MST/MDT | America/Denver |
| PST/PDT | America/Los_Angeles |
| GMT/UTC | UTC |

## API Workflow

### Step 1: Get Current User

```bash
curl -s "https://api.calendly.com/users/me" \
  -H "Authorization: Bearer $CALENDLY_API_TOKEN"
```

### Step 2: Get Event Types

```bash
curl -s "https://api.calendly.com/event_types?user={USER_URI}" \
  -H "Authorization: Bearer $CALENDLY_API_TOKEN"
```

### Step 3: Get Available Times

```bash
curl -s "https://api.calendly.com/event_type_available_times?event_type={EVENT_TYPE_URI}&start_time={START_UTC}&end_time={END_UTC}" \
  -H "Authorization: Bearer $CALENDLY_API_TOKEN"
```

### Step 4: Create Booking

```bash
curl -s -X POST "https://api.calendly.com/invitees" \
  -H "Authorization: Bearer $CALENDLY_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "{EVENT_TYPE_URI}",
    "start_time": "{TIME_UTC}",
    "invitee": {
      "name": "{NAME}",
      "email": "{EMAIL}",
      "timezone": "{TIMEZONE_IANA}"
    }
  }'
```

## Response Format

### Success
```
✅ Meeting Booked!

📅 [Date]
⏰ [Time] [Timezone]
👤 [Name] ([Email])
📍 Calendar invite sent automatically
```

### No Availability
```
⚠️ No availability at [time]

Nearest slots:
1. [Option 1]
2. [Option 2]
3. [Option 3]
```

### Errors

| Error | Response |
|-------|----------|
| Invalid email | Ask to confirm email |
| Token expired | Direct to Calendly settings |
| No event types | Direct to create one in Calendly |
