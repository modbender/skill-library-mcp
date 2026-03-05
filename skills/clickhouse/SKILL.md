---
name: ClickHouse
slug: clickhouse
version: 1.0.1
homepage: https://clawic.com/skills/clickhouse
description: Query, optimize, and administer ClickHouse OLAP databases with schema design, performance tuning, and data ingestion patterns.
metadata: {"clawdbot":{"emoji":"🏠","requires":{"bins":["clickhouse-client"]},"os":["linux","darwin"],"install":[{"id":"brew","kind":"brew","formula":"clickhouse","bins":["clickhouse-client"],"label":"Install ClickHouse (Homebrew)"}]}}
---

# ClickHouse 🏠

Real-time analytics on billions of rows. Sub-second queries. No indexes needed.

## Setup

On first use, read `setup.md` for connection configuration.

## When to Use

User needs OLAP analytics, log analysis, time-series data, or real-time dashboards. Agent handles schema design, query optimization, data ingestion, and cluster administration.

## Architecture

Memory lives in `~/clickhouse/`. See `memory-template.md` for structure.

```
~/clickhouse/
├── memory.md        # Connection profiles + query patterns
├── schemas/         # Table definitions per database
└── queries/         # Saved analytical queries
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup & connection | `setup.md` |
| Memory template | `memory-template.md` |
| Query patterns | `queries.md` |
| Performance tuning | `performance.md` |
| Data ingestion | `ingestion.md` |

## Core Rules

### 1. Always Specify Engine
Every table needs an explicit engine. Default to MergeTree family:

```sql
-- Time-series / logs
CREATE TABLE events (
    timestamp DateTime,
    event_type String,
    data String
) ENGINE = MergeTree()
ORDER BY (timestamp, event_type);

-- Aggregated metrics
CREATE TABLE daily_stats (
    date Date,
    metric String,
    value AggregateFunction(sum, UInt64)
) ENGINE = AggregatingMergeTree()
ORDER BY (date, metric);
```

### 2. ORDER BY is Your Index
ClickHouse has no traditional indexes. The `ORDER BY` clause determines data layout:

- Put high-cardinality filter columns first
- Put range columns (dates, timestamps) early
- Match your most common WHERE patterns

```sql
-- Good: filters by user_id, then date range
ORDER BY (user_id, date, event_type)

-- Bad: date first when you filter by user_id
ORDER BY (date, user_id, event_type)
```

### 3. Use Appropriate Data Types

| Use Case | Type | Why |
|----------|------|-----|
| Timestamps | `DateTime` or `DateTime64` | Native time functions |
| Low-cardinality strings | `LowCardinality(String)` | 10x compression |
| Enums with few values | `Enum8` or `Enum16` | Smallest footprint |
| Nullable only if needed | `Nullable(T)` | Adds overhead |
| IPs | `IPv4` or `IPv6` | 4 bytes vs 16+ |

### 4. Batch Inserts
Never insert row-by-row. ClickHouse is optimized for batch writes:

```bash
# Good: batch insert
clickhouse-client --query="INSERT INTO events FORMAT JSONEachRow" < batch.json

# Bad: individual inserts in a loop
for row in data:
    INSERT INTO events VALUES (...)
```

Minimum batch: 1,000 rows. Optimal: 10,000-100,000 rows.

### 5. Prewarm Queries with FINAL
Queries on ReplacingMergeTree/CollapsingMergeTree need `FINAL` for accuracy:

```sql
-- May return duplicates/old versions
SELECT * FROM users WHERE id = 123;

-- Guaranteed latest version
SELECT * FROM users FINAL WHERE id = 123;
```

`FINAL` has performance cost. For dashboards, consider materialized views.

### 6. Materialized Views for Speed
Pre-aggregate expensive computations:

```sql
CREATE MATERIALIZED VIEW hourly_events
ENGINE = SummingMergeTree()
ORDER BY (hour, event_type)
AS SELECT
    toStartOfHour(timestamp) AS hour,
    event_type,
    count() AS events
FROM events
GROUP BY hour, event_type;
```

### 7. Check System Tables First
Before debugging, check system tables:

```sql
-- Running queries
SELECT * FROM system.processes;

-- Recent query performance
SELECT query, elapsed, read_rows, memory_usage
FROM system.query_log
WHERE type = 'QueryFinish'
ORDER BY event_time DESC
LIMIT 10;

-- Table sizes
SELECT database, table, formatReadableSize(total_bytes) as size
FROM system.tables
ORDER BY total_bytes DESC;
```

## Common Traps

- **String instead of LowCardinality** → 10x larger storage for status/type columns
- **Wrong ORDER BY** → Full table scans instead of index lookups
- **Row-by-row inserts** → Massive part fragmentation, slow writes
- **Missing TTL** → Unbounded table growth, disk full
- **SELECT *** → Reads all columns, kills columnar advantage
- **Nullable everywhere** → Overhead + NULL handling complexity
- **Forgetting FINAL** → Stale/duplicate data in merge tables

## Performance Checklist

Before running expensive queries:

1. **Check EXPLAIN**: `EXPLAIN SELECT ...` shows execution plan
2. **Sample first**: `SELECT ... FROM table SAMPLE 0.01` for 1% sample
3. **Limit columns**: Only SELECT what you need
4. **Use PREWHERE**: Filters before reading all columns
5. **Check parts**: `SELECT count() FROM system.parts WHERE table='X'`

```sql
-- PREWHERE optimization
SELECT user_id, event_type, data
FROM events
PREWHERE date = today()
WHERE event_type = 'click';
```

## Cluster Administration

### Adding TTL for Data Retention

```sql
-- Delete old data
ALTER TABLE events
MODIFY TTL timestamp + INTERVAL 90 DAY;

-- Move to cold storage
ALTER TABLE events
MODIFY TTL timestamp + INTERVAL 30 DAY TO VOLUME 'cold';
```

### Monitoring Disk Usage

```sql
SELECT
    database,
    table,
    formatReadableSize(sum(bytes_on_disk)) as disk_size,
    sum(rows) as total_rows,
    count() as parts
FROM system.parts
WHERE active
GROUP BY database, table
ORDER BY sum(bytes_on_disk) DESC;
```

## External Endpoints

| Endpoint | Data Sent | Purpose |
|----------|-----------|---------|
| localhost:8123 | SQL queries | HTTP interface |
| localhost:9000 | SQL queries | Native TCP interface |

No external services contacted. All queries run against user-specified ClickHouse instances.

## Security & Privacy

**Data saved locally (with user consent):**
- Connection profiles (host, port, database) in ~/clickhouse/memory.md
- Query patterns and schema documentation
- Authentication method preferences (password vs certificate)

**Important:** If you provide database passwords, they are stored in plain text in ~/clickhouse/. Consider using environment variables or connection profiles managed by clickhouse-client instead.

**This skill does NOT:**
- Connect to any ClickHouse without explicit user configuration
- Send data to external services
- Automatically collect or store credentials without asking

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `sql` — SQL query patterns
- `analytics` — data analysis workflows
- `data-analysis` — structured data exploration

## Feedback

- If useful: `clawhub star clickhouse`
- Stay updated: `clawhub sync`
