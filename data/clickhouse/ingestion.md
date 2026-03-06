# Data Ingestion — ClickHouse

## Batch Insert Patterns

### Minimum Batch Size

ClickHouse creates a "part" per INSERT. Too many small inserts = part explosion.

| Insert Size | Recommendation |
|-------------|----------------|
| < 100 rows | Buffer or skip |
| 100-1000 rows | Acceptable for low volume |
| 1000-10000 rows | Good |
| 10000-100000 rows | Optimal |
| > 100000 rows | Split into multiple batches |

### Formats for Insertion

```bash
# JSON (most common)
cat data.json | clickhouse-client --query="INSERT INTO events FORMAT JSONEachRow"

# CSV
clickhouse-client --query="INSERT INTO events FORMAT CSV" < data.csv

# Native (fastest, binary)
clickhouse-client --query="INSERT INTO events FORMAT Native" < data.native

# TSV (tab-separated)
clickhouse-client --query="INSERT INTO events FORMAT TabSeparated" < data.tsv
```

### HTTP Interface

```bash
# JSON via HTTP
curl 'http://localhost:8123/?query=INSERT%20INTO%20events%20FORMAT%20JSONEachRow' \
  --data-binary @data.json

# With authentication
curl 'http://localhost:8123/?user=default&password=xxx' \
  --data-binary @data.json \
  -H "X-ClickHouse-Query: INSERT INTO events FORMAT JSONEachRow"
```

## Buffer Tables

For high-frequency small writes, use Buffer engine:

```sql
-- Main table
CREATE TABLE events (
    timestamp DateTime,
    event_type String,
    data String
) ENGINE = MergeTree()
ORDER BY timestamp;

-- Buffer that flushes to main table
CREATE TABLE events_buffer AS events
ENGINE = Buffer(
    currentDatabase(), events,  -- destination
    16,           -- num_layers
    10, 100,      -- min/max time (seconds)
    10000, 1000000,  -- min/max rows
    10000000, 100000000  -- min/max bytes
);

-- Write to buffer (fast)
INSERT INTO events_buffer VALUES (...);
```

Buffer flushes automatically based on time, rows, or bytes thresholds.

## Kafka Integration

```sql
-- Kafka source table
CREATE TABLE events_kafka (
    timestamp DateTime,
    event_type String,
    data String
) ENGINE = Kafka()
SETTINGS
    kafka_broker_list = 'kafka:9092',
    kafka_topic_list = 'events',
    kafka_group_name = 'clickhouse',
    kafka_format = 'JSONEachRow',
    kafka_num_consumers = 4;

-- Target table
CREATE TABLE events (
    timestamp DateTime,
    event_type String,
    data String
) ENGINE = MergeTree()
ORDER BY timestamp;

-- Materialized view to move data
CREATE MATERIALIZED VIEW events_mv TO events AS
SELECT * FROM events_kafka;
```

## File Imports

### S3

```sql
-- Direct query from S3
SELECT * FROM s3(
    'https://bucket.s3.amazonaws.com/data/*.parquet',
    'AWS_KEY', 'AWS_SECRET',
    'Parquet'
);

-- Insert from S3
INSERT INTO events
SELECT * FROM s3('https://bucket.s3.amazonaws.com/events.json', 'JSONEachRow');
```

### Local Files

```sql
-- Query local file
SELECT * FROM file('/path/to/data.csv', CSV);

-- Insert from file
INSERT INTO events
SELECT * FROM file('/var/lib/clickhouse/user_files/data.json', 'JSONEachRow');
```

### URL

```sql
-- Fetch and insert from URL
INSERT INTO events
SELECT * FROM url('https://api.example.com/events', JSONEachRow);
```

## Deduplication

### ReplacingMergeTree

For upsert-style operations:

```sql
CREATE TABLE users (
    user_id UInt64,
    name String,
    email String,
    updated_at DateTime
) ENGINE = ReplacingMergeTree(updated_at)
ORDER BY user_id;

-- Insert (will replace on merge)
INSERT INTO users VALUES (1, 'John', 'john@example.com', now());

-- Query with deduplication
SELECT * FROM users FINAL WHERE user_id = 1;
```

### CollapsingMergeTree

For append + cancel patterns:

```sql
CREATE TABLE balances (
    user_id UInt64,
    balance Int64,
    sign Int8  -- 1 = insert, -1 = cancel
) ENGINE = CollapsingMergeTree(sign)
ORDER BY user_id;

-- Insert
INSERT INTO balances VALUES (1, 100, 1);

-- Update: cancel old + insert new
INSERT INTO balances VALUES
    (1, 100, -1),  -- cancel old
    (1, 150, 1);   -- insert new
```

## Schema Migrations

### Adding Columns

```sql
-- Add nullable column (instant)
ALTER TABLE events ADD COLUMN new_field String;

-- Add with default (backfills lazily)
ALTER TABLE events ADD COLUMN status String DEFAULT 'pending';

-- Add at specific position
ALTER TABLE events ADD COLUMN priority UInt8 AFTER event_type;
```

### Changing Types

```sql
-- Safe type changes
ALTER TABLE events MODIFY COLUMN count UInt64;  -- UInt32 → UInt64

-- Requires rewrite
ALTER TABLE events MODIFY COLUMN data JSON;  -- String → JSON
```

### Dropping Columns

```sql
-- Mark for deletion (fast)
ALTER TABLE events DROP COLUMN old_field;

-- Actually remove data (slow, scheduled)
OPTIMIZE TABLE events FINAL;
```

## Error Handling

### Skip Bad Rows

```sql
-- Skip malformed JSON
SET input_format_allow_errors_num = 100;  -- max errors
SET input_format_allow_errors_ratio = 0.1;  -- max 10% errors

INSERT INTO events FORMAT JSONEachRow ...
```

### Async Inserts

```sql
-- Enable async (buffers writes server-side)
SET async_insert = 1;
SET wait_for_async_insert = 0;  -- don't wait for confirmation

INSERT INTO events VALUES (...);
```

Good for high-frequency small writes from many clients.

## Monitoring Ingestion

```sql
-- Insert throughput
SELECT
    toStartOfMinute(event_time) AS minute,
    sum(written_rows) AS rows,
    sum(written_bytes) / 1000000 AS mb
FROM system.query_log
WHERE type = 'QueryFinish'
    AND query_kind = 'Insert'
    AND event_date = today()
GROUP BY minute
ORDER BY minute DESC
LIMIT 30;

-- Part creation rate
SELECT
    toStartOfHour(modification_time) AS hour,
    count() AS new_parts
FROM system.parts
WHERE modification_time >= now() - INTERVAL 24 HOUR
GROUP BY hour
ORDER BY hour;
```
