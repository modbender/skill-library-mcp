---
name: calcom
description: |
  Cal.com API integration with managed OAuth. Create and manage event types, bookings, schedules, and availability.
  Use this skill when users want to manage scheduling, create bookings, configure event types, or check availability.
  For other third party apps, use the api-gateway skill (https://clawhub.ai/byungkyu/api-gateway).
  Requires network access and valid Maton API key.
metadata:
  author: maton
  version: "1.0"
  clawdbot:
    emoji: 🧠
    homepage: "https://maton.ai"
    requires:
      env:
        - MATON_API_KEY
---

# Cal.com

Access the Cal.com API with managed OAuth authentication. Create and manage event types, bookings, schedules, calendars, and webhooks.

## Quick Start

```bash
# Get your profile
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/cal-com/v2/me')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

## Base URL

```
https://gateway.maton.ai/cal-com/v2/{resource}
```

Replace `{resource}` with the Cal.com API endpoint path. The gateway proxies requests to `api.cal.com` and automatically injects your OAuth token.

## Authentication

All requests require the Maton API key in the Authorization header:

```
Authorization: Bearer $MATON_API_KEY
```

**Environment Variable:** Set your API key as `MATON_API_KEY`:

```bash
export MATON_API_KEY="YOUR_API_KEY"
```

### Getting Your API Key

1. Sign in or create an account at [maton.ai](https://maton.ai)
2. Go to [maton.ai/settings](https://maton.ai/settings)
3. Copy your API key

## Connection Management

Manage your Cal.com OAuth connections at `https://ctrl.maton.ai`.

### List Connections

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections?app=cal-com&status=ACTIVE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Create Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
data = json.dumps({'app': 'cal-com'}).encode()
req = urllib.request.Request('https://ctrl.maton.ai/connections', data=data, method='POST')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Content-Type', 'application/json')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Get Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

**Response:**
```json
{
  "connection": {
    "connection_id": "4481afaa-03e4-4b2d-a1c6-7daaf4bff512",
    "status": "ACTIVE",
    "creation_time": "2026-02-12T22:52:17.140998Z",
    "last_updated_time": "2026-02-12T22:55:20.376189Z",
    "url": "https://connect.maton.ai/?session_token=...",
    "app": "cal-com",
    "metadata": {}
  }
}
```

Open the returned `url` in a browser to complete OAuth authorization.

### Delete Connection

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections/{connection_id}', method='DELETE')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Specifying Connection

If you have multiple Cal.com connections, specify which one to use with the `Maton-Connection` header:

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://gateway.maton.ai/cal-com/v2/me')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
req.add_header('Maton-Connection', '4481afaa-03e4-4b2d-a1c6-7daaf4bff512')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

If omitted, the gateway uses the default (oldest) active connection.

## API Reference

### User Profile

#### Get Profile

```bash
GET /cal-com/v2/me
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 2152180,
    "email": "user@example.com",
    "name": "User Name",
    "avatarUrl": "https://...",
    "bio": "",
    "timeFormat": 12,
    "defaultScheduleId": null,
    "weekStart": "Sunday",
    "timeZone": "America/New_York"
  }
}
```

#### Update Profile

```bash
PATCH /cal-com/v2/me
Content-Type: application/json

{
  "bio": "Updated bio",
  "name": "New Name"
}
```

### Event Types

#### List Event Types

```bash
GET /cal-com/v2/event-types
```

With username filter:

```bash
GET /cal-com/v2/event-types?username={username}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "eventTypeGroups": [
      {
        "teamId": null,
        "bookerUrl": "https://cal.com",
        "profile": {
          "slug": "username",
          "name": "User Name"
        },
        "eventTypes": [
          {
            "id": 4716831,
            "title": "30 min meeting",
            "slug": "30min",
            "length": 30,
            "hidden": false
          }
        ]
      }
    ]
  }
}
```

#### Get Event Type

```bash
GET /cal-com/v2/event-types/{eventTypeId}
```

#### Create Event Type

```bash
POST /cal-com/v2/event-types
Content-Type: application/json

{
  "title": "Meeting",
  "slug": "meeting",
  "length": 30
}
```

**Required fields:**
- `title` - Event type name
- `slug` - URL slug (must be unique)
- `length` - Duration in minutes

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 4745911,
    "title": "Meeting",
    "slug": "meeting",
    "length": 30,
    "locations": [{"type": "integrations:daily"}],
    "hidden": false,
    "userId": 2152180
  }
}
```

#### Update Event Type

```bash
PATCH /cal-com/v2/event-types/{eventTypeId}
Content-Type: application/json

{
  "title": "Updated Meeting Title",
  "description": "Updated description"
}
```

#### Delete Event Type

```bash
DELETE /cal-com/v2/event-types/{eventTypeId}
```

### Event Type Webhooks

#### List Webhooks

```bash
GET /cal-com/v2/event-types/{eventTypeId}/webhooks
```

#### Create Webhook

```bash
POST /cal-com/v2/event-types/{eventTypeId}/webhooks
Content-Type: application/json

