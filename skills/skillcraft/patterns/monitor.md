# Monitor Pattern

Watch for conditions and notify.

## Trigger: Cron vs Heartbeat

| Use Cron | Use Heartbeat |
|----------|---------------|
| Precise timing matters | Approximate frequency OK |
| Resource-intensive checks | Quick, lightweight checks |
| Dedicated scheduling | Piggyback on existing heartbeat |
| Needs to wake system | Only when session active |

### Cron
Use `cron` tool. See docs: `/automation/cron-jobs`.

### Heartbeat
Add check instructions to `<workspace>/HEARTBEAT.md` with a time threshold.

## State

Store in `{baseDir}/state.json`:
```json
{
  "lastCheck": "2025-01-20T10:00:00Z",
  "lastValue": 42,
  "lastNotified": "2025-01-20T09:00:00Z"
}
```

## De-duplication

Avoid notification spam:
- **Time-based:** Max once per N hours for same condition
- **Threshold-crossing:** Only on crossing, not while above/below

## Notification

Use `message` tool. Format:
```
🚨 **[Monitor Name]**
Condition: [what happened]
Current: [value]  
Previous: [value]
```

## Checklist

- [ ] Trigger chosen: cron or heartbeat
- [ ] State in `{baseDir}/state.json`
- [ ] De-duplication to prevent spam
- [ ] Notification via `message` with channel
- [ ] Manual check command documented
