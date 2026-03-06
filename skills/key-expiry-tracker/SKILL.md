---
name: Key Expiry Tracker
description: Track only expiry dates (metadata) for API keys/client
  secrets/certificates and alert before they expire.
---

# Key Expiry Tracker

Track **only expiry dates** (metadata) for API keys/client secrets/certificates and alert before they expire.

## Description

Key Expiry Tracker helps you avoid outages by tracking **only the expiry dates** of credentials (API keys, client secrets, certificates) and reminding you ahead of time.

**It never stores, reads, or transmits any credential values** — you maintain a local JSON list with labels and expiry timestamps.

**Token cost:** ~200-500 tokens per run (cron + simple JSON parsing).

## Usage

### Add a new credential

Edit `~/.openclaw/workspace/.credentials.json`:

```json
{
  "credentials": [
    {
      "name": "Azure OpenClaw Calendar",
      "type": "client-secret",
      "expires": "2026-03-15T00:00:00Z",
      "provider": "Microsoft Azure",
      "notes": "For M365 calendar integration"
    }
  ]
}
```

### Run check manually

```bash
~/.openclaw/workspace/skills/key-expiry-tracker/scripts/check-credentials.sh
```

### Cron schedule

Weekly on Sunday at 10:00:

```
cron add --name "key-expiry-tracker" \
  --schedule "0 10 * * 0" \
  --payload '{"kind":"systemEvent","text":"Run key-expiry-tracker weekly check"}' \
  --sessionTarget main
```

## Credential Types

- `client-secret`: Azure AD, API keys
- `api-key`: Third-party APIs (OpenAI, etc.)
- `certificate`: SSL/TLS certs
- `token`: OAuth tokens, refresh tokens
- `password`: Passwords with expiry

## Alert Thresholds

- **14 days**: Warning (yellow)
- **7 days**: Critical (red)
- **Expired**: Already expired!

## JSON Schema

```json
{
  "credentials": [
    {
      "name": "string (required)",
      "type": "client-secret|api-key|certificate|token|password",
      "expires": "ISO-8601 timestamp (required)",
      "provider": "string (optional)",
      "renewed": "ISO-8601 timestamp (optional, last renewal)",
      "notes": "string (optional)"
    }
  ]
}
```
