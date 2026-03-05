# SQL Reference

ClickHouse-specific syntax, security model, and query patterns for `outlit_query`.

**Always call `outlit_schema` first** to discover tables and columns before writing SQL.

---

## Available Tables

| Table | Description |
|-------|-------------|
| `events` | Activity events from all channels (SDK, email, Slack, calls, CRM, billing) |
| `customer_dimensions` | Customer attributes, billing status, revenue metrics |
| `user_dimensions` | User attributes, journey stages, activity timestamps |
| `mrr_snapshots` | Daily MRR snapshots for trend analysis |

Use `outlit_schema` with a table name for full column definitions.

---

## ClickHouse Syntax

ClickHouse differs from MySQL/PostgreSQL. Use these patterns:

### Date/Time Functions

```sql
-- Current time
now()
today()

-- Date extraction
toDate(occurred_at)
toStartOfMonth(occurred_at)
toStartOfWeek(occurred_at)
toHour(occurred_at)
toDayOfWeek(occurred_at)

-- Date arithmetic (NOT DATE_SUB)
occurred_at >= now() - INTERVAL 30 DAY
occurred_at BETWEEN '2025-01-01' AND '2025-01-31'

-- Date formatting
formatDateTime(occurred_at, '%Y-%m-%d')

-- Date diff
dateDiff('day', first_seen_at, now()) as days_since_signup
```

### Conditional Aggregation

```sql
-- ClickHouse-specific conditional counts
countIf(billing_status = 'PAYING') as paying_count
sumIf(mrr_cents, billing_status = 'PAYING') as paying_mrr

-- CASE expressions
CASE
  WHEN mrr_cents > 100000 THEN 'Enterprise'
  WHEN mrr_cents > 10000 THEN 'Mid-Market'
  ELSE 'SMB'
END as segment
```

### String & Array Operations

```sql
-- Split string
splitByChar('@', email)[2] as domain

-- JSON extraction from properties column
JSONExtractString(properties, 'path') as page_path

-- Array contains
has(arrayOfTags, 'important')
```

### Window Functions

```sql
-- Month-over-month change
lagInFrame(total_mrr) OVER (ORDER BY snapshot_date) as prev_mrr
```

---

## Security Model

- **Read-only access** — only SELECT queries are allowed
- **Organization isolation** — queries are automatically scoped to your organization's data
- Standard ClickHouse functions, JOINs, aggregations, window functions, CTEs, and subqueries are all supported

---

## Error Codes

| Code | Meaning | Fix |
|------|---------|-----|
| `SYNTAX_ERROR` | SQL doesn't parse | Use ClickHouse syntax, not MySQL/PostgreSQL |
| `TABLE_NOT_FOUND` | Table doesn't exist | Run `outlit_schema` to see available tables |
| `FUNCTION_NOT_ALLOWED` | Blocked function | Use standard ClickHouse functions |
| `QUERY_NOT_ALLOWED` | Non-SELECT query | Only SELECT is allowed |
| `EXECUTION_ERROR` | Runtime error | Add time filters, reduce scope, use LIMIT |

---

## Representative Query Patterns

These demonstrate ClickHouse idioms. The agent can compose variations from these.

**Churn analysis with conditional aggregation:**
```sql
SELECT toStartOfMonth(first_seen_at) as cohort,
       count(*) as total,
       countIf(billing_status = 'PAYING') as paying,
       countIf(billing_status = 'CHURNED') as churned,
       countIf(billing_status = 'CHURNED') * 100.0 / count(*) as churn_rate
FROM customer_dimensions
WHERE first_seen_at >= now() - INTERVAL 12 MONTH
GROUP BY 1 ORDER BY 1
```

**At-risk customers with date diff:**
```sql
SELECT customer_id, name, domain, mrr_cents/100 as mrr_dollars,
       dateDiff('day', last_activity_at, now()) as days_inactive
FROM customer_dimensions
WHERE billing_status = 'PAYING' AND last_activity_at < now() - INTERVAL 30 DAY
ORDER BY mrr_cents DESC LIMIT 25
```

**Cross-table JOIN with activity:**
```sql
SELECT cd.customer_id, cd.name, cd.mrr_cents/100 as mrr,
       count(DISTINCT e.event_id) as event_count,
       count(DISTINCT e.user_id) as active_users
FROM customer_dimensions cd
LEFT JOIN events e ON cd.customer_id = e.customer_id
  AND e.occurred_at >= now() - INTERVAL 30 DAY
WHERE cd.billing_status = 'PAYING'
GROUP BY cd.customer_id, cd.name, cd.mrr_cents
ORDER BY event_count DESC LIMIT 25
```

**MRR trend with snapshots:**
```sql
SELECT snapshot_date, sum(mrr_cents)/100 as total_mrr,
       count(DISTINCT customer_id) as paying_customers
FROM mrr_snapshots
WHERE snapshot_date >= today() - 90
GROUP BY 1 ORDER BY 1
```

**Feature adoption with distinct users:**
```sql
SELECT event_type as feature,
       count(DISTINCT user_id) as unique_users,
       count(*) as total_uses
FROM events
WHERE occurred_at >= now() - INTERVAL 30 DAY
GROUP BY 1 ORDER BY 2 DESC LIMIT 20
```

---

## Performance Tips

1. **Always add time filters** — `WHERE occurred_at >= now() - INTERVAL N DAY` for events
2. **Use LIMIT** — Cap result sets, don't return millions of rows
3. **Select specific columns** — Avoid `SELECT *`
4. **Filter early** — Put WHERE conditions before aggregations
5. **Aggregate server-side** — Use GROUP BY instead of fetching raw rows

---

## When to Use SQL vs Customer Tools

| Use Case | Tool |
|----------|------|
| Single customer lookup | `outlit_get_customer` |
| Customer list with filters | `outlit_list_customers` |
| Activity timeline | `outlit_get_timeline` |
| Revenue for one customer | `outlit_get_customer` with `include: ["revenue"]` |
| Aggregate metrics (MRR, churn, cohorts) | `outlit_query` (SQL) |
| Custom analytics, JOINs, time-series | `outlit_query` (SQL) |