{
  "subscriberUrl": "https://example.com/webhook",
  "triggers": ["BOOKING_CREATED"],
  "active": true
}
```

**Available triggers:** `BOOKING_CREATED`, `BOOKING_RESCHEDULED`, `BOOKING_CANCELLED`, `BOOKING_CONFIRMED`, `BOOKING_REJECTED`, `BOOKING_REQUESTED`, `BOOKING_PAYMENT_INITIATED`, `BOOKING_NO_SHOW_UPDATED`, `MEETING_ENDED`, `MEETING_STARTED`, `RECORDING_READY`, `INSTANT_MEETING`, `RECORDING_TRANSCRIPTION_GENERATED`

#### Get Webhook

```bash
GET /cal-com/v2/event-types/{eventTypeId}/webhooks/{webhookId}
```

#### Update Webhook

```bash
PATCH /cal-com/v2/event-types/{eventTypeId}/webhooks/{webhookId}
Content-Type: application/json

{
  "active": false
}
```

#### Delete Webhook

```bash
DELETE /cal-com/v2/event-types/{eventTypeId}/webhooks/{webhookId}
```

### Bookings

#### List Bookings

```bash
GET /cal-com/v2/bookings
```

With filters:

```bash
GET /cal-com/v2/bookings?status=upcoming
GET /cal-com/v2/bookings?status=past
GET /cal-com/v2/bookings?status=cancelled
GET /cal-com/v2/bookings?status=accepted
GET /cal-com/v2/bookings?take=10
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "bookings": [
      {
        "id": 15893969,
        "uid": "gZJNR7FQG2qLsBqnFdxAPE",
        "title": "30 min meeting between User and Guest",
        "startTime": "2026-02-13T17:00:00.000Z",
        "endTime": "2026-02-13T17:30:00.000Z",
        "status": "ACCEPTED"
      }
    ],
    "totalCount": 1,
    "nextCursor": null
  }
}
```

#### Get Booking

```bash
GET /cal-com/v2/bookings/{bookingUid}
```

#### Create Booking

```bash
POST /cal-com/v2/bookings
Content-Type: application/json

{
  "eventTypeId": 4716831,
  "start": "2026-02-13T17:00:00Z",
  "timeZone": "America/New_York",
  "language": "en",
  "responses": {
    "name": "Guest Name",
    "email": "guest@example.com"
  },
  "metadata": {}
}
```

**Required fields:**
- `eventTypeId` - ID of the event type
- `start` - Start time in ISO 8601 format (must be an available slot)
- `timeZone` - Valid IANA timezone
- `language` - Language code (e.g., "en")
- `responses.name` - Attendee name
- `responses.email` - Attendee email

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 15893969,
    "uid": "gZJNR7FQG2qLsBqnFdxAPE",
    "title": "30 min meeting between User and Guest Name",
    "startTime": "2026-02-13T17:00:00.000Z",
    "endTime": "2026-02-13T17:30:00.000Z",
    "status": "ACCEPTED",
    "location": "integrations:daily"
  }
}
```

#### Cancel Booking

```bash
POST /cal-com/v2/bookings/{bookingUid}/cancel
Content-Type: application/json

{
  "cancellationReason": "Reason for cancellation"
}
```

### Schedules

#### Get Default Schedule

```bash
GET /cal-com/v2/schedules/default
```

#### Get Schedule

```bash
GET /cal-com/v2/schedules/{scheduleId}
```

#### Create Schedule

```bash
POST /cal-com/v2/schedules
Content-Type: application/json

{
  "name": "Work Hours",
  "timeZone": "America/New_York",
  "isDefault": false
}
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "id": 1243030,
    "name": "Work Hours",
    "isManaged": false,
    "workingHours": [
      {
        "days": [1, 2, 3, 4, 5],
        "startTime": 540,
        "endTime": 1020
      }
    ]
  }
}
```

#### Update Schedule

```bash
PATCH /cal-com/v2/schedules/{scheduleId}
Content-Type: application/json

{
  "name": "Updated Schedule Name"
}
```

#### Delete Schedule

```bash
DELETE /cal-com/v2/schedules/{scheduleId}
```

### Availability Slots

#### Get Available Slots

```bash
GET /cal-com/v2/slots/available?eventTypeId={eventTypeId}&startTime={startTime}&endTime={endTime}
```

**Parameters:**
- `eventTypeId` - Required. The event type ID
- `startTime` - Required. Start of range (ISO 8601)
- `endTime` - Required. End of range (ISO 8601)

**Response:**
```json
{
  "status": "success",
  "data": {
    "slots": {
      "2026-02-13": [
        {"time": "2026-02-13T17:00:00.000Z"},
        {"time": "2026-02-13T17:30:00.000Z"},
        {"time": "2026-02-13T18:00:00.000Z"}
      ],
      "2026-02-14": [
        {"time": "2026-02-14T14:00:00.000Z"}
      ]
    }
  }
}
```

#### Reserve Slot

```bash
POST /cal-com/v2/slots/reserve
Content-Type: application/json

{
  "eventTypeId": 4716831,
  "slotUtcStartDate": "2026-02-20T14:00:00Z",
  "slotUtcEndDate": "2026-02-20T14:30:00Z"
}
```

