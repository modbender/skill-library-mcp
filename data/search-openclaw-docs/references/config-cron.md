# Config Pattern: Cron Jobs

**What:** Schedule tasks to run at specific times or intervals.

**When to use:** Reminders, periodic checks, scheduled reports, maintenance tasks.

---

## Critical Pattern: Cron Job Structure

### ✅ Correct: Basic Cron Job

```json
{
  "name": "Daily backup reminder",
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",
    "tz": "Asia/Kolkata"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "Reminder: Check backup status and verify last backup completed successfully."
  },
  "sessionTarget": "main"
}
```

**Key points:**
- `schedule.kind` - "cron", "at", or "every"
- `schedule.tz` - MUST match user timezone (not UTC!)
- `payload.kind` - "systemEvent" for main, "agentTurn" for isolated
- `sessionTarget` - "main" or "isolated"

---

## Schedule Types

### 1. Cron Expression (Recurring)

```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *",    // Every day at 9 AM
    "tz": "Asia/Kolkata"
  }
}
```

**Common expressions:**
- `0 9 * * *` - Daily at 9 AM
- `0 */6 * * *` - Every 6 hours
- `0 9 * * MON` - Every Monday at 9 AM
- `0 0 1 * *` - First day of month at midnight

### 2. One-Time (Absolute)

```json
{
  "schedule": {
    "kind": "at",
    "at": "2026-02-15T14:30:00+05:30"  // ISO-8601 with timezone
  }
}
```

**Note:** Timestamps without explicit timezone are treated as UTC!

### 3. Interval (Recurring)

```json
{
  "schedule": {
    "kind": "every",
    "everyMs": 3600000,       // 1 hour in milliseconds
    "anchorMs": 1707995400000 // Optional start time
  }
}
```

---

## Payload Types

### Main Session: systemEvent

```json
{
  "payload": {
    "kind": "systemEvent",
    "text": "Reminder: Team standup in 10 minutes."
  },
  "sessionTarget": "main"
}
```

**Use for:** Reminders, alerts, context injection.

### Isolated Session: agentTurn

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Check server health and report any issues.",
    "model": "haiku",
    "timeoutSeconds": 300
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce",
    "channel": "discord",
    "to": "1469004697305092288"
  }
}
```

**Use for:** Background tasks, isolated processing, automated reports.

---

## ❌ Common Mistakes

### Wrong: Missing timezone

```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 9 * * *"
    // Missing "tz" - uses UTC!
  }
}
```

**Why it fails:** Without timezone, runs at 9 AM UTC, not user local time.

### Wrong: systemEvent in isolated session

```json
{
  "payload": {
    "kind": "systemEvent",
    "text": "Do something"
  },
  "sessionTarget": "isolated"  // WRONG combination
}
```

**Why it fails:** `sessionTarget: "isolated"` requires `payload.kind: "agentTurn"`.

### Wrong: agentTurn in main session

```json
{
  "payload": {
    "kind": "agentTurn",
    "message": "Check something"
  },
  "sessionTarget": "main"  // WRONG combination
}
```

**Why it fails:** `sessionTarget: "main"` requires `payload.kind: "systemEvent"`.

### Wrong: ISO timestamp without timezone

```json
{
  "schedule": {
    "kind": "at",
    "at": "2026-02-15T14:30:00"  // WRONG - ambiguous timezone
  }
}
```

**Why it fails:** Treated as UTC. Must include offset: `+05:30` or `Z`.

---

## Common Patterns

### Daily reminder (main session)

```json
{
  "name": "Morning standup reminder",
  "schedule": {
    "kind": "cron",
    "expr": "50 9 * * MON-FRI",
    "tz": "Asia/Kolkata"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "Reminder: Daily standup in 10 minutes."
  },
  "sessionTarget": "main"
}
```

### Periodic check (isolated, auto-announce)

```json
{
  "name": "Hourly server health check",
  "schedule": {
    "kind": "cron",
    "expr": "0 * * * *",
    "tz": "Asia/Kolkata"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Check server health (CPU, memory, disk, services). Report only if issues found.",
    "model": "haiku",
    "timeoutSeconds": 120
  },
  "sessionTarget": "isolated",
  "delivery": {
    "mode": "announce",
    "channel": "discord",
    "to": "1470269989671141479"  // Errors channel
  }
}
```

### One-time reminder (20 minutes)

```json
{
  "name": "Meeting reminder",
  "schedule": {
    "kind": "at",
    "at": "2026-02-12T15:00:00+05:30"
  },
  "payload": {
    "kind": "systemEvent",
    "text": "Reminder (set 20 min ago): Client meeting starting now. Join Zoom."
  },
  "sessionTarget": "main"
}
```

---

## Session Cleanup Automation

**Problem:** Isolated cron sessions accumulate (24+ per day for hourly jobs).

**Solution:** Daily cleanup job.

```json
{
  "name": "Daily session cleanup",
  "schedule": {
    "kind": "cron",
    "expr": "0 3 * * *",        // 3 AM daily
    "tz": "Asia/Kolkata"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Clean up old isolated sessions: keep last 10 runs, apply age thresholds (24h for hourly, 7d for daily, 30d for weekly).",
    "model": "haiku",
    "timeoutSeconds": 60
  },
  "sessionTarget": "isolated"
}
```

---

## Managing Cron Jobs

### List jobs

```bash
openclaw cron list
```

### Add job (via config)

Use `config.patch`:

```json
{
  "cron": {
    "jobs": [
      {
        "name": "New job",
        "schedule": { "kind": "cron", "expr": "0 9 * * *", "tz": "Asia/Kolkata" },
        "payload": { "kind": "systemEvent", "text": "Message" },
        "sessionTarget": "main",
        "enabled": true
      }
    ]
  }
}
```

### Disable job

```json
{
  "cron": {
    "jobs": [
      {
        "name": "Job name",
        "enabled": false
      }
    ]
  }
}
```

### Remove job

Omit from `jobs` array in config.

---

## Cron vs Heartbeat

**Use cron when:**
- ✅ Exact timing matters ("9:00 AM sharp")
- ✅ Task needs isolation from main session
- ✅ Want different model/thinking level
- ✅ One-shot reminders

**Use heartbeat when:**
- ✅ Multiple checks can batch together
- ✅ Need conversational context
- ✅ Timing can drift slightly
- ✅ Want to reduce API calls

---

## Verification

```bash
# List all cron jobs
openclaw cron list

# Check job history
openclaw cron runs --job-id <id>

# View next scheduled run
openclaw cron status

# Test job immediately
openclaw cron run --job-id <id>
```

---

## References

- OpenClaw docs: `automation/cron-jobs.md`
- OpenClaw docs: `gateway/configuration.md`
- Related: `config-heartbeat.md`

---

**Critical: Always set timezone matching user's location. Default UTC causes wrong timing.**
