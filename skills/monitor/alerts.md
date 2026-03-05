# Alert Configuration

## config.json Structure

```json
{
  "alerts": {
    "default_channel": "log",
    "channels": {
      "pushover": {
        "token": "ENV:PUSHOVER_TOKEN",
        "user": "ENV:PUSHOVER_USER"
      },
      "webhook": {
        "url": "USER_PROVIDED_WEBHOOK_URL"
      }
    }
  },
  "monitors": {
    "my-api": {
      "url": "USER_PROVIDED_URL",
      "interval": "1m",
      "alert_channels": ["pushover", "webhook"],
      "failure_threshold": 2
    }
  }
}
```

## Alert Logic

### When to Alert
- Status change: ok→fail or fail→ok
- After N consecutive failures (failure_threshold)
- Recovery: include duration of outage

### Alert Payload
```json
{
  "ts": "2024-03-15T10:30:00Z",
  "monitor": "my-api",
  "status": "fail",
  "previous": "ok",
  "consecutive_failures": 3,
  "message": "HTTP 503 after 2 minutes of failures"
}
```

### Recovery Alert
```json
{
  "ts": "2024-03-15T10:45:00Z",
  "monitor": "my-api",
  "status": "ok",
  "previous": "fail",
  "downtime_minutes": 15,
  "message": "Back to OK after 15 minutes"
}
```

## Channel Implementation

### Pushover
```bash
curl -s -X POST https://api.pushover.net/1/messages.json \
  -d "token=$PUSHOVER_TOKEN" \
  -d "user=$PUSHOVER_USER" \
  -d "message=$MESSAGE"
```

### Webhook
```bash
curl -s -X POST "$WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d "$ALERT_JSON"
```

## Trap: Spam Prevention
- Track last alert per monitor in alerts/state.json
- Only alert on STATUS CHANGE, not repeated failures
- Use failure_threshold to avoid flapping alerts
