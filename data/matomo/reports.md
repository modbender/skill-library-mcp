# Report Templates — Matomo

## Quick Dashboard

Fast overview of key metrics:

```bash
# 1. Traffic summary
method=VisitsSummary.get&period=day&date=today

# 2. Real-time
method=Live.getCounters&lastMinutes=30

# 3. Top pages today
method=Actions.getPageUrls&period=day&date=today&filter_limit=5
```

Present as:
```
📊 Today: {visits} visits ({unique} unique)
⏱️ Live: {visitors} visitors in last 30 min
📄 Top pages: {page1}, {page2}, {page3}
```

## Weekly Summary

Compare this week vs last week:

```bash
# This week
method=VisitsSummary.get&period=week&date=today

# Last week
method=VisitsSummary.get&period=week&date=lastWeek
```

Calculate deltas:
```
visits_delta = ((this_week - last_week) / last_week) * 100
```

Present as:
```
📈 Weekly Report

Visits: {this_week} ({delta}% vs last week)
Unique visitors: {unique} ({delta}%)
Pageviews: {pageviews} ({delta}%)
Avg time: {time} ({delta}%)

Top pages:
1. {page} — {views} views
2. {page} — {views} views
3. {page} — {views} views

Top sources:
1. {source} — {visits} visits
2. {source} — {visits} visits
```

## Monthly Report

Comprehensive monthly analysis:

```bash
# Traffic
method=VisitsSummary.get&period=month&date=lastMonth

# Pages
method=Actions.getPageUrls&period=month&date=lastMonth&filter_limit=10

# Sources
method=Referrers.getWebsites&period=month&date=lastMonth&filter_limit=10

# Devices
method=DevicesDetection.getType&period=month&date=lastMonth

# Countries
method=UserCountry.getCountry&period=month&date=lastMonth&filter_limit=10

# Goals (if configured)
method=Goals.get&period=month&date=lastMonth
```

## Conversion Analysis

For e-commerce or goal tracking:

```bash
# All goals
method=Goals.get&period=month&date=lastMonth

# Goal by traffic source
method=Referrers.getWebsites&period=month&date=lastMonth&segment=visitConverted==1

# Conversion funnel
method=Goals.get&idGoal={id}&period=month&date=lastMonth
```

Present as:
```
🎯 Conversions — Last Month

Overall rate: {rate}%
Total conversions: {count}
Revenue: ${revenue}

By source:
1. {source}: {conversions} ({rate}%)
2. {source}: {conversions} ({rate}%)

By device:
- Desktop: {rate}%
- Mobile: {rate}%
- Tablet: {rate}%
```

## SEO Report

Search engine traffic analysis:

```bash
# Search engines
method=Referrers.getSearchEngines&period=month&date=lastMonth

# Keywords (if available)
method=Referrers.getKeywords&period=month&date=lastMonth

# Landing pages from search
method=Actions.getEntryPageUrls&period=month&date=lastMonth&segment=referrerType==search
```

## Anomaly Detection

Compare recent periods to identify issues:

```bash
# Last 7 days, daily
method=VisitsSummary.get&period=day&date=last7

# Response: array of 7 days
# Calculate: avg, std_dev
# Flag: any day >2 std_dev from avg
```

Alert thresholds:
- Traffic drop >30% vs previous day
- Bounce rate increase >20%
- Avg time decrease >40%
- Zero conversions (if normally >0)
