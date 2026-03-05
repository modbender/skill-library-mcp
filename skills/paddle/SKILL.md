---
name: Paddle
slug: paddle
version: 1.0.0
homepage: https://clawic.com/skills/paddle
description: Integrate Paddle payments with subscriptions, webhooks, checkout, and tax compliance.
changelog: Initial release with API reference, webhook handling, and checkout integration.
metadata: {"clawdbot":{"emoji":"🏓","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User needs to integrate Paddle for SaaS payments. Agent handles API calls, webhook verification, checkout setup, subscription management, and tax compliance configuration.

## Architecture

Memory lives in `~/paddle/`. See `memory-template.md` for structure.

```
~/paddle/
├── memory.md     # API keys, environment, product IDs
└── webhooks.md   # Webhook endpoints and event handling
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| API endpoints | `api.md` |
| Webhook handling | `webhooks.md` |

## Core Rules

### 1. Always Use Sandbox First
- Test ALL integrations in sandbox before production
- Sandbox API: `https://sandbox-api.paddle.com`
- Production API: `https://api.paddle.com`
- Never skip sandbox testing for payment flows

### 2. Verify Webhook Signatures
- Every webhook MUST be verified before processing
- Use the webhook secret from Paddle dashboard
- Reject requests with invalid signatures immediately
- Log failed verifications for debugging

### 3. Handle Subscription States Correctly
| State | Meaning | Action |
|-------|---------|--------|
| `active` | Paying customer | Grant access |
| `trialing` | In trial period | Grant access, remind before end |
| `past_due` | Payment failed | Retry period, warn user |
| `paused` | User paused | Restrict access, allow resume |
| `canceled` | Subscription ended | Revoke access at period end |

### 4. Store Paddle IDs Correctly
- `customer_id` (ctm_xxx) — unique per customer
- `subscription_id` (sub_xxx) — unique per subscription
- `transaction_id` (txn_xxx) — unique per payment
- `price_id` (pri_xxx) — your pricing configuration
- Map these to your internal user/subscription records

### 5. Use Paddle Retain for Dunning
- Enable Paddle Retain in dashboard for failed payments
- It handles retry logic and customer communication
- Track `subscription.past_due` events but let Paddle retry first
- Only take action after `subscription.canceled` from failed payments

## Common Traps

- **Hardcoding price IDs** → Use environment variables, prices change between sandbox/production
- **Processing webhooks without verification** → Security vulnerability, anyone can fake events
- **Ignoring `past_due` state** → User loses access during retry window, bad UX
- **Not handling proration** → Confusing charges when users upgrade/downgrade mid-cycle
- **Testing with production keys** → Real charges, angry customers, refund headaches

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| https://api.paddle.com | Customer data, subscription info | Payment processing |
| https://sandbox-api.paddle.com | Test customer data | Sandbox testing |

No other data is sent externally.

## Security & Privacy

**Data that leaves your machine:**
- Customer email and name sent to Paddle for billing
- Payment amounts and subscription details
- IP addresses for tax calculation

**Data that stays local:**
- API keys stored in environment variables
- Webhook secrets never logged
- Internal user mappings

**This skill does NOT:**
- Store credit card numbers (Paddle handles PCI compliance)
- Access payment methods directly
- Share customer data with third parties beyond Paddle

## Trust

By using this skill, customer and payment data is sent to Paddle.
Only install if you trust Paddle with your billing data.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `billing` — General billing patterns
- `payments` — Payment processing
- `subscriptions` — Subscription management

## Feedback

- If useful: `clawhub star paddle`
- Stay updated: `clawhub sync`
