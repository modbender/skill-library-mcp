# Firebase Analytics — Mobile App Analytics

## When to Use

User asks about Firebase Analytics, Google Analytics for Firebase, or needs real-time app metrics. Firebase is the default analytics for most mobile apps.

## Key Concepts

### Event Types

| Type | Examples | Auto-tracked? |
|------|----------|---------------|
| Automatic | first_open, session_start, app_update | Yes |
| Recommended | login, sign_up, purchase, share | Log manually |
| Custom | view_product, complete_level | Define yourself |

### User Properties

Built-in: age, gender, interests, country, device, app_version
Custom: subscription_status, user_tier, preferred_language

## Essential Reports

### Real-time
- Active users right now
- Events in last 30 minutes
- Good for: launch monitoring, campaign spikes

### Retention
- D1, D7, D30 cohort retention
- Compare by acquisition source
- Good for: onboarding optimization

### Funnel Analysis
- Multi-step conversion paths
- Drop-off between steps
- Good for: identifying friction points

### User Engagement
- DAU, WAU, MAU
- Session duration, screens per session
- Good for: feature adoption tracking

## BigQuery Export

For advanced analysis, export to BigQuery:
```sql
-- Daily active users by platform
SELECT
  DATE(TIMESTAMP_MICROS(event_timestamp)) as date,
  platform,
  COUNT(DISTINCT user_pseudo_id) as dau
FROM `project.analytics_*.events_*`
WHERE event_name = 'session_start'
GROUP BY 1, 2
ORDER BY 1 DESC
```

## Common Queries

### Check D1 Retention
```sql
-- D1 retention by install date
WITH installs AS (
  SELECT 
    user_pseudo_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) as install_date
  FROM `project.analytics_*.events_*`
  WHERE event_name = 'first_open'
),
returns AS (
  SELECT 
    user_pseudo_id,
    DATE(TIMESTAMP_MICROS(event_timestamp)) as return_date
  FROM `project.analytics_*.events_*`
  WHERE event_name = 'session_start'
)
SELECT
  i.install_date,
  COUNT(DISTINCT i.user_pseudo_id) as installs,
  COUNT(DISTINCT r.user_pseudo_id) as d1_returns,
  ROUND(COUNT(DISTINCT r.user_pseudo_id) / COUNT(DISTINCT i.user_pseudo_id) * 100, 1) as d1_retention
FROM installs i
LEFT JOIN returns r ON i.user_pseudo_id = r.user_pseudo_id
  AND r.return_date = DATE_ADD(i.install_date, INTERVAL 1 DAY)
GROUP BY 1
ORDER BY 1 DESC
```

### Revenue by Cohort
```sql
-- LTV by monthly cohort
SELECT
  FORMAT_DATE('%Y-%m', install_date) as cohort,
  COUNT(DISTINCT user_pseudo_id) as users,
  SUM(revenue) as total_revenue,
  ROUND(SUM(revenue) / COUNT(DISTINCT user_pseudo_id), 2) as arpu
FROM (
  SELECT 
    user_pseudo_id,
    MIN(DATE(TIMESTAMP_MICROS(event_timestamp))) as install_date,
    SUM((SELECT value.double_value FROM UNNEST(event_params) WHERE key = 'value')) as revenue
  FROM `project.analytics_*.events_*`
  GROUP BY 1
)
GROUP BY 1
ORDER BY 1 DESC
```

## Debugging Events

### DebugView
Enable debug mode to see events in real-time:
```bash
# iOS Simulator
adb shell setprop debug.firebase.analytics.app com.your.app

# Android
adb shell setprop debug.firebase.analytics.app com.your.app
```

### Common Issues

| Problem | Likely Cause | Fix |
|---------|--------------|-----|
| Events not appearing | 1h batching delay | Wait or use DebugView |
| Missing user properties | Not set before event | Set properties at app start |
| Wrong event counts | Duplicate logging | Check for multiple init calls |
| Revenue $0 | Currency not set | Include currency param |

## Limits

| Limit | Value |
|-------|-------|
| Custom events | 500 per app |
| Event parameters | 25 per event |
| User properties | 25 per user |
| Parameter name length | 40 chars |
| Parameter value length | 100 chars |

## Integration with Other Tools

- **BigQuery**: Free daily export, 13-month retention
- **Google Ads**: Share audiences for remarketing
- **Crashlytics**: Link crashes to user behavior
- **Remote Config**: Target by user properties
