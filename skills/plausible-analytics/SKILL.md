---
name: plausible-analytics
description: Query and analyze website analytics from Plausible Analytics. Use when you need to check real-time visitors, get page views and visitor statistics for a time period, analyze traffic sources or top pages, examine geographic distribution, or generate analytics reports and insights for websites tracked with Plausible Analytics.
metadata:
  openclaw:
    requires:
      env:
        - PLAUSIBLE_API_KEY
      bins:
        - node
    primaryEnv: PLAUSIBLE_API_KEY
---

# Plausible Analytics

## Overview

Retrieve and analyze website analytics data from Plausible Analytics API. Supports real-time visitor tracking, historical statistics, traffic source analysis, and detailed breakdowns by page, source, or country.

## Quick Start

All scripts require `PLAUSIBLE_API_KEY` environment variable. Site ID can be provided via `PLAUSIBLE_SITE_ID` environment variable or as a script argument.

```bash
# Set API key
export PLAUSIBLE_API_KEY="your-api-key"

# Quick example: Get today's stats
node scripts/stats.mjs example.com --period day
```

## Real-Time Visitors

Check how many people are currently viewing your site:

```bash
node scripts/realtime.mjs <site-id>
```

Example output:
```json
{
  "visitors": 42
}
```

## Statistics

Get page views, visitors, bounce rate, and visit duration for a time period:

```bash
node scripts/stats.mjs <site-id> [--period day|7d|30d|month|6mo|12mo] [--date YYYY-MM-DD]
```

Parameters:
- `period` - Time period to query (default: `day`)
- `date` - Specific date for the period (default: today)

Example:
```bash
# Get today's stats
node scripts/stats.mjs example.com

# Get last 7 days
node scripts/stats.mjs example.com --period 7d

# Get stats for a specific month
node scripts/stats.mjs example.com --period month --date 2026-02-01
```

Example output:
```json
{
  "results": {
    "visitors": {
      "value": 1234
    },
    "pageviews": {
      "value": 5678
    },
    "bounce_rate": {
      "value": 45
    },
    "visit_duration": {
      "value": 180
    }
  }
}
```

## Detailed Breakdown

Analyze traffic by specific dimensions (pages, sources, countries, etc.):

```bash
node scripts/breakdown.mjs <site-id> <property> [--period day|7d|30d] [--limit N]
```

Properties:
- `visit:source` - Traffic sources (Google, Twitter, direct, etc.)
- `visit:referrer` - Referring URLs
- `visit:utm_medium` / `visit:utm_source` / `visit:utm_campaign` - UTM parameters
- `visit:device` - Desktop vs Mobile
- `visit:browser` - Browser breakdown
- `visit:os` - Operating system
- `visit:country` - Countries
- `event:page` - Top pages

Example:
```bash
# Top 10 pages in the last 7 days
node scripts/breakdown.mjs example.com event:page --period 7d --limit 10

# Traffic sources today
node scripts/breakdown.mjs example.com visit:source

# Countries in the last 30 days
node scripts/breakdown.mjs example.com visit:country --period 30d
```

Example output:
```json
{
  "results": [
    {
      "page": "/",
      "visitors": 542,
      "pageviews": 1024
    },
    {
      "page": "/about",
      "visitors": 123,
      "pageviews": 145
    }
  ]
}
```

## Environment Variables

- `PLAUSIBLE_API_KEY` (required) - Your Plausible API key
- `PLAUSIBLE_SITE_ID` (optional) - Default site ID to use

## Resources

### scripts/

- `stats.mjs` - Aggregate statistics for a time period
- `realtime.mjs` - Current visitor count
- `breakdown.mjs` - Detailed breakdown by dimension
