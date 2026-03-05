# Calendars & Appointments API Reference

Base: `https://services.leadconnectorhq.com/calendars/`

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/calendars/?locationId={id}` | List calendars |
| POST | `/calendars/` | Create calendar |
| GET | `/calendars/{calendarId}` | Get calendar |
| PUT | `/calendars/{calendarId}` | Update calendar |
| DELETE | `/calendars/{calendarId}` | Delete calendar |
| GET | `/calendars/{calendarId}/free-slots?startDate={}&endDate={}` | Get free slots |
| GET | `/calendars/blocked-slots?locationId={id}` | Get blocked slots |
| GET | `/calendars/events?locationId={id}` | List appointments |
| POST | `/calendars/events` | Create appointment |
| GET | `/calendars/events/{eventId}` | Get appointment |
| PUT | `/calendars/events/{eventId}` | Update appointment |
| DELETE | `/calendars/events/{eventId}` | Delete appointment |
| GET | `/calendars/groups?locationId={id}` | List calendar groups |
| POST | `/calendars/groups` | Create group |
| GET | `/calendars/resources?locationId={id}` | List resources |
| POST | `/calendars/resources` | Create resource |

## Free Slots Parameters
- `startDate` — YYYY-MM-DD (required)
- `endDate` — YYYY-MM-DD (required)
- `timezone` — e.g., "America/New_York" (optional, defaults to location TZ)

## Create Appointment Body
```json
{
  "calendarId": "calendar_id",
  "locationId": "location_id",
  "contactId": "contact_id",
  "startTime": "2026-03-15T10:00:00-05:00",
  "endTime": "2026-03-15T11:00:00-05:00",
  "title": "Strategy Call",
  "appointmentStatus": "confirmed",
  "assignedUserId": "user_id"
}
```

## Scopes Required
`calendars.readonly`, `calendars.write`, `calendars/events.readonly`, `calendars/events.write`, `calendars/groups.readonly`, `calendars/groups.write`, `calendars/resources.readonly`, `calendars/resources.write`
