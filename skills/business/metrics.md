# Metrics Reference — Business Strategy

## Universal Metrics

### Growth
| Metric | Formula | Good | Great |
|--------|---------|------|-------|
| MoM Growth | (This month - Last month) / Last month | >10% | >20% |
| WoW Growth | (This week - Last week) / Last week | >3% | >7% |
| YoY Growth | (This year - Last year) / Last year | >100% | >200% |

### Retention
| Metric | Formula | Good | Great |
|--------|---------|------|-------|
| Day 1 Retention | Users active Day 1 / Users signed up | >40% | >60% |
| Day 7 Retention | Users active Day 7 / Users signed up | >20% | >35% |
| Day 30 Retention | Users active Day 30 / Users signed up | >10% | >20% |
| Monthly Churn | Users lost / Starting users | <5% | <2% |

### Revenue
| Metric | Formula | Good | Great |
|--------|---------|------|-------|
| LTV/CAC Ratio | Customer Lifetime Value / Cost to Acquire | >3× | >5× |
| Gross Margin | (Revenue - COGS) / Revenue | >60% | >80% |
| Net Revenue Retention | (MRR from existing) / (Starting MRR) | >100% | >120% |
| Quick Ratio | (New MRR + Expansion) / (Churn + Contraction) | >2 | >4 |

---

## By Business Type

### SaaS B2B

**North Star:** Net Revenue Retention (NRR)

| Stage | Focus Metric | Target |
|-------|--------------|--------|
| Pre-PMF | Activation rate | >40% complete onboarding |
| Early | Churn rate | <5% monthly |
| Growth | NRR | >110% |
| Scale | LTV/CAC | >5× |

**Benchmark Targets:**
```
Conversion: Free trial → Paid:     15-25%
Activation: Complete key action:   40-60%
Monthly churn: SMB:                 3-5%
Monthly churn: Enterprise:         <1%
Expansion revenue (% of new ARR):  >30%
```

### SaaS B2C / Consumer Subscription

**North Star:** Monthly Active Users → Paid conversion

| Stage | Focus Metric | Target |
|-------|--------------|--------|
| Pre-PMF | D1 retention | >40% |
| Early | Free → Paid conversion | >5% |
| Growth | D30 retention | >20% |
| Scale | LTV/CAC | >3× |

**Benchmark Targets:**
```
Free → Paid conversion:    2-5%
D1 retention:              40-60%
D7 retention:              20-40%
D30 retention:             15-25%
Yearly churn:              <40%
```

### E-commerce / DTC

**North Star:** Repeat Purchase Rate

| Stage | Focus Metric | Target |
|-------|--------------|--------|
| Early | Conversion rate | >2% |
| Growth | Repeat purchase | >25% |
| Scale | LTV/CAC | >3× |
| Mature | AOV growth | >10% YoY |

**Benchmark Targets:**
```
Site conversion rate:       1-3%
Cart abandonment:           <70%
Repeat purchase rate:       25-40%
AOV (Average Order Value):  Varies by category
Email capture rate:         >5%
```

### Marketplace

**North Star:** GMV (Gross Merchandise Value)

| Stage | Focus Metric | Target |
|-------|--------------|--------|
| Pre-PMF | Supply liquidity | >70% match rate |
| Early | Take rate sustainability | Stable at target % |
| Growth | GMV growth | >15% MoM |
| Scale | Network effects | Increasing retention |

**Benchmark Targets:**
```
Take rate:              5-20% (category dependent)
Buyer repeat rate:      >40%
Seller retention:       >80%
Supply utilization:     >60%
Match rate:             >70%
```

### Mobile App (Free)

**North Star:** DAU/MAU Ratio

| Stage | Focus Metric | Target |
|-------|--------------|--------|
| Pre-PMF | D1 retention | >40% |
| Early | D7 retention | >20% |
| Growth | DAU/MAU | >20% |
| Scale | Monetization | $1-5 ARPU |

**Benchmark Targets:**
```
D1 retention:           25-40%
D7 retention:           15-25%
D30 retention:          8-15%
DAU/MAU:                20-30% (good), >50% (great)
Sessions per DAU:       >2
```

---

## Stage-Based Focus

### Pre-Product-Market-Fit
**Only metric that matters:** Do people come back without prompting?

| Signal | Measurement |
|--------|-------------|
| Organic retention | Users return without email/push |
| Word of mouth | "How did you hear about us?" = friend |
| Disappointment | 40%+ would be "very disappointed" if gone |
| Usage depth | Completing core action repeatedly |

**Stop measuring:**
- Revenue (too early)
- Growth rate (meaningless at small scale)
- Conversion optimization (optimize what works)

### Early Stage (Pre-Series A)
**Focus:** Activation → Retention → Revenue

| Priority | Metric | Why |
|----------|--------|-----|
| 1 | Activation rate | Users must experience value |
| 2 | Week 1 retention | Must prove stickiness |
| 3 | Revenue per user | Must prove monetization |

### Growth Stage (Series A+)
**Focus:** Efficient growth

| Priority | Metric | Why |
|----------|--------|-----|
| 1 | LTV/CAC by channel | Identify efficient channels |
| 2 | Net Revenue Retention | Expansion > churn |
| 3 | Payback period | Cash efficiency |

---

## Warning Signs

### Red Flags (Act Immediately)
- Monthly churn >10%: You have a retention crisis
- LTV/CAC <1: You're losing money on every customer
- NRR <80%: Revenue shrinking from existing base
- CAC increasing >20% QoQ: Channels saturating

### Yellow Flags (Investigate)
- Activation rate <30%: Onboarding friction
- D1 retention <25%: First experience failing
- Trial-to-paid <10%: Value prop unclear
- Support tickets per user increasing: Product issues

### Green Flags (Double Down)
- Organic growth >30% of new users: Word of mouth working
- NRR >120%: Strong expansion revenue
- Payback <6 months: Efficient growth possible
- CAC decreasing: Channels improving

---

## Quick Calculations

### LTV Calculation
```
Simple:
LTV = ARPU / Monthly Churn Rate

Example:
ARPU = $50/month, Churn = 5%
LTV = $50 / 0.05 = $1,000
```

### CAC Calculation
```
CAC = (Sales + Marketing Spend) / New Customers

Example:
Spent $10,000, got 50 customers
CAC = $10,000 / 50 = $200
```

### Payback Period
```
Payback = CAC / (ARPU × Gross Margin)

Example:
CAC = $200, ARPU = $50, Margin = 80%
Payback = $200 / ($50 × 0.80) = 5 months
```

### Break-Even Customers
```
Break-even = Fixed Costs / (ARPU - Variable Cost per Customer)

Example:
Fixed = $10,000/month, ARPU = $50, Variable = $10
Break-even = $10,000 / ($50 - $10) = 250 customers
```
