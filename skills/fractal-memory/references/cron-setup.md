# Cron Setup Guide

This guide shows how to set up automated memory rollups using OpenClaw's cron system.

## Overview

The fractal memory system uses three cron jobs:
1. **Daily rollup** - Runs at 23:59 every day
2. **Weekly rollup** - Runs at 23:59 every Sunday
3. **Monthly rollup** - Runs at 23:59 on the last day of each month

## Setting Up Cron Jobs

Use the `cron` tool to create these jobs:

### 1. Daily Rollup

```javascript
{
  "name": "Daily Memory Rollup",
  "schedule": {
    "kind": "cron",
    "expr": "59 23 * * *",
    "tz": "Asia/Shanghai"  // Use your timezone
  },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat",
  "payload": {
    "kind": "agentTurn",
    "message": "Execute daily memory rollup: cd ~/.openclaw/workspace && python3 scripts/rollup-daily.py && python3 scripts/update_now.py. This compresses today's diary entry into this week's summary. Log the result.",
    "timeoutSeconds": 90
  },
  "delivery": {
    "mode": "none"
  },
  "enabled": true
}
```

### 2. Weekly Rollup

```javascript
{
  "name": "Weekly Memory Rollup",
  "schedule": {
    "kind": "cron",
    "expr": "59 23 * * 0",  // Sunday at 23:59
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat",
  "payload": {
    "kind": "agentTurn",
    "message": "Execute weekly memory rollup: cd ~/.openclaw/workspace && python3 scripts/rollup-weekly.py. This compresses this week's summary into this month's summary. Log the result.",
    "timeoutSeconds": 60
  },
  "delivery": {
    "mode": "none"
  },
  "enabled": true
}
```

### 3. Monthly Rollup

```javascript
{
  "name": "Monthly Memory Rollup",
  "schedule": {
    "kind": "cron",
    "expr": "59 23 28-31 * *",  // Last days of month
    "tz": "Asia/Shanghai"
  },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat",
  "payload": {
    "kind": "agentTurn",
    "message": "Execute monthly memory rollup (only on last day of month): cd ~/.openclaw/workspace && python3 scripts/rollup-monthly.py. This distills this month's summary into MEMORY.md. Log the result.",
    "timeoutSeconds": 60
  },
  "delivery": {
    "mode": "none"
  },
  "enabled": true
}
```

## Creating the Jobs

Use the `cron` tool with `action=add`:

```javascript
cron(action="add", job={...})
```

## Verifying Jobs

Check that jobs are running:

```javascript
cron(action="list")
```

Check job run history:

```javascript
cron(action="runs", jobId="<job-id>")
```

## Troubleshooting

### Job Failed
- Check the job runs: `cron(action="runs", jobId="<job-id>")`
- Verify scripts are executable: `chmod +x scripts/*.py`
- Check script paths are correct

### Job Not Running
- Verify cron expression is correct
- Check timezone matches your location
- Ensure `enabled: true`

### Manual Testing

Test scripts manually before setting up cron:

```bash
cd ~/.openclaw/workspace
python3 scripts/rollup-daily.py
python3 scripts/rollup-weekly.py
python3 scripts/rollup-monthly.py
```

## Customization

### Change Schedule
Modify the `expr` field in the schedule. Use standard cron syntax:
- `0 * * * *` - Every hour
- `0 0 * * *` - Daily at midnight
- `0 9 * * 1` - Every Monday at 9 AM

### Change Timezone
Update the `tz` field to your timezone (e.g., "America/New_York", "Europe/London")

### Adjust Timeout
Increase `timeoutSeconds` if rollups take longer on your system
