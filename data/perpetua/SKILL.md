---
name: perpetua
description: "OAuth proxy for calling external APIs (Oura, Google Calendar, etc.) via Perpetua.sh hosted API using a single API key. Use when fetching Oura data, Google Calendar events, or managing OAuth connections."
version: "1.0.0"
read_when:
  - User asks about Oura Ring data (sleep, readiness, activity, workouts, HRV)
  - User asks about Google Calendar events or schedule
  - User wants to add or manage OAuth provider connections
  - Perpetua proxy setup or troubleshooting
  - User asks what's on their calendar or how they slept
triggers:
  - oura
  - sleep score
  - readiness score
  - hrv
  - perpetua
  - oauth proxy
  - calendar
  - google calendar
metadata:
  {
    "openclaw":
      {
        "emoji": "🔑",
        "kind": "service",
        "notes": "Primary endpoint is hosted Perpetua.sh API at https://www.perpetua.sh/api."
      }
  }
---

# Perpetua Skill (Hosted)

## Overview

Use **Perpetua.sh hosted API** as the default path:

- Base URL: `https://www.perpetua.sh`
- API routes: `/api/*`
- Auth: `Authorization: Bearer $PERPETUA_API_KEY`

Load secrets with:

```bash
op run --env-file="$HOME/.openclaw/secrets.env" -- <command>
```

## Credentials

Set API key via env var from any secret source (1Password, CI, `.env`, secret manager):

```bash
export PERPETUA_API_KEY="<your-key>"
```

## Core endpoints (hosted)

```bash
# Connection status summary
curl -s "https://www.perpetua.sh/api/status" \
  -H "Authorization: Bearer $PERPETUA_API_KEY"

# Active connections
curl -s "https://www.perpetua.sh/api/connections" \
  -H "Authorization: Bearer $PERPETUA_API_KEY"

# Providers
curl -s "https://www.perpetua.sh/api/providers" \
  -H "Authorization: Bearer $PERPETUA_API_KEY"
```

## Proxy call pattern

```bash
GET https://www.perpetua.sh/api/proxy/:provider/:path
Authorization: Bearer $PERPETUA_API_KEY
```

Optional: `?account=default` for explicit account selection.

### Oura examples

> Avoid huge endpoints (`daily_activity`, detailed `sleep`) unless explicitly needed.

```bash
# Daily sleep
curl -s "https://www.perpetua.sh/api/proxy/oura/v2/usercollection/daily_sleep?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&account=default" \
  -H "Authorization: Bearer $PERPETUA_API_KEY" | jq .

# Daily readiness
curl -s "https://www.perpetua.sh/api/proxy/oura/v2/usercollection/daily_readiness?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&account=default" \
  -H "Authorization: Bearer $PERPETUA_API_KEY" | jq .

# Workout
curl -s "https://www.perpetua.sh/api/proxy/oura/v2/usercollection/workout?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&account=default" \
  -H "Authorization: Bearer $PERPETUA_API_KEY" | jq .
```

### Google Calendar examples

```bash
# Upcoming primary calendar events
curl -s "https://www.perpetua.sh/api/proxy/gcal/calendars/primary/events?account=default&maxResults=10&orderBy=startTime&singleEvents=true&timeMin=$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  -H "Authorization: Bearer $PERPETUA_API_KEY" | jq '[.items[] | {summary, start}]'

# Calendar list
curl -s "https://www.perpetua.sh/api/proxy/gcal/users/me/calendarList?account=default" \
  -H "Authorization: Bearer $PERPETUA_API_KEY" | jq .
```

## Connection management (hosted)

```bash
# Start OAuth flow for provider
curl -s -X POST "https://www.perpetua.sh/api/auth/connect/:provider/start" \
  -H "Authorization: Bearer $PERPETUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"account":"default"}' | jq .authUrl
```

## Troubleshooting

- `401` → wrong/expired API key
- `403/404` on provider routes → missing connection or wrong provider/account
- `5xx` → hosted service issue; retry and/or notify Daniel

## Local OSS note

Local `http://localhost:3001` is for OSS development only. Default operational path in this workspace is hosted Perpetua.sh.
