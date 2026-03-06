---
name: Webhook Router for OpenClaw
description: A general-purpose webhook receiver that routes incoming webhooks
  from any source to appropriate handlers. Integrates seamlessly with OpenClaw's
  hooks system and Tailscale Funnel for secure, public ...
---

# Webhook Router for OpenClaw

A general-purpose webhook receiver that routes incoming webhooks from any source to appropriate handlers. Integrates seamlessly with OpenClaw's hooks system and Tailscale Funnel for secure, public webhook endpoints.

## Overview

This skill provides a complete webhook routing infrastructure:

- **Secure endpoint** via Tailscale Funnel (HTTPS)
- **Automatic routing** based on webhook source
- **Built-in handlers** for GitHub, ClawHub, and generic sources
- **Registration system** for adding new webhook sources
- **Audit logging** of all received webhooks
- **Smart alerting** on important events

## How It Works

### Architecture

```
External Service → Tailscale Funnel → OpenClaw /hooks → router.sh → Handler Script
```

1. External service sends webhook to your Tailscale Funnel URL
2. OpenClaw's hooks system receives the webhook
3. `router.sh` inspects the payload and routes to the appropriate handler
4. Handler processes the event and triggers alerts/actions as needed

### Your Webhook Endpoint

```
https://gregs-mac-mini.taila31444.ts.net/hooks
```

**Authentication:** Use OpenClaw's hook token in the `X-Hook-Token` header:
```
X-Hook-Token: 19e78f0288d476ee1197d4b374b6f73394abe121c12cc38a
```

## Quick Start

### 1. Verify Tailscale Funnel is Running

```bash
openclaw gateway status
# Should show: Tailscale Funnel: ACTIVE
```

If not active:
```bash
openclaw gateway start
```

### 2. Test the Router Locally

```bash
cd /Users/gregborden/.openclaw/workspace/clawhub-skills/webhook-router
./test.sh
```

### 3. Register a New Webhook Source

```bash
./register.sh github my-repo
# Output: https://gregs-mac-mini.taila31444.ts.net/hooks?source=github-my-repo
```

### 4. Configure in Your Service

Use the generated URL in your service's webhook settings with the hook token header.

## Available Handlers

### GitHub (`handlers/github.sh`)

Handles GitHub webhook events:
- **push** - Code pushed to repository
- **pull_request** - PR opened, closed, merged, synchronized
- **issues** - Issue opened, closed, assigned, labeled
- **release** - Release published

**Alert triggers:**
- PR merged → Notification
- Issue assigned to you → Notification  
- New release → Notification

**Configuration:**
```bash
# Set your GitHub username for personalized alerts
export GITHUB_USERNAME="your-username"
```

### Generic (`handlers/generic.sh`)

Fallback handler for unknown webhook sources:
- Logs full payload
- Attempts to extract event type and meaningful fields
- Creates alert for manual review

### ClawHub (`handlers/clawhub.sh`)

Handles ClawHub-specific webhooks (auto-created by `register.sh`):
- New skill published
- Skill updated
- User mentions

## Registration System

### Register a New Source

```bash
./register.sh <source-type> <name>
```

**Examples:**

```bash
# GitHub repository
./register.sh github my-awesome-app

# Stripe payments
./register.sh stripe payments

# Custom service
./register.sh custom my-service
```

This will:
1. Generate a unique source identifier
2. Create a handler template (if new source type)
3. Output the webhook URL to configure

### Webhook URL Format

```
https://gregs-mac-mini.taila31444.ts.net/hooks?source=<source-id>
```

Or with header:
```
X-Webhook-Source: <source-id>
```

## Advanced Configuration

### Custom Handler Development

Create a new handler in `handlers/<type>.sh`:

```bash
#!/bin/bash
# handlers/myapp.sh

PAYLOAD="$1"
SOURCE="$2"
EVENT_TYPE="$3"

# Extract fields using jq
field=$(echo "$PAYLOAD" | jq -r '.field // "unknown"')

# Log to vault
vault write "webhooks/$SOURCE/$EVENT_TYPE" \
  --data "$PAYLOAD" \
  --tags "webhook,$SOURCE,$EVENT_TYPE"

# Alert on important events
if [[ "$EVENT_TYPE" == "critical" ]]; then
  alert "🚨 Critical event from $SOURCE" "$field"
fi
```

