---
name: PayPal
slug: paypal
version: 1.0.0
description: Integrate PayPal payments with proper webhook verification, OAuth handling, and security validation for checkout flows and subscriptions.
metadata: {"clawdbot":{"emoji":"💳","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to integrate PayPal REST API for payments, subscriptions, or payouts. Agent handles checkout flows, webhook verification, OAuth token management, and dispute workflows.

## Quick Reference

| Topic | File |
|-------|------|
| Code patterns | `patterns.md` |
| Webhook events | `webhooks.md` |

## Core Rules

### 1. Environment URLs are Different
- Sandbox: `api.sandbox.paypal.com`
- Production: `api.paypal.com`
- Ask which environment BEFORE generating code
- Credentials are environment-specific — never mix

### 2. OAuth Token Management
```javascript
// Token expires ~8 hours — handle refresh
const getToken = async () => {
  const res = await fetch('https://api.paypal.com/v1/oauth2/token', {
    method: 'POST',
    headers: {
      'Authorization': `Basic ${Buffer.from(`${clientId}:${secret}`).toString('base64')}`,
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: 'grant_type=client_credentials'
  });
  return res.json(); // { access_token, expires_in }
};
```
Never hardcode tokens. Implement refresh logic.

### 3. Webhook Verification is Mandatory
PayPal webhooks MUST be verified via API call — not simple HMAC:
```javascript
// POST /v1/notifications/verify-webhook-signature
const verification = await fetch('https://api.paypal.com/v1/notifications/verify-webhook-signature', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' },
  body: JSON.stringify({
    auth_algo: headers['paypal-auth-algo'],
    cert_url: headers['paypal-cert-url'],
    transmission_id: headers['paypal-transmission-id'],
    transmission_sig: headers['paypal-transmission-sig'],
    transmission_time: headers['paypal-transmission-time'],
    webhook_id: WEBHOOK_ID,
    webhook_event: body
  })
});
// verification_status === 'SUCCESS'
```

### 4. CAPTURE vs AUTHORIZE — Ask First
| Intent | Behavior |
|--------|----------|
| `CAPTURE` | Charges immediately on approval |
| `AUTHORIZE` | Reserves funds, capture later (up to 29 days) |

Changing intent after integration breaks the entire flow.

### 5. Server-Side Validation — Never Trust Client
```javascript
// After client approves, VERIFY on server before fulfillment
const order = await fetch(`https://api.paypal.com/v2/checkout/orders/${orderId}`, {
  headers: { 'Authorization': `Bearer ${token}` }
}).then(r => r.json());

// Validate ALL of these:
if (order.status !== 'APPROVED') throw new Error('Not approved');
if (order.purchase_units[0].amount.value !== expectedAmount) throw new Error('Amount mismatch');
if (order.purchase_units[0].amount.currency_code !== expectedCurrency) throw new Error('Currency mismatch');
if (order.purchase_units[0].payee.merchant_id !== YOUR_MERCHANT_ID) throw new Error('Wrong merchant');
```

### 6. Idempotency in Webhooks
PayPal may send the same webhook multiple times:
```javascript
const processed = await db.webhooks.findOne({ eventId: body.id });
if (processed) return res.status(200).send('Already processed');
await db.webhooks.insert({ eventId: body.id, processedAt: new Date() });
// Now process the event
```

### 7. Currency Decimal Rules
Some currencies have NO decimal places:
| Currency | Decimals | Example |
|----------|----------|---------|
| USD, EUR | 2 | "10.50" |
| JPY, TWD | 0 | "1050" (NOT "1050.00") |

Sending "10.50" for JPY = API error.

## Common Traps

- **IPN vs Webhooks** — IPN is legacy. Use Webhooks for new integrations. Never mix.
- **Order states** — CREATED → APPROVED → COMPLETED (or VOIDED). Handle ALL states, not just happy path.
- **Decimal confusion** — PayPal uses strings for amounts ("10.50"), not floats. Some currencies forbid decimals.
- **Sandbox rate limits** — Lower than production. Don't assume prod will fail the same way.
- **Payout vs Payment** — Payouts API is separate. Don't confuse sending money (Payouts) with receiving (Orders).
