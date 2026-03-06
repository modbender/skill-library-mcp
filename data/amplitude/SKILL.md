---
name: amplitude
description: "Amplitude product analytics — track events, analyze user behavior, run cohort analysis, manage user properties, and query funnel/retention data via the Amplitude API. Understand product usage, measure feature adoption, and analyze user journeys. Built for AI agents — Python stdlib only, zero dependencies. Use for product analytics, user behavior tracking, funnel analysis, retention analysis, and cohort segmentation."
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+ (stdlib only — no dependencies)
metadata: {"openclaw": {"emoji": "📉", "requires": {"env": ["AMPLITUDE_API_KEY", "AMPLITUDE_SECRET_KEY"]}, "primaryEnv": "AMPLITUDE_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# 📉 Amplitude

Amplitude product analytics — track events, analyze user behavior, run cohort analysis, manage user properties, and query funnel/retention data via the Amplitude API.

## Features

- **Event tracking** — log user events with properties
- **User analytics** — active users, sessions, engagement
- **Funnel analysis** — conversion through event sequences
- **Retention analysis** — user return rates over time
- **Cohort management** — create and manage user cohorts
- **User properties** — set and query user attributes
- **Revenue analytics** — LTV, ARPU, revenue tracking
- **Segmentation** — query by properties and events
- **Event segmentation** — event counts and breakdowns
- **Dashboard export** — export chart data

## Requirements

| Variable | Required | Description |
|----------|----------|-------------|
| `AMPLITUDE_API_KEY` | ✅ | API key/token for Amplitude |
| `AMPLITUDE_SECRET_KEY` | ✅ | Amplitude secret key for Export/Dashboard APIs |

## Quick Start

```bash
# Track an event
python3 {baseDir}/scripts/amplitude.py track '{"user_id":"user123","event_type":"purchase","event_properties":{"amount":29.99}}'
```

```bash
# Track batch events
python3 {baseDir}/scripts/amplitude.py track-batch events.json
```

```bash
# Set user properties
python3 {baseDir}/scripts/amplitude.py identify '{"user_id":"user123","user_properties":{"plan":"pro","company":"Acme"}}'
```

```bash
# Get active user counts
python3 {baseDir}/scripts/amplitude.py active-users --start 2026-01-01 --end 2026-02-01
```



## Commands

### `track`
Track an event.
```bash
python3 {baseDir}/scripts/amplitude.py track '{"user_id":"user123","event_type":"purchase","event_properties":{"amount":29.99}}'
```

### `track-batch`
Track batch events.
```bash
python3 {baseDir}/scripts/amplitude.py track-batch events.json
```

### `identify`
Set user properties.
```bash
python3 {baseDir}/scripts/amplitude.py identify '{"user_id":"user123","user_properties":{"plan":"pro","company":"Acme"}}'
```

### `active-users`
Get active user counts.
```bash
python3 {baseDir}/scripts/amplitude.py active-users --start 2026-01-01 --end 2026-02-01
```

### `events`
Get event data.
```bash
python3 {baseDir}/scripts/amplitude.py events --start 2026-01-01 --end 2026-02-01 --event purchase
```

### `funnel`
Run funnel analysis.
```bash
python3 {baseDir}/scripts/amplitude.py funnel '{"events":[{"event_type":"page_view"},{"event_type":"signup"},{"event_type":"purchase"}]}' --start 2026-01-01 --end 2026-02-01
```

### `retention`
Retention analysis.
```bash
python3 {baseDir}/scripts/amplitude.py retention --start 2026-01-01 --end 2026-02-01
```

### `cohorts`
List cohorts.
```bash
python3 {baseDir}/scripts/amplitude.py cohorts
```

### `cohort-get`
Get cohort details.
```bash
python3 {baseDir}/scripts/amplitude.py cohort-get abc123
```

### `revenue`
Revenue analysis.
```bash
python3 {baseDir}/scripts/amplitude.py revenue --start 2026-01-01 --end 2026-02-01
```

### `user-search`
Search for a user.
```bash
python3 {baseDir}/scripts/amplitude.py user-search "user@example.com"
```

### `user-activity`
Get user activity.
```bash
python3 {baseDir}/scripts/amplitude.py user-activity user123
```

### `segments`
Event segmentation query.
```bash
python3 {baseDir}/scripts/amplitude.py segments --event purchase --group-by platform --start 2026-01-01 --end 2026-02-01
```


## Output Format

All commands output JSON by default. Add `--human` for readable formatted output.

```bash
# JSON (default, for programmatic use)
python3 {baseDir}/scripts/amplitude.py track --limit 5

# Human-readable
python3 {baseDir}/scripts/amplitude.py track --limit 5 --human
```

## Script Reference

| Script | Description |
|--------|-------------|
| `{baseDir}/scripts/amplitude.py` | Main CLI — all Amplitude operations |

## Data Policy

This skill **never stores data locally**. All requests go directly to the Amplitude API and results are returned to stdout. Your data stays on Amplitude servers.

## Credits
---
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
