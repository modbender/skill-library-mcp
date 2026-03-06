# Subscription Billing

## Billing Models

### Flat-Rate
Fixed price per period. Simple to implement and understand.
- $10/month for Pro
- $99/year for Premium
- Best for: Most SaaS, clear value proposition

### Tiered / Volume
Price changes based on usage tiers.
- 0-100 users: $50/mo
- 101-500 users: $200/mo
- 501+: $500/mo
- Best for: Collaboration tools, seat-based products

### Usage-Based / Metered
Pay for what you use.
- $0.01 per API call
- $0.10 per GB stored
- Best for: APIs, infrastructure, variable workloads
- Harder to predict revenue

### Hybrid
Base fee + usage.
- $50/mo + $0.01 per additional request
- Best for: Predictable base revenue with upside

---

## Trial Strategies

### Free Trial (Card Required)
- Higher conversion (they're committed)
- Some users won't start (friction)
- Easy chargeback if they forget

### Free Trial (No Card)
- More signups, lower conversion
- Requires good trial-to-paid nurture
- Common for enterprise sales

### Freemium
- Free tier forever, paid for more
- Best for products with viral/network effects
- Can cannibalize paid if free is too generous

**Trial length:** 7 days for simple products, 14-30 for complex. Don't default to 30 — shorter trials create urgency.

---

## Subscription Lifecycle Events

| Event | Handle By |
|-------|-----------|
| Trial started | Send onboarding sequence |
| Trial ending (3 days) | Remind to upgrade |
| Trial ended, no conversion | Offer extension or discount |
| Subscription activated | Send welcome, confirm access |
| Payment failed | Dunning sequence (emails + retries) |
| Plan upgraded | Prorate immediately |
| Plan downgraded | Apply at period end |
| Subscription canceled | Ask why, confirm end date |
| Subscription ended | Revoke access, offer win-back |

---

## Dunning (Failed Payment Recovery)

When a card fails, you have ~30 days before giving up.

**Standard Dunning Sequence:**
1. Day 0: Auto-retry, email "payment failed, updating card?"
2. Day 3: Retry, email with warning
3. Day 7: Retry, email "access at risk"
4. Day 14: Final retry, "account suspended tomorrow"
5. Day 15+: Suspend access, keep trying weekly
6. Day 30: Cancel subscription

**Involuntary churn (failed cards) is 20-40% of all churn.** Good dunning recovers 50%+ of these.

---

## Proration

When users upgrade/downgrade mid-cycle:

**Upgrade:** Charge difference immediately (or at next billing).
**Downgrade:** Credit remaining value, apply at period end.

Most providers handle this automatically. Verify behavior in test mode.

---

## Cancellation Flow

**Don't make it hard to cancel.** Dark patterns create chargebacks and bad reviews.

**Do:**
- Clear "Cancel Subscription" in settings
- Confirm cancel date (end of period, not immediate)
- Offer pause or downgrade as alternatives
- Exit survey (why leaving?)

**Don't:**
- Hidden cancel behind "contact support"
- Immediate access revocation
- Guilt-trip copy ("Your data will be deleted forever!")

---

## Metrics to Track

| Metric | What It Tells You |
|--------|-------------------|
| MRR | Monthly recurring revenue |
| Churn Rate | % of subscribers lost per period |
| LTV | Lifetime value per customer |
| CAC | Cost to acquire customer |
| LTV:CAC | Ratio (3:1+ is healthy) |
| Net Revenue Retention | Expansion - Churn (>100% = growth without new customers) |
| Trial-to-Paid Conversion | % of trials that convert |

---

## Common Mistakes

- **No grace period:** Suspend access immediately on failed payment = angry users
- **No dunning:** One email isn't enough. Keep trying.
- **Prorating wrong:** User pays $100/year, upgrades month 2 to $200 plan — they owe $91.67, not $100
- **Offering only monthly:** Annual plans have 2-3x retention. Always offer both.
- **Ignoring timezone:** "End of day" is different in SF and Singapore. Use UTC or explicit timestamps.
