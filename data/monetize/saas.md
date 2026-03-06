# SaaS: Subscriptions That Scale

## Freemium vs Trial

No universal rule. Consider:

| Factor | → Freemium | → Trial |
|--------|------------|---------|
| Network effects | Strong | Weak |
| Time to value | <5 min | >30 min |
| Viral coefficient | >0.5 | <0.3 |
| Sales cycle | Self-serve | Touch needed |

**The real question:** Do free users CREATE value for paid users?
- Yes → Freemium (Slack, Figma)
- No → Trial (Superhuman, Linear)

## Tier Structure

Three tiers. Make the middle one a decoy.

| | Starter | Pro | Team |
|---|---------|-----|------|
| Price | $29/mo | $79/mo | $99/mo |
| Core features | ✓ | ✓ | ✓ |
| Limits | Low | High | Unlimited |
| Key differentiator | — | Main feature | + Team features |

Pro at $79 makes Team at $99 obvious value.

**Per-seat?** Only if value scales with people. If not, usage-based or flat.

## Value Metric Selection

**Test:** If customer doubles the metric, do they pay 2x AND feel good about it?

| Metric | Works For |
|--------|-----------|
| Per seat | Collaboration (Slack, Notion) |
| Per usage | APIs, infrastructure (Twilio) |
| Per feature | Horizontal (Zapier) |
| Flat + overage | Predictable + growth (Intercom) |

## Annual vs Monthly

- Discount: 15-20% (more devalues)
- Frame as savings: "$79/year (save $79)" not "17% off"
- Default UI to annual
- Target: 60% annual, 40% monthly

## Enterprise Readiness

**Don't build enterprise features until enterprises ask.**

When they do, minimum requirements:

| Feature | Why |
|---------|-----|
| SSO (SAML) | Security compliance |
| SCIM | Auto user provisioning |
| Audit logs | Who did what, when |
| Role-based access | Admin/Member/Viewer |

**If they ask for SSO, price floor is $1,000/month.** They can pay it.

## Expansion Revenue

Target: Net Revenue Retention >110%

| Tactic | When to Trigger |
|--------|-----------------|
| Seat expansion | Team invites increase |
| Usage upsell | 80% of limit |
| Tier upgrade | Request Pro feature |

**Automate:** Emails at 70%, 90%, 100% of limits.

## Churn Prevention

**Warning signs:**
- Login <1x/week
- Core features unused
- Support tickets spike then silence

**Actions:**
- Health score alerts to CS
- Offer "pause" instead of cancel
- Exit survey with retention offer (meaningful, not desperate)

## Quick NRR Formula

```
NRR = (Start MRR + Expansion - Contraction - Churn) ÷ Start MRR

Target: >110%
Great: >120%
```

## What to Avoid

- Pricing tables copied from competitors without understanding why
- "Contact us" as the only enterprise option (lazy)
- Free tier that's 90% of the product (no urgency)
- Discounting to close every deal (trains customers)
- Grandfathering everyone forever (pricing debt)