Make it executable:
```bash
chmod +x handlers/myapp.sh
```

### Environment Variables

```bash
# GitHub username for personalized alerts
export GITHUB_USERNAME="your-github-username"

# Alert channel (default: main)
export WEBHOOK_ALERT_CHANNEL="telegram"

# Log file path (default: /Users/gregborden/.openclaw/workspace/memory/webhooks.jsonl)
export WEBHOOK_LOG_PATH="/custom/path/webhooks.jsonl"
```

### Log Format

All webhooks are logged to `/Users/gregborden/.openclaw/workspace/memory/webhooks.jsonl`:

```json
{
  "timestamp": "2026-02-07T20:30:00Z",
  "source": "github-myrepo",
  "event_type": "push",
  "repository": "owner/repo",
  "sender": "username",
  "payload_hash": "sha256:abc123...",
  "processed": true
}
```

## Service-Specific Setup

### GitHub

1. Go to repository → Settings → Webhooks → Add webhook
2. **Payload URL:** `https://gregs-mac-mini.taila31444.ts.net/hooks?source=github-<repo>`
3. **Content type:** `application/json`
4. **Secret:** (leave blank, token is in header)
5. **Events:** Select events or "Let me select individual events"
6. Add header: `X-Hook-Token: 19e78f0288d476ee1197d4b374b6f73394abe121c12cc38a`

### Stripe

1. Dashboard → Developers → Webhooks → Add endpoint
2. **Endpoint URL:** `https://gregs-mac-mini.taila31444.ts.net/hooks?source=stripe-payments`
3. Select events to listen for
4. Add header: `X-Hook-Token: 19e78f0288d476ee1197d4b374b6f73394abe121c12cc38a`

### ClawHub

Use the built-in hooks integration or register:
```bash
./register.sh clawhub skills
```

### Custom Services

Any service that supports webhooks:
1. Run `./register.sh <type> <name>`
2. Copy the generated URL
3. Configure in your service with the `X-Hook-Token` header

## Testing

### Local Test

```bash
./test.sh
```

Sends mock webhooks to test the routing system.

### Manual Test with curl

```bash
# GitHub push event
curl -X POST "https://gregs-mac-mini.taila31444.ts.net/hooks?source=github-test" \
  -H "X-Hook-Token: 19e78f0288d476ee1197d4b374b6f73394abe121c12cc38a" \
  -H "X-GitHub-Event: push" \
  -H "Content-Type: application/json" \
  -d '{
    "ref": "refs/heads/main",
    "repository": {"full_name": "test/repo"},
    "pusher": {"name": "testuser"},
    "commits": [{"message": "Test commit"}]
  }'
```

## Troubleshooting

### Check Recent Webhooks

```bash
# View last 10 webhooks
tail -10 /Users/gregborden/.openclaw/workspace/memory/webhooks.jsonl | jq .
```

### Verify Handler Exists

```bash
ls -la handlers/
```

### Test Router Directly

```bash
echo '{"test": "data"}' | ./router.sh --source test --event push
```

### Check OpenClaw Hooks Status

```bash
openclaw gateway status
```

### Logs

- Webhook audit log: `/Users/gregborden/.openclaw/workspace/memory/webhooks.jsonl`
- Handler logs: Check your vault or notification channel

## Security Notes

- The hook token authenticates requests to OpenClaw
- Tailscale Funnel provides HTTPS encryption
- Webhook payloads are logged (hashed) but consider sanitizing sensitive data
- Each source can have its own validation in its handler

## Files

- `router.sh` - Main routing logic
- `register.sh` - Source registration
- `handlers/github.sh` - GitHub webhook handler
- `handlers/generic.sh` - Generic fallback handler
- `test.sh` - Test suite
- `SKILL.md` - This documentation

## License

MIT - See ClawHub repository for details.
