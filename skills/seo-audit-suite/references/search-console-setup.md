# Google Search Console API Setup

## 1. Enable the API
1. Go to https://console.cloud.google.com/apis/library
2. Search "Search Console API" (also called "Google Search Console API")
3. Click Enable

## 2. Create Service Account
1. Go to IAM & Admin → Service Accounts
2. Create service account
3. Grant "Owner" role on the Search Console property
4. Create JSON key → download it

## 3. Add to Search Console
1. Go to https://search.google.com/search-console/
2. Select your property
3. Settings → Users and permissions → Add user
4. Add the service account email with "Full" permission

## 4. Configure
```bash
export GOOGLE_SEARCH_CONSOLE_KEY="/path/to/service-account-key.json"
```

## 5. Available Data
- **Search Analytics:** queries, impressions, clicks, CTR, position
- **URL Inspection:** index status, crawl info
- **Sitemaps:** submission status

## API Endpoints Used
- `searchanalytics/query` — keyword performance data
- `sitemaps/list` — sitemap status
- `urlInspection/index/inspect` — page index status

## Rate Limits
- 1,200 queries/minute per project
- 10,000 rows max per query (use pagination)
