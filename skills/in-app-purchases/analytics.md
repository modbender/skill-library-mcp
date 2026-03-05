# Subscription Analytics — Metrics & Tracking

## Core Metrics

### Revenue Metrics

| Metric | Definition | Formula |
|--------|------------|---------|
| MRR | Monthly Recurring Revenue | Sum of all monthly subscription value |
| ARR | Annual Recurring Revenue | MRR × 12 |
| MTR | Monthly Tracked Revenue | Platform-specific (for pricing tiers) |
| ARPU | Average Revenue Per User | Revenue / Active Users |
| ARPPU | Average Revenue Per Paying User | Revenue / Paying Users |
| LTV | Lifetime Value | ARPU × Average Lifespan (months) |

### Growth Metrics

| Metric | Definition | Formula |
|--------|------------|---------|
| New MRR | MRR from new subscribers | Sum of first subscriptions |
| Expansion MRR | MRR from upgrades | Upgrade revenue increase |
| Contraction MRR | MRR lost to downgrades | Downgrade revenue decrease |
| Churned MRR | MRR lost to cancellations | Cancelled subscription value |
| Net MRR | Monthly MRR change | New + Expansion - Contraction - Churned |

### Conversion Metrics

| Metric | Definition | Target |
|--------|------------|--------|
| Install → Trial | Trial starts / Installs | 10-30% |
| Trial → Paid | Paid / Trial starts | 40-70% |
| Install → Paid | Paid / Installs | 2-10% |
| Paywall → Trial | Trials / Paywall views | 15-40% |
| Overall conversion | Subscribers / Installs | 2-5% |

### Retention Metrics

| Metric | Definition | Healthy |
|--------|------------|---------|
| Day 1 retention | Users active day after install | >40% |
| Day 7 retention | Users active 7 days after | >20% |
| Day 30 retention | Users active 30 days after | >10% |
| Monthly churn | Churned / Start of month subscribers | <5% |
| Annual retention | 1 - Annual churn | >70% |

## LTV Calculation

### Simple LTV
```
LTV = ARPU × Average Customer Lifespan

Example:
- ARPU: $5/month
- Average lifespan: 8 months
- LTV: $40
```

### LTV with Churn
```
LTV = ARPU / Monthly Churn Rate

Example:
- ARPU: $5/month
- Monthly churn: 10%
- LTV: $5 / 0.10 = $50
```

### LTV by Cohort
Track LTV for each signup cohort:
```
Jan cohort: $35 average LTV at month 12
Feb cohort: $42 average LTV at month 12
→ Feb improvements working
```

## Churn Analysis

### Types of Churn

| Type | Cause | Action |
|------|-------|--------|
| Voluntary | User cancels | Win-back campaigns |
| Involuntary | Payment fails | Dunning, grace period |
| Implicit | Trial expires | Onboarding improvement |

### Churn Reasons (Track These)
```
- Found alternative
- Too expensive
- Not using enough
- Missing features
- Technical issues
- Just trying out
```

Collect via cancellation survey.

### Reducing Churn

1. **Grace period** - Don't revoke immediately
2. **Dunning** - Retry failed payments
3. **Win-back** - Email churned users with offer
4. **Annual upsell** - Lower churn than monthly
5. **Engagement** - Push notifications, emails
6. **Value reminders** - "You saved 10 hours this month"

## Dashboard Setup

### RevenueCat Charts
Built-in dashboard shows:
- Active subscribers
- MRR over time
- Trial conversion
- Churn rate
- Revenue by product

### Custom Analytics

Track events:
```swift
// Track paywall view
Analytics.log("paywall_viewed", params: [
    "placement": "onboarding",
    "offering": offerings.current?.identifier
])

// Track trial start
Analytics.log("trial_started", params: [
    "product_id": package.storeProduct.productIdentifier,
    "price": package.storeProduct.price
])

// Track conversion
Analytics.log("subscription_started", params: [
    "product_id": productId,
    "is_trial_conversion": wasInTrial,
    "ltv_estimate": estimatedLTV
])
```

## Cohort Analysis

Track by signup date:
```
         | Month 1 | Month 2 | Month 3 | Month 6 | Month 12
---------|---------|---------|---------|---------|----------
Jan 2024 |   100%  |   80%   |   70%   |   55%   |   45%
Feb 2024 |   100%  |   85%   |   75%   |   60%   |    -
Mar 2024 |   100%  |   82%   |   72%   |    -    |    -
```

Look for:
- Improving cohorts = product improvements working
- Seasonal patterns = plan marketing
- Drop-off points = fix onboarding/value

## SQL Queries

### Active Subscribers
```sql
SELECT COUNT(DISTINCT user_id) as active_subscribers
FROM subscriptions
WHERE status = 'active'
  AND (expires_at IS NULL OR expires_at > NOW());
```

### MRR Calculation
```sql
SELECT 
  DATE_TRUNC('month', created_at) as month,
  SUM(CASE 
    WHEN billing_period = 'monthly' THEN price
    WHEN billing_period = 'yearly' THEN price / 12
    ELSE 0
  END) as mrr
FROM subscriptions
WHERE status = 'active'
GROUP BY 1
ORDER BY 1;
```

### Churn Rate
```sql
WITH monthly_counts AS (
  SELECT
    DATE_TRUNC('month', churned_at) as month,
    COUNT(*) as churned,
    LAG(COUNT(*)) OVER (ORDER BY DATE_TRUNC('month', churned_at)) as prev_active
  FROM subscriptions
  WHERE churned_at IS NOT NULL
  GROUP BY 1
)
SELECT 
  month,
  churned::float / NULLIF(prev_active, 0) as churn_rate
FROM monthly_counts;
```

### Trial Conversion by Source
```sql
SELECT 
  acquisition_source,
  COUNT(*) as trials,
  COUNT(CASE WHEN converted_at IS NOT NULL THEN 1 END) as conversions,
  COUNT(CASE WHEN converted_at IS NOT NULL THEN 1 END)::float / COUNT(*) as rate
FROM trials
GROUP BY 1
ORDER BY rate DESC;
```

## Reporting Template

### Weekly Report
```
WEEK OF [DATE]

Revenue:
- MRR: $XX,XXX (+X%)
- New subscribers: XXX
- Churned: XX
- Net new: XXX

Conversion:
- Paywall views: X,XXX
- Trial starts: XXX (XX%)
- Conversions: XX (XX%)

Health:
- Day 7 retention: XX%
- Trial-to-paid: XX%
- Avg time to convert: X.X days
```

### Monthly Report
Add:
- Cohort analysis
- LTV trends
- Churn by reason
- A/B test results
- Product roadmap impact

## Integration Points

| Platform | Integration |
|----------|-------------|
| RevenueCat | Native dashboard + Charts |
| Amplitude | RevenueCat integration |
| Mixpanel | RevenueCat integration |
| Firebase | Manual event logging |
| Custom | Webhooks → your DB |

```javascript
// Webhook to data warehouse
app.post('/revenuecat/webhook', async (req, res) => {
  await db.events.insert({
    event_type: req.body.type,
    user_id: req.body.app_user_id,
    product_id: req.body.product_id,
    price: req.body.price,
    currency: req.body.currency,
    timestamp: new Date(req.body.event_timestamp_ms)
  });
  res.sendStatus(200);
});
```
