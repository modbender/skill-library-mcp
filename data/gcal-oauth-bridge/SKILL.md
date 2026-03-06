---
name: calendar-bridge
description: Interact with the Calendar Bridge — a self-hosted Node.js service that provides a persistent REST API for Google Calendar events. Handles OAuth token auto-refresh so you never have to re-authenticate. Use when checking upcoming events, listing calendars, setting up Google Calendar access, or troubleshooting calendar auth.
homepage: https://github.com/DanielKillenberger/gcal-oauth-bridge
version: 1.0.2
read_when:
  - User asks about upcoming events or calendar
  - User asks what's scheduled or what meetings they have
  - Calendar Bridge setup or troubleshooting needed
metadata:
  {
    "openclaw":
      {
        "emoji": "📅",
        "requires": { "env": ["GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET"] },
        "optional": { "env": ["CALENDAR_BRIDGE_API_KEY"] },
        "notes": "GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET are required for initial OAuth setup only — once authenticated, the agent only needs network access to localhost:3000. CALENDAR_BRIDGE_API_KEY is optional; if set, the agent must send it as Authorization: Bearer <key> when calling /events. Tokens stored locally in tokens.json on your server, never sent externally."
      }
  }
triggers:
  - what's on my calendar
  - upcoming events
  - check my calendar
  - do I have anything scheduled
  - what meetings do I have
  - calendar today
  - calendar this week
  - calendar next week
  - list my calendars
  - google calendar
  - calendar bridge
  - set up calendar
  - calendar auth
  - calendar access
  - calendar not working
---

# Calendar Bridge Skill

Use this skill to interact with the Calendar Bridge service — a local REST API that wraps Google Calendar OAuth with persistent token storage and auto-refresh.

**GitHub:** https://github.com/DanielKillenberger/gcal-oauth-bridge

## What is Calendar Bridge?

A tiny Node.js/Express service running at `http://localhost:3000` that:
- Handles Google Calendar OAuth once via browser
- Stores and auto-refreshes tokens (solves the "token expired every 7 days" problem)
- Exposes a dead-simple REST API for events, calendars, and auth

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /health` | Service status + auth state |
| `GET /auth/url` | Get OAuth consent URL |
| `GET /events?days=7` | Upcoming events from primary calendar |
| `GET /events?days=7&calendar=all` | Events from ALL calendars |
| `GET /events?days=7&calendar=<id>` | Events from a specific calendar |
| `GET /calendars` | List all available calendars |
| `POST /auth/refresh` | Force token refresh (normally automatic) |

Events response includes: `id`, `summary`, `start`, `end`, `location`, `description`, `htmlLink`, `status`, `calendarId`, `calendarSummary`

## Checking Events

```bash
# Quick event check (7 days, primary calendar)
curl http://localhost:3000/events

# All calendars, next 14 days
curl http://localhost:3000/events?days=14&calendar=all

# With API key (if CALENDAR_BRIDGE_API_KEY is configured)
curl -H "Authorization: Bearer $API_KEY" http://localhost:3000/events?calendar=all
```

To call from OpenClaw/skill context (no API key needed when running on same host):
```
GET http://localhost:3000/events?calendar=all&days=7
```

## First-Time Setup

### 1. Clone and install
```bash
git clone https://github.com/DanielKillenberger/gcal-oauth-bridge.git
cd gcal-oauth-bridge
npm install
cp .env.example .env
# Edit .env with GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET
```

### 2. Get Google OAuth credentials
- Go to https://console.cloud.google.com/apis/credentials
- Create OAuth 2.0 Client ID (Desktop app)
- Enable Google Calendar API
- Add redirect URI: `http://localhost:3000/auth/callback`
- Copy Client ID + Secret to `.env`

### 3. Start the service
```bash
node app.js
# or: npm start
```

### 4. Authorize (one-time browser flow)
If on a remote VPS, first tunnel port 3000:
```bash
# From your local machine:
ssh -L 3000:localhost:3000 your-server
```

Then:
```bash
curl http://localhost:3000/auth/url
# Open the returned URL in your browser
# Complete Google consent → tokens saved automatically
```

Verify:
```bash
curl http://localhost:3000/health
# {"status":"ok","authenticated":true,"needsRefresh":false}
```

### 5. Keep it running (systemd)
```bash
systemctl --user enable calendar-bridge.service
systemctl --user start calendar-bridge.service
```

## Re-authentication

If tokens are ever revoked (rare — auto-refresh prevents expiry):
1. `ssh -L 3000:localhost:3000 your-server`
2. `curl http://localhost:3000/auth/url` → open URL → complete consent
3. Done — new tokens overwrite old ones

## Troubleshooting

- **`{"error":"Not authenticated"}`** → Run the OAuth setup flow above
- **`401 Unauthorized`** → `CALENDAR_BRIDGE_API_KEY` is set; add `Authorization: Bearer <key>` header
- **Can't reach localhost:3000** → Service not running; check `systemctl --user status calendar-bridge`
- **"invalid_grant" / "token expired"** → Tokens were revoked externally; re-authenticate

## Personal Gmail Users

Works with personal Gmail. Google shows an "unverified app" warning — click **Advanced → Go to [app]** to proceed. Tokens are stored locally on your server, not shared with anyone.

## Files

- **GitHub repo:** https://github.com/DanielKillenberger/gcal-oauth-bridge
- App: `app.js` — main Express server
- Config: `.env` (from `.env.example`)
- Tokens: `tokens.json` (auto-generated, gitignored, never committed)
