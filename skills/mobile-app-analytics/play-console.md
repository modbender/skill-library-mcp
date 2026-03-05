# Google Play Console Analytics — Mobile App Analytics

## When to Use

User needs Android app performance data, Play Store metrics, or Google-specific analytics. Play Console is the source of truth for Android distribution.

## Key Reports

### Statistics Dashboard

| Metric | What It Measures |
|--------|------------------|
| Installs by user | Unique users who installed |
| Uninstalls | Users who removed app |
| Active devices | Devices with app installed |
| Update rate | % of users on latest version |
| Crashes | ANRs and crashes by version |

### Acquisition Reports

| Source | Description |
|--------|-------------|
| Play Store (organic) | Store search and browse |
| Google Ads | Paid campaigns |
| Third-party referrers | External links |
| Pre-registered | Users who pre-registered |

### User Acquisition

Tracks full funnel:
```
Store listing visitors → Installers → Buyers

With breakdown by:
- Country
- Language  
- UTM source
- Play Store placement
```

## Retention Data

Play Console provides:
- Day 1, Day 7, Day 30 retention
- By country
- By acquisition channel
- By device type

### Cohort Analysis

Compare retention across:
- App versions
- Install dates
- Countries
- Acquisition sources

## Android Vitals

Critical metrics Google uses for ranking:

| Vital | Bad Threshold | Impact |
|-------|---------------|--------|
| ANR rate | > 0.47% | Ranking penalty |
| Crash rate | > 1.09% | Ranking penalty |
| Excessive wakeups | > 10/hour | Battery warning |
| Stuck partial wake locks | > 0.10% | Battery warning |

### Fixing Vitals Issues

```kotlin
// Bad: Crash from null
val name = user.name.uppercase()

// Good: Safe handling
val name = user?.name?.uppercase() ?: "Unknown"
```

## Custom Store Listings

A/B test with Experiments:
- Test: icon, feature graphic, screenshots, description
- Up to 5 variants
- Target by country or language
- 90% confidence required

### What to Test

| Element | Impact | Test Duration |
|---------|--------|---------------|
| Icon | High | 2+ weeks |
| Feature graphic | Medium | 1-2 weeks |
| Screenshots | High | 2+ weeks |
| Short description | Medium | 1 week |
| Full description | Low | Don't bother |

## API Access

### Google Play Developer API

```bash
# Get app stats
curl -X GET \
  "https://androidpublisher.googleapis.com/androidpublisher/v3/applications/{package}/reviews" \
  -H "Authorization: Bearer {access_token}"
```

### BigQuery Export

Enable in Play Console → Download Reports → Copy to BigQuery

```sql
-- Installs by country, last 30 days
SELECT
  date,
  country,
  SUM(daily_device_installs) as installs
FROM `play_store_stats.installs_*`
WHERE _TABLE_SUFFIX >= FORMAT_DATE('%Y%m%d', DATE_SUB(CURRENT_DATE(), INTERVAL 30 DAY))
GROUP BY 1, 2
ORDER BY 3 DESC
```

## Pre-Launch Reports

Before release, Play Console runs:
- Automated testing on Firebase Test Lab
- Accessibility checks
- Performance benchmarks
- Security vulnerability scan

## Pricing & Monetization

### Pricing Experiments

Test price changes:
- By country
- By user segment
- With statistical significance

### Subscription Metrics

| Metric | What to Track |
|--------|---------------|
| New subscriptions | Growth rate |
| Renewals | Retention health |
| Cancellations | Churn rate |
| Grace period recoveries | Payment failure saves |
| Subscription pause | Temporary churn |

## Country-Specific Notes

| Country | Notes |
|---------|-------|
| China | Play Store blocked, use alternatives |
| India | High volume, low ARPU, test pricing |
| Brazil | Local payment methods matter |
| Japan | High ARPU, quality expectations |

## Benchmarks

| Category | Install Rate | D1 Retention |
|----------|--------------|--------------|
| Games | 30-40% | 25-35% |
| Social | 25-35% | 20-30% |
| Tools | 35-45% | 15-25% |
| Shopping | 20-30% | 10-20% |

## Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Installs ≠ Firebase | Different definitions | Firebase = opened app |
| Revenue mismatch | Refunds, currency | Wait for settlement |
| Missing countries | Low volume threshold | Aggregate small markets |
| Delayed data | Processing time | 24-48h is normal |
