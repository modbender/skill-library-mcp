# Performance Tuning — ClickHouse

## Query Optimization

### EXPLAIN First

Always check the execution plan before optimizing:

```sql
EXPLAIN SELECT ...
EXPLAIN PLAN SELECT ...
EXPLAIN ESTIMATE SELECT ...  -- row estimates
EXPLAIN SYNTAX SELECT ...    -- rewritten query
```

### PREWHERE vs WHERE

PREWHERE filters before reading all columns. Huge win for wide tables:

```sql
-- Read only date column first, then filter
SELECT user_id, event_type, data
FROM events
PREWHERE date = today()  -- filtered first
WHERE event_type = 'click' AND JSONHas(data, 'price');
```

ClickHouse auto-promotes simple WHERE to PREWHERE, but explicit is clearer.

### SELECT Only What You Need

```sql
-- Bad: reads all columns
SELECT * FROM events WHERE date = today();

-- Good: reads only needed columns
SELECT user_id, event_type, timestamp
FROM events
WHERE date = today();
```

For 100 columns, this can be 50x faster.

### Use Subqueries for Filtering

```sql
-- Inefficient: scans full table
SELECT * FROM events
WHERE user_id IN (SELECT user_id FROM premium_users);

-- Better: filter with join
SELECT e.*
FROM events e
INNER JOIN (
    SELECT DISTINCT user_id FROM premium_users
) p ON e.user_id = p.user_id;
```

## Schema Optimization

### ORDER BY Design

The ORDER BY clause is your "index". Design it for your query patterns:

| Query Pattern | ORDER BY |
|---------------|----------|
| Filter by user, then date | `(user_id, date)` |
| Time-series dashboard | `(date, metric_name)` |
| Multi-tenant + time | `(tenant_id, date, user_id)` |

**Rule:** Put columns you filter on with `=` first, then ranges.

### Partitioning

Partition large tables for faster queries and easier maintenance:

```sql
CREATE TABLE events (
    date Date,
    timestamp DateTime,
    user_id UInt64,
    event_type String
) ENGINE = MergeTree()
PARTITION BY toYYYYMM(date)  -- monthly partitions
ORDER BY (user_id, timestamp);
```

Benefits:
- Queries with date filter skip entire partitions
- TTL drops whole partitions (fast)
- Easier backups per partition

### Data Types Matter

| Bad | Good | Savings |
|-----|------|---------|
| String (status) | LowCardinality(String) | 10x |
| String (UUID) | UUID | 4x |
| String (IP) | IPv4/IPv6 | 4-8x |
| UInt64 (small numbers) | UInt8/UInt16 | 4-8x |
| Nullable(X) everywhere | X with default | 1 byte/row |

### Codecs for Compression

```sql
CREATE TABLE metrics (
    timestamp DateTime CODEC(Delta, ZSTD),  -- time series
    value Float64 CODEC(Gorilla, ZSTD),     -- floating point
    user_id UInt64 CODEC(T64, ZSTD),        -- integers
    status LowCardinality(String)           -- auto-compressed
) ENGINE = MergeTree()
ORDER BY timestamp;
```

Codec combinations:
- **Delta + ZSTD**: monotonic timestamps
- **Gorilla + ZSTD**: floating point metrics
- **T64 + ZSTD**: integer sequences
- **DoubleDelta + ZSTD**: very regular timestamps

## Materialized Views

Pre-aggregate expensive queries:

```sql
-- Hourly aggregations (computed on insert)
CREATE MATERIALIZED VIEW events_hourly
ENGINE = SummingMergeTree()
ORDER BY (hour, event_type)
AS SELECT
    toStartOfHour(timestamp) AS hour,
    event_type,
    count() AS count,
    uniq(user_id) AS unique_users
FROM events
GROUP BY hour, event_type;

-- Query the materialized view (instant)
SELECT * FROM events_hourly
WHERE hour >= now() - INTERVAL 24 HOUR;
```

### MV Patterns

| Use Case | Engine |
|----------|--------|
| Sum/count aggregations | SummingMergeTree |
| Avg, quantiles (states) | AggregatingMergeTree |
| Last value per key | ReplacingMergeTree |
| Deduplication | ReplacingMergeTree |

## Resource Management

### Memory Limits

```sql
-- Per-query limit
SET max_memory_usage = 10000000000;  -- 10 GB

-- Enable spilling to disk
SET max_bytes_before_external_group_by = 5000000000;
SET max_bytes_before_external_sort = 5000000000;
```

### Parallel Processing

```sql
-- Use more threads for complex queries
SET max_threads = 16;

-- Distributed queries
SET max_parallel_replicas = 3;
```

### Query Timeouts

```sql
SET max_execution_time = 300;  -- 5 minutes max
SET timeout_before_checking_execution_speed = 60;
```

## Monitoring Queries

### Find Slow Queries

```sql
SELECT
    query,
    user,
    elapsed,
    read_rows,
    formatReadableSize(read_bytes) AS read_size,
    formatReadableSize(memory_usage) AS memory
FROM system.query_log
WHERE type = 'QueryFinish'
    AND event_date = today()
    AND elapsed > 5
ORDER BY elapsed DESC
LIMIT 20;
```

### Currently Running

```sql
SELECT
    query_id,
    user,
    elapsed,
    read_rows,
    formatReadableSize(memory_usage) AS memory,
    query
FROM system.processes
ORDER BY elapsed DESC;
```

### Kill Long Queries

```sql
KILL QUERY WHERE query_id = 'abc-123';
KILL QUERY WHERE user = 'analytics' AND elapsed > 600;
```

## Part Management

Too many parts = slow queries. Monitor and optimize:

```sql
-- Parts per table
SELECT
    database,
    table,
    count() AS parts,
    sum(rows) AS rows,
    formatReadableSize(sum(bytes_on_disk)) AS size
FROM system.parts
WHERE active
GROUP BY database, table
HAVING parts > 100
ORDER BY parts DESC;

-- Force merge
OPTIMIZE TABLE events FINAL;  -- expensive, use carefully
```

### Preventing Part Explosion

1. **Batch inserts** (1000+ rows per insert)
2. **Avoid INSERT SELECT** from small result sets
3. **Set up TTL** for automatic cleanup
4. **Schedule OPTIMIZE** during low traffic
