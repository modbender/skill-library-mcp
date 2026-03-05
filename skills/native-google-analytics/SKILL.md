---
name: google-analytics
description: "Query Google Analytics 4 (GA4) data directly via the Analytics Data API. Use when you need website analytics like top pages, traffic sources, sessions, users, conversions, bounce rate, or any GA4 metrics and dimensions. Supports custom date ranges, filtering, and multi-metric queries. Calls analyticsdata.googleapis.com directly with no third-party proxy."
metadata:
  openclaw:
    requires:
      env:
        - GA4_PROPERTY_ID
        - GOOGLE_CLIENT_ID
        - GOOGLE_CLIENT_SECRET
        - GOOGLE_REFRESH_TOKEN
      bins:
        - python3
    primaryEnv: GA4_PROPERTY_ID
    files:
      - "scripts/*"
---

# Google Analytics 4

Query GA4 properties directly via the Google Analytics Data API (`analyticsdata.googleapis.com`).

## Setup (one-time)

### 1. Create a Google Cloud project (or use an existing one)

Go to https://console.cloud.google.com and create or select a project.

### 2. Set the OAuth consent screen to Internal

Go to **APIs & Credentials > OAuth consent screen > Audience** and set:
- **User type**: Internal

This avoids Google's app verification process (which requires a demo video for sensitive scopes like Analytics). Internal is fine for personal/team use. Note: this requires a Google Workspace account (not a personal @gmail.com).

If you must use External (e.g. you have a personal Gmail), set publishing status to "In production" and add the `analytics.readonly` scope under **Data Access / Scopes**.

### 3. Add the Analytics scope

Go to **OAuth consent screen > Data Access** (or Scopes) and add:
```
https://www.googleapis.com/auth/analytics.readonly
```
This is listed as a "sensitive scope" by Google. If your app is Internal, no verification is needed.

### 4. Enable the Analytics Data API

Go to: https://console.cloud.google.com/apis/library/analyticsdata.googleapis.com

Click **Enable**.

### 5. Create OAuth 2.0 credentials

Go to **APIs & Credentials > Credentials > Create Credentials > OAuth client ID**
- Application type: **Desktop app**
- Name: anything you want

Save the **Client ID** and **Client Secret**.

### 6. Get your GA4 Property ID

Go to https://analytics.google.com > **Admin** (gear icon) > **Property Settings**. The Property ID is the numeric value at the top.

### 7. Generate a refresh token

Run this on your local machine (needs a browser for the Google login flow):

```bash
pip install google-auth-oauthlib
```

```bash
python3 -c "from google_auth_oauthlib.flow import InstalledAppFlow; flow = InstalledAppFlow.from_client_config({'installed': {'client_id': 'YOUR_CLIENT_ID', 'client_secret': 'YOUR_CLIENT_SECRET', 'auth_uri': 'https://accounts.google.com/o/oauth2/auth', 'token_uri': 'https://oauth2.googleapis.com/token'}}, scopes=['https://www.googleapis.com/auth/analytics.readonly']); creds = flow.run_local_server(port=0); print('REFRESH TOKEN:', creds.refresh_token)"
```

Replace `YOUR_CLIENT_ID` and `YOUR_CLIENT_SECRET` with your values. A browser window will open for you to log in with Google. Copy the refresh token from the output.

### 8. Set environment variables

```
GA4_PROPERTY_ID=123456789
GOOGLE_CLIENT_ID=your-client-id
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REFRESH_TOKEN=your-refresh-token
```

## Troubleshooting

- **403 HTML error page**: The `analytics.readonly` scope is probably not added to your OAuth consent screen. Go to Data Access/Scopes and add it, then regenerate your refresh token.
- **403 JSON error "caller does not have permission"**: Your Google account doesn't have access to the GA4 property. Check Admin > Property Access Management in Google Analytics.
- **Token refresh fails**: Your refresh token may be expired. Regenerate it using step 7.

## Queries

### Top pages by pageviews
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics screenPageViews \
  --dimension pagePath \
  --limit 20
```

### Top pages with sessions and users
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics screenPageViews,sessions,totalUsers \
  --dimension pagePath \
  --limit 20
```

### Traffic sources
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics sessions \
  --dimension sessionSource \
  --limit 20
```

### Traffic by source and medium
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics sessions,totalUsers,conversions \
  --dimensions sessionSource,sessionMedium \
  --limit 20
```

### Landing pages
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics sessions,bounceRate \
  --dimension landingPage \
  --limit 30
```

### Custom date range
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics screenPageViews,sessions \
  --dimension pagePath \
  --start 2026-01-01 \
  --end 2026-01-31 \
  --limit 20
```

### Filter by path prefix
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics screenPageViews,sessions \
  --dimension pagePath \
  --filter "pagePath=~/blog/" \
  --limit 20
```

### Conversions by campaign
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics conversions,sessions \
  --dimensions sessionCampaignName,sessionSource \
  --limit 20
```

### Device breakdown
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics sessions,totalUsers \
  --dimension deviceCategory \
  --limit 10
```

### Country breakdown
```bash
python3 /mnt/skills/user/google-analytics/scripts/ga4_query.py \
  --metrics sessions,totalUsers \
  --dimension country \
  --limit 20
```

## Common metrics
`screenPageViews`, `sessions`, `totalUsers`, `newUsers`, `activeUsers`, `bounceRate`, `averageSessionDuration`, `conversions`, `eventCount`, `engagementRate`, `userEngagementDuration`

## Common dimensions
`pagePath`, `pageTitle`, `landingPage`, `sessionSource`, `sessionMedium`, `sessionCampaignName`, `country`, `city`, `deviceCategory`, `browser`, `date`, `week`, `month`

## Output
Results are printed as a formatted table to stdout. Pipe to `| python3 -m json.tool` if you need raw JSON.
