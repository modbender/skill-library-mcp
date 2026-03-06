---
name: Payments
description: Integrate payments with provider selection, checkout flows, subscription billing, and security best practices.
---

## Situation Detection

| Context | Load |
|---------|------|
| Choosing Stripe vs Paddle vs LemonSqueezy | `providers.md` |
| Implementing checkout, webhooks, refunds | `integration.md` |
| Subscription billing, trials, upgrades | `subscriptions.md` |
| PCI compliance, fraud prevention | `security.md` |

---

## Universal Rules

**Never store card data.** Use provider-hosted checkout or tokenization. PCI compliance burden explodes the moment raw card numbers touch your server.

**Webhooks are truth.** Client-side success callbacks lie. A payment succeeded only when your webhook confirms it. Design for webhook-first verification.

**Test mode exists for a reason.** Use test cards, simulate failures, verify webhook handling. Production surprises cost real money and real customers.

**Pricing psychology:** $9.99/mo feels cheaper than $120/year, but annual retention is 2-3x higher. Default to annual with monthly option, not the reverse.

---

## Provider Quick Compare

| Need | Recommendation |
|------|----------------|
| US/global B2C | Stripe (best docs, widest coverage) |
| SaaS selling to EU (VAT headache) | Paddle, LemonSqueezy (merchant of record) |
| Simple product, no dev resources | Gumroad, Lemonsqueezy hosted |
| Marketplace with splits | Stripe Connect |
| High-risk or adult | Specialized processors (CCBill, Epoch) |

See `providers.md` for detailed comparison.

---

## Integration Checklist

Before going live:
- [ ] Webhook endpoint secured and verified
- [ ] Idempotency keys on all charges
- [ ] Failure states handled (declined, expired, insufficient)
- [ ] Receipts and invoices configured
- [ ] Refund flow tested
- [ ] Subscription lifecycle events handled (upgrade, downgrade, cancel)
- [ ] Currency handling explicit (store in cents/smallest unit)

---

## Red Flags

- Storing CVV anywhere, ever → Instant PCI violation
- Trusting client-side payment confirmation → Fraud vector
- No retry logic for failed webhooks → Lost transactions
- Hardcoding prices in frontend → Easy manipulation
- Missing `cancel_at_period_end` handling → Angry customers

---

## When to Load More

| Situation | Reference |
|-----------|-----------|
| Evaluating payment processors | `providers.md` |
| Building checkout, handling webhooks | `integration.md` |
| Recurring billing, metering, trials | `subscriptions.md` |
| Fraud, PCI, chargebacks | `security.md` |
