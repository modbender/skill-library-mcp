# SurrealDB Performance

This guide covers storage engine selection, indexing strategies, query optimization, write and read performance tuning, distributed deployment considerations, and monitoring for SurrealDB.

---

## Storage Engine Selection

SurrealDB supports multiple storage backends, each suited to different deployment scenarios.

| Engine | Best For | Persistence | Distributed | Versioning |
|---|---|---|---|---|
| In-Memory | Development, testing, ephemeral caches | No | No | No |
| RocksDB | Single-node production, proven reliability | Yes | No | No |
| SurrealKV | Single-node production, time-travel queries | Yes | No | Yes |
| TiKV | Distributed HA, horizontal scaling | Yes | Yes | No |
| IndexedDB | Browser-based apps (WASM) | Yes (browser) | No | No |

### Starting with Each Engine

```bash
# In-Memory (data lost on restart)
surreal start memory

# RocksDB (single file path)
surreal start rocksdb:///var/data/surreal.db

# SurrealKV (default in SurrealDB 3.x for file-based storage)
surreal start surrealkv:///var/data/surreal.db
# Or simply:
surreal start file:///var/data/surreal.db

# TiKV (distributed, requires running TiKV cluster)
surreal start tikv://pd-host:2379

# IndexedDB (browser WASM only, configured in SDK)
# Not started from CLI; used within browser SDK initialization
```

### Engine Selection Criteria

Use **In-Memory** when:
- Running tests or CI/CD pipelines
- Prototyping and development
- Temporary data processing

Use **RocksDB** when:
- You need battle-tested persistence (RocksDB powers many production databases)
- Single-node deployment is sufficient
- You want well-understood tuning options

Use **SurrealKV** when:
- You want the SurrealDB-native storage engine
- You need time-travel queries (version history of records)
- Single-node deployment with SurrealDB-optimized performance

Use **TiKV** when:
- You need horizontal scaling across multiple nodes
- High availability with automatic failover is required
- Your dataset exceeds single-node capacity
- You need distributed transactions

Use **IndexedDB** when:
- Building browser-based applications with SurrealDB WASM
- Offline-first applications that sync later

---

## Indexing Strategies

Indexes are the single most impactful performance optimization. SurrealDB supports standard indexes, unique indexes, composite indexes, full-text search indexes, and vector (HNSW) indexes.

### Standard Indexes

```surrealql
-- Single-field index
DEFINE INDEX idx_email ON TABLE user COLUMNS email;

-- The index accelerates WHERE clauses on the indexed field:
-- FAST (uses index):
SELECT * FROM user WHERE email = 'alice@example.com';
-- SLOW (full table scan):
SELECT * FROM user WHERE name = 'Alice';
```

### Unique Indexes

```surrealql
-- Unique index prevents duplicate values
DEFINE INDEX idx_unique_email ON TABLE user COLUMNS email UNIQUE;

-- This also speeds up lookups and enforces data integrity
-- Attempting to insert a duplicate will fail:
CREATE user SET email = 'alice@example.com';  -- succeeds
CREATE user SET email = 'alice@example.com';  -- fails with unique constraint error
```

### Composite Indexes

```surrealql
-- Multi-column index for queries that filter on multiple fields
DEFINE INDEX idx_tenant_status ON TABLE order COLUMNS tenant, status;

-- FAST (uses composite index, left-to-right prefix match):
SELECT * FROM order WHERE tenant = tenant:acme AND status = 'active';
SELECT * FROM order WHERE tenant = tenant:acme;  -- prefix match

-- SLOW (cannot use this index, wrong column order):
SELECT * FROM order WHERE status = 'active';  -- no leading 'tenant' filter

-- The order of columns matters: put the most selective or most frequently
-- filtered column first
DEFINE INDEX idx_status_created ON TABLE order COLUMNS status, created_at;
```

### Full-Text Search Indexes

