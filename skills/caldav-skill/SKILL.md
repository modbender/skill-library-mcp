---
name: caldav
description: Manage CalDAV calendars and events, with special support for Radicale server. Use when the user wants to create, update, delete, or query calendar events, manage calendars, or configure/administer a Radicale CalDAV server.
homepage: https://github.com/python-caldav/caldav
metadata:
  clawdbot:
    emoji: "📅"
    requires:
      bins: ["python3"]
      env: []
---

# CalDAV & Radicale Management

Interact with CalDAV servers (calendars, events, todos) and manage Radicale server configurations.

## Overview

CalDAV is a protocol for accessing and managing calendaring information (RFC 4791). Radicale is a lightweight CalDAV/CardDAV server. This skill enables:

- Calendar CRUD operations (create, list, update, delete)
- Event management (create, update, delete, query)
- Todo/task management
- Radicale server configuration and administration

## Prerequisites

### Python Library

Install the caldav library:

```bash
pip install caldav
```

For async support:
```bash
pip install caldav[async]
```

### Environment Variables (Recommended)

Store credentials securely in environment or config:

```bash
export CALDAV_URL="http://localhost:5232"
export CALDAV_USER="your_username"
export CALDAV_PASSWORD="your_password"
```

Or use a config file at `~/.config/caldav/config.json`:

```json
{
  "url": "http://localhost:5232",
  "username": "your_username",
  "password": "your_password"
}
```

## Scripts

### Calendar Operations

```bash
# List all calendars
python3 {baseDir}/scripts/calendars.py list

# Create a new calendar
python3 {baseDir}/scripts/calendars.py create --name "Work Calendar" --id work

# Delete a calendar
python3 {baseDir}/scripts/calendars.py delete --id work

# Get calendar info
python3 {baseDir}/scripts/calendars.py info --id work
```

### Event Operations

```bash
# List events (all calendars, next 30 days)
python3 {baseDir}/scripts/events.py list

# List events from specific calendar
python3 {baseDir}/scripts/events.py list --calendar work

# List events in date range
python3 {baseDir}/scripts/events.py list --start 2024-01-01 --end 2024-01-31

# Create an event
python3 {baseDir}/scripts/events.py create \
  --calendar work \
  --summary "Team Meeting" \
  --start "2024-01-15 14:00" \
  --end "2024-01-15 15:00" \
  --description "Weekly sync"

# Create all-day event
python3 {baseDir}/scripts/events.py create \
  --calendar personal \
  --summary "Birthday" \
  --start 2024-02-14 \
  --allday

# Update an event
python3 {baseDir}/scripts/events.py update \
  --uid "event-uid-here" \
  --summary "Updated Title"

# Delete an event
python3 {baseDir}/scripts/events.py delete --uid "event-uid-here"

# Search events by text
python3 {baseDir}/scripts/events.py search --query "meeting"
```

### Todo Operations

```bash
# List todos
python3 {baseDir}/scripts/todos.py list [--calendar name]

# Create a todo
python3 {baseDir}/scripts/todos.py create \
  --calendar work \
  --summary "Complete report" \
  --due "2024-01-20"

# Complete a todo
python3 {baseDir}/scripts/todos.py complete --uid "todo-uid-here"

# Delete a todo
python3 {baseDir}/scripts/todos.py delete --uid "todo-uid-here"
```

### Radicale Server Management

```bash
# Check Radicale status
python3 {baseDir}/scripts/radicale.py status

# List users (from htpasswd file)
python3 {baseDir}/scripts/radicale.py users list

# Add user
python3 {baseDir}/scripts/radicale.py users add --username newuser

# View Radicale config
python3 {baseDir}/scripts/radicale.py config show

# Validate Radicale config
python3 {baseDir}/scripts/radicale.py config validate

# Check storage integrity
python3 {baseDir}/scripts/radicale.py storage verify
```

## Direct HTTP/DAV Operations

For low-level operations, use curl with CalDAV:

```bash
# Discover principal URL
curl -u user:pass -X PROPFIND \
  -H "Depth: 0" \
  -H "Content-Type: application/xml" \
  -d '<d:propfind xmlns:d="DAV:"><d:prop><d:current-user-principal/></d:prop></d:propfind>' \
  http://localhost:5232/

# List calendars
curl -u user:pass -X PROPFIND \
  -H "Depth: 1" \
  -H "Content-Type: application/xml" \
  -d '<d:propfind xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav"><d:prop><d:displayname/><c:calendar-timezone/><d:resourcetype/></d:prop></d:propfind>' \
  http://localhost:5232/user/

# Query events by time range
curl -u user:pass -X REPORT \
  -H "Depth: 1" \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0" encoding="utf-8"?>
<c:calendar-query xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
  <d:prop><d:getetag/><c:calendar-data/></d:prop>
  <c:filter>
    <c:comp-filter name="VCALENDAR">
      <c:comp-filter name="VEVENT">
        <c:time-range start="20240101T000000Z" end="20240131T235959Z"/>
      </c:comp-filter>
    </c:comp-filter>
  </c:filter>
</c:calendar-query>' \
  http://localhost:5232/user/calendar/

# Create calendar (MKCALENDAR)
curl -u user:pass -X MKCALENDAR \
  -H "Content-Type: application/xml" \
  -d '<?xml version="1.0" encoding="utf-8"?>
<d:mkcalendar xmlns:d="DAV:" xmlns:c="urn:ietf:params:xml:ns:caldav">
  <d:set><d:prop>
    <d:displayname>New Calendar</d:displayname>
  </d:prop></d:set>
</d:mkcalendar>' \
  http://localhost:5232/user/new-calendar/
```

