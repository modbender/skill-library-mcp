# Cron Patterns Reference

Consult when building schedules. Always include timezone.

## Quick Reference

| Intent | Cron | Notes |
|--------|------|-------|
| Every day 9am | `0 9 * * *` | |
| Weekdays 9am | `0 9 * * 1-5` | Mon-Fri |
| Weekends 10am | `0 10 * * 0,6` | Sat-Sun |
| Monday 9am | `0 9 * * 1` | Weekly |
| First of month | `0 9 1 * *` | |
| Last Friday | `0 17 * * 5L` | Non-standard |
| Every 2 hours | `0 */2 * * *` | On the hour |
| Every 30 min | `*/30 * * * *` | |

## Interval vs Cron

| Use interval (`every`) when | Use cron when |
|----------------------------|---------------|
| Simple repetition (every 2h) | Specific times (9am) |
| Duration-based (every 30min) | Day-based (weekdays) |
| No clock alignment needed | Clock alignment needed |

## Format

```
┌───────────── minute (0-59)
│ ┌───────────── hour (0-23)
│ │ ┌───────────── day of month (1-31)
│ │ │ ┌───────────── month (1-12)
│ │ │ │ ┌───────────── day of week (0-6, Sun-Sat)
│ │ │ │ │
* * * * *
```

## Examples with Timezone

```json
{ "kind": "cron", "expr": "0 9 * * 1-5", "tz": "Europe/Madrid" }
{ "kind": "every", "everyMs": 3600000 }  // 1 hour
{ "kind": "at", "at": "2026-02-15T09:00:00+01:00" }  // one-shot
```

## Common Mistakes

- `0 9 * * *` without tz → runs at 9 UTC, not local
- `* 9 * * *` → runs every MINUTE of 9am hour (60 times!)
- `0 0 31 * *` → skips months without 31 days
