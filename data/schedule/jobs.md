# Job Storage Format

Jobs are stored in ~/schedule/jobs.json. Each job captures what the USER requested.

## Format

```json
{
  "job_id": {
    "task": "User's exact request",
    "cron": "cron expression or ISO timestamp",
    "timezone": "Europe/Madrid",
    "requires": ["skill1", "skill2"],
    "created": "2024-03-15",
    "status": "active"
  }
}
```

## Fields

| Field | Required | Description |
|-------|----------|-------------|
| task | Yes | What user asked to do (their words) |
| cron | Yes | When to run (cron expr or ISO for one-shot) |
| timezone | Yes | User's timezone |
| requires | No | Skills/permissions this job needs |
| created | Yes | When job was created |
| status | Yes | active, paused, or completed |

## Example Jobs

```json
{
  "morning_reminder": {
    "task": "Remind me to check calendar",
    "cron": "0 8 * * *",
    "timezone": "Europe/Madrid",
    "requires": [],
    "created": "2024-03-15",
    "status": "active"
  },
  "weekly_summary": {
    "task": "Summarize my week and send to my email",
    "cron": "0 18 * * 5",
    "timezone": "Europe/Madrid",
    "requires": ["mail"],
    "created": "2024-03-15",
    "status": "active"
  }
}
```

## Notes

- `requires` is populated when user explicitly grants access
- Empty `requires` = notification/reminder only
- Jobs with `requires` will use those skills when executing
