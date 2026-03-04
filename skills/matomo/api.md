# Matomo API Reference

## Authentication

All API calls require `token_auth` parameter. Get it from:
Settings → Personal → Security → Create new token

```bash
# Base request pattern
curl -s "https://{matomo_url}/index.php?\
module=API&\
method={method}&\
idSite={site_id}&\
period={period}&\
date={date}&\
format=json&\
token_auth={token}"
```

## Common Methods

### Traffic Overview

```bash
# Basic metrics: visits, unique visitors, pageviews, avg time
method=VisitsSummary.get

# Example response
{
  "nb_visits": 1523,
  "nb_uniq_visitors": 1102,
  "nb_actions": 4521,
  "avg_time_on_site": 185
}
```

### Page Analytics

```bash
# Top pages by URL
method=Actions.getPageUrls

# Top pages by title
method=Actions.getPageTitles

# Entry pages (landing pages)
method=Actions.getEntryPageUrls

# Exit pages
method=Actions.getExitPageUrls
```

### Traffic Sources

```bash
# All referrers summary
method=Referrers.get

# Websites referring traffic
method=Referrers.getWebsites

# Search engines
method=Referrers.getSearchEngines

# Social networks
method=Referrers.getSocials

# Campaigns (UTM)
method=Referrers.getCampaigns
```

### Goals & Conversions

```bash
# All goals summary
method=Goals.get

# Specific goal
method=Goals.get&idGoal={goal_id}

# Goal conversion rate
# Returns: conversion_rate, nb_conversions, revenue
```

### Visitors

```bash
# Visitor devices
method=DevicesDetection.getType

# Browsers
method=DevicesDetection.getBrowsers

# Operating systems
method=DevicesDetection.getOsVersions

# Countries
method=UserCountry.getCountry

# Real-time visitors (last 30 min)
method=Live.getCounters&lastMinutes=30
```

## Date Parameters

| period | date format | description |
|--------|-------------|-------------|
| `day` | `2025-01-15` | Single day |
| `week` | `2025-01-15` | Week containing date |
| `month` | `2025-01` | Full month |
| `year` | `2025` | Full year |
| `range` | `2025-01-01,2025-01-31` | Custom range |

### Special date values
- `today` — current day
- `yesterday` — previous day
- `last7` — last 7 days
- `last30` — last 30 days
- `lastWeek` — previous full week
- `lastMonth` — previous full month
- `lastYear` — previous full year

## Segments

Filter data by visitor attributes:

```bash
# Only mobile visitors
&segment=deviceType==smartphone

# Only from Google
&segment=referrerName==Google

# Only conversions
&segment=visitConverted==1

# Country filter
&segment=countryCode==US

# Combine with AND (;) or OR (,)
&segment=deviceType==smartphone;countryCode==US
```

## Useful Parameters

```bash
# Limit results
&filter_limit=10

# Sort by column
&filter_sort_column=nb_visits
&filter_sort_order=desc

# Flatten nested results
&flat=1

# Include totals row
&showColumns=nb_visits,nb_uniq_visitors
```

## Bulk Requests

Query multiple methods in one call:

```bash
method=API.getBulkRequest&urls[0]=method=VisitsSummary.get...&urls[1]=method=Actions.getPageUrls...
```

## Error Handling

| Response | Meaning |
|----------|---------|
| `{"result":"error","message":"..."}` | API error, check message |
| Empty array `[]` | No data for period |
| 403 | Invalid or missing token |
| 500 | Server error, retry later |
