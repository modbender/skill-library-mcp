# Troubleshooting Guide

Quick reference for common issues. Run `diagnose.sh` first to identify the problem.

---

## Issue: BB Server Unreachable

**Symptom:** `diagnose.sh` fails at health check, curl to `/api/v1/ping` times out.

**Causes:**
- BlueBubbles app not running on Mac
- Wrong port (default is 1234)
- Firewall blocking connection

**Fix:**
1. Open BlueBubbles app on Mac
2. Check Settings → API → Port number
3. Verify with: `curl "http://127.0.0.1:1234/api/v1/ping?password=YOUR_PASSWORD"`

---

## Issue: Webhook Missing

**Symptom:** `diagnose.sh` shows no webhook registered for OpenClaw gateway.

**Causes:**
- Never registered (fresh install)
- BB was reinstalled/reset
- Webhook was manually deleted

**Fix:**
```bash
./scripts/heal.sh  # Auto-registers webhook
```

---

## Issue: Webhook Registered But Delivery Broken

**Symptom:** Webhook exists, gateway is up, but messages don't arrive.

**Root Cause:** BlueBubbles enters exponential backoff when webhook deliveries fail (e.g., during gateway restart). Even after gateway is back, BB waits before retrying.

**This is the most common silent failure mode.**

**Fix:**
```bash
./scripts/reset-webhook.sh  # Delete + re-register, clears backoff state
```

Or manually:
```bash
# Delete existing webhook (get ID from list first)
curl -X DELETE "http://127.0.0.1:1234/api/v1/webhook/WEBHOOK_ID?password=YOUR_PASSWORD"

# Re-register
curl -X POST "http://127.0.0.1:1234/api/v1/webhook?password=YOUR_PASSWORD" \
  -H "Content-Type: application/json" \
  -d '{"url": "http://localhost:18789/api/channels/bluebubbles/webhook", "events": ["*"]}'
```

---

## Issue: Gateway Endpoint Unresponsive

**Symptom:** BB server healthy, webhook registered, but gateway endpoint returns error.

**Causes:**
- OpenClaw gateway not running
- Wrong gateway port (default is 18789)
- Gateway crashed

**Fix:**
```bash
# Check gateway status
openclaw gateway status

# Restart if needed
openclaw gateway restart

# Verify endpoint
curl http://localhost:18789/api/channels/bluebubbles/webhook
```

---

## When to Use `--dry-run`

Use `heal.sh --dry-run` to:
- See what would be fixed without making changes
- Verify diagnosis before auto-healing
- Debug in sensitive environments

```bash
./scripts/heal.sh --dry-run
```

---

## Manual Verification Sequence

When all else fails, verify each component:

```bash
# 1. BB server running?
curl "http://127.0.0.1:1234/api/v1/ping?password=$BB_PASSWORD"

# 2. Webhook registered?
curl "http://127.0.0.1:1234/api/v1/webhook?password=$BB_PASSWORD"

# 3. Gateway endpoint responding?
curl http://localhost:18789/api/channels/bluebubbles/webhook

# 4. Check BB logs for delivery errors
curl "http://127.0.0.1:1234/api/v1/server/logs?password=$BB_PASSWORD" | grep -i "webhook\|delivery\|backoff"
```

If steps 1-3 pass but messages still don't arrive → reset webhook to clear backoff state.
