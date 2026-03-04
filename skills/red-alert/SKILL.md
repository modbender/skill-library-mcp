---
name: red-alert
version: 1.1.0
description: Israel Red Alert API — real-time and historical rocket/missile alert data. Query alerts by city, time range, generate shelter time stats. Uses redalert.orielhaim.com (socket.io for real-time) and tzevaadom.co.il (REST for history).
provides:
  - capability: israel-alerts
    methods: [history, realtime, shelter-stats]
credentials:
  - name: RED_ALERT_API_KEY
    required: false
    description: API key from redalert.orielhaim.com — optional, used for authenticated socket.io real-time connection. History via tzevaadom works without any key.
dependencies:
  - name: socket.io-client
    type: npm
    required: false
    description: Only needed for real-time alerts (realtime.mjs). History analysis works without it.
---

# Red Alert — Israel Emergency Alerts

Real-time and historical alert data for Israeli cities. Track rocket alerts, calculate shelter time, generate charts.

## Get an API Key

Sign up at **<https://redalert.orielhaim.com/>** to get your API key. Store it as env var `RED_ALERT_API_KEY`.

This skill is a wrapper around the RedAlert API — it provides convenient CLI tools for querying, analyzing, and visualizing alert data.

## Data Sources

| Source | Type | Auth | Use For |
|--------|------|------|---------|
| `api.tzevaadom.co.il` | REST | None | Alert history (last ~24h, 50 records) |
| `redalert.orielhaim.com` | Socket.IO | `RED_ALERT_API_KEY` | Real-time alerts, status |

## Setup

```bash
# API key is stored as Fly secret: RED_ALERT_API_KEY
# Socket.io client needed for real-time
cd /data/clawd/skills/red-alert/scripts && npm install
```

## Quick Usage

### Get Alert History (REST)
```bash
# Last ~24h of alerts nationwide (50 most recent alert groups)
curl -s "https://api.tzevaadom.co.il/alerts-history" -o /tmp/alerts.json
```

Response format:
```json
[{
  "id": 5718,
  "description": null,
  "alerts": [{
    "time": 1772352828,     // Unix timestamp
    "cities": ["כפר סבא", "תל אביב"],
    "threat": 0,            // 0=rockets, 1=aircraft, 5=infiltration
    "isDrill": false
  }]
}]
```

### Check System Status
```bash
curl -s -H "Accept: application/json" "https://redalert.orielhaim.com/api/status"
```

### Real-Time Alerts (Socket.IO)
```bash
node /data/clawd/skills/red-alert/scripts/realtime.mjs
# Listens for: alert, rockets, hostileAircraftIntrusion, tsunami, earthquake
```

### Analyze Shelter Time for a City
```bash
node /data/clawd/skills/red-alert/scripts/analyze.mjs --city "כפר סבא" --since "2026-02-28T08:00"
# Outputs: alert count, shelter sessions, total shelter time, hourly data as JSON
```

## Threat Types

| Code | Type (Hebrew) | Type (English) | Shelter Time |
|------|---------------|----------------|--------------|
| 0 | רקטות וטילים | Rockets & Missiles | 15s-90s (varies by city) |
| 1 | חדירת כלי טיס עוין | Hostile Aircraft | 10 min |
| 2 | רעידת אדמה | Earthquake | Until safe |
| 3 | צונאמי | Tsunami | Evacuate coast |
| 5 | חדירת מחבלים | Terrorist Infiltration | Stay inside |

## Shelter Times by Region (for rockets)

| Region | Time |
|--------|------|
| Gaza envelope | 15 seconds |
| Ashkelon, Sderot | 30 seconds |
| Beer Sheva, Ashdod | 45 seconds |
| Tel Aviv, Kfar Saba, Netanya | 90 seconds |
| Haifa, Hadera | 60 seconds |
| North (border) | 30 seconds |

## Combining with Chart/Table Skills

```bash
# Generate hourly alert chart
node /data/clawd/skills/red-alert/scripts/analyze.mjs --city "כפר סבא" --since "2026-02-28T08:00" --format chart-json \
  | node /data/clawd/skills/chart-image/scripts/chart.mjs --type bar --dark --title "Kfar Saba Alerts" --output alerts.png

# Generate shelter session table
node /data/clawd/skills/red-alert/scripts/analyze.mjs --city "כפר סבא" --since "2026-02-28T08:00" --format table-json \
  | node /data/clawd/skills/table-image/scripts/table.mjs --dark --title "Shelter Sessions" --output shelter.png
```

## Architecture Notes

- **redalert.orielhaim.com** — Oriel Haim's service. Polls Pikud HaOref, redistributes via Socket.IO. Has better-auth for API key management. REST endpoints blocked by Cloudflare challenge (except `/api/status`).
- **api.tzevaadom.co.il** — Free REST API, no auth needed, returns last ~24h of alert history.
- **Pikud HaOref direct** (`oref.org.il`) — Blocked from cloud IPs (Akamai WAF).

## Limitations

- History limited to ~24h (50 groups) from tzevaadom
- For longer history, would need to store alerts ourselves via socket.io listener
- Real-time requires persistent socket.io connection
