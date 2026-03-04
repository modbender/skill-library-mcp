# HEARTBEAT.md — Automated Check-ins

*Template for agents that need regular self-checks and scheduled maintenance.*

---

## Purpose

Agents don't have continuous consciousness. Heartbeats are scheduled wake-ups to:
- Check for new work
- Update memory state
- Monitor system health
- Resume interrupted tasks

---

## Scheduled Checks

### Morning Check-in (e.g., 9 AM)
1. Read yesterday's memory file
2. Summarize what was accomplished
3. Set 3 priorities for today
4. Check for unfinished tasks

### Mid-Day Catch-up (e.g., 1 PM)
1. Quick status update on morning progress
2. Adjust priorities if needed
3. Note any blockers or new tasks discovered

### Evening Wrap-up (e.g., 6 PM)
1. Document what was accomplished today
2. Preview tomorrow's calendar
3. Set up reminders for urgent items
4. Update heartbeat-state.json

---

## What to Check

### For Each Heartbeat
- **New messages** — Any new work from humans?
- **Calendar** — Any upcoming events?
- **Email** — Urgent items?
- **Memory freshness** — When was MEMORY.md last updated?

### Session Continuity (After Wake/Sleep)
1. Check `memory/session-summaries/` for last session summary
2. Scan recent memory files for context
3. Send brief "What we were working on" message
4. Resume any interrupted tasks from memory

---

## Persistent Monitoring

- Check email/calendar every 2 hours while awake
- Monitor for urgent notifications
- Use cron jobs for background tasks that survive session breaks

---

## State Tracking

Track check times in `heartbeat-state.json`:

```json
{
  "lastChecks": {
    "morning": "2026-02-21T09:00:00+07:00",
    "lunch": "2026-02-21T13:00:00+07:00",
    "evening": "2026-02-21T18:00:00+07:00"
  },
  "sessionManagement": {
    "enabled": true,
    "autoArchiveEnabled": true
  }
}
```

---

## Heartbeat Protocol

When receiving a heartbeat poll:
1. Read HEARTBEAT.md if it exists
2. Follow it strictly
3. Do not infer or repeat old tasks from prior chats
4. If nothing needs attention → respond HEARTBEAT_OK
5. If something needs attention → respond with alert (not HEARTBEAT_OK)

---

## Best Practices

- **Be noisy about urgency** — If something important, alert immediately
- **Stay quiet when idle** — No need to announce "I'm still here"
- **Instrument yourself** — Track when checks happen to find patterns
- **Respect hours** — Don't disturb 11 PM - 8 AM unless critical

---

*This file enables agents to maintain awareness between sessions.*