```surrealql
-- Define an analyzer with tokenizers and filters
DEFINE ANALYZER english_analyzer
    TOKENIZERS blank, class
    FILTERS lowercase, snowball(english);

-- Define a full-text search index using BM25 scoring
DEFINE INDEX idx_ft_content ON TABLE article
    FIELDS content
    SEARCH ANALYZER english_analyzer BM25;

-- Full-text search query using the @@ operator
-- The number after @ is the scoring reference (used with search::score)
SELECT
    id,
    title,
    search::score(1) AS relevance
FROM article
WHERE content @1@ 'distributed database performance'
ORDER BY relevance DESC
LIMIT 20;

-- Highlight matching terms
SELECT
    id,
    title,
    search::highlight('<b>', '</b>', 1) AS highlighted
FROM article
WHERE content @1@ 'SurrealDB graph queries';

-- Combined analyzer for multiple languages
DEFINE ANALYZER multi_analyzer
    TOKENIZERS blank, class, camel
    FILTERS lowercase, ascii;
```

### Vector Indexes (HNSW)

See the vector-search rules file for detailed HNSW configuration. Summary:

```surrealql
-- Standard vector index
DEFINE INDEX idx_embedding ON TABLE document
    FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE;

-- High-recall configuration
DEFINE INDEX idx_embedding_hr ON TABLE document
    FIELDS embedding
    HNSW DIMENSION 1536 DIST COSINE EFC 300 M 32
    EXTEND_CANDIDATES KEEP_PRUNED_CONNECTIONS;
```

### When NOT to Index

- Columns with very low cardinality (e.g., boolean `active` with only true/false). The index overhead may exceed the scan cost.
- Tables with very few rows (under 1000). Full scans are fast on small tables.
- Columns that are rarely queried in WHERE clauses.
- Columns that are updated extremely frequently. Each update must also update the index.
- Temporary or staging tables used for bulk data processing.

### Index Rebuild Strategies

```surrealql
-- Remove and recreate an index to rebuild it
REMOVE INDEX idx_email ON TABLE user;
DEFINE INDEX idx_email ON TABLE user COLUMNS email;

-- Check current indexes on a table
INFO FOR TABLE user;
-- Returns index definitions and metadata
```

---

## Query Optimization

### EXPLAIN Statement

Use `EXPLAIN` to understand how SurrealDB executes a query and whether it uses indexes.

```surrealql
-- See the query execution plan
SELECT * FROM user WHERE email = 'alice@example.com' EXPLAIN;

-- EXPLAIN FULL provides more detail
SELECT * FROM user WHERE email = 'alice@example.com' EXPLAIN FULL;

-- Look for:
-- - "Index" operations (good: using an index)
-- - "Table" operations (bad: full table scan)
-- - "Iterate" step details show which index is used

-- Example output interpretation:
-- Operation: Iterate Index   -> using idx_email (fast)
-- Operation: Iterate Table   -> full scan (slow, needs index)
```

### Avoiding Full Table Scans

```surrealql
-- BAD: No index on 'status', causes full scan
SELECT * FROM order WHERE status = 'pending';

-- GOOD: Add an index first
DEFINE INDEX idx_order_status ON TABLE order COLUMNS status;
SELECT * FROM order WHERE status = 'pending';

-- BAD: Function call on indexed column prevents index use
SELECT * FROM user WHERE string::lowercase(email) = 'alice@example.com';

-- GOOD: Store normalized data, index it, query directly
-- (normalize at write time, not query time)
DEFINE FIELD email ON TABLE user VALUE string::lowercase($value);
SELECT * FROM user WHERE email = 'alice@example.com';

-- BAD: OR conditions across different columns may not use indexes efficiently
SELECT * FROM user WHERE email = 'alice@example.com' OR name = 'Alice';

-- GOOD: Use separate indexed queries if needed
-- or create a composite approach
```

### Efficient Graph Traversal

