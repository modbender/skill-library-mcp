---
name: Smart Cron — Natural Language Cron Scheduler for OpenClaw
description: Schedule any OpenClaw task using plain English. No cron syntax
  required. Just say what you want, when you want it.
---

# Smart Cron — Natural Language Cron Scheduler for OpenClaw

Schedule any OpenClaw task using plain English. No cron syntax required. Just say what you want, when you want it.

## What It Does

- **Natural language scheduling** — "every weekday at 9am", "every 30 minutes", "first Monday of month"
- **Full cron job lifecycle** — add, list, remove, pause, resume
- **Timezone-aware** — schedule in any timezone (UTC, Europe/Bucharest, etc.)
- **Failure alerts** — WhatsApp/Telegram alert if a job fails
- **Next run preview** — shows exactly when each job runs next
- **Run logs** — persisted history of every execution
- **Zero external dependencies** — uses system cron + OpenClaw orchestration

## Quick Start

```bash
# Add a daily digest job
smart-cron add "every weekday at 9am" --task "summarize my emails"

# Add an interval job
smart-cron add "every 30 minutes" --task "check server health"

# Monthly job
smart-cron add "first Monday of month at 10am" --task "generate monthly report"

# List all scheduled jobs
smart-cron list

# Show next run times
smart-cron next

# View job logs
smart-cron logs

# Pause a job (without deleting it)
smart-cron pause <job-id>

# Resume paused job
smart-cron resume <job-id>

# Remove a job
smart-cron remove <job-id>
```

## Commands

| Command | Description |
|---------|-------------|
| `smart-cron add <schedule> --task <task>` | Schedule a new task |
| `smart-cron list` | List all jobs with status |
| `smart-cron remove <id>` | Remove a job |
| `smart-cron next` | Show next run time for all jobs |
| `smart-cron run <id>` | Run a job immediately |
| `smart-cron logs [id]` | View execution logs |
| `smart-cron pause <id>` | Pause a job |
| `smart-cron resume <id>` | Resume a paused job |

## Supported Schedule Expressions

### Intervals
- `every 5 minutes` → `*/5 * * * *`
- `every hour` → `0 * * * *`
- `every 2 hours` → `0 */2 * * *`
- `every 30 minutes` → `*/30 * * * *`

### Daily
- `every day at 9am` → `0 9 * * *`
- `every weekday at 9am` → `0 9 * * 1-5`
- `every weekend at noon` → `0 12 * * 6,0`
- `daily at midnight` → `0 0 * * *`

### Weekly
- `every Monday at 8am` → `0 8 * * 1`
- `every Friday at 5pm` → `0 17 * * 5`

### Monthly
- `first Monday of month` → calculated and re-scheduled
- `1st of month at 9am` → `0 9 1 * *`
- `last day of month` → calculated dynamically

### Custom cron (passthrough)
- `0 */6 * * *` → runs as-is for advanced users

## Timezone Support

```bash
# Schedule in your local timezone
smart-cron add "every weekday at 9am" \
  --task "daily standup reminder" \
  --timezone Europe/Bucharest

# List shows times in both UTC and local tz
```

## Failure Alerts

When a scheduled task fails, Smart Cron sends an alert via your configured channel:

```
⚠️ Smart Cron: "daily standup reminder" FAILED
Time: 09:00 EET (07:00 UTC)
Error: Task timed out after 300s
Last success: yesterday at 09:00
Logs: smart-cron logs job-123
```

## Data Storage

All job configs and logs stored locally at `~/.openclaw/workspace/smart-cron-data/`. SQLite, no telemetry.

## Configuration

Edit `~/.openclaw/workspace/smart-cron-data/config.json`:

```json
{
  "default_timezone": "Europe/Bucharest",
  "alert_channel": "whatsapp",
  "alert_on_failure": true,
  "log_retention_days": 30
}
```

## Use Cases

### Morning Briefing
```bash
smart-cron add "every weekday at 8am" --task "summarize overnight emails and news"
```

### Uptime Monitoring
```bash
smart-cron add "every 5 minutes" --task "check all APIs and alert if any is down"
```

### Weekly Reports
```bash
smart-cron add "every Friday at 5pm" --task "generate weekly work summary and log to MEMORY.md"
```

### Monthly Cleanup
```bash
smart-cron add "1st of month at 2am" --task "clean old logs and archive memory files older than 90 days"
```

## Requirements

- OpenClaw 1.0+
- Python 3.8+ (for schedule parsing)
- cron daemon (standard on Linux/macOS)

## Source & Issues

- **Source:** https://github.com/mariusfit/smart-cron
- **Issues:** https://github.com/mariusfit/smart-cron/issues
- **Author:** [@mariusfit](https://github.com/mariusfit)
