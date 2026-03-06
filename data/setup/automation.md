# Automation Configuration

## Cron Jobs

Enable cron scheduler:

```json
{
  "cron": {
    "enabled": true,
    "maxConcurrentRuns": 3
  }
}
```

**Job types:**
- `systemEvent` — Inject text into main session
- `agentTurn` — Run isolated task with result delivery

---

## Heartbeat vs Cron

| Feature | Heartbeat | Cron |
|---------|-----------|------|
| Timing | Approximate (every X) | Exact (at specific time) |
| Context | Has session history | Isolated |
| Use | Periodic checks | Scheduled tasks |
| Model | Main session model | Can specify different |

**Heartbeat:** For batching periodic checks (email, calendar, etc.)
**Cron:** For exact timing, isolated tasks, reminders

---

## Heartbeat Setup

```json
{
  "agents": {
    "defaults": {
      "heartbeat": {
        "every": "30m",
        "target": "telegram",
        "to": "YOUR_USER_ID",
        "activeHours": {
          "start": "08:00",
          "end": "23:00",
          "timezone": "America/New_York"
        },
        "prompt": "Read HEARTBEAT.md if it exists. Follow it strictly. If nothing needs attention, reply HEARTBEAT_OK."
      }
    }
  }
}
```

Create `HEARTBEAT.md` in workspace with periodic tasks.

---

## Webhooks

```json
{
  "hooks": {
    "enabled": true,
    "path": "/hooks",
    "token": "${WEBHOOK_TOKEN}",
    "mappings": [
      {
        "id": "github-push",
        "match": { "path": "/hooks/github" },
        "action": "agent",
        "messageTemplate": "GitHub push: {{body.repository.name}}"
      }
    ]
  }
}
```

**Actions:**
- `wake` — Wake the session
- `agent` — Send message to agent

---

## Gmail Pub/Sub

Real-time email notifications:

```json
{
  "hooks": {
    "gmail": {
      "account": "your@gmail.com",
      "label": "INBOX",
      "includeBody": true,
      "maxBytes": 50000,
      "model": "anthropic/claude-haiku"
    }
  }
}
```

**Setup:**
```bash
openclaw gmail setup
```

---

## Session Reset

Auto-reset sessions on schedule:

```json
{
  "session": {
    "reset": {
      "mode": "daily",
      "atHour": 4
    },
    "resetByType": {
      "dm": { "mode": "idle", "idleMinutes": 120 },
      "group": { "mode": "idle", "idleMinutes": 60 }
    }
  }
}
```

**modes:** `daily` (at specific hour), `idle` (after inactivity)

---

## Message Queue

Handle rapid messages:

```json
{
  "messages": {
    "queue": {
      "mode": "steer",
      "debounceMs": 500,
      "cap": 10
    }
  }
}
```

**modes:**
- `steer` — Inject follow-ups into current turn ⭐
- `collect` — Batch messages
- `queue` — Process one at a time
- `interrupt` — Cancel current, start new

---

## Ack Reactions

React to messages while processing:

```json
{
  "messages": {
    "ackReaction": "👀",
    "ackReactionScope": "all",
    "removeAckAfterReply": true
  }
}
```

**scopes:** `group-mentions`, `group-all`, `direct`, `all`

---

## Inbound Debouncing

Batch rapid messages from same sender:

```json
{
  "messages": {
    "inbound": {
      "debounceMs": 1000,
      "byChannel": {
        "whatsapp": 2000
      }
    }
  }
}
```

---

## Typing Indicators

Show "typing..." while processing:

```json
{
  "agents": {
    "defaults": {
      "typingMode": "thinking",
      "typingIntervalSeconds": 5
    }
  }
}
```

**modes:** `never`, `instant`, `thinking`, `message`
