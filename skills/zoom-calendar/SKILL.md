---
name: zoom-calendar
description: >
  Create Zoom meetings and add them to Google Calendar events with proper conferenceData
  (icon, video entry, notes). Use when creating calendar events with Zoom, adding Zoom to
  existing events, or any Zoom + Google Calendar integration. Requires Zoom Server-to-Server
  OAuth credentials and Google Calendar (gog) auth.
metadata: {"clawdbot":{"emoji":"📹","version":"1.0.0","author":"Leo 🦁","tags":["zoom","calendar","google-calendar","meetings","video-conference","scheduling"],"requires":{"env":["GOG_KEYRING_PASSWORD","GOG_ACCOUNT"],"credentials":[".credentials/zoom.json"]}}}
allowed-tools: [exec]
---

# Zoom + Google Calendar 📹

Create Zoom meetings via API and attach them to Google Calendar events — identical to the Zoom for Google Workspace add-on UI.

## Quick Usage

```bash
bash skills/zoom-calendar/scripts/zoom_meeting.sh <event_id> "Meeting Title" "2026-03-01T11:50:00" 60
```

**Parameters:**
| Param | Description | Example |
|-------|-------------|---------|
| `event_id` | Google Calendar event ID | `dgth9d45bb93a0q7ohfnckq88k` |
| `topic` | Meeting title | `"Team Meeting"` |
| `start_time` | ISO format, no timezone (Jerusalem assumed) | `"2026-03-01T11:50:00"` |
| `duration` | Minutes (optional, default 60) | `45` |

**Output:** Join URL, Meeting ID, Password + event patched automatically.

## Typical Workflow

1. Create calendar event with `gog calendar create`
2. Run `zoom_meeting.sh` with the event ID
3. Done — conferenceData with icon, video link, and notes are set

## Critical Rules

| Rule | Detail |
|------|--------|
| **iconUri** | Use EXACTLY the URL in the script — official Zoom Marketplace icon |
| **entryPoints** | ONLY `video` — no phone, no SIP |
| **`passcode`** | Not `pin` — field name matters |
| **`meetingCode`** | Include the meeting ID here too |
| **notes** | Use `<br />` for line breaks (not `\n`) |
| **description** | Leave empty — don't duplicate info |
| **location** | Leave empty — Zoom link lives in conferenceData |
| **Default** | Do NOT add Zoom unless explicitly requested |

## Auth Setup

### Zoom (Server-to-Server OAuth)

Credentials: `.credentials/zoom.json`
```json
{"account_id": "...", "client_id": "...", "client_secret": "..."}
```

Create at marketplace.zoom.us → Develop → Server-to-Server OAuth.
Scopes: `meeting:write:admin`, `meeting:read:admin`.

### Google Calendar

Uses `gog` CLI auth. The script handles token export + refresh automatically.
Requires: `GOG_KEYRING_PASSWORD` and `GOG_ACCOUNT` env vars.
