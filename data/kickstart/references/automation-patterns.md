# Automation Patterns — Common Cron & Heartbeat Templates

## Cron Jobs vs Heartbeats

**Use cron when:**
- Exact timing matters ("9:00 AM every day")
- Task needs isolation from main session
- You want a different model or thinking level
- One-shot reminders ("remind me in 20 minutes")
- Output should deliver to a specific channel

**Use heartbeat when:**
- Multiple checks can batch together
- You need conversational context from recent messages
- Timing can drift (every ~30 min is fine)
- You want to reduce API calls by combining checks

---

## Cron Job Templates

### Morning Briefing
```json
{
  "name": "morning-briefing",
  "schedule": { "kind": "cron", "expr": "0 8 * * *", "tz": "Europe/London" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Generate a morning briefing. Check: 1) Unread emails (urgent only), 2) Calendar events in next 12h, 3) Any overnight notifications. Format as a concise bullet list. Post to the main channel.",
    "timeoutSeconds": 120
  },
  "delivery": { "mode": "announce" }
}
```

### Content Scanner
```json
{
  "name": "content-scanner",
  "schedule": { "kind": "cron", "expr": "0 */4 * * *", "tz": "Europe/London" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Scan [SOURCE] for new content in the last 4 hours. Summarise top 3 items with links. If nothing notable, reply with just 'Nothing notable.' Post to [CHANNEL].",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce" }
}
```

### Reminder
```json
{
  "name": "standup-reminder",
  "schedule": { "kind": "cron", "expr": "55 9 * * 1-5", "tz": "Europe/London" },
  "sessionTarget": "main",
  "payload": {
    "kind": "systemEvent",
    "text": "Reminder: standup in 5 minutes. Check if there are any blockers to flag."
  }
}
```

### Weekly Digest
```json
{
  "name": "weekly-digest",
  "schedule": { "kind": "cron", "expr": "0 18 * * 5", "tz": "Europe/London" },
  "sessionTarget": "isolated",
  "payload": {
    "kind": "agentTurn",
    "message": "Generate a weekly summary. Review memory files from the past 7 days. Highlight: key decisions made, tasks completed, blockers encountered, priorities for next week. Keep it under 300 words.",
    "timeoutSeconds": 180
  },
  "delivery": { "mode": "announce" }
}
```

---

## Heartbeat Patterns

### Basic Rotation
```markdown
# HEARTBEAT.md

## Check Rotation (pick 1-2 per heartbeat, rotate through)
- [ ] Email — any urgent unread messages?
- [ ] Calendar — upcoming events in next 24h?
- [ ] Weather — relevant if human might go out?
- [ ] Project status — any builds failing, deploys stuck?

## Always Check
- [ ] Context usage — if >60%, alert immediately

## Track State
Use memory/heartbeat-state.json to track last check times.
Don't repeat a check within 2 hours unless something changed.
```

### Heartbeat State File
```json
{
  "lastChecks": {
    "email": "2026-02-25T08:30:00Z",
    "calendar": "2026-02-25T09:00:00Z",
    "weather": null,
    "projects": "2026-02-25T08:30:00Z"
  }
}
```

### Context Monitor Heartbeat
```markdown
# HEARTBEAT.md

## Context Monitor
- Check all active sessions via sessions_list
- If any session exceeds 60% context usage, alert in main channel
- Include which channel and current usage percentage
```

---

## Tips

1. **Start with one cron, get it stable, then add more.** Don't create 10 crons on day one.
2. **Set reasonable timeouts.** 120-180s for most tasks. Complex tasks may need 300s.
3. **Use `delivery.mode: "announce"`** for isolated jobs that should report back.
4. **Use `sessionTarget: "main"` + `systemEvent`** for reminders that need main session context.
5. **Use `sessionTarget: "isolated"` + `agentTurn`** for independent tasks.
6. **Monitor your crons.** Check `cron(action="runs", jobId="...")` periodically to see if they're timing out or failing.
7. **Disable before deleting.** If a cron misbehaves, disable it first to debug.