**Response:**
```json
{
  "status": "success",
  "data": "968ed924-83fb-4da7-969e-eaa621643535"
}
```

### Calendars

#### List Connected Calendars

```bash
GET /cal-com/v2/calendars
```

**Response:**
```json
{
  "status": "success",
  "data": {
    "connectedCalendars": [
      {
        "integration": {
          "name": "Google Calendar",
          "type": "google_calendar"
        },
        "calendars": [...]
      }
    ]
  }
}
```

### Conferencing

#### List Conferencing Apps

```bash
GET /cal-com/v2/conferencing
```

**Response:**
```json
{
  "status": "success",
  "data": [
    {
      "id": 1769268,
      "type": "google_video",
      "appId": "google-meet"
    }
  ]
}
```

#### Get Default Conferencing App

```bash
GET /cal-com/v2/conferencing/default
```

### Webhooks (User-level)

#### List Webhooks

```bash
GET /cal-com/v2/webhooks
```

#### Create Webhook

```bash
POST /cal-com/v2/webhooks
Content-Type: application/json

{
  "subscriberUrl": "https://example.com/webhook",
  "triggers": ["BOOKING_CREATED"],
  "active": true
}
```

#### Get Webhook

```bash
GET /cal-com/v2/webhooks/{webhookId}
```

#### Update Webhook

```bash
PATCH /cal-com/v2/webhooks/{webhookId}
Content-Type: application/json

{
  "active": false
}
```

#### Delete Webhook

```bash
DELETE /cal-com/v2/webhooks/{webhookId}
```

### Teams

#### List Teams

```bash
GET /cal-com/v2/teams
```

### Verified Resources

#### List Verified Emails

```bash
GET /cal-com/v2/verified-resources/emails
```

## Pagination

Bookings use cursor-based pagination with `take` and `nextCursor`:

```bash
GET /cal-com/v2/bookings?take=10
```

Response includes pagination info:

```json
{
  "data": {
    "bookings": [...],
    "totalCount": 25,
    "nextCursor": "abc123"
  }
}
```

For next page:

```bash
GET /cal-com/v2/bookings?take=10&cursor=abc123
```

## Code Examples

### JavaScript

```javascript
const response = await fetch(
  'https://gateway.maton.ai/cal-com/v2/event-types',
  {
    headers: {
      'Authorization': `Bearer ${process.env.MATON_API_KEY}`
    }
  }
);
const data = await response.json();
```

### Python

```python
import os
import requests

response = requests.get(
    'https://gateway.maton.ai/cal-com/v2/event-types',
    headers={'Authorization': f'Bearer {os.environ["MATON_API_KEY"]}'}
)
data = response.json()
```

## Notes

- All times are in UTC unless a timezone is specified
- `length` field in event types is in minutes
- Booking creation requires an available slot - check `/v2/slots/available` first
- Schedule working hours use minutes from midnight (540 = 9:00 AM, 1020 = 5:00 PM)
- Days in schedules: 0 = Sunday, 1 = Monday, ... 6 = Saturday
- The `GET /v2/schedules` endpoint may return 500 errors; use `GET /v2/schedules/{id}` instead
- IMPORTANT: When using curl commands, use `curl -g` when URLs contain brackets to disable glob parsing
- IMPORTANT: When piping curl output to `jq` or other commands, environment variables like `$MATON_API_KEY` may not expand correctly in some shell environments

## Error Handling

| Status | Meaning |
|--------|---------|
| 400 | Missing Cal.com connection or invalid request |
| 401 | Invalid or missing Maton API key |
| 404 | Resource not found |
| 409 | Conflict (duplicate resource) |
| 429 | Rate limited |
| 500 | Cal.com API error |

### Troubleshooting: API Key Issues

1. Check that the `MATON_API_KEY` environment variable is set:

```bash
echo $MATON_API_KEY
```

2. Verify the API key is valid by listing connections:

```bash
python3 <<'EOF'
import urllib.request, os, json
req = urllib.request.Request('https://ctrl.maton.ai/connections')
req.add_header('Authorization', f'Bearer {os.environ["MATON_API_KEY"]}')
print(json.dumps(json.load(urllib.request.urlopen(req)), indent=2))
EOF
```

### Troubleshooting: Invalid App Name

1. Ensure your URL path starts with `cal-com`. For example:

- Correct: `https://gateway.maton.ai/cal-com/v2/me`
- Incorrect: `https://gateway.maton.ai/v2/me`

### Troubleshooting: Booking Creation Fails

1. Check available slots before creating a booking:

```bash
GET /cal-com/v2/slots/available?eventTypeId={id}&startTime=...&endTime=...
```

2. Ensure all required fields are provided:
   - `eventTypeId`
   - `start` (must match an available slot)
   - `timeZone`
   - `language`
   - `responses.name`
   - `responses.email`

## Resources

- [Cal.com API Documentation](https://cal.com/docs/api-reference/v2/introduction)
- [Cal.com API Reference](https://cal.com/docs/api-reference/v2)
- [Maton Community](https://discord.com/invite/dBfFAcefs2)
- [Maton Support](mailto:support@maton.ai)