```surrealql
-- Index edge tables for fast traversal
DEFINE INDEX idx_knows_in ON TABLE knows COLUMNS in;
DEFINE INDEX idx_knows_out ON TABLE knows COLUMNS out;

-- GOOD: Bounded depth with limits
SELECT ->knows->(person LIMIT 20).name AS connections
FROM person:alice;

-- BAD: Unbounded multi-hop without limits
-- This can explode exponentially
SELECT ->knows->person->knows->person->knows->person
FROM person:alice;

-- GOOD: Use LIMIT at each hop to cap explosion
SELECT
    ->(knows LIMIT 10)->person
    ->(knows LIMIT 10)->person.name AS fof
FROM person:alice
LIMIT 50;
```

### Pagination Patterns

```surrealql
-- Basic offset pagination (simple but slower for deep pages)
SELECT * FROM article
ORDER BY created_at DESC
LIMIT 20
START 0;   -- page 1

SELECT * FROM article
ORDER BY created_at DESC
LIMIT 20
START 20;  -- page 2

SELECT * FROM article
ORDER BY created_at DESC
LIMIT 20
START 40;  -- page 3

-- Cursor-based pagination (faster for deep pages)
-- First page
SELECT * FROM article
ORDER BY created_at DESC
LIMIT 20;

-- Subsequent pages: use the last record's timestamp as cursor
SELECT * FROM article
WHERE created_at < $last_seen_timestamp
ORDER BY created_at DESC
LIMIT 20;

-- For guaranteed uniqueness, combine with record ID
SELECT * FROM article
WHERE created_at < $cursor_time
    OR (created_at = $cursor_time AND id < $cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

### Projection Optimization

```surrealql
-- BAD: SELECT * fetches all fields, including large ones
SELECT * FROM document;

-- GOOD: Select only the fields you need
SELECT id, title, created_at FROM document;

-- Especially important for tables with embeddings or large text
-- BAD:
SELECT * FROM document;  -- fetches embedding (6KB per row)

-- GOOD:
SELECT id, title, snippet FROM document;

-- GOOD: Use destructuring for nested/computed results
SELECT
    id,
    title,
    author.name AS author_name
FROM document;
```

### Subquery Optimization

```surrealql
-- BAD: Correlated subquery that runs for every row
SELECT *,
    (SELECT count() FROM comment WHERE post = $parent.id GROUP ALL) AS comment_count
FROM post;

-- GOOD: Use precomputed counts or batch the query
-- Option 1: Store count on the parent record
DEFINE EVENT update_comment_count ON TABLE comment WHEN $event = "CREATE" THEN {
    UPDATE $after.post SET comment_count += 1;
};

-- Option 2: Use a single aggregation query
SELECT post, count() AS comment_count FROM comment GROUP BY post;

-- GOOD: Use LET to precompute and reuse
LET $active_users = SELECT VALUE id FROM user WHERE active = true;
SELECT * FROM order WHERE customer IN $active_users;
```

### Parallel Query Execution

```surrealql
-- SurrealDB can execute independent statements in parallel within a request
-- Sending multiple queries in a single request is more efficient than
-- sending them one at a time

-- These three queries can be sent together in one request:
SELECT count() FROM user GROUP ALL;
SELECT count() FROM order GROUP ALL;
SELECT count() FROM product GROUP ALL;

-- The SDK will pipeline these and SurrealDB processes them efficiently
```

---

## Write Performance

### Batch Operations

```surrealql
-- BAD: Individual inserts (one round trip each)
CREATE user:1 SET name = 'Alice', email = 'alice@example.com';
CREATE user:2 SET name = 'Bob', email = 'bob@example.com';
CREATE user:3 SET name = 'Charlie', email = 'charlie@example.com';

-- GOOD: Batch insert (single operation)
INSERT INTO user [
    { id: user:1, name: 'Alice', email: 'alice@example.com' },
    { id: user:2, name: 'Bob', email: 'bob@example.com' },
    { id: user:3, name: 'Charlie', email: 'charlie@example.com' }
];

-- For large batches, use groups of 100-1000 records
-- Too small = too many round trips
-- Too large = high memory usage per transaction
```

### Transaction Sizing

```surrealql
-- SurrealDB wraps each request in an implicit transaction
-- For large data modifications, consider chunking

