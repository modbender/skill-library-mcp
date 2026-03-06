# Query Patterns — ClickHouse

## Time-Series Aggregations

### Hourly/Daily Rollups

```sql
-- Events per hour
SELECT
    toStartOfHour(timestamp) AS hour,
    count() AS events,
    uniqExact(user_id) AS unique_users
FROM events
WHERE timestamp >= now() - INTERVAL 7 DAY
GROUP BY hour
ORDER BY hour;

-- Daily with fill
SELECT
    toDate(timestamp) AS date,
    count() AS events
FROM events
WHERE timestamp >= today() - 30
GROUP BY date
ORDER BY date
WITH FILL FROM today() - 30 TO today();
```

### Moving Averages

```sql
SELECT
    date,
    events,
    avg(events) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS ma_7d
FROM (
    SELECT toDate(timestamp) AS date, count() AS events
    FROM events
    GROUP BY date
);
```

## Funnel Analysis

```sql
-- Simple conversion funnel
SELECT
    level,
    users,
    users / first_value(users) OVER (ORDER BY level) AS conversion_rate
FROM (
    SELECT 1 AS level, uniqExact(user_id) AS users FROM events WHERE event = 'visit'
    UNION ALL
    SELECT 2, uniqExact(user_id) FROM events WHERE event = 'signup'
    UNION ALL
    SELECT 3, uniqExact(user_id) FROM events WHERE event = 'purchase'
);
```

## Top-N Queries

```sql
-- Top 10 users by events (efficient)
SELECT user_id, count() AS events
FROM events
WHERE date = today()
GROUP BY user_id
ORDER BY events DESC
LIMIT 10;

-- Top N per category
SELECT *
FROM (
    SELECT
        category,
        product_id,
        sales,
        row_number() OVER (PARTITION BY category ORDER BY sales DESC) AS rn
    FROM products
)
WHERE rn <= 5;
```

## Session Analysis

```sql
-- Session duration (30-min gap = new session)
SELECT
    user_id,
    session_id,
    min(timestamp) AS session_start,
    max(timestamp) AS session_end,
    dateDiff('minute', min(timestamp), max(timestamp)) AS duration_minutes
FROM (
    SELECT
        user_id,
        timestamp,
        sum(new_session) OVER (PARTITION BY user_id ORDER BY timestamp) AS session_id
    FROM (
        SELECT
            user_id,
            timestamp,
            if(dateDiff('minute', lagInFrame(timestamp) OVER (PARTITION BY user_id ORDER BY timestamp), timestamp) > 30
               OR lagInFrame(timestamp) OVER (PARTITION BY user_id ORDER BY timestamp) IS NULL, 1, 0) AS new_session
        FROM events
    )
)
GROUP BY user_id, session_id;
```

## Percentiles

```sql
-- Response time percentiles
SELECT
    quantile(0.50)(response_time) AS p50,
    quantile(0.90)(response_time) AS p90,
    quantile(0.99)(response_time) AS p99,
    max(response_time) AS max
FROM requests
WHERE timestamp >= now() - INTERVAL 1 HOUR;

-- Percentiles over time
SELECT
    toStartOfMinute(timestamp) AS minute,
    quantile(0.95)(response_time) AS p95
FROM requests
WHERE timestamp >= now() - INTERVAL 1 HOUR
GROUP BY minute
ORDER BY minute;
```

## Retention Analysis

```sql
-- Weekly cohort retention
WITH cohorts AS (
    SELECT
        user_id,
        toMonday(min(timestamp)) AS cohort_week
    FROM events
    GROUP BY user_id
)
SELECT
    c.cohort_week,
    dateDiff('week', c.cohort_week, toMonday(e.timestamp)) AS weeks_since_signup,
    uniqExact(e.user_id) AS users
FROM events e
JOIN cohorts c ON e.user_id = c.user_id
WHERE e.timestamp >= c.cohort_week
GROUP BY c.cohort_week, weeks_since_signup
ORDER BY c.cohort_week, weeks_since_signup;
```

## Array Operations

```sql
-- Explode array column
SELECT
    user_id,
    tag
FROM events
ARRAY JOIN tags AS tag
WHERE arrayExists(x -> x = 'premium', tags);

-- Aggregate into array
SELECT
    user_id,
    groupArray(event_type) AS event_sequence
FROM events
GROUP BY user_id;

-- Array intersection
SELECT
    user_id,
    arrayIntersect(tags, ['premium', 'enterprise']) AS matching_tags
FROM events
WHERE length(arrayIntersect(tags, ['premium', 'enterprise'])) > 0;
```

## Approximate Queries

```sql
-- HyperLogLog for unique counts (faster, approximate)
SELECT uniqHLL12(user_id) AS approx_users FROM events;

-- Sampling for quick estimates
SELECT count() * 100 AS estimated_total
FROM events SAMPLE 0.01
WHERE event_type = 'purchase';

-- Approximate percentile (faster)
SELECT quantileTDigest(0.99)(response_time) AS approx_p99
FROM requests;
```

## JSON Handling

```sql
-- Extract from JSON string
SELECT
    JSONExtractString(data, 'name') AS name,
    JSONExtractInt(data, 'age') AS age,
    JSONExtractFloat(data, 'score') AS score
FROM events
WHERE JSONHas(data, 'name');

-- Nested JSON
SELECT
    JSONExtractString(data, 'user', 'email') AS email
FROM events;
```