## Radicale Configuration

### Config File Location

Radicale looks for config in:
- `/etc/radicale/config` (system-wide)
- `~/.config/radicale/config` (user)
- Custom path via `--config` or `RADICALE_CONFIG` env

### Key Configuration Sections

```ini
[server]
hosts = localhost:5232
max_connections = 20
max_content_length = 100000000
timeout = 30
ssl = False

[auth]
type = htpasswd
htpasswd_filename = /etc/radicale/users
htpasswd_encryption = autodetect

[storage]
filesystem_folder = /var/lib/radicale/collections

[rights]
type = owner_only
```

### Authentication Types

| Type | Description |
|------|-------------|
| `none` | No authentication (development only!) |
| `denyall` | Deny all (default since 3.5.0) |
| `htpasswd` | Apache htpasswd file |
| `remote_user` | WSGI-provided username |
| `http_x_remote_user` | Reverse proxy header |
| `ldap` | LDAP/AD authentication |
| `dovecot` | Dovecot auth socket |
| `imap` | IMAP server authentication |
| `oauth2` | OAuth2 authentication |
| `pam` | PAM authentication |

### Creating htpasswd Users

```bash
# Create new file with SHA-512
htpasswd -5 -c /etc/radicale/users user1

# Add another user
htpasswd -5 /etc/radicale/users user2
```

### Running as Service (systemd)

```bash
# Enable and start
sudo systemctl enable radicale
sudo systemctl start radicale

# Check status
sudo systemctl status radicale

# View logs
journalctl -u radicale -f
```

## iCalendar Format Quick Reference

Events use iCalendar (RFC 5545) format:

```ics
BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Example Corp//CalDAV Client//EN
BEGIN:VEVENT
UID:unique-id@example.com
DTSTAMP:20240115T120000Z
DTSTART:20240115T140000Z
DTEND:20240115T150000Z
SUMMARY:Team Meeting
DESCRIPTION:Weekly sync
LOCATION:Conference Room
END:VEVENT
END:VCALENDAR
```

### Common Properties

| Property | Description |
|----------|-------------|
| `UID` | Unique identifier |
| `DTSTART` | Start time |
| `DTEND` | End time |
| `DTSTAMP` | Creation/modification time |
| `SUMMARY` | Event title |
| `DESCRIPTION` | Event description |
| `LOCATION` | Location |
| `RRULE` | Recurrence rule |
| `EXDATE` | Excluded dates |
| `ATTENDEE` | Participant |
| `ORGANIZER` | Event organizer |
| `STATUS` | CONFIRMED/TENTATIVE/CANCELLED |

### Date Formats

```
# DateTime with timezone
DTSTART:20240115T140000Z  ; UTC (Z suffix)
DTSTART;TZID=America/New_York:20240115T090000

# All-day event
DTSTART;VALUE=DATE:20240214

# DateTime local (floating)
DTSTART:20240115T140000
```

## Troubleshooting

### Connection Issues

```bash
# Test basic connectivity
curl -v http://localhost:5232/

# Check with authentication
curl -v -u user:pass http://localhost:5232/

# Verify CalDAV support
curl -X OPTIONS http://localhost:5232/ -I | grep -i dav
```

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| 401 Unauthorized | Wrong credentials | Check htpasswd file |
| 403 Forbidden | Rights restriction | Check `[rights]` config |
| 404 Not Found | Wrong URL path | Check principal/calendar path |
| 409 Conflict | Resource exists | Use different UID |
| 415 Unsupported Media Type | Wrong Content-Type | Use `text/calendar` |

### Debug Mode

Run Radicale with debug logging:
```bash
python3 -m radicale --debug
```

## Python API Quick Reference

```python
from caldav import DAVClient

# Connect
client = DAVClient(
    url="http://localhost:5232",
    username="user",
    password="pass"
)

# Get principal
principal = client.principal()

# List calendars
for cal in principal.calendars():
    print(f"Calendar: {cal.name} ({cal.url})")

# Create calendar
cal = principal.make_calendar(name="My Calendar", cal_id="my-cal")

# Create event
cal.save_event(
    dtstart="2024-01-15 14:00",
    dtend="2024-01-15 15:00",
    summary="Meeting"
)

# Query events by date range
events = cal.date_search(
    start="2024-01-01",
    end="2024-01-31"
)
for event in events:
    print(event.vobject_instance.vevent.summary.value)

# Get event by UID
event = cal.event_by_uid("event-uid")

# Delete event
event.delete()

# Create todo
todo = cal.save_todo(
    summary="Task",
    due="2024-01-20"
)
```

## Workflow Examples

### Create Recurring Event

```bash
python3 {baseDir}/scripts/events.py create \
  --calendar work \
  --summary "Weekly Standup" \
  --start "2024-01-15 09:00" \
  --end "2024-01-15 09:30" \
  --rrule "FREQ=WEEKLY;BYDAY=MO,WE,FR"
```

### Export Calendar to ICS

```bash
# Via curl
curl -u user:pass http://localhost:5232/user/calendar/ > calendar.ics

# Via script
python3 {baseDir}/scripts/calendars.py export --id work --output work.ics
```

### Sync with Git (Radicale)

Configure Radicale to version changes:

```ini
[storage]
hook = git add -A && (git diff --cached --quiet || git commit -m "Changes by \"%(user)s\"")
```

Initialize git in storage folder:
```bash
cd /var/lib/radicale/collections
git init
git config user.email "radicale@localhost"
```
