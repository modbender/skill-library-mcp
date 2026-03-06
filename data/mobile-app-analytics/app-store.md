# App Store Connect Analytics — Mobile App Analytics

## When to Use

User needs iOS app performance data, App Store metrics, or Apple-specific analytics. App Store Connect is the source of truth for iOS distribution.

## Key Reports

### App Analytics

| Metric | What It Measures | Timeframe |
|--------|------------------|-----------|
| Impressions | Times app shown in search/browse | Daily |
| Product Page Views | Visits to your app page | Daily |
| Conversion Rate | Views → Downloads | Daily |
| Downloads | Total installs | Daily |
| Redownloads | Users reinstalling | Daily |
| Updates | Users updating app | Daily |

### Sales & Trends

| Metric | What It Measures |
|--------|------------------|
| Units | Downloads + in-app purchases |
| Sales | Revenue (before Apple's cut) |
| Proceeds | Revenue after Apple's 15-30% |

### Retention

App Store Connect shows retention at:
- Day 1, Day 7, Day 14, Day 28
- By app version
- By source type (App Store Search, Browse, etc.)

## Data Sources

### Source Types

| Source | Description |
|--------|-------------|
| App Store Search | User searched keywords |
| App Store Browse | Featured, Top Charts, categories |
| App Referrer | Deep link from another app |
| Web Referrer | Link from website |
| Unavailable | Can't determine source |

### Attribution Windows

- Downloads: Same-day attribution
- In-app events: 30-day window to originating source

## API Access

### App Store Connect API

Generate key in App Store Connect → Users and Access → Keys.

```bash
# Get app analytics
curl -X GET "https://api.appstoreconnect.apple.com/v1/apps/{app_id}/analyticsReportRequests" \
  -H "Authorization: Bearer {jwt_token}"
```

### JWT Generation
```python
import jwt
import time

def generate_token(key_id, issuer_id, private_key):
    payload = {
        'iss': issuer_id,
        'iat': int(time.time()),
        'exp': int(time.time()) + 1200,
        'aud': 'appstoreconnect-v1'
    }
    return jwt.encode(payload, private_key, algorithm='ES256', 
                      headers={'kid': key_id})
```

## Key Metrics to Track

### Acquisition Funnel

```
Impressions → Product Page Views → Downloads

Conversion benchmarks:
- Search impression → view: 5-15%
- View → download: 20-40% (varies by category)
```

### By Region

Top markets often differ:
- US: Highest revenue per user
- India: Highest volume, lowest ARPU
- China: Requires separate App Store account
- Europe: GDPR compliance required

## Common Issues

| Problem | Cause | Solution |
|---------|-------|----------|
| Data delayed 48h | Apple's processing | Plan for lag in dashboards |
| Missing proceeds | Currency conversion delay | Wait 3-5 days after month end |
| Wrong country data | User VPN/travel | Accept ~5% noise |
| Low conversion | Poor screenshots/description | A/B test with Product Page Optimization |

## Product Page Optimization (PPO)

Apple's native A/B testing:
- Test up to 3 treatments
- Test: icon, screenshots, preview videos, descriptions
- Minimum 7 days, 90% confidence target
- Only available in some countries

## Benchmarks by Category

| Category | Typical Conversion | D1 Retention |
|----------|-------------------|--------------|
| Games | 25-35% | 25-35% |
| Social | 20-30% | 20-30% |
| Productivity | 15-25% | 15-25% |
| Health & Fitness | 20-30% | 20-30% |
| Finance | 10-20% | 30-40% |

## Privacy Changes (iOS 14.5+)

### ATT Impact
- ~25% of users opt-in to tracking
- SKAdNetwork for attribution
- Aggregated, delayed conversion data

### SKAdNetwork
- 24-48h delay on install attribution
- Limited conversion value (0-63)
- No user-level data
