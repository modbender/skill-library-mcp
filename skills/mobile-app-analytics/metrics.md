# Core Metrics — Mobile App Analytics

## When to Use

User asks about mobile app KPIs, needs metric definitions, or wants to understand what numbers to track. This is the reference for all standard mobile metrics.

## Engagement Metrics

### DAU / MAU

| Metric | Definition | Good Benchmark |
|--------|------------|----------------|
| DAU | Unique users opening app per day | Depends on category |
| WAU | Unique users per week | 2-3x DAU |
| MAU | Unique users per month | 3-5x WAU |
| DAU/MAU | Stickiness ratio | >20% is good |

**DAU/MAU by category:**
| Category | Typical DAU/MAU |
|----------|-----------------|
| Social | 40-60% |
| Games (casual) | 15-25% |
| Games (hardcore) | 30-50% |
| Productivity | 20-30% |
| News | 25-40% |
| Fitness | 15-25% |

### Session Metrics

| Metric | Definition | Benchmark |
|--------|------------|-----------|
| Sessions/DAU | App opens per active user | 2-5x |
| Session length | Time per session | 3-15 min |
| Session interval | Time between sessions | Varies |

## Retention Metrics

### Cohort Retention

| Day | Definition | Good Benchmark |
|-----|------------|----------------|
| D1 | % returning next day | >25% |
| D7 | % returning after 7 days | >15% |
| D30 | % returning after 30 days | >10% |
| D90 | % returning after 90 days | >5% |

**Formula:**
```
D{N} Retention = Users active on day N / Users who installed on day 0
```

### Rolling Retention

Users still active ON OR AFTER day N:
```
Rolling D7 = Users active on day 7+ / Install cohort
```

Always higher than classic retention.

### Churn Rate

```
Monthly Churn = (Lost users in month) / (Users at month start)
```

For subscriptions:
```
Subscription Churn = Cancellations / Active subscriptions
```

**Benchmarks:**
| Type | Acceptable | Good |
|------|------------|------|
| Monthly (free app) | <10% | <5% |
| Monthly (subscription) | <8% | <5% |
| Annual (subscription) | <20% | <15% |

## Revenue Metrics

### ARPU / ARPPU

| Metric | Formula | Use Case |
|--------|---------|----------|
| ARPU | Revenue / All users | Overall monetization |
| ARPPU | Revenue / Paying users | Payer value |
| ARPDAU | Revenue / DAU | Daily efficiency |

### LTV (Lifetime Value)

**Simple formula:**
```
LTV = ARPU × Average lifespan (months)
```

**Subscription formula:**
```
LTV = ARPU × (1 / Monthly churn rate)
```

**Example:**
- ARPU: $5/month
- Monthly churn: 5%
- LTV = $5 × (1 / 0.05) = $100

### LTV:CAC Ratio

```
LTV:CAC = Lifetime Value / Customer Acquisition Cost
```

| Ratio | Meaning |
|-------|---------|
| < 1:1 | Losing money |
| 1-3:1 | Unsustainable |
| 3-5:1 | Healthy |
| > 5:1 | Under-investing in growth |

### MRR / ARR

| Metric | Formula |
|--------|---------|
| MRR | Sum of all monthly subscription revenue |
| ARR | MRR × 12 |
| Net MRR | New + Expansion - Churn - Contraction |

## Acquisition Metrics

### CAC (Customer Acquisition Cost)

```
CAC = Marketing spend / New customers acquired
```

**By channel:**
| Channel | Typical CAC |
|---------|-------------|
| Organic | $0-2 |
| ASO | $0.50-2 |
| Facebook Ads | $2-10 |
| Google Ads | $1-8 |
| Influencer | $3-15 |

### Conversion Funnel

```
Impressions → Store visits → Installs → Registrations → Purchases

Track conversion rate at each step:
- Store visit rate = Visits / Impressions
- Install rate = Installs / Visits
- Registration rate = Registrations / Installs
- Purchase rate = Purchases / Registrations
```

### K-Factor (Virality)

```
K = Invites per user × Conversion rate of invites
```

| K-Factor | Meaning |
|----------|---------|
| < 1 | Not viral, need paid acquisition |
| = 1 | Self-sustaining |
| > 1 | Viral growth |

## Quality Metrics

### Crash-Free Rate

```
Crash-free = Sessions without crash / Total sessions
```

| Rate | Status |
|------|--------|
| < 99% | Critical, fix immediately |
| 99-99.5% | Needs attention |
| 99.5-99.9% | Acceptable |
| > 99.9% | Excellent |

### App Rating

| Rating | Impact |
|--------|--------|
| < 3.5 | Conversion penalty |
| 3.5-4.0 | Below average |
| 4.0-4.5 | Good |
| > 4.5 | Excellent, featured potential |

## Formulas Quick Reference

```
DAU/MAU Ratio = DAU / MAU

D1 Retention = Day 1 active / Day 0 installs

Churn Rate = Lost users / Starting users

LTV = ARPU / Churn rate

LTV:CAC = LTV / CAC

K-Factor = Invites × Invite conversion

ARPU = Revenue / Active users

ARPPU = Revenue / Paying users
```

## Metric Priorities by Stage

| Stage | Focus On |
|-------|----------|
| Pre-launch | Crash rate, early retention |
| Launch | D1/D7 retention, conversion |
| Growth | CAC, LTV:CAC, virality |
| Maturity | Churn, ARPU expansion, retention |
| Decline | Reactivation, feature usage |
