---
name: cron-dashboard
description: View, manage, and debug OpenClaw cron jobs with status overview and
  health checks.
---


# Cron Dashboard

View and manage OpenClaw cron jobs at a glance.

## Instructions

1. **List all jobs**:
   ```bash
   openclaw cron list
   ```
   Display as table: Name | Schedule | Model | Status | Last Run | Next Run

2. **Job details**: `openclaw cron show <id>` — full config, recent runs, output logs

3. **Health checks** — Flag issues:
   - ⚠️ Job hasn't run when expected (missed schedule)
   - 🔴 Repeated failures (3+ consecutive)
   - 🟡 Stale schedule (no runs in >24h for hourly jobs)

4. **Quick actions**:
   ```bash
   openclaw cron create --name "task" --schedule "*/30 * * * *" --prompt "..."
   openclaw cron pause <id>
   openclaw cron resume <id>
   openclaw cron delete <id>
   ```

5. **Dashboard view** (when asked for overview):
   ```
   🕐 Cron Dashboard — 5 jobs

   ✅ Active (3)
   | Name          | Schedule    | Last Run      | Next Run      |
   |---------------|-------------|---------------|---------------|
   | email-check   | */30 * * *  | 5 min ago ✅  | in 25 min     |

   ⏸️ Paused (1)
   | backup-daily  | 0 2 * * *   | 2 days ago    | —             |

   🔴 Failing (1)
   | tweet-bot     | 0 9 * * *   | 1h ago ❌     | tomorrow 9:00 |
   ```

## Cron Expression Cheat Sheet

| Expression | Meaning |
|-----------|---------|
| `*/15 * * * *` | Every 15 minutes |
| `0 */2 * * *` | Every 2 hours |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 2 * * *` | Daily at 2 AM |
| `0 0 1 * *` | First of each month |

## Troubleshooting

- **Job not running**: Check if paused; verify schedule with `crontab.guru`
- **Repeated failures**: Check `openclaw cron show <id>` for error output
- **Consider heartbeat**: For flexible-timing checks, use HEARTBEAT.md instead of cron

## Requirements

- OpenClaw CLI installed and configured
- No API keys needed
