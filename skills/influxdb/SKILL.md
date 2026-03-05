---
name: InfluxDB
description: Store and query time-series data with proper schema design and retention.
metadata: {"clawdbot":{"emoji":"📈","requires":{"anyBins":["influx","curl"]},"os":["linux","darwin","win32"]}}
---

## Version Differences

- InfluxDB 2.x uses Flux query language, 1.x uses InfluxQL—syntax completely different
- 2.x: buckets, organizations, tokens; 1.x: databases, retention policies, users
- Don't mix documentation—check version before copying queries

## Tags vs Fields (Critical)

- Tags are indexed, fields are not—filter on tags, aggregate on fields
- Tag values must be strings—numbers as tags work but waste index space
- Fields support numbers, strings, booleans—store metrics as fields
- Wrong choice kills query performance—can't change after data written

## Cardinality Trap

- High-cardinality tags destroy performance—unique user IDs as tags = disaster
- Cardinality = unique combinations of tag values—grows multiplicatively
- Check with `SHOW CARDINALITY` (1.x) or `influx bucket inspect` (2.x)
- Rule of thumb: <100K series per measurement; millions = problems

## Line Protocol

- Format: `measurement,tag1=v1,tag2=v2 field1=1,field2="str" timestamp`
- No spaces around `=` in tags—space separates tags from fields
- String fields need quotes, tag values don't—`field="text"` vs `tag=text`
- Timestamps in nanoseconds by default—specify precision to avoid mistakes

## Timestamps

- Default precision is nanoseconds—sending seconds without precision flag = year 2000 data
- Specify on write: `precision=s` for seconds, `precision=ms` for milliseconds
- Missing timestamp uses server time—usually fine for real-time ingestion
- Timestamps are UTC—client timezone doesn't matter

## Retention and Downsampling

- Set retention policy/bucket duration—data older than retention auto-deleted
- Raw data at 10s intervals for 7 days, downsample to 1min for 30 days, 1h for 1 year
- 2.x: Tasks for downsampling; 1.x: Continuous Queries
- Without downsampling, storage grows forever and queries slow down

## Flux Query Patterns (2.x)

- Always start with `from(bucket:)` then `|> range(start:)`—range is required
- `|> filter(fn: (r) => r._measurement == "cpu")` for filtering
- `|> aggregateWindow(every: 1h, fn: mean)` for time-based aggregation
- Chain transforms with `|>` pipe operator—order matters for performance

## InfluxQL Patterns (1.x)

- `SELECT mean("value") FROM "measurement" WHERE time > now() - 1h GROUP BY time(5m)`
- Double quotes for identifiers, single quotes for string literals
- `GROUP BY time()` for time-based aggregation—required for most dashboards
- `FILL(none)` to skip empty intervals, `FILL(previous)` to carry forward

## Schema Design

- Measurement name = table name—one per metric type (cpu, memory, requests)
- Tag for dimensions you filter/group by—host, region, service
- Field for values you aggregate—usage_percent, count, latency_ms
- Avoid encoding data in measurement names—`cpu.host1` wrong, `cpu` + `host=host1` right

## Write Performance

- Batch writes—individual points have HTTP overhead
- Telegraf for production ingestion—handles batching, buffering, retry
- Write to localhost if possible—network latency adds up at high throughput
- `async` writes in client libraries—don't block on each write

## Query Performance

- Always include time range—unbounded queries scan everything
- Filter on tags before fields—tags use index, fields scan data
- Limit results with `LIMIT` or `|> limit()`—dashboard doesn't need 1M points
- Use `GROUP BY` / `aggregateWindow` to reduce data before returning

## Common Errors

- "partial write: field type conflict"—same field with different types; fix at source
- "max-values-per-tag limit exceeded"—cardinality too high; redesign schema
- "database not found"—2.x uses buckets, not databases; check API version
- Query timeout—add narrower time range or aggregate more aggressively
