# Product Metrics

## Revenue Metrics

### MRR (Monthly Recurring Revenue)
**Definition:** Predictable monthly subscription revenue

**Components:**
| Type | Definition |
|------|------------|
| New MRR | Revenue from new customers |
| Expansion MRR | Upgrades, add-ons from existing |
| Contraction MRR | Downgrades from existing |
| Churn MRR | Lost from cancellations |
| Net New MRR | New + Expansion - Contraction - Churn |

**ARR = MRR × 12**

### Net Revenue Retention (NRR)
**Formula:** (Starting MRR + Expansion - Contraction - Churn) / Starting MRR

| Range | Meaning |
|-------|---------|
| <100% | Losing revenue; need constant new customers |
| 100-110% | Healthy |
| 110-130% | Great expansion motion |
| >130% | Exceptional |

## Acquisition Metrics

### CAC (Customer Acquisition Cost)
**Formula:** (Sales + Marketing Costs) / New Customers

Include: ads, salaries, tools, agency fees

### LTV (Customer Lifetime Value)
**Simple:** ARPU × Average Customer Lifetime

**SaaS:** ARPU × Gross Margin × (1 / Churn Rate)

### LTV:CAC Ratio
| Ratio | Meaning |
|-------|---------|
| <1:1 | Losing money per customer |
| 1:1-3:1 | Unsustainable |
| **3:1** | Healthy target |
| 3:1-5:1 | Efficient |
| >5:1 | Under-investing in growth |

### CAC Payback Period
**Formula:** CAC / (ARPU × Gross Margin)

| Period | Meaning |
|--------|---------|
| <6 months | Great |
| 6-12 months | Healthy |
| 12-18 months | Acceptable for enterprise |
| >18 months | Concerning |

## Retention Metrics

### Churn Rate
**Formula:** Customers Lost / Starting Customers

**Monthly to Annual:** 5% monthly ≈ 46% annual (1 - 0.95^12)

**Targets:**
- SMB SaaS: <2% monthly
- Enterprise: <1% monthly

### Retention Rate
**Formula:** 100% - Churn Rate

## Engagement Metrics

### DAU/MAU Ratio
**Definition:** Stickiness indicator

| Ratio | Meaning | Example |
|-------|---------|---------|
| >50% | Very sticky | Slack, messaging |
| 25-50% | Healthy | Project tools |
| 10-25% | Periodic use | Reports, billing |
| <10% | Low engagement | One-time tasks |

### Activation Rate
**Formula:** Users completing activation / Total signups

Define activation by product:
- Notion: Created page + invited collaborator
- Figma: Design with 5+ elements
- Slack: 10 messages in 2+ channels

### Time-to-Value (TTV)
Median time from signup to activation event

**Goal:** Minimize TTV → higher conversion + retention

## Growth Metrics

### Quick Ratio
**Formula:** (New MRR + Expansion) / (Contraction + Churn)

| Ratio | Meaning |
|-------|---------|
| <1 | Shrinking |
| 1-2 | Slow growth |
| 2-4 | Healthy |
| >4 | Hypergrowth |

### Viral Coefficient (K-factor)
**Formula:** Invites Sent × Conversion Rate

- K > 1: Viral growth
- K < 1: Need paid acquisition

### NPS (Net Promoter Score)
**Question:** "How likely to recommend?" (0-10)

- 9-10: Promoters
- 7-8: Passives
- 0-6: Detractors

**Formula:** % Promoters - % Detractors

| Score | Meaning |
|-------|---------|
| <0 | Problem |
| 0-30 | Good |
| 30-50 | Great |
| 50-70 | Excellent |
| >70 | World class |

## Stage-Based Focus

| Stage | Focus Metrics |
|-------|---------------|
| Pre-PMF | Activation, Retention, Sean Ellis |
| Finding PMF | NRR, Sean Ellis >40%, Retention curve |
| Post-PMF Scaling | MRR Growth, CAC Payback, LTV:CAC |
| Mature | NRR >110%, Quick Ratio >4 |
