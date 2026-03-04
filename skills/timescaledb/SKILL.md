---
name: TimescaleDB
description: Store and query time-series data with hypertables, compression, and continuous aggregates.
metadata: {"clawdbot":{"emoji":"⏱️","requires":{"anyBins":["psql"]},"os":["linux","darwin","win32"]}}
---

## Hypertables

- Convert table to hypertable: `SELECT create_hypertable('metrics', 'time')`
- Must have time column (TIMESTAMPTZ recommended)—partition key for chunks
- Call BEFORE inserting data—converting large tables is expensive
- Can't undo easily—plan schema before converting

## Chunk Interval

- Default 7 days per chunk—tune based on data volume
- `SELECT set_chunk_time_interval('metrics', INTERVAL '1 day')` for high-volume
- Chunks should be 25% of memory—too small = overhead, too large = slow queries
- Check chunk sizes: `SELECT * FROM chunks_detailed_size('metrics')`

## time_bucket

- `time_bucket('1 hour', time)` groups timestamps—like date_trunc but with arbitrary intervals
- Use in GROUP BY for aggregation: `GROUP BY time_bucket('5 minutes', time)`
- Origin parameter for offset: `time_bucket('1 day', time, '2024-01-01'::timestamptz)`
- Beats date_trunc for non-standard intervals—15min, 4h, etc.

## Continuous Aggregates

- Materialized views that auto-refresh—pre-compute expensive aggregations
- `CREATE MATERIALIZED VIEW hourly_stats WITH (timescaledb.continuous) AS SELECT ...`
- Add refresh policy: `SELECT add_continuous_aggregate_policy('hourly_stats', ...)`
- Query aggregate view instead of raw hypertable—orders of magnitude faster

## Real-Time Aggregates

- Continuous aggregates include recent data automatically—no stale reads
- `WITH (timescaledb.continuous, timescaledb.materialized_only = false)` for real-time
- Combines materialized historical + live recent—transparent to queries
- Small performance cost for real-time—disable if batch-only acceptable

## Compression

- Compress old chunks to save 90%+ storage: `ALTER TABLE metrics SET (timescaledb.compress)`
- Add compression policy: `SELECT add_compression_policy('metrics', INTERVAL '7 days')`
- Compressed chunks are read-only—can't update/delete individual rows
- Decompress for modifications: `SELECT decompress_chunk('chunk_name')`

## Retention

- Auto-delete old data: `SELECT add_retention_policy('metrics', INTERVAL '90 days')`
- Drops entire chunks—efficient, no row-by-row delete
- Retention runs on scheduler—data persists slightly past interval
- Combine with compression: compress at 7d, drop at 90d

## Indexing

- Time column auto-indexed in hypertable—don't add redundant index
- Add indexes on filter columns: `CREATE INDEX ON metrics (device_id, time DESC)`
- Composite indexes with time last—enables chunk exclusion
- Skip indexes on rarely-filtered columns—each index slows writes

## Insert Performance

- Batch inserts critical—single-row inserts are slow
- Use COPY or multi-value INSERT: `INSERT INTO metrics VALUES (...), (...), ...`
- Parallel COPY with `timescaledb-parallel-copy` tool—saturates I/O
- Out-of-order inserts work but slower—prefer time-ordered writes

## Query Patterns

- Always include time range in WHERE—enables chunk exclusion
- `WHERE time > now() - INTERVAL '1 day'` skips old chunks entirely
- ORDER BY time DESC with LIMIT for "latest N"—index scan, fast
- Avoid SELECT * on wide tables—fetch only needed columns

## Distributed Hypertables

- Multi-node for horizontal scale—data sharded across nodes
- Create access node + data nodes—access node coordinates queries
- More operational complexity—start single-node, distribute when needed
- Not needed for most workloads—single node handles millions of rows/sec
