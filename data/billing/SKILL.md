---
name: Billing
slug: billing
version: 1.0.0
description: Build payment integrations, subscription management, and invoicing systems with webhook handling, tax compliance, and revenue recognition.
metadata: {"clawdbot":{"emoji":"💳","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs to implement or debug payment processing, subscription lifecycles, invoicing, or revenue operations. Agent handles Stripe/Paddle integration, webhook architecture, multi-currency, tax compliance, chargebacks, usage-based billing, marketplace splits, and revenue recognition patterns.

## Quick Reference

| Topic | File |
|-------|------|
| Stripe integration | `stripe.md` |
| Webhooks & events | `webhooks.md` |
| Subscription lifecycle | `subscriptions.md` |
| Invoice generation | `invoicing.md` |
| Tax compliance | `tax.md` |
| Usage-based billing | `usage-billing.md` |
| Chargebacks & disputes | `disputes.md` |
| Marketplace payments | `marketplace.md` |
| Revenue recognition | `revenue-recognition.md` |

## Core Rules

### 1. Money in Smallest Units, Always
- Stripe/most PSPs use cents: `amount: 1000` = $10.00
- Store amounts as integers, NEVER floats (floating-point math fails)
- Always clarify currency in variable names: `amount_cents_usd`
- Different currencies have different decimal places (JPY has 0, KWD has 3)

### 2. Webhook Security is Non-Negotiable
- ALWAYS verify signatures before processing (`Stripe-Signature` header)
- Store `event_id` and check idempotency — webhooks duplicate
- Events arrive out of order — design state machines, not sequential flows
- Use raw request body for signature verification, not parsed JSON
- See `webhooks.md` for implementation patterns

### 3. Subscription State Machine
Critical states and transitions:
| State | Meaning | Access |
|-------|---------|--------|
| `trialing` | Free trial period | ✅ Full |
| `active` | Paid and current | ✅ Full |
| `past_due` | Payment failed, retrying | ⚠️ Grace period |
| `canceled` | Will end at period end | ✅ Until period_end |
| `unpaid` | Exhausted retries | ❌ None |

Never grant access based on `status === 'active'` alone — check `current_period_end`.

### 4. Cancel vs Delete: Revenue at Stake
- `cancel_at_period_end: true` → Access until period ends, stops renewal
- `subscription.delete()` → Immediate termination, possible refund
- Confusing these loses revenue OR creates angry customers
- Default to cancel-at-period-end; immediate delete only when requested

### 5. Proration Requires Explicit Choice
When changing plans mid-cycle:
| Mode | Behavior | Use When |
|------|----------|----------|
| `create_prorations` | Credit unused, charge new | Standard upgrades |
| `none` | Change at renewal only | Downgrades |
| `always_invoice` | Immediate charge/credit | Enterprise billing |

Never rely on PSP defaults — specify explicitly every time.

### 6. Race Conditions Are Guaranteed
`customer.subscription.updated` fires BEFORE `invoice.paid` frequently.
- Design for eventual consistency
- Use database transactions for access changes
- Idempotent handlers that can safely reprocess
- Status checks before granting/revoking access

### 7. Tax Compliance Is Not Optional
| Scenario | Action |
|----------|--------|
| Same country | Charge local VAT/sales tax |
| EU B2B + valid VAT | 0% reverse charge (verify via VIES) |
| EU B2C | MOSS — charge buyer's country VAT |
| US | Sales tax varies by 11,000+ jurisdictions |
| Export (non-EU) | 0% typically |

Missing required invoice fields = legally invalid invoice. See `tax.md`.

### 8. PCI-DSS: Never Touch Card Data
- NEVER store PAN, CVV, or magnetic stripe data
- Only store PSP tokens (`pm_*`, `cus_*`)
- Tokenization happens client-side (Stripe.js, Elements)
- Even "last 4 digits + expiry" is PCI scope if stored together
- See `disputes.md` for compliance patterns

### 9. Chargebacks Have Deadlines
| Stage | Timeline | Action |
|-------|----------|--------|
| Inquiry | 1-3 days | Provide evidence proactively |
| Dispute opened | 7-21 days | Submit compelling evidence |
| Deadline missed | Automatic loss | Set alerts |

>3 intentos de cobro fallidos consecutivos = posible trigger de fraude monitoring.

### 10. Revenue Recognition ≠ Cash Collected
For SaaS under ASC 606/IFRS 15:
- Annual payment ≠ annual revenue (recognized monthly)
- Deferred revenue is a liability, not an asset
- Multi-element contracts require allocation to performance obligations
- See `revenue-recognition.md` for accounting patterns

## Billing Traps

### Security & Compliance
- Webhook without signature verification → attackers fake `invoice.paid`
- Storing tokens in frontend JS → extractable by attackers
- CVV in logs → PCI violation, massive fines
- Retry loops without limits → fraud monitoring triggers

### Integration Errors
- Not storing `subscription_id` → impossible to reconcile refunds
- Assuming charge success = payment complete (3D Secure exists)
- Ignoring `payment_intent.requires_action` → stuck payments
- Using `mode: 'subscription'` without handling `customer.subscription.deleted`

### Financial Errors
- Hardcoding tax rates → wrong when rates change
- Amounts in dollars when PSP expects cents → 100x overcharge
- Recognizing 100% revenue upfront on annual plans → audit findings
- Confusing bookings vs billings vs revenue → material discrepancies

### Operational Errors
- Sending payment reminders during contractual grace period
- Dunning without checking for open disputes → double loss
- Proration without specifying mode → unexpected customer charges
- Refunding without checking for existing chargeback → paying twice