-- BAD: Updating millions of rows in one transaction
UPDATE user SET verified = true WHERE created_at < d'2025-01-01';

-- BETTER: Process in chunks using LIMIT
-- Chunk 1
UPDATE user SET verified = true WHERE created_at < d'2025-01-01' AND verified = false LIMIT 1000;
-- Chunk 2 (repeat until no more matches)
UPDATE user SET verified = true WHERE created_at < d'2025-01-01' AND verified = false LIMIT 1000;

-- Use application-level loop:
-- while (affected > 0) { run UPDATE ... LIMIT 1000 }
```

### Bulk Import

```bash
# Import from SurrealQL file
surreal import --conn http://localhost:8000 --user root --pass root --ns test --db test data.surql

# Import from JSON/JSONL
# Prepare a .surql file with INSERT statements for best performance

# For very large imports:
# 1. Disable/remove indexes before import
# 2. Perform bulk insert
# 3. Recreate indexes after import
# This avoids index maintenance overhead during bulk loading
```

```surrealql
-- Pre-import: remove expensive indexes
REMOVE INDEX idx_embedding ON TABLE document;
REMOVE INDEX idx_ft_content ON TABLE document;

-- ... perform bulk import ...

-- Post-import: recreate indexes (they build from existing data)
DEFINE INDEX idx_embedding ON TABLE document
    FIELDS embedding HNSW DIMENSION 1536 DIST COSINE;
DEFINE INDEX idx_ft_content ON TABLE document
    FIELDS content SEARCH ANALYZER english_analyzer BM25;
```

### Concurrent Write Patterns

```surrealql
-- Use record-level operations to minimize contention
-- SurrealDB uses MVCC, so concurrent writes to different records do not block

-- Atomic counter increment (safe under concurrency)
UPDATE product:123 SET stock -= 1 WHERE stock > 0;

-- Conditional update (optimistic concurrency)
UPDATE order:456 SET status = 'shipped'
WHERE status = 'approved';
-- Returns empty if the order was already changed by another transaction

-- For high-contention counters, consider sharding
-- Instead of one counter record, use multiple shards:
UPDATE counter_shard:1 SET count += 1;
-- Total = SUM across all shards
SELECT math::sum(count) FROM counter_shard GROUP ALL;
```

---

## Read Performance

### Computed Views for Pre-Aggregation

```surrealql
-- Pre-compute expensive aggregations using events
DEFINE TABLE product_stats SCHEMAFULL;
DEFINE FIELD product ON TABLE product_stats TYPE record<product>;
DEFINE FIELD total_orders ON TABLE product_stats TYPE int DEFAULT 0;
DEFINE FIELD total_revenue ON TABLE product_stats TYPE decimal DEFAULT 0;
DEFINE FIELD avg_rating ON TABLE product_stats TYPE float DEFAULT 0;
DEFINE FIELD review_count ON TABLE product_stats TYPE int DEFAULT 0;
DEFINE FIELD last_ordered ON TABLE product_stats TYPE option<datetime>;

-- Update stats when orders are created
DEFINE EVENT update_product_stats ON TABLE order_item WHEN $event = "CREATE" THEN {
    UPSERT product_stats:{$after.product} SET
        product = $after.product,
        total_orders += 1,
        total_revenue += $after.price * $after.quantity,
        last_ordered = time::now();
};

-- Update stats when reviews are created
DEFINE EVENT update_review_stats ON TABLE review WHEN $event = "CREATE" THEN {
    LET $stats = SELECT * FROM product_stats:{$after.product};
    LET $new_count = $stats.review_count + 1;
    LET $new_avg = (($stats.avg_rating * $stats.review_count) + $after.rating) / $new_count;

    UPSERT product_stats:{$after.product} SET
        product = $after.product,
        review_count = $new_count,
        avg_rating = $new_avg;
};

