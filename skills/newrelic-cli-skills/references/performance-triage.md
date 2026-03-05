# Performance Triage Guide

Step-by-step guide for investigating a reported performance issue.

---

## Step 1: Confirm the Problem

```bash
# Is there actually a performance issue right now?
./scripts/check-performance.sh "" 30
```

Look for:
- Avg response time > 1s (warning) or > 2s (critical)
- Error rate > 1% (warning) or > 5% (critical)
- RPM significantly lower than baseline (could indicate traffic drop or outage)

---

## Step 2: Narrow to One App

```bash
# Which app is affected?
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query "
  SELECT average(duration) AS 'Avg (s)', percentage(count(*), WHERE error IS true) AS 'Error %'
  FROM Transaction
  FACET appName
  SINCE 30 minutes ago
  ORDER BY average(duration) DESC
"
```

---

## Step 3: Find the Slow Endpoint

```bash
./scripts/top-slow-transactions.sh "my-app" 30
```

Identify the top offender by avg duration.

---

## Step 4: Is It the Database?

```bash
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query "
  SELECT average(duration) AS 'Total', average(databaseDuration) AS 'DB',
         percentage(average(databaseDuration), average(duration)) AS 'DB %'
  FROM Transaction
  WHERE appName = 'my-app'
  FACET name
  SINCE 30 minutes ago
  ORDER BY average(databaseDuration) DESC
  LIMIT 10
"
```

**If DB% > 60%:** Focus on database query optimization.
**If DB% < 20% but total is slow:** Look at external calls or application logic.

---

## Step 5: Is It the Host?

```bash
# Check if host is under pressure
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query "
  SELECT average(cpuPercent), average(memoryUsedPercent)
  FROM SystemSample
  FACET hostname
  SINCE 30 minutes ago
"
```

**CPU > 80%:** Server is overloaded — check for runaway processes.
**Memory > 90%:** Memory pressure — check for leaks or insufficient allocation.

---

## Step 6: Is It a New Deployment?

```bash
newrelic apm deployment list --applicationId <APP_ID>
```

If a deploy happened in the last few hours, compare performance before/after:

```bash
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query "
  SELECT average(duration)
  FROM Transaction
  WHERE appName = 'my-app'
  TIMESERIES 10 minutes
  SINCE 3 hours ago
"
```

Look for an inflection point matching the deployment timestamp.

---

## Step 7: Check for Errors

```bash
./scripts/error-report.sh "my-app" 30
```

A spike in errors often precedes or accompanies a performance degradation.

---

## Step 8: External Dependencies

```bash
newrelic nrql query --accountId $NEW_RELIC_ACCOUNT_ID --query "
  SELECT average(duration), count(*)
  FROM ExternalTrace
  WHERE appName = 'my-app'
  FACET host
  SINCE 30 minutes ago
  ORDER BY average(duration) DESC
  LIMIT 10
"
```

If an external service (API, auth provider, CDN) is slow, that's often the root cause.

---

## Decision Tree Summary

```
Slow app reported
    │
    ├─ Check all apps ──► Which one is slow?
    │
    ├─ Check transactions ──► Which endpoint?
    │
    ├─ DB % high? ──► Yes ──► Slow query / N+1 / missing index
    │                └─ No ──► External call? / CPU pressure? / code logic?
    │
    ├─ Host CPU/memory high? ──► Yes ──► Scale up or find runaway process
    │
    ├─ Recent deployment? ──► Yes ──► Regression — compare before/after
    │
    └─ Error spike? ──► Yes ──► Error-report.sh ──► Stack trace ──► Fix
```

---

## What the CLI Cannot Do

- View distributed trace waterfalls (requires NR UI)
- Show flame graphs / code-level profiling (requires NR UI)
- Access custom dashboards interactively
- Resolve alerts or acknowledge incidents (UI only)

For deep dives requiring call graphs, hand the NRQL findings to the UI:
`https://one.newrelic.com/data-exploration` → paste NRQL query
