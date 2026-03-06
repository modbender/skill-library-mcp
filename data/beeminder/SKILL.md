---
name: beeminder
description: Beeminder API for goal tracking and commitment devices. Use when checking Beeminder goals, adding datapoints, viewing due goals, managing commitments, or tracking habits. Triggers on "beeminder", "goals due", "add datapoint", "track habit", "goal status", "derail".
---

# Beeminder API

Direct REST API access to Beeminder. No CLI dependencies.

## Setup

Set two env vars:
- `BEEMINDER_USERNAME` - Beeminder username
- `BEEMINDER_AUTH_TOKEN` - personal auth token from https://www.beeminder.com/api/v1/auth_token.json (requires login)

All examples use:
```bash
BASE="https://www.beeminder.com/api/v1/users/$BEEMINDER_USERNAME"
```

## Goals

### List all goals
```bash
curl -s "$BASE/goals.json?auth_token=$BEEMINDER_AUTH_TOKEN" | jq '[.[] | {slug, safebuf, baremin, limsum}]'
```

### Get single goal
```bash
curl -s "$BASE/goals/GOAL.json?auth_token=$BEEMINDER_AUTH_TOKEN"
```

Key fields:
- `slug` - goal identifier
- `safebuf` - days of safety buffer (0 = due today, negative = in the red)
- `baremin` - minimum needed today to stay on track
- `limsum` - human-readable summary (e.g. "+1 due in 2 days")
- `losedate` - unix timestamp of derail date
- `rate` - commitment rate
- `runits` - rate units (d/w/m/y)
- `headsum` - summary of current status
- `goalval` - end goal value (null if no end goal)
- `gunits` - goal units (e.g. "hours", "pages")

### Goals due today
```bash
curl -s "$BASE/goals.json?auth_token=$BEEMINDER_AUTH_TOKEN" \
  | jq '[.[] | select(.safebuf <= 0)] | sort_by(.losedate) | .[] | {slug, baremin, limsum}'
```

### Goals due within N days
```bash
curl -s "$BASE/goals.json?auth_token=$BEEMINDER_AUTH_TOKEN" \
  | jq --arg cutoff "$(date -d '+2 days' +%s)" \
    '[.[] | select(.losedate <= ($cutoff | tonumber))] | sort_by(.losedate) | .[] | {slug, baremin, limsum}'
```

## Datapoints

### Add datapoint
```bash
curl -s -X POST "$BASE/goals/GOAL/datapoints.json" \
  -d "auth_token=$BEEMINDER_AUTH_TOKEN" \
  -d "value=N" \
  -d "comment=TEXT"
```
Optional: `-d "requestid=UNIQUE_ID"` for idempotent retries (safe to repeat without duplicating).

### Get recent datapoints
```bash
curl -s "$BASE/goals/GOAL/datapoints.json?auth_token=$BEEMINDER_AUTH_TOKEN&count=5&sort=daystamp"
```

### Update datapoint
```bash
curl -s -X PUT "$BASE/goals/GOAL/datapoints/DATAPOINT_ID.json" \
  -d "auth_token=$BEEMINDER_AUTH_TOKEN" \
  -d "value=N" \
  -d "comment=TEXT"
```

### Delete datapoint
```bash
curl -s -X DELETE "$BASE/goals/GOAL/datapoints/DATAPOINT_ID.json?auth_token=$BEEMINDER_AUTH_TOKEN"
```

## Common Patterns

### Check and report what's due
```bash
curl -s "$BASE/goals.json?auth_token=$BEEMINDER_AUTH_TOKEN" \
  | jq '[.[] | select(.safebuf <= 1)] | sort_by(.safebuf) | .[] | {slug, baremin, limsum, safebuf}'
```

### Add with idempotent retry
```bash
curl -s -X POST "$BASE/goals/GOAL/datapoints.json" \
  -d "auth_token=$BEEMINDER_AUTH_TOKEN" \
  -d "value=1" \
  -d "comment=done" \
  -d "requestid=GOAL-$(date +%Y%m%d)"
```

## Notes

- Base URL must be exactly `https://www.beeminder.com/api/v1/` (https, www required)
- All responses are JSON
- Use `jq` to parse responses
- Daystamps use `YYYYMMDD` format
- Timestamps are unix epoch seconds
