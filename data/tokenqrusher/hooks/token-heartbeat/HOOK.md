---
name: token-heartbeat
description: "Optimized heartbeat execution - reduces heartbeat calls by 75%"
homepage: https://github.com/qsmtco/tokenQrusher
metadata: 
  openclaw: 
    emoji: "💓"
    events: ["agent:bootstrap"]
---

# Token Heartbeat Hook

Optimizes heartbeat execution to reduce unnecessary API calls and token usage.

## What It Does

1. Checks if checks should run based on intervals
2. Respects quiet hours (23:00-08:00)
3. Returns `HEARTBEAT_OK` when nothing to report
4. Only runs checks when interval has elapsed

## Optimization Results

| Metric | Before | After | Savings |
|--------|--------|-------|---------|
| Checks/day | 48 | 12 | 75% |
| Tokens/day | ~5000 | ~1250 | 75% |

## Check Intervals

| Check | Interval | 
|-------|----------|
| Email | 2 hours |
| Calendar | 4 hours |
| Weather | 4 hours |
| Monitoring | 2 hours |

## Quiet Hours

Skip all checks between 23:00 and 08:00.

## Response Format

```
HEARTBEAT_OK
```

Or for alerts:
```
🔔 Email: 2 urgent messages
🔔 Calendar: Meeting in 30 min
```

## Configuration

Edit `config.json` to customize intervals and quiet hours.

## Events

Listens to: `agent:bootstrap`
