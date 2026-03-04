---
name: zoom-meeting
description: >
  Create or delete Zoom meetings via Server-to-Server OAuth.
  Use this skill when the user asks to: schedule a Zoom call, create a Zoom meeting,
  set up a video conference, book a Zoom session, cancel a Zoom meeting, delete a Zoom meeting,
  or remove a scheduled Zoom call.
  Returns join URL, meeting ID, and password on creation.
  Requires Zoom Server-to-Server OAuth credentials at .openclaw/credentials/zoom.json.
metadata:
  {
    "clawdbot":
      {
        "emoji": "📹",
        "version": "1.1.0",
        "author": "Neuyazvimyi",
        "tags":
          [
            "zoom",
            "meetings",
            "video-conference",
            "scheduling",
            "delete",
            "cancel",
          ],
        "requires": { "credentials": [".openclaw/credentials/zoom.json"] },
      },
  }
allowed-tools: [exec]
---

# Zoom Meeting 📹

Create and delete Zoom meetings via the Zoom API using Server-to-Server OAuth.

## Scripts Overview

| Script                   | Purpose                                 | Key Input         | Key Output             |
| ------------------------ | --------------------------------------- | ----------------- | ---------------------- |
| `zoom_meeting.sh`        | Create a scheduled meeting              | topic, start_time | join_url, id, password |
| `zoom_delete_meeting.sh` | Delete a meeting by ID                  | meeting_id        | confirmation JSON      |
| `zoom_auth.sh`           | Shared auth helper (sourced internally) | creds file path   | access token           |

---

## Create a Meeting

```bash
bash skills/zoom-meeting/scripts/zoom_meeting.sh <topic> <start_time> [duration] [timezone]
```

### Parameters

| Param        | Type    | Required | Default       | Description                                                        |
| ------------ | ------- | -------- | ------------- | ------------------------------------------------------------------ |
| `topic`      | string  | ✅       | —             | Meeting title shown to participants                                |
| `start_time` | string  | ✅       | —             | Start time in `YYYY-MM-DDTHH:MM:SS` format, **no timezone suffix** |
| `duration`   | integer | ❌       | `60`          | Duration in minutes                                                |
| `timezone`   | string  | ❌       | `Asia/Aqtobe` | IANA timezone name (e.g. `Europe/London`, `America/New_York`)      |

### Examples

```bash
# Minimal — 60 min meeting in default timezone
bash skills/zoom-meeting/scripts/zoom_meeting.sh "Team Standup" "2026-03-01T09:00:00"

# Full — custom duration and timezone
bash skills/zoom-meeting/scripts/zoom_meeting.sh "Product Review" "2026-03-15T14:30:00" 45 "Europe/London"
```

### Output

```json
{
  "join_url": "https://us05web.zoom.us/j/123456789?pwd=...",
  "id": 123456789,
  "password": "abc123"
}
```

### Meeting Settings (fixed)

| Setting           | Value              |
| ----------------- | ------------------ |
| Type              | Scheduled (type 2) |
| Host video        | on                 |
| Participant video | on                 |
| Join before host  | allowed            |

---

## Delete a Meeting

```bash
bash skills/zoom-meeting/scripts/zoom_delete_meeting.sh <meeting_id>
```

### Parameters

| Param        | Type    | Required | Description                                         |
| ------------ | ------- | -------- | --------------------------------------------------- |
| `meeting_id` | integer | ✅       | Zoom Meeting ID (the `id` field from create output) |

### Example

```bash
bash skills/zoom-meeting/scripts/zoom_delete_meeting.sh 123456789
```

### Output

```json
{ "status": "deleted", "meeting_id": "123456789" }
```

---

## Error Handling

| Situation                       | Script behaviour                                                     |
| ------------------------------- | -------------------------------------------------------------------- |
| Missing required argument       | Exits with usage message                                             |
| Invalid `start_time` format     | Exits with format hint                                               |
| Bad credentials / OAuth failure | Exits with `ERROR: Failed to get Zoom access token`                  |
| Meeting creation failed         | Exits with `ERROR: Failed to create Zoom meeting` + raw API response |
| Meeting not found (delete)      | Exits with `ERROR: Meeting <id> not found`                           |
| Other API error (delete)        | Exits with `ERROR: Failed to delete meeting (HTTP <code>)`           |

---

## Credentials Setup

### File location

```
.openclaw/credentials/zoom.json
```

Override path via environment variable:

```bash
ZOOM_CREDENTIALS=/custom/path/zoom.json bash skills/zoom-meeting/scripts/zoom_meeting.sh ...
```

### File format

```json
{
  "account_id": "YOUR_ACCOUNT_ID",
  "client_id": "YOUR_CLIENT_ID",
  "client_secret": "YOUR_CLIENT_SECRET"
}
```

### How to obtain

1. Go to [marketplace.zoom.us](https://marketplace.zoom.us) → **Develop** → **Build App**
2. Choose **Server-to-Server OAuth**
3. Add the following scopes:

| Scope                  | Required for            |
| ---------------------- | ----------------------- |
| `meeting:write:admin`  | Creating meetings       |
| `meeting:read:admin`   | Reading meeting details |
| `meeting:delete:admin` | Deleting meetings       |

4. Copy **Account ID**, **Client ID**, **Client Secret** into `.openclaw/credentials/zoom.json`
