# BlueBubbles Healthcheck

**Diagnose and auto-heal BlueBubbles ↔ OpenClaw iMessage connectivity.**

If you've ever restarted your OpenClaw gateway and wondered why iMessages stopped coming through — this skill is for you.

## The Problem

BlueBubbles uses webhooks to push iMessage events to OpenClaw. When OpenClaw's gateway restarts, BlueBubbles doesn't know the endpoint is back. It may:

- Keep trying to deliver to a dead endpoint
- Enter exponential backoff (waiting longer between retries)
- Stop trying entirely after too many failures

The result: **messages silently stop flowing**, and there's no obvious error.

## The Solution

This skill provides scripts to:

1. **Diagnose** the connection (4 targeted health checks)
2. **Auto-heal** common issues (gateway restart, webhook reset)
3. **Verify** the fix worked

## Quick Start

### Prerequisites

- [OpenClaw](https://openclaw.ai) running on your Mac
- [BlueBubbles](https://bluebubbles.app) server configured
- BlueBubbles API password (from BB settings)

### Installation

The skill lives in your OpenClaw workspace:

```bash
# Clone or copy to your workspace
~/.openclaw/workspace/skills/bluebubbles-healthcheck/
```

### Usage

**Run a health check:**

```bash
export BB_URL="http://127.0.0.1:1234"
export BB_PASSWORD="your-bluebubbles-password"

~/.openclaw/workspace/skills/bluebubbles-healthcheck/scripts/diagnose.sh
```

**Auto-heal if issues are detected:**

```bash
~/.openclaw/workspace/skills/bluebubbles-healthcheck/scripts/heal.sh
```

## What It Checks

| Check | What It Tests | Common Failures |
|-------|--------------|-----------------|
| **1. BB Server Reachable** | `GET /api/v1/ping` returns 200 | BlueBubbles.app not running |
| **2. Webhook Registered** | A webhook exists pointing to port 18789 | Webhook deleted or misconfigured |
| **3. Gateway Endpoint Alive** | POST to webhook endpoint returns "ok" | OpenClaw gateway not running |
| **4. Webhook Delivery** | Recent webhook dispatches in BB logs | Backoff state, network issues |

## What It Heals

| Issue | Auto-Heal Action |
|-------|-----------------|
| Gateway endpoint down | Runs `openclaw gateway restart`, waits for startup |
| Webhook missing/stale | Deletes all webhooks, re-registers fresh |
| Backoff state | Same as above (delete + re-register clears backoff) |
| BlueBubbles not running | **Cannot auto-heal** — user must start the app |

## Configuration

Scripts read configuration from environment variables or command-line arguments:

| Variable | CLI Arg | Default | Description |
|----------|---------|---------|-------------|
| `BB_URL` | `--bb-url` | `http://127.0.0.1:1234` | BlueBubbles server URL |
| `BB_PASSWORD` | `--password` | (required) | BlueBubbles API password |
| `OPENCLAW_WEBHOOK_URL` | `--webhook-url` | `http://127.0.0.1:18789/bluebubbles-webhook` | OpenClaw webhook endpoint |

### Example with Arguments

```bash
./diagnose.sh --bb-url http://192.168.1.50:1234 --password "my-password"
```

## Output Examples

### Healthy System

```
─── CHECK 1: BlueBubbles server reachable ───
✅ CHECK bb_server_reachable: PASS (HTTP 200)
─── CHECK 2: Webhook registered ───
✅ CHECK webhook_registered: PASS (http://127.0.0.1:18789/bluebubbles-webhook?password=xxx)
─── CHECK 3: OpenClaw webhook endpoint alive ───
✅ CHECK gateway_endpoint_alive: PASS (responded ok)
─── CHECK 4: Recent webhook delivery ───
✅ CHECK webhook_delivery: PASS (messages exist (1234 total), delivery assumed working)

═══════════════════════════════════════════════
✅ ALL CHECKS PASSED - BlueBubbles connectivity healthy
═══════════════════════════════════════════════
```

### Unhealthy System (Webhook Missing)

```
─── CHECK 1: BlueBubbles server reachable ───
✅ CHECK bb_server_reachable: PASS (HTTP 200)
─── CHECK 2: Webhook registered ───
❌ CHECK webhook_registered: FAIL (no webhooks registered)
─── CHECK 3: OpenClaw webhook endpoint alive ───
✅ CHECK gateway_endpoint_alive: PASS (responded ok)
─── CHECK 4: Recent webhook delivery ───
❌ CHECK webhook_delivery: FAIL (cannot confirm recent delivery)

═══════════════════════════════════════════════
❌ SOME CHECKS FAILED - healing may be required
═══════════════════════════════════════════════
```

## Integration with OpenClaw

### Manual Trigger

Ask your OpenClaw agent:
> "Check if BlueBubbles is working"
> "iMessages aren't coming through, can you fix it?"

The agent will run the diagnostic and healing scripts.

### Automated Healthcheck

Add to your `HEARTBEAT.md` for periodic checks:

```markdown
## BlueBubbles Health
Every 4 hours, run the BlueBubbles healthcheck skill.
If any checks fail, attempt auto-heal and report results.
```

## File Structure

```
skills/bluebubbles-healthcheck/
├── SKILL.md              # Agent instructions (when/how to use)
├── README.md             # This file
└── scripts/
    ├── diagnose.sh       # Read-only health checks (exit 0 = healthy)
    ├── heal.sh           # Auto-heal orchestrator
    └── reset-webhook.sh  # Atomic webhook delete + re-register
```

## Troubleshooting

### "BlueBubbles server unreachable"

- Is BlueBubbles.app running on your Mac?
- Is the port correct? Default is 1234.
- Firewall blocking the connection?

### "Gateway endpoint not responding"

- Run `openclaw gateway status` to check if it's running
- Try `openclaw gateway restart`
- Check OpenClaw logs: `~/.openclaw/logs/gateway.log`

### "Webhook registered but delivery failing"

- BlueBubbles may be in backoff state
- Run `heal.sh` to reset the webhook
- Check BlueBubbles logs for errors

### Healing didn't fix it

If auto-heal doesn't resolve the issue:
1. Stop BlueBubbles completely
2. Restart OpenClaw gateway
3. Start BlueBubbles
4. Run `reset-webhook.sh` manually

## Contributing

This skill is part of the OpenClaw community skills. Issues and PRs welcome.

## License

MIT
