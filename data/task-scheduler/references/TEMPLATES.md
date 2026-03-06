# Cron Templates for Scheduler

## One-Shot Shell Command

```json
{
  "name": "Task: npm test",
  "schedule": {
    "kind": "at",
    "at": "2026-02-12T15:00:00-05:00"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "SCHEDULED TASK: Run `npm test` in the project root. Execute the command and report the results including pass/fail counts."
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "<chatId>",
    "bestEffort": true
  },
  "deleteAfterRun": true
}
```

## One-Shot Silent Task

```json
{
  "name": "Task: clean tmp",
  "schedule": {
    "kind": "at",
    "at": "2026-02-12T03:00:00-05:00"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "SCHEDULED TASK (SILENT): Clean temporary files older than 7 days from /tmp. Log what was deleted."
  },
  "deleteAfterRun": true
}
```

## Recurring API Health Check

```json
{
  "name": "Recurring Task: API health check",
  "schedule": {
    "kind": "every",
    "everyMs": 1800000
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "RECURRING TASK: Check https://api.example.com/health — GET request. If status is not 200 or response time > 5s, report as ALERT. Otherwise report OK with response time."
  },
  "delivery": {
    "mode": "announce",
    "channel": "discord",
    "to": "channel:<channelId>",
    "bestEffort": true
  }
}
```

## Daily Report Generation (Cron)

```json
{
  "name": "Recurring Task: daily git summary",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * 1-5",
    "tz": "America/New_York"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "RECURRING TASK: Generate a git activity summary for the last 24 hours. Run `git log --since='24 hours ago' --oneline` and summarize: number of commits, authors, changed files. Format as a clean report."
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "<chatId>",
    "bestEffort": true
  }
}
```

## Weekly Database Backup

```json
{
  "name": "Recurring Task: weekly db backup",
  "schedule": {
    "kind": "cron",
    "expr": "0 2 * * 0",
    "tz": "America/New_York"
  },
  "sessionTarget": "isolated",
  "wakeMode": "now",
  "payload": {
    "kind": "agentTurn",
    "message": "RECURRING TASK: Back up the SQLite database. Copy the database file to a timestamped backup location. Verify the backup by checking file size. Report success or failure."
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram",
    "to": "<chatId>",
    "bestEffort": true
  }
}
```

## Scheduler Cleanup Job

Install this once to clean up expired one-shot scheduled tasks every 24 hours:

```json
{
  "name": "Recurring Task: scheduler cleanup",
  "schedule": {
    "kind": "every",
    "everyMs": 86400000
  },
  "sessionTarget": "isolated",
  "wakeMode": "next-heartbeat",
  "payload": {
    "kind": "agentTurn",
    "message": "Time for the 24-hour scheduler cleanup. List all cron jobs. Only delete jobs whose name starts with 'Task:' that are disabled (enabled: false) and have lastStatus: ok (finished one-shots). Do NOT delete any jobs that don't start with 'Task:' or 'Recurring Task:' — those belong to other skills. Do NOT delete active recurring jobs. Log what you deleted."
  },
  "delivery": {
    "mode": "none"
  }
}
```

## Timezone Reference

Common timezone identifiers:
- `America/New_York` (EST/EDT)
- `America/Chicago` (CST/CDT)
- `America/Los_Angeles` (PST/PDT)
- `Europe/London` (GMT/BST)
- `Europe/Berlin` (CET/CEST)
- `Asia/Tokyo` (JST)
- `Africa/Cairo` (EET)
- `Australia/Sydney` (AEST/AEDT)
