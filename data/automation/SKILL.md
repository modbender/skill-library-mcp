---
name: automation
description: Task automation specialist. Workflow optimization and scheduled tasks.
---

# Task Automation

Automate repetitive tasks and optimize workflows using OpenClaw cron, shell scripts, and system tools.

## Instructions

1. **Identify the task**: Ask what the user wants automated — frequency, trigger, input/output.
2. **Choose the right tool**:

   | Task Type | Tool | Example |
   |-----------|------|---------|
   | Periodic checks | OpenClaw cron | Email check every 30 min |
   | File processing | Shell + cron | Compress logs nightly |
   | API polling | curl + jq + cron | Price alerts |
   | Web scraping | Puppeteer / fetch | Competitor monitoring |
   | Data pipeline | Shell pipeline | CSV → JSON → API |
   | Event-driven | Webhooks / inotifywait | File change triggers |

3. **Implement with OpenClaw cron** (preferred for agent tasks):
   ```bash
   # Example: System event every 30 minutes
   openclaw cron add --name "task-name" \
     --schedule "*/30 * * * *" \
     --payload '{"kind":"systemEvent","text":"Check X notifications"}'
   ```

4. **Implement with system cron** (for shell scripts):
   ```bash
   # Edit crontab
   crontab -e
   # Add entry: every day at 2 AM
   0 2 * * * /path/to/backup.sh >> /var/log/backup.log 2>&1
   ```

5. **Implement with systemd timers** (for services):
   ```ini
   # /etc/systemd/system/task.timer
   [Timer]
   OnCalendar=*-*-* 02:00:00
   Persistent=true
   [Install]
   WantedBy=timers.target
   ```

## Automation Patterns

### Retry with Backoff
```bash
#!/bin/bash
MAX_RETRIES=3
DELAY=5
for i in $(seq 1 $MAX_RETRIES); do
  if your_command; then break; fi
  echo "Retry $i/$MAX_RETRIES in ${DELAY}s..."
  sleep $DELAY
  DELAY=$((DELAY * 2))
done
```

### File Watcher
```bash
inotifywait -m -e modify,create /path/to/watch | while read dir action file; do
  echo "File $file was $action"
  # trigger processing
done
```

### Idempotent Scripts
```bash
# Use lock files to prevent concurrent runs
LOCKFILE="/tmp/mytask.lock"
if [ -f "$LOCKFILE" ]; then echo "Already running"; exit 0; fi
trap "rm -f $LOCKFILE" EXIT
touch "$LOCKFILE"
# ... your task here
```

### Pipeline with Error Handling
```bash
set -euo pipefail
fetch_data | transform_json | upload_result \
  || { echo "Pipeline failed at stage $?"; notify_admin; exit 1; }
```

## Cron Expression Reference

| Expression | Meaning |
|-----------|---------|
| `*/5 * * * *` | Every 5 minutes |
| `0 */2 * * *` | Every 2 hours |
| `0 9 * * 1-5` | Weekdays at 9 AM |
| `0 2 * * *` | Daily at 2 AM |
| `0 0 * * 0` | Weekly on Sunday midnight |
| `0 0 1 * *` | Monthly on the 1st |

## Security

- **Never store secrets in crontab** — use environment variables or secret files
- **Log all automated actions** — append to `~/.automation/logs/`
- **Rate limit API calls** — respect service terms
- **Use lock files** — prevent duplicate runs
- **Validate inputs** — never pass unsanitized data to shell commands

## Requirements

- `cron` or `systemd` (pre-installed on Linux)
- OpenClaw for agent-based automation
- Optional: `inotifywait` (inotify-tools), `jq`, `curl`
