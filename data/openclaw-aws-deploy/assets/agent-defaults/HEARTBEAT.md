# HEARTBEAT.md

## What To Do On Heartbeat

Check the time, then do what makes sense:

### Periodic Checks (rotate through, 2-4x daily)
- **Calendar** — Upcoming events in the next 24h?
- **Email** — Anything urgent or unread?
- **Projects** — Any repos to check on? (`git status`, PRs, etc.)

### When to Reach Out
- Important email or notification arrived
- Calendar event coming up (<2h)
- Something interesting you found while checking

### When to Stay Quiet (HEARTBEAT_OK)
- Late night (11 PM – 8 AM) unless urgent
- Nothing new since last check
- You just checked <30 min ago

### Track Your Checks
Update `memory/heartbeat-state.json`:
```json
{
  "lastChecks": {
    "email": null,
    "calendar": null
  }
}
```

### Memory Maintenance
Every few days, review recent `memory/` files and update `MEMORY.md` with anything worth keeping long-term.