-- Queries against the stats table are instant (no aggregation at query time)
SELECT * FROM product_stats ORDER BY total_revenue DESC LIMIT 10;
```

### Caching Strategies

```surrealql
-- Application-level cache table for expensive computations
DEFINE TABLE cache_entry SCHEMAFULL;
DEFINE FIELD key ON TABLE cache_entry TYPE string;
DEFINE FIELD value ON TABLE cache_entry TYPE object;
DEFINE FIELD expires_at ON TABLE cache_entry TYPE datetime;
DEFINE FIELD created_at ON TABLE cache_entry TYPE datetime DEFAULT time::now();

DEFINE INDEX idx_cache_key ON TABLE cache_entry COLUMNS key UNIQUE;
DEFINE INDEX idx_cache_expiry ON TABLE cache_entry COLUMNS expires_at;

-- Read from cache or compute
DEFINE FUNCTION fn::cached_query($key: string, $ttl: duration) {
    LET $cached = SELECT VALUE value FROM cache_entry
        WHERE key = $key AND expires_at > time::now()
        LIMIT 1;

    IF count($cached) > 0 {
        RETURN $cached[0];
    };

    RETURN NONE;  -- cache miss, application should compute and store
};

-- Store in cache
DEFINE FUNCTION fn::cache_set($key: string, $value: object, $ttl: duration) {
    UPSERT cache_entry SET
        key = $key,
        value = $value,
        expires_at = time::now() + $ttl;
};

-- Clean expired cache entries periodically
DELETE cache_entry WHERE expires_at < time::now();
```

### Live Query Efficiency

```surrealql
-- Live queries push changes to connected clients in real-time
-- Use them for dashboards, notifications, and collaborative features

-- Subscribe to changes on a table
LIVE SELECT * FROM message WHERE channel = 'general';

-- Subscribe to changes on a specific record
LIVE SELECT * FROM user:alice;

-- Performance tips for live queries:
-- 1. Use WHERE clauses to narrow the subscription scope
-- 2. Project only needed fields to reduce payload size
LIVE SELECT id, title, status FROM task WHERE project = project:123;

-- 3. Avoid subscribing to high-churn tables without filters
-- BAD:
LIVE SELECT * FROM log;  -- fires on every log entry

-- GOOD:
LIVE SELECT * FROM log WHERE severity = 'error';

-- 4. Kill live queries when no longer needed
-- KILL $live_query_id;
```

### Connection Pooling (SDK-Level)

```javascript
// JavaScript SDK: Connection pooling is managed by the SDK
import Surreal from 'surrealdb';

// Create a single client instance and reuse it
const db = new Surreal();
await db.connect('wss://db.example.com/rpc');
await db.use({ namespace: 'production', database: 'app' });

// Reuse this 'db' instance across your application
// Do NOT create a new connection per request

// For server-side applications, consider a connection pool wrapper:
// - Maintain a pool of authenticated connections
// - Checkout/checkin connections per request
// - Set reasonable pool size (start with 10-20 per server)
```

```rust
// Rust SDK: Create one client, clone for concurrent tasks
use surrealdb::engine::remote::ws::Ws;
use surrealdb::Surreal;

let db = Surreal::new::<Ws>("ws://localhost:8000").await?;
db.use_ns("production").use_db("app").await?;

// Clone the client for use in spawned tasks
// The underlying connection is shared
let db_clone = db.clone();
tokio::spawn(async move {
    let result = db_clone.select("user").await;
});
```

---

## Distributed Performance (TiKV)

### TiKV Architecture Overview

When using TiKV as the storage backend, SurrealDB operates in a distributed mode:

- **PD (Placement Driver)**: Manages cluster metadata and region scheduling
- **TiKV nodes**: Store data in regions, handle read/write requests
- **SurrealDB compute nodes**: Stateless query processors that connect to TiKV

```bash
# Start SurrealDB with TiKV backend
surreal start tikv://pd1:2379,pd2:2379,pd3:2379

# Multiple SurrealDB compute nodes can connect to the same TiKV cluster
# Each compute node is stateless and can handle any request
```

### Region Management

```
# TiKV automatically splits and merges regions based on data size
# Default region size: 96MB
# Regions are automatically distributed across TiKV nodes

