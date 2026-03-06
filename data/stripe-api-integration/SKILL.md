---
name: Stripe API Integration
slug: stripe-api-integration
version: 1.0.2
homepage: https://clawic.com/skills/stripe-api-integration
description: Complete Stripe API integration for payments, subscriptions, checkout, invoices, webhooks, Connect, Issuing, Terminal, and Treasury.
changelog: Use ~/stripe-api-integration/ as config path (matching slug).
metadata: {"clawdbot":{"emoji":"💳","requires":{"env":["STRIPE_SECRET_KEY","STRIPE_WEBHOOK_SECRET"],"config":["~/stripe-api-integration/"]},"primaryEnv":"STRIPE_SECRET_KEY","os":["linux","darwin","win32"]}}
---

# Stripe API Integration

Complete Stripe API reference. See auxiliary files for detailed operations.

## Quick Start

```bash
curl https://api.stripe.com/v1/balance -u "$STRIPE_SECRET_KEY:"
```

## Setup

On first use, read `setup.md`. Preferences stored in `~/stripe-api-integration/memory.md`.

## When to Use

Any Stripe operation: payments, subscriptions, invoices, checkout, webhooks, Connect, Issuing, Terminal, Treasury.

## Architecture

```
~/stripe-api-integration/
├── memory.md      # Account context
└── webhooks.md    # Webhook configs
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup & memory | `setup.md`, `memory-template.md` |
| Payments, refunds, disputes | `payments.md` |
| Customers, products, prices | `customers.md` |
| Subscriptions, usage billing | `subscriptions.md` |
| Checkout Sessions | `checkout.md` |
| Connect (marketplaces) | `connect.md` |
| Webhooks & events | `webhooks.md` |
| Invoices, quotes, tax | `invoices.md` |
| Issuing, Terminal, Treasury, Identity, Radar | `advanced.md` |

## Core Rules

1. **Test mode first** — Use `sk_test_*` keys. Test card: `4242424242424242`
2. **Amounts in cents** — $10.00 = 1000
3. **Idempotency keys** — Prevent duplicate charges
4. **Webhooks required** — Never trust API response alone
5. **Expand objects** — Use `?expand[]=customer` for related data
6. **Pagination** — Use `starting_after` for large lists
7. **Error handling** — See `payments.md` for error codes

## Authentication

**Required environment variables:**
- `STRIPE_SECRET_KEY` — API key for all Stripe operations (starts with `sk_test_` or `sk_live_`)
- `STRIPE_WEBHOOK_SECRET` — Signing secret for webhook verification (starts with `whsec_`)

```bash
curl https://api.stripe.com/v1/customers -u "$STRIPE_SECRET_KEY:"
```

## Common Traps

- Amount in dollars not cents → 100x wrong charge
- No idempotency key → duplicate charges
- Skip webhook verification → accept fake events
- Ignore `requires_action` → 3DS stuck

## External Endpoints

| Endpoint | Purpose |
|----------|---------|
| `https://api.stripe.com/v1/*` | API |

## Security & Privacy

**Environment variables used:**
- `STRIPE_SECRET_KEY` — for API authentication
- `STRIPE_WEBHOOK_SECRET` — for webhook signature verification

**Sent to Stripe:** Customer info, payment data via api.stripe.com
**Stays local:** API keys (never logged), ~/stripe-api-integration/ preferences
**Never:** Log card numbers, skip webhook verification, expose keys

## Trust

This skill sends data to Stripe (stripe.com).

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `api` — REST API patterns
- `saas` — SaaS metrics
- `webhook` — Webhook patterns

## Feedback

- If useful: `clawhub star stripe-api-integration`
- Stay updated: `clawhub sync`
