# OpenClaw Cron Jobs Guide

## Overview

OpenClaw has a built-in cron scheduler that runs tasks on a schedule. Cron jobs fire as agent messages — the agent wakes up, processes the task, and goes back to sleep.

## CLI Commands

```bash
openclaw cron list              # List all cron jobs
openclaw cron create            # Interactive creation
openclaw cron delete <id>       # Delete a job
openclaw cron enable <id>       # Enable a disabled job
openclaw cron disable <id>      # Disable without deleting
```

## Cron Job Configuration

Jobs are defined in `openclaw.json` or managed via CLI. Key fields:

| Field | Description | Example |
|-------|-------------|---------|
| `name` | Job identifier | `daily-checkin` |
| `schedule` | Cron expression | `0 9 * * *` (9 AM daily) |
| `message` | What the agent receives | `"Run daily check-in routine"` |
| `delivery` | How it's delivered | `announce`, `system`, `channel` |
| `target` | Where to deliver | Channel ID or user ID |
| `enabled` | Active or not | `true` / `false` |

## Schedule Syntax (Cron Expressions)

```
┌───── minute (0-59)
│ ┌───── hour (0-23, UTC)
│ │ ┌───── day of month (1-31)
│ │ │ ┌───── month (1-12)
│ │ │ │ ┌───── day of week (0-7, 0=Sun)
│ │ │ │ │
* * * * *
```

**Common patterns:**
```
0 9 * * *       # Daily at 9 AM UTC
0 */6 * * *     # Every 6 hours
*/30 * * * *    # Every 30 minutes
0 9 * * 1-5     # Weekdays at 9 AM
0 0 1 * *       # 1st of month at midnight
0 14,21 * * *   # At 2 PM and 9 PM
```

**Time zone note:** All cron times are UTC. Convert from your local time:
- CST = UTC-6 → 9 AM CST = 15:00 UTC = `0 15 * * *`
- EST = UTC-5 → 9 AM EST = 14:00 UTC = `0 14 * * *`

## Delivery Modes

### `announce` — Agent speaks to the user
The agent receives the message and responds in the target channel. Good for check-ins, reports, reminders.

### `system` — Silent system event
The agent processes internally without visible output. Good for maintenance tasks, data sync.

### `channel` — Direct to channel
Message goes directly to a channel without agent processing.

## Real Examples from Production

### Morning Founder Check-in (9 AM CST)
```json
{
  "name": "daily-founder-checkin",
  "schedule": "0 15 * * *",
  "message": "Run the morning founder check-in: recap yesterday, top 3 priorities, AI coaching question",
  "delivery": "announce",
  "target": "telegram:5162552495"
}
```

### Evening Reflection (9 PM CST)
```json
{
  "name": "evening-reflection",
  "schedule": "0 3 * * *",
  "message": "Run evening reflection: prompt for voice note, prep tomorrow's plan, flush important memories to brain",
  "delivery": "announce"
}
```

### Auto-Update Check (1 AM CST)
```json
{
  "name": "auto-update-check",
  "schedule": "0 7 * * *",
  "message": "Check for OpenClaw updates and report if available",
  "delivery": "system"
}
```

### Skill Publisher (Hourly)
```json
{
  "name": "skill-publisher",
  "schedule": "0 * * * *",
  "message": "Check for unpublished skills and publish next batch",
  "delivery": "system"
}
```

### Claude Credits Monitor
```json
{
  "name": "claude-credits-monitor",
  "schedule": "0 */4 * * *",
  "message": "Check Claude/OpenRouter credit balance and alert if low",
  "delivery": "system"
}
```

## Common Issues

### Job fires but nothing happens
- Check delivery mode — `system` is silent, use `announce` if you want visible output
- Check target — must match a valid channel/user

### Job fires at wrong time
- All times are UTC! Double-check your conversion
- `0 15 * * *` = 3 PM UTC = 9 AM CST

### Job keeps failing
- Check `openclaw cron list` for error counts
- Review gateway logs: `openclaw logs`
- Common: exec permissions, script paths, missing env vars

### Too many cron jobs consuming credits
- Each cron fire = a model inference call = credits used
- Use `system` delivery for maintenance (cheaper, no streaming)
- Batch related tasks into one cron job
- Disable jobs that aren't providing value
