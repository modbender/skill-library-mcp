---
name: skill-agent-broadcast
version: 1.0.0
description: Broadcast a message to multiple OpenClaw group sessions simultaneously. Use for cross-agent coordination, alerts, and announcements.
metadata:
  openclaw:
    requires: { bins: ["node"] }
---

# skill-agent-broadcast

Cross-group signal router. Send one message to multiple OpenClaw Telegram/Discord groups simultaneously.

## Usage

```bash
# Broadcast to named groups
node scripts/broadcast.js --message "Deploy complete!" --groups "github-ops,amazon-ops"

# Broadcast to all registered groups
node scripts/broadcast.js --message "⚡ System alert" --groups all

# Use raw Telegram chat IDs
node scripts/broadcast.js --message "Hello" --groups "-1003871838436,-1003578613620"

# Custom delay between sends
node scripts/broadcast.js --message "Update" --groups all --delay 1000
```

## Arguments

| Arg | Default | Description |
|---|---|---|
| `--message` / `-m` | required | Message text to broadcast |
| `--groups` / `-g` | all | Comma-separated group names or IDs. Use `all` for all registered groups |
| `--channel` | `telegram` | Channel type: `telegram` or `discord` |
| `--delay` | `500` | Milliseconds between sends (rate limiting) |

## Environment Variables

| Var | Default | Description |
|---|---|---|
| `OPENCLAW_PORT` | `3000` | OpenClaw gateway port |
| `OPENCLAW_TOKEN` | — | Gateway auth token |
| `GROUPS_CONFIG_PATH` | `config/groups.json` | Path to group registry JSON |

## Group Registry

Edit `config/groups.json` to add/remove groups:

```json
{
  "github-ops": "-1003871838436",
  "social-media": "-1003578613620",
  "amazon-ops": "-1003898064257"
}
```

## Output

Delivery receipt per group:
```
✅ github-ops (-1003871838436)
✅ amazon-ops (-1003898064257)
❌ social-media (-1003578613620) (status: 500)

✅ Broadcast complete: 2 sent, 1 failed
```
