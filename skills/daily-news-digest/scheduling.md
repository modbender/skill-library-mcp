# Scheduling Guide — Daily News Digest

## OpenClaw Cron Integration

This skill integrates with OpenClaw's cron system for automated briefings.

### Setting Up Scheduled Briefings

When user requests automation:

```
User: "Send me news every morning at 8am"

Agent action:
1. Confirm time and channel
2. Create cron job via OpenClaw
3. Log schedule in memory.md
```

### Cron Job Configuration

Use OpenClaw's cron tool with isolated session:

```json
{
  "schedule": {
    "kind": "cron",
    "expr": "0 8 * * *",
    "tz": "Europe/Madrid"
  },
  "payload": {
    "kind": "agentTurn",
    "message": "Deliver scheduled morning news briefing. Read ~/daily-news-digest/memory.md for preferences. Use Standard format unless user prefers Brief. Include local news for their region."
  },
  "delivery": {
    "mode": "announce",
    "channel": "telegram"
  },
  "sessionTarget": "isolated"
}
```

### Common Schedules

| Request | Cron Expression | Notes |
|---------|-----------------|-------|
| "Every morning at 8am" | `0 8 * * *` | Daily |
| "Weekday mornings at 7am" | `0 7 * * 1-5` | Mon-Fri |
| "Morning and evening" | `0 8,18 * * *` | Twice daily |
| "Every Monday morning" | `0 8 * * 1` | Weekly |
| "Every 6 hours" | `0 */6 * * *` | Frequent |

### Timezone Handling

Always ask user's timezone on first schedule setup:
- Store in memory.md
- Pass to cron job configuration
- If not specified, use system timezone

### Channel Delivery

Briefings can be delivered to:
- Telegram (default for most users)
- WhatsApp
- Discord
- Email (via skill integration)

Store preferred channel in memory.md.

### Managing Schedules

**List schedules:**
```
User: "What news schedules do I have?"
→ Read memory.md Schedule section
→ Optionally query OpenClaw cron status
```

**Modify schedule:**
```
User: "Change my morning briefing to 7:30am"
→ Update cron job
→ Update memory.md
→ Confirm change
```

**Cancel schedule:**
```
User: "Stop the morning briefings"
→ Remove cron job
→ Update memory.md
→ Confirm cancellation
```

### Avoiding Duplicates

Before creating scheduled briefing:
1. Check if schedule already exists for that time
2. Check last delivery timestamp in memory.md
3. Don't deliver if already sent within 30 minutes

### Format per Schedule

Different times can have different formats:
```
Memory entry example:
## Schedule
Morning 8am: Brief format (quick read with coffee)
Evening 6pm: Standard format (more time to read)
```

### Error Handling

If scheduled delivery fails:
1. Log failure in memory.md Notes
2. Retry on next heartbeat
3. After 3 failures, notify user to check configuration

### Weekend vs Weekday

Some users want different schedules:
```
User: "Light briefing on weekends"
→ Weekday: Standard format, 0 8 * * 1-5
→ Weekend: Brief format, 0 9 * * 0,6
```
