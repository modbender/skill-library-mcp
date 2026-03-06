# Thrd API Reference

Thrd provides a machine-first email infrastructure for AI agents.

## Endpoints

### Keep Contract Updated (Auto-sync)
Use:
```bash
python3 scripts/openapi_sync.py
python3 scripts/openapi_sync.py --print-version
```
The script caches `openapi.json` and revalidates via `ETag` / `Last-Modified` so agents do not stay pinned to stale `info.version`.

### Instant Onboarding
**POST** `https://api.thrd.email/v1/onboarding/instant`
Provisions a new tenant, inbox, and API key in one call.

### Poll Events
**GET** `https://api.thrd.email/v1/events`
Uses long-polling (25s window) to deliver inbound email events.

### Wake Webhook (Optional, Recommended)
**GET** `https://api.thrd.email/v1/wake/webhook` - Get webhook status.
**PUT** `https://api.thrd.email/v1/wake/webhook` - Create/update wake webhook.
**DELETE** `https://api.thrd.email/v1/wake/webhook` - Disable wake webhook.

When configured, THRD sends signed `inbox.pending` pings so the runtime can immediately pull `/v1/events`.
Signature format:
- `x-thrd-timestamp: <unix_seconds>`
- `x-thrd-signature: v1=<hex_hmac_sha256(timestamp + "." + raw_body)>`

If your runtime cannot expose a webhook, use:
```bash
python3 scripts/poll_daemon.py --cursor-file .thrd_cursor
```

### Acknowledge Events
**POST** `https://api.thrd.email/v1/events/ack`
Acknowledges processed batches of events.

### Send/Reply
**POST** `https://api.thrd.email/v1/reply`
**POST** `https://api.thrd.email/v1/send`
**GET** `https://api.thrd.email/v1/usage`

**Requirements:**
- `Idempotency-Key` header is mandatory.
- **PoR (Proof of Reasoning):** If you get a `428 por_required`, you must solve the challenge and include `por_token` and `por_answer` in the body.
- **Monthly limits:** Monitor `GET /v1/usage` before/after sends. If you receive `429 monthly_limit_reached`, stop sending and request an upgrade or wait until `reset_at`.

**Reply CC behavior (important):**
- Replies use reply-all behavior: they preserve existing thread CC and keep recipients from the latest inbound `To` line.
- You may pass an optional `cc: string[]` to add additional CC recipients on Tier 2/3.
- Tier 1 (Sandbox) may include only CC addresses that already exist in the thread history; adding new CC will return `403 plan_not_allowed_to_add_cc`.
- Practical tip for Tier 1: omit `cc` unless needed; reply-all preservation is automatic.

**Prompt Shield (inbound prompt-injection firewall):**
- Each inbound message can include a deterministic prompt-injection assessment (`score`, `level`, `flags`).
- Read assessment: **GET** `https://api.thrd.email/v1/messages/{message_id}/security`
- Create ack token when required: **POST** `https://api.thrd.email/v1/security/ack`
- For high-risk inbound context (Tier 2/3), include `security_ack_token` in `POST /v1/reply` or `POST /v1/send`.
- `POST /v1/send` supports optional `source_message_id` to enforce Prompt Shield decisions from a specific inbound email.

### Human Claiming (X)
**POST** `https://api.thrd.email/v1/claim/x/start` - Start verification flow.
**GET** `https://api.thrd.email/v1/claim/x/status` - Check verification status.

### Trust Score
**GET** `https://api.thrd.email/v1/trust/score`
Returns a 0-100 score based on verification, delivery outcomes, and recipient feedback.

### Outbound Status
**GET** `https://api.thrd.email/v1/outbound/{request_id}`
Checks the real-time delivery status of an email.

### Billing and Upgrades
**POST** `https://api.thrd.email/v1/billing/checkout/self`
Creates a Stripe Checkout URL for subscription changes.
- `plan=sandbox`: Sandbox Starter (9 EUR/month, 2,000 emails/month in Tier 1)
- `plan=limited`: Tier 2
- `plan=verified`: Tier 3
