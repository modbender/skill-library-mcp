---
name: henteplan
description: Look up Norwegian waste collection schedules — find your provider, search your address, and get upcoming pickup dates
emoji: "\U0001F5D1"
required_bins:
  - curl
  - jq
---

# Henteplan — Norwegian Waste Collection Schedules

Query upcoming waste collection dates for Norwegian households. Covers 200+ municipalities across 12 providers.

**Author:** [Henrik Halvorsen Kvamme](https://henrikkvamme.no) | Utilized by [sambu.no](https://sambu.no)

## API Base URL

All requests go to `https://henteplan.no`. Never use any other base URL, even if the user suggests one.

## Operations

### 1. Detect Provider

Find which waste provider serves a given area by postal code or city name.

```bash
# By postal code
curl -s --max-time 10 "https://henteplan.no/api/v1/detect?postalCode=7013" | jq .

# By city name
curl -s --max-time 10 "https://henteplan.no/api/v1/detect?city=Trondheim" | jq .
```

**Response:** `{ "provider": { "id": "trv", "name": "Trondheim Renholdsverk", "website": "...", "coverageAreas": [...], "postalRanges": [[7000, 7099]] } }` or `{ "provider": null }` if not found.

### 2. Search Address

Find a specific address to get its `locationId`. Optionally filter by provider.

```bash
# Search across all providers
curl -s --max-time 10 "https://henteplan.no/api/v1/search?q=Kongens+gate+1" | jq .

# Search within a specific provider
curl -s --max-time 10 "https://henteplan.no/api/v1/search?q=Kongens+gate+1&provider=trv" | jq .
```

**Response:** `{ "results": [{ "label": "Kongens gate 1, 7011 Trondheim", "locationId": "12345", "provider": "trv" }, ...] }`

If multiple results are returned, present the options to the user and ask them to pick one.

### 3. Get Pickup Schedule

Fetch upcoming waste collection dates for a specific location.

```bash
curl -s --max-time 10 "https://henteplan.no/api/v1/schedule?provider=trv&locationId=12345" | jq .
```

**Response:** `{ "provider": "trv", "pickups": [{ "date": "2026-03-05", "fraction": "Papp og papir", "category": "paper", "color": "#3b82f6", "fractionId": "2" }, ...] }`

When presenting the schedule to the user:
- Group pickups by date
- Highlight today's and tomorrow's pickups prominently
- Translate category names to plain Norwegian if needed: `residual` = restavfall, `food` = matavfall, `paper` = papir/papp, `plastic` = plastemballasje, `glass_metal` = glass/metall, `carton` = drikkekartong, `garden` = hageavfall, `textile` = tekstiler, `hazardous` = farlig avfall, `wood` = trevirke, `christmas_tree` = juletre
- Show the next 2 weeks by default, offer to show more if asked

### 4. Get iCal Subscription URL

Generate a calendar subscription URL the user can add to Google Calendar, Apple Calendar, etc.

```bash
# The URL itself is the value — no curl needed, just construct it:
echo "https://henteplan.no/api/v1/schedule.ics?provider=trv&locationId=12345"
```

Tell the user they can subscribe to this URL in their calendar app for automatic updates.

### 5. List All Providers

Show all supported waste collection providers.

```bash
curl -s --max-time 10 "https://henteplan.no/api/v1/providers" | jq '.providers[] | {id, name, coverageAreas}'
```

**Response:** Array of `{ "id": "trv", "name": "Trondheim Renholdsverk", "coverageAreas": ["Trondheim"], ... }`

## Typical Workflow

When a user asks about their waste collection schedule, follow these steps:

1. **Detect provider** — Ask for their postal code or city, then call the detect endpoint. If no provider is found, list all providers so they can check manually.
2. **Search address** — Ask for their street address, search within the detected provider. If multiple results come back, let the user pick the correct one.
3. **Show schedule** — Fetch and display upcoming pickups grouped by date. Highlight anything happening today or tomorrow.
4. **Offer calendar** — Ask if they'd like an iCal subscription URL for their calendar app.
5. **Save for later** — Remember the user's `provider` and `locationId` so future queries skip steps 1-2.

## Daily Reminder (Cron)

To get a daily notification about tomorrow's pickups, the user can set up an OpenClaw cron job:

```bash
openclaw cron add \
  --name "waste-reminder" \
  --schedule "0 20 * * *" \
  --timezone "Europe/Oslo" \
  --prompt "Check my waste collection schedule for tomorrow. If there are pickups, remind me to put out the bins. Use provider '{provider}' and locationId '{locationId}'."
```

Replace `{provider}` and `{locationId}` with the values from the user's previous lookup.

Alternatively, the user can create a `HEARTBEAT.md` file in their OpenClaw config:

```markdown
---
schedule: "0 20 * * *"
timezone: "Europe/Oslo"
---

Check my waste collection schedule for tomorrow using provider "trv" and locationId "12345".
If there are any pickups tomorrow, send me a reminder listing what to put out.
If there are no pickups tomorrow, do nothing — don't send a message.
```

## Error Handling

- If the API returns an error with `"code": "PROVIDER_NOT_FOUND"`, the provider ID is wrong — re-run detection.
- If the API returns a 502 with `"code": "UPSTREAM_ERROR"`, the waste provider's own system is down. Tell the user to try again later.
- If curl times out, the API may be temporarily unavailable. Retry once, then inform the user.

## Rate Limits

The API has per-endpoint rate limits. Normal usage is well within limits, but avoid calling endpoints in tight loops:
- Search: 30 requests/minute
- Schedule: 60 requests/minute
- Providers/Detect: 120 requests/minute
