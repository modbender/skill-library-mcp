# native-google-analytics

An OpenClaw skill that queries Google Analytics 4 (GA4) directly via the [Analytics Data API](https://developers.google.com/analytics/devguides/reporting/data/v1). No third-party proxies, no external APIs, no SDK wrappers. Just your credentials talking to `analyticsdata.googleapis.com`.

## What it does

Ask OpenClaw for analytics data in plain English and it runs the appropriate GA4 query. Top pages, traffic sources, device breakdowns, custom date ranges, filters, etc.

## What you need

- A Google Cloud project with the Analytics Data API enabled
- OAuth 2.0 credentials (Desktop app)
- A GA4 property you have access to

## Setup

### 1. Google Cloud project

Go to [console.cloud.google.com](https://console.cloud.google.com) and create or select a project.

### 2. OAuth consent screen

Go to **APIs & Credentials > OAuth consent screen > Audience**.

Set **User type** to **Internal**. This skips Google's app verification process (which requires a demo video for sensitive scopes). Internal works for personal and team use but requires a Google Workspace account.

If you're on a personal @gmail.com, set it to External with publishing status "In production" instead.

### 3. Add the Analytics scope

Go to **OAuth consent screen > Data Access** and add:

```
https://www.googleapis.com/auth/analytics.readonly
```

### 4. Enable the API

Go to [Analytics Data API](https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com) and click **Enable**.

### 5. Create OAuth credentials

Go to **Credentials > Create Credentials > OAuth client ID**. Select **Desktop app**.

Save the Client ID and Client Secret.

### 6. Get your GA4 Property ID

Go to [analytics.google.com](https://analytics.google.com) > **Admin** > **Property Settings**. Copy the numeric Property ID.

### 7. Generate a refresh token

```bash
pip install google-auth-oauthlib
```

```bash
python3 -c "
from google_auth_oauthlib.flow import InstalledAppFlow
flow = InstalledAppFlow.from_client_config(
    {'installed': {
        'client_id': 'YOUR_CLIENT_ID',
        'client_secret': 'YOUR_CLIENT_SECRET',
        'auth_uri': 'https://accounts.google.com/o/oauth2/auth',
        'token_uri': 'https://oauth2.googleapis.com/token'}},
    scopes=['https://www.googleapis.com/auth/analytics.readonly'])
creds = flow.run_local_server(port=0)
print('REFRESH TOKEN:', creds.refresh_token)
"
```

A browser window will open for Google login. Copy the refresh token from the output.

### 8. Set environment variables

```
GA4_PROPERTY_ID=123456789
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token
```

## Example queries

```bash
# Top pages
python3 scripts/ga4_query.py --metrics screenPageViews,sessions,totalUsers --dimension pagePath --limit 20

# Traffic sources
python3 scripts/ga4_query.py --metrics sessions --dimension sessionSource --limit 20

# Landing pages with bounce rate
python3 scripts/ga4_query.py --metrics sessions,bounceRate --dimension landingPage --limit 30

# Custom date range
python3 scripts/ga4_query.py --metrics screenPageViews,sessions --dimension pagePath --start 2026-01-01 --end 2026-01-31 --limit 20

# Filter by path
python3 scripts/ga4_query.py --metrics screenPageViews,sessions --dimension pagePath --filter "pagePath=~/blog/" --limit 20
```

## Available metrics

`screenPageViews`, `sessions`, `totalUsers`, `newUsers`, `activeUsers`, `bounceRate`, `averageSessionDuration`, `conversions`, `eventCount`, `engagementRate`, `userEngagementDuration`

## Available dimensions

`pagePath`, `pageTitle`, `landingPage`, `sessionSource`, `sessionMedium`, `sessionCampaignName`, `country`, `city`, `deviceCategory`, `browser`, `date`, `week`, `month`

## Troubleshooting

**403 HTML error page**: The `analytics.readonly` scope isn't added to your OAuth consent screen. Add it, then regenerate your refresh token.

**403 "caller does not have permission"**: Your Google account doesn't have access to the GA4 property. Check Admin > Property Access Management in Google Analytics.

**Token refresh fails**: Refresh token expired. Regenerate it using step 7.
