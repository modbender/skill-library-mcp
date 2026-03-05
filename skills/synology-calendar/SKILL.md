---
name: synology-calendar
description: Manage Synology Calendar events and todos via API. Supports calendars, events, todos, and contacts. Based on official Calendar API Guide (v5).
---

# Synology Calendar API Skill

## Overview

Manage Synology Calendar using the official Calendar API.

**Documentation:** [Calendar_API_Guide_enu.pdf](references/Calendar_API_Guide_enu.pdf)

## Connection

### Environment Variables

```bash
export SYNOLOGY_URL="http://{nas_ip}:5000"  # 内网地址
export SYNOLOGY_USER="{username}"
export SYNOLOGY_PASSWORD="your-password"
```

### Quick Start

```python
from client import SynologyCalendar

cal = SynologyCalendar()
cal.login()

# List calendars
calendars = cal.get_calendars()
for c in calendars:
    print(f"{c['cal_id']}: {c['cal_displayname']}")

cal.logout()
```

---

## API Reference

### Calendar Operations (SYNO.Cal.Cal)

| Method | Description | Status |
|--------|-------------|--------|
| `get_calendars()` | List all calendars | ✅ Working |
| `get_calendar(cal_id)` | Get calendar details | ✅ Working |
| `create_calendar(...)` | Create calendar | ✅ Working |
| `delete_calendar(cal_id)` | Delete calendar | ✅ Working |

### Event Operations (SYNO.Cal.Event)

| Method | Description | Status |
|--------|-------------|--------|
| `list_events(cal_id_list)` | List events | ✅ Working |
| `get_event(evt_id)` | Get event details | ✅ Working |
| `create_event(...)` | Create event | ✅ Working |
| `delete_event(evt_id)` | Delete event | ✅ Working |

**Event Creation Notes:**

✅ Working:
- All event types now work correctly with v1 API

**⚠️ Critical: SID must be in URL parameter, not JSON body**

The Synology Calendar v1 API requires the `_sid` parameter in the URL query string, not in the JSON body.

**create_event Parameters:**

| Parameter | Type | Required | Example |
|-----------|------|----------|---------|
| cal_id | string | ✅ | `/admin/home/` |
| summary | string | ✅ | Event title |
| dtstart | int | ✅ | 1770440000 |
| dtend | int | ✅ | 1770443600 |
| is_all_day | bool | ✅ | `false` |
| is_repeat_evt | bool | ✅ | `false` |
| color | string | ✅ | `#D9AE00` |
| description | string | ✅ | Description |
| notify_setting | array | ✅ | `[]` |
| participant | array | ✅ | `[]` |
| timezone | string | (if not all-day) | `Asia/Shanghai` |

**Example:**
```python
# Non-all-day event (working)
cal.create_event(
    cal_id='/{username}/home/',
    summary='Meeting',
    dtstart=now,
    dtend=now + 3600,
    is_all_day=False,
    is_repeat_evt=False,
    description='Team meeting',
    color='#D9AE00',
    timezone='Asia/Shanghai'
)
```

### Todo Operations (SYNO.Cal.Todo)

| Method | Description | Status |
|--------|-------------|--------|
| `create_todo(...)` | Create task | ✅ Working |
| `list_todos(...)` | List tasks | ✅ Working |
| `get_todo(evt_id)` | Get task details | ✅ Working |
| `delete_todo(evt_id)` | Delete task | ✅ Working |
| `complete_todo(evt_id)` | Mark complete | ✅ Working |

### Contact Operations (SYNO.Cal.Contact)

| Method | Description | Status |
|--------|-------------|--------|
| `list_contacts()` | List participants | ✅ Working |

---

## CLI Usage

```bash
# Login
python client.py login

# List calendars
python client.py list-calendars

# List todos
python client.py list-todos --cal-id "/{username}/home_todo/"

# Create todo
python client.py create-todo \
  --cal-id "/{username}/home_todo/" \
  --title "Task name"

# Complete todo
python client.py complete-todo --evt-id "1012"
```

---

## Known Issues

### Event Creation (Fixed with v1 API)

**Previous Issue:** Event creation returned error 9009 due to:
1. Using v5 API instead of v1 API
2. Missing `original_cal_id` parameter
3. SID passed in wrong location (JSON body vs URL parameter)

**Solution:** Use v1 API with:
- `cal_id` from `get_calendars()` response
- `original_cal_id` = `cal_id` (for non-shared calendars)
- SID in URL parameter: `?_sid=xxx`


---

## Calendars

| ID | Name | Type |
|----|------|------|
| `/{username}/home/` | My Calendar | event |
| `/{username}/home_todo/` | Inbox | todo |

---

## Links

- [Official API Guide](https://global.download.synology.com/download/Document/Software/DeveloperGuide/Package/Calendar/All/enu/Calendar_API_Guide_enu.pdf)
