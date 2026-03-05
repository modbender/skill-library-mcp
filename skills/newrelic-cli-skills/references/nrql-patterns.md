# NRQL Patterns Reference

## Transaction Performance

```nrql
-- Response time percentiles
SELECT percentile(duration, 50, 75, 95, 99)
FROM Transaction
WHERE appName = 'my-app'
SINCE 1 hour ago

-- Apdex score (T = 0.5s threshold)
SELECT apdex(duration, 0.5)
FROM Transaction
WHERE appName = 'my-app'
TIMESERIES 5 minutes
SINCE 1 hour ago

-- Compare this week vs last week
SELECT average(duration)
FROM Transaction
WHERE appName = 'my-app'
SINCE 1 week ago
COMPARE WITH 1 week ago

-- Request volume by hour of day
SELECT count(*)
FROM Transaction
WHERE appName = 'my-app'
FACET hourOf(timestamp)
SINCE 1 week ago
```

## Error Analysis

```nrql
-- Error rate trend
SELECT percentage(count(*), WHERE error IS true)
FROM Transaction
WHERE appName = 'my-app'
TIMESERIES 5 minutes
SINCE 3 hours ago

-- Top errors by frequency
SELECT count(*)
FROM TransactionError
WHERE appName = 'my-app'
FACET error.class, message
SINCE 1 hour ago
LIMIT 20

-- Errors in the last 10 minutes
SELECT timestamp, transactionName, error.class, message
FROM TransactionError
WHERE appName = 'my-app'
SINCE 10 minutes ago
LIMIT 25

-- HTTP 5xx errors (if using HTTP status tracking)
SELECT count(*)
FROM Transaction
WHERE appName = 'my-app' AND response.status >= '500'
FACET response.status, name
SINCE 1 hour ago
```

## Database Performance

```nrql
-- DB time breakdown by operation type
SELECT average(duration)
FROM DatabaseTrace
WHERE appName = 'my-app'
FACET databaseVendor, category
SINCE 1 hour ago

-- Queries with high execution count (potential N+1)
SELECT count(*), average(duration)
FROM DatabaseTrace
WHERE appName = 'my-app'
FACET statement
SINCE 30 minutes ago
LIMIT 20
ORDER BY count(*) DESC

-- DB connection pool issues
SELECT count(*)
FROM TransactionError
WHERE appName = 'my-app' AND error.class LIKE '%connection%'
SINCE 1 hour ago
```

## Infrastructure

```nrql
-- All hosts CPU over time
SELECT average(cpuPercent)
FROM SystemSample
FACET hostname
TIMESERIES 10 minutes
SINCE 3 hours ago

-- Memory pressure (used > 85%)
SELECT latest(memoryUsedPercent)
FROM SystemSample
FACET hostname
WHERE memoryUsedPercent > 85
SINCE 5 minutes ago

-- Disk almost full (> 90%)
SELECT latest(diskUsedPercent), latest(mountPoint)
FROM StorageSample
FACET hostname
WHERE diskUsedPercent > 90
SINCE 10 minutes ago
```

## Browser / Front-End

```nrql
-- Page load time by page
SELECT average(duration)
FROM PageView
FACET pageUrl
SINCE 1 hour ago
LIMIT 20
ORDER BY average(duration) DESC

-- Core Web Vitals: LCP
SELECT average(largestContentfulPaint)
FROM PageViewTiming
FACET pageUrl
SINCE 1 hour ago

-- JS errors by page
SELECT count(*)
FROM JavaScriptError
FACET pageUrl, errorMessage
SINCE 1 hour ago
LIMIT 20
```

## Deployments

```nrql
-- Recent deployments
SELECT *
FROM Deployment
SINCE 1 week ago
LIMIT 20

-- Performance before vs after a specific deployment
SELECT average(duration)
FROM Transaction
WHERE appName = 'my-app'
SINCE '2026-02-25 10:00:00' UNTIL '2026-02-25 14:00:00'
TIMESERIES 5 minutes
```

## Logs

```nrql
-- Recent error logs
SELECT message, timestamp
FROM Log
WHERE level = 'ERROR'
SINCE 30 minutes ago
LIMIT 25

-- Log volume by level
SELECT count(*)
FROM Log
FACET level
SINCE 1 hour ago
```
