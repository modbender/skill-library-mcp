# CalDAV Protocol Reference

## Overview

CalDAV (RFC 4791) is an HTTP-based protocol for accessing calendar data. iCloud implements a standard CalDAV server at `caldav.icloud.com`.

## Authentication

iCloud uses Basic Auth with:
- Username: Your Apple ID email
- Password: An **app-specific password** (not your regular iCloud password)

## Key Endpoints

### Discovery

```
PROPFIND /
Depth: 0
```

Returns `current-user-principal` — your unique iCloud user path.

### Calendar Home

```
PROPFIND /12345678/principal/
Depth: 0
```

Returns `calendar-home-set` — where your calendars live.

### List Calendars

```
PROPFIND /12345678/calendars/
Depth: 1
```

Returns all calendars with their properties (display name, read-only status, etc.)

### Query Events

```
REPORT /12345678/calendars/CalendarName/
Depth: 1
Content-Type: text/xml

<calendar-query xmlns="DAV:" xmlns:cal="urn:ietf:params:xml:ns:caldav">
  <prop>
    <cal:calendar-data/>
  </prop>
  <filter>
    <cal:comp-filter name="VCALENDAR">
      <cal:comp-filter name="VEVENT">
        <cal:time-range start="20250720T000000Z" end="20250727T000000Z"/>
      </cal:comp-filter>
    </cal:comp-filter>
  </filter>
</calendar-query>
```

### Create Event (PUT)

```
PUT /12345678/calendars/CalendarName/event-uuid.ics
Content-Type: text/calendar; charset=utf-8

BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//OpenClaw//iCloud CalDAV//EN
BEGIN:VEVENT
UID:event-uuid@openclaw
DTSTAMP:20250720T120000Z
DTSTART:20250725T140000Z
DTEND:20250725T150000Z
SUMMARY:Meeting
DESCRIPTION:Project review
LOCATION:Conference Room
END:VEVENT
END:VCALENDAR
```

### Update Event

Same as create, but with existing UID. iCloud merges/overwrites based on UID.

### Delete Event

```
DELETE /12345678/calendars/CalendarName/event-uuid.ics
```

## iCalendar (ICS) Format

Key properties for events:

| Property | Description | Example |
|----------|-------------|---------|
| UID | Unique identifier | `uid-123@openclaw` |
| DTSTAMP | Creation timestamp | `20250720T120000Z` |
| DTSTART | Start time | `20250725T140000Z` |
| DTEND | End time | `20250725T150000Z` |
| SUMMARY | Title | `Team Meeting` |
| DESCRIPTION | Notes | `Agenda: review Q3` |
| LOCATION | Place | `Room 302` |
| RRULE | Recurrence | `FREQ=WEEKLY;COUNT=10` |

## Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 OK | Success |
| 201 Created | Resource created |
| 204 No Content | Success, no body |
| 401 Unauthorized | Bad credentials |
| 403 Forbidden | Read-only or no access |
| 404 Not Found | Resource doesn't exist |
| 412 Precondition Failed | ETag mismatch (concurrent edit) |

## References

- [RFC 4791: CalDAV](https://tools.ietf.org/html/rfc4791)
- [RFC 5545: iCalendar](https://tools.ietf.org/html/rfc5545)
- [Apple Support: App-Specific Passwords](https://support.apple.com/en-us/102654)