# Monitor region distribution:
# - Use TiKV's built-in metrics (Prometheus/Grafana)
# - Watch for hot regions (regions receiving disproportionate traffic)
```

### Replication Factor Tuning

```
# TiKV uses Raft consensus for replication
# Default replication factor: 3 (data exists on 3 nodes)
# Configure via PD:

# Higher replication factor:
# + Better read availability
# + Survives more node failures
# - More storage used
# - Slightly higher write latency

# For most production deployments, 3 replicas is appropriate
# 5 replicas for critical data requiring higher durability
```

### Compute Node Scaling

```bash
# SurrealDB compute nodes are stateless -- scale horizontally
# Put a load balancer in front of multiple compute nodes

# Node 1
surreal start tikv://pd:2379 --bind 0.0.0.0:8000

# Node 2
surreal start tikv://pd:2379 --bind 0.0.0.0:8000

# Node 3
surreal start tikv://pd:2379 --bind 0.0.0.0:8000

# Load balancer distributes requests across nodes
# All nodes see the same data (shared TiKV cluster)
```

### Network Latency Considerations

```
# For distributed deployments:
# - Place SurrealDB compute nodes close to TiKV nodes (same datacenter)
# - Use dedicated network links between compute and storage tiers
# - Cross-region replication adds latency proportional to network distance
# - Read-heavy workloads benefit from local read replicas

# Latency budget (typical):
# - Same rack: <1ms
# - Same datacenter: 1-5ms
# - Cross-datacenter (same region): 5-20ms
# - Cross-region: 50-200ms
```

### Cross-Region Deployment Patterns

```
# Pattern 1: Active-passive (simpler)
# - Primary region handles all writes
# - Secondary region has read replicas
# - Failover to secondary if primary fails

# Pattern 2: Active-active (complex)
# - Both regions handle reads and writes
# - TiKV Raft handles consensus across regions
# - Higher write latency due to cross-region consensus
# - Use region-local reads with follower read feature

# Pattern 3: Region-local with async sync
# - Each region has its own SurrealDB + TiKV cluster
# - Application-level async replication between regions
# - Eventual consistency between regions
# - Lowest latency for local operations
```

---

## Monitoring and Benchmarking

### INFO FOR Statements

```surrealql
-- Introspect database structure and metadata
INFO FOR ROOT;
-- Shows all namespaces

INFO FOR NAMESPACE;
-- Shows all databases in the current namespace

INFO FOR DATABASE;
-- Shows all tables, access methods, and functions in the current database

INFO FOR TABLE user;
-- Shows fields, indexes, events, and permissions for a table
-- Use this to verify indexes exist and are correctly defined
```

### Query Timing

```surrealql
-- Use EXPLAIN to understand query performance
SELECT * FROM user WHERE email = 'alice@example.com' EXPLAIN FULL;

-- Time queries at the application level
-- Most SDKs support timing query execution

-- Compare query plans before and after adding indexes:
-- Before:
SELECT * FROM order WHERE status = 'pending' EXPLAIN;
-- Result: Iterate Table (full scan)

DEFINE INDEX idx_status ON TABLE order COLUMNS status;

-- After:
SELECT * FROM order WHERE status = 'pending' EXPLAIN;
-- Result: Iterate Index idx_status (index scan)
```

### Resource Monitoring

```bash
# Monitor SurrealDB process
# CPU and memory usage
ps aux | grep surreal

# Disk usage for RocksDB/SurrealKV
du -sh /var/data/surreal.db

# Network connections
ss -tnp | grep surreal

# For TiKV deployments, monitor:
# - PD dashboard (cluster overview)
# - TiKV metrics (region count, leader count, store size)
# - Raft metrics (proposal latency, log append latency)
# Use Prometheus + Grafana for comprehensive monitoring
```

### Benchmark Methodologies

```surrealql
-- Benchmark write throughput
-- Create a test table
DEFINE TABLE bench_write SCHEMALESS;

