# Google Analytics 4 API Setup

## 1. Enable the API
1. Go to https://console.cloud.google.com/apis/library
2. Search "Google Analytics Data API"
3. Click Enable

## 2. Create Service Account
1. IAM & Admin → Service Accounts → Create
2. Grant "Viewer" role
3. Create JSON key → download

## 3. Add to GA4 Property
1. GA4 → Admin → Property → Property Access Management
2. Add the service account email as "Viewer"

## 4. Find Your Property ID
- GA4 → Admin → Property → Property Settings
- Copy the numeric Property ID (e.g., `123456789`)

## 5. Configure
In client config:
```json
{
  "ga4_property_id": "123456789"
}
```

In global config:
```json
{
  "ga4_credentials_file": "/path/to/service-account.json"
}
```

## Available Metrics
- `sessions`, `totalUsers`, `newUsers`
- `screenPageViews`, `bounceRate`
- `averageSessionDuration`, `engagementRate`
- `conversions`, `eventCount`

## Available Dimensions
- `date`, `pagePath`, `pageTitle`
- `sessionSource`, `sessionMedium`
- `deviceCategory`, `browser`, `country`

## Rate Limits
- 10 concurrent requests per property
- 10,000 requests per day per project