-- Time how long it takes to insert N records
-- Use batch inserts of 100-1000 records per request
-- Measure requests/second and records/second

-- Benchmark read throughput
-- Create test data, then measure SELECT performance
-- Test with and without indexes
-- Test with varying result set sizes (LIMIT 1, 10, 100, 1000)

-- Benchmark graph traversal
-- Create a known graph topology
-- Time traversals at different depths
-- Measure with and without edge table indexes

-- Benchmark vector search
-- Insert N vectors of known dimension
-- Time KNN queries with varying K values
-- Measure recall against brute-force results
```

### Common Bottlenecks and Solutions

| Bottleneck | Symptom | Solution |
|---|---|---|
| Missing index | Slow WHERE queries, EXPLAIN shows "Iterate Table" | Add appropriate index |
| Over-indexing | Slow writes, high disk usage | Remove unused indexes |
| Large result sets | High memory, slow response | Use LIMIT, pagination, projections |
| Deep graph traversal | Exponential query time | Limit depth, add LIMIT per hop, precompute |
| Vector search on large dataset | Slow KNN queries | Tune HNSW parameters (EFC, M), use metadata pre-filtering |
| Correlated subqueries | Slow queries on large tables | Precompute with events, use LET variables |
| Full-text search on large corpus | Slow text queries | Tune analyzer, use more specific search terms |
| Lock contention | Slow concurrent writes | Reduce transaction size, shard hot records |
| Network latency (TiKV) | High query latency | Co-locate compute and storage, use follower reads |
| Large transactions | Timeout or OOM | Chunk into smaller batches |

---

## Memory Management

### Cache Configuration

```bash
# RocksDB block cache size (controls memory usage for caching data blocks)
# Default is typically 50% of available RAM
# Adjust via environment variables or config
surreal start --rocksdb-cache-size 4GB rocksdb:///var/data/surreal.db
```

### Connection Limits

```bash
# Limit maximum concurrent connections
# Prevents resource exhaustion under load
surreal start --max-connections 1000

# Each connection consumes memory for:
# - Connection state
# - Query buffers
# - Live query subscriptions
# - Transaction context
```

### WASM Memory Considerations

```javascript
// When running SurrealDB in the browser via WASM:
// - Default WASM memory limit is typically 256MB-2GB depending on browser
// - Large datasets or vector indexes may exceed browser memory
// - Use pagination and lazy loading for large result sets
// - Consider server-side SurrealDB for heavy workloads

// For WASM deployments:
// - Keep dataset sizes small (thousands, not millions of records)
// - Avoid HNSW indexes on high-dimensional vectors in WASM
// - Use the server SDK for heavy analytics/search
```

### General Memory Guidelines

| Workload | Recommended RAM | Notes |
|---|---|---|
| Development | 1-2 GB | In-memory or small datasets |
| Small production (< 1M records) | 4-8 GB | Single-node, moderate indexes |
| Medium production (1-10M records) | 16-32 GB | Multiple indexes, vector search |
| Large production (10M+ records) | 64+ GB | Heavy indexing, HNSW on large datasets |
| TiKV node | 16-32 GB per node | Based on region count and data volume |

---

## Performance Checklist

Before deploying to production:

- Run EXPLAIN on all frequent queries to verify index usage
- Add indexes for every field used in WHERE clauses of frequent queries
- Index `in` and `out` columns on all edge tables used in graph traversals
- Use SCHEMAFULL tables to avoid schema inference overhead
- Select only needed fields (avoid `SELECT *` on wide tables)
- Use cursor-based pagination instead of OFFSET for deep pages
- Batch writes in groups of 100-1000 records
- Precompute aggregations using events and stats tables
- Set appropriate HNSW parameters for your dataset size and accuracy needs
- Monitor query latency and index usage regularly
- Use TiKV for workloads requiring horizontal scaling
- Co-locate compute and storage nodes for distributed deployments
- Test with realistic data volumes before production deployment
