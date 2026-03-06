---
name: Database Engineering Mastery
description: "Before writing any DDL, fill this out:"
---

# Database Engineering Mastery

> Complete database design, optimization, migration, and operations system. From schema design to production monitoring — covers PostgreSQL, MySQL, SQLite, and general SQL patterns.

## Phase 1 — Schema Design

### Design Brief

Before writing any DDL, fill this out:

```yaml
project: ""
domain: ""
primary_use_case: "OLTP | OLAP | mixed"
expected_scale:
  rows_year_1: ""
  rows_year_3: ""
  concurrent_users: ""
  read_write_ratio: "80:20 | 50:50 | 20:80"
compliance: [] # GDPR, HIPAA, PCI-DSS, SOX
multi_tenancy: "none | schema-per-tenant | row-level | database-per-tenant"
```

### Normalization Decision Framework

| Form | Rule | When to Denormalize |
|------|------|---------------------|
| 1NF | No repeating groups, atomic values | Never skip |
| 2NF | No partial dependencies on composite keys | Never skip |
| 3NF | No transitive dependencies | Reporting tables, read-heavy aggregations |
| BCNF | Every determinant is a candidate key | Rarely needed unless complex key relationships |

**Denormalization triggers:**
- Query joins > 4 tables consistently
- Read latency > 100ms on indexed queries
- Cache invalidation complexity exceeds denormalization maintenance
- Reporting queries block OLTP workloads

### Naming Conventions

```
Tables:      snake_case, plural (users, order_items, payment_methods)
Columns:     snake_case, singular (first_name, created_at, is_active)
PKs:         id (bigint/uuid) or {table_singular}_id
FKs:         {referenced_table_singular}_id
Indexes:     idx_{table}_{columns}
Constraints: chk_{table}_{rule}, uq_{table}_{columns}, fk_{table}_{ref}
Enums:       Use VARCHAR + CHECK, not DB enums (easier to migrate)
Booleans:    is_, has_, can_ prefix (is_active, has_subscription)
Timestamps:  _at suffix (created_at, updated_at, deleted_at)
```

### Column Type Decision Tree

```
Text < 255 chars, fixed set?     → VARCHAR(N) + CHECK
Text < 255 chars, variable?      → VARCHAR(255)
Text > 255 chars?                → TEXT
Whole numbers < 2B?              → INTEGER
Whole numbers > 2B?              → BIGINT
Money/financial?                 → NUMERIC(precision, scale) — NEVER float
True/false?                      → BOOLEAN
Date only?                       → DATE
Date + time?                     → TIMESTAMPTZ (always with timezone)
Unique identifier?               → UUID (distributed) or BIGSERIAL (single DB)
JSON/flexible schema?            → JSONB (Postgres) or JSON (MySQL)
Binary/file?                     → Store in object storage, reference by URL
IP address?                      → INET (Postgres) or VARCHAR(45)
Geospatial?                      → PostGIS geometry/geography types
```

### Essential Table Template

```sql
CREATE TABLE {table_name} (
    id          BIGSERIAL PRIMARY KEY,
    -- domain columns here --
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    created_by  BIGINT REFERENCES users(id),
    version     INTEGER NOT NULL DEFAULT 1,  -- optimistic locking
    
    -- soft delete (optional)
    deleted_at  TIMESTAMPTZ,
    
    -- multi-tenant (optional)  
    tenant_id   BIGINT NOT NULL REFERENCES tenants(id)
);

-- Updated_at trigger (PostgreSQL)
CREATE OR REPLACE FUNCTION update_modified_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    NEW.version = OLD.version + 1;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trg_{table_name}_updated
    BEFORE UPDATE ON {table_name}
    FOR EACH ROW
    EXECUTE FUNCTION update_modified_column();
```

### Relationship Patterns

**One-to-Many:**
```sql
-- Parent
CREATE TABLE departments (id BIGSERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL);
-- Child  
CREATE TABLE employees (
    id BIGSERIAL PRIMARY KEY,
    department_id BIGINT NOT NULL REFERENCES departments(id) ON DELETE RESTRICT,
    -- ON DELETE options: RESTRICT (safe default), CASCADE (children die), SET NULL
);
CREATE INDEX idx_employees_department_id ON employees(department_id);
```

**Many-to-Many:**
```sql
CREATE TABLE user_roles (
    user_id BIGINT NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL REFERENCES roles(id) ON DELETE CASCADE,
    granted_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    granted_by BIGINT REFERENCES users(id),
    PRIMARY KEY (user_id, role_id)
);
```

**Self-Referencing (hierarchy):**
```sql
CREATE TABLE categories (
    id BIGSERIAL PRIMARY KEY,
    parent_id BIGINT REFERENCES categories(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    depth INTEGER NOT NULL DEFAULT 0,
    path TEXT NOT NULL DEFAULT ''  -- materialized path: '/1/5/12/'
);
CREATE INDEX idx_categories_parent ON categories(parent_id);
CREATE INDEX idx_categories_path ON categories(path text_pattern_ops);
```

**Polymorphic (avoid if possible, use if you must):**
```sql
-- Preferred: separate FKs
CREATE TABLE comments (
    id BIGSERIAL PRIMARY KEY,
    post_id BIGINT REFERENCES posts(id),
    ticket_id BIGINT REFERENCES tickets(id),
    body TEXT NOT NULL,
    CONSTRAINT chk_one_parent CHECK (
        (post_id IS NOT NULL)::int + (ticket_id IS NOT NULL)::int = 1
    )
);
```

---

## Phase 2 — Indexing Strategy

### Index Type Selection

| Index Type | Use When | Example |
|-----------|----------|---------|
| B-tree (default) | Equality, range, sorting, LIKE 'prefix%' | `CREATE INDEX idx_users_email ON users(email)` |
| Hash | Equality only, no range | `CREATE INDEX idx_sessions_token ON sessions USING hash(token)` |
| GIN | JSONB, full-text search, arrays, tsvector | `CREATE INDEX idx_products_tags ON products USING gin(tags)` |
| GiST | Geospatial, range types, nearest-neighbor | `CREATE INDEX idx_locations_geom ON locations USING gist(geom)` |
| BRIN | Very large tables with natural ordering (time-series) | `CREATE INDEX idx_events_created ON events USING brin(created_at)` |
| Partial | Subset of rows | `CREATE INDEX idx_orders_pending ON orders(created_at) WHERE status = 'pending'` |
| Covering | Include columns to avoid table lookup | `CREATE INDEX idx_orders_user ON orders(user_id) INCLUDE (status, total)` |

### Indexing Rules

1. **Always index:** Foreign keys, columns in WHERE/JOIN/ORDER BY
2. **Never index:** Low-cardinality columns alone (boolean, status with 3 values) — combine in composite
3. **Composite order:** Most selective column first, then left-to-right matches query patterns
4. **Watch write overhead:** Each index slows INSERT/UPDATE. >8 indexes on a write-heavy table = review
5. **Unused index audit:** Run monthly — drop indexes with 0 scans

### Find Unused Indexes (PostgreSQL)

```sql
SELECT schemaname, tablename, indexname, idx_scan, 
       pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
WHERE idx_scan = 0 AND indexrelid NOT IN (
    SELECT conindid FROM pg_constraint WHERE contype IN ('p', 'u')
)
ORDER BY pg_relation_size(indexrelid) DESC;
```

### Find Missing Indexes (PostgreSQL)

```sql
SELECT relname, seq_scan, seq_tup_read, 
       idx_scan, seq_tup_read / GREATEST(seq_scan, 1) as avg_tuples_per_scan
FROM pg_stat_user_tables
WHERE seq_scan > 100 AND seq_tup_read > 10000
ORDER BY seq_tup_read DESC;
-- High seq_scan + high seq_tup_read = missing index candidate
```

---

## Phase 3 — Query Optimization

### EXPLAIN Interpretation

```sql
EXPLAIN (ANALYZE, BUFFERS, FORMAT TEXT) SELECT ...;
```

**Red flags in query plans:**
| Pattern | Problem | Fix |
|---------|---------|-----|
| Seq Scan on large table | Missing index | Add appropriate index |
| Nested Loop with large outer | O(n×m) join | Add index on join column, consider Hash Join |
| Sort with high cost | Missing index for ORDER BY | Add index matching sort order |
| Hash Join spilling to disk | work_mem too low | Increase work_mem or reduce result set |
| Bitmap Heap Scan with many recheck | Low selectivity index | More selective index or partial index |
| SubPlan (correlated subquery) | Executes per row | Rewrite as JOIN or lateral |
| Rows estimate wildly wrong | Stale statistics | ANALYZE table |

### Query Anti-Patterns & Fixes

**1. SELECT * in production:**
```sql
-- Bad: fetches all columns, breaks covering indexes
SELECT * FROM orders WHERE user_id = 123;
-- Good: explicit columns
SELECT id, status, total, created_at FROM orders WHERE user_id = 123;
```

**2. N+1 queries:**
```sql
-- Bad: 1 query for users + N queries for orders
SELECT id FROM users WHERE active = true;  -- returns 100 rows
SELECT * FROM orders WHERE user_id = ?;     -- called 100 times

-- Good: single JOIN or IN
SELECT u.id, o.id, o.total 
FROM users u
JOIN orders o ON o.user_id = u.id
WHERE u.active = true;
```

**3. Functions on indexed columns:**
```sql
-- Bad: can't use index on created_at
WHERE EXTRACT(YEAR FROM created_at) = 2025
-- Good: range scan uses index
WHERE created_at >= '2025-01-01' AND created_at < '2026-01-01'

-- Bad: can't use index on email  
WHERE LOWER(email) = 'user@example.com'
-- Good: expression index
CREATE INDEX idx_users_email_lower ON users(LOWER(email));
```

**4. OR conditions killing indexes:**
```sql
-- Bad: often causes Seq Scan
WHERE status = 'pending' OR status = 'processing'
-- Good: IN uses index
WHERE status IN ('pending', 'processing')
```

**5. Pagination with OFFSET:**
```sql
-- Bad: OFFSET 10000 scans and discards 10000 rows
SELECT * FROM products ORDER BY id LIMIT 20 OFFSET 10000;
-- Good: keyset pagination
SELECT * FROM products WHERE id > :last_seen_id ORDER BY id LIMIT 20;
```

**6. COUNT(*) on large tables:**
```sql
-- Bad: full table scan
SELECT COUNT(*) FROM events;
-- Good: approximate count (PostgreSQL)
SELECT reltuples::bigint FROM pg_class WHERE relname = 'events';
-- Or maintain a counter cache table
```

### Window Functions Reference

```sql
-- Running total
SELECT id, amount, SUM(amount) OVER (ORDER BY created_at) as running_total FROM payments;

-- Rank within group
SELECT *, RANK() OVER (PARTITION BY department_id ORDER BY salary DESC) as dept_rank FROM employees;

-- Previous/next row
SELECT *, LAG(amount) OVER (ORDER BY created_at) as prev_amount,
          LEAD(amount) OVER (ORDER BY created_at) as next_amount FROM payments;

-- Moving average
SELECT *, AVG(amount) OVER (ORDER BY created_at ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) as ma_7 FROM daily_sales;

-- Percent of total
SELECT *, amount / SUM(amount) OVER () * 100 as pct_of_total FROM line_items WHERE order_id = 1;
```

### CTE Patterns

```sql
-- Recursive: org chart traversal
WITH RECURSIVE org AS (
    SELECT id, name, manager_id, 1 as depth FROM employees WHERE manager_id IS NULL
    UNION ALL
    SELECT e.id, e.name, e.manager_id, o.depth + 1
    FROM employees e JOIN org o ON e.manager_id = o.id
    WHERE o.depth < 10  -- safety limit
)
SELECT * FROM org ORDER BY depth, name;

-- Data pipeline: clean → transform → aggregate
WITH cleaned AS (
    SELECT *, TRIM(LOWER(email)) as clean_email FROM raw_signups WHERE email IS NOT NULL
),
deduped AS (
    SELECT DISTINCT ON (clean_email) * FROM cleaned ORDER BY clean_email, created_at DESC
)
SELECT DATE_TRUNC('week', created_at) as week, COUNT(*) FROM deduped GROUP BY 1 ORDER BY 1;
```

---

## Phase 4 — Migrations

### Migration Safety Rules

1. **Never** rename columns/tables in production without a multi-step process
2. **Never** add NOT NULL without a DEFAULT on existing tables with data
3. **Never** drop columns that application code still references
4. **Always** test migrations on a copy of production data first
5. **Always** have a rollback plan (down migration)
6. **Always** take a backup before schema changes in production

### Safe Migration Patterns

**Add column (safe):**
```sql
-- Step 1: Add nullable column
ALTER TABLE users ADD COLUMN phone VARCHAR(20);
-- Step 2: Backfill (in batches!)
UPDATE users SET phone = '' WHERE phone IS NULL AND id BETWEEN 1 AND 10000;
-- Step 3: Add NOT NULL after backfill
ALTER TABLE users ALTER COLUMN phone SET NOT NULL;
ALTER TABLE users ALTER COLUMN phone SET DEFAULT '';
```

**Rename column (safe multi-step):**
```sql
-- Step 1: Add new column
ALTER TABLE users ADD COLUMN full_name VARCHAR(200);
-- Step 2: Dual-write in application code (write to both old + new)
-- Step 3: Backfill
UPDATE users SET full_name = name WHERE full_name IS NULL;
-- Step 4: Switch application to read from new column
-- Step 5: Drop old column (after confirming no reads)
ALTER TABLE users DROP COLUMN name;
```

**Add index without locking (PostgreSQL):**
```sql
CREATE INDEX CONCURRENTLY idx_orders_customer ON orders(customer_id);
-- Takes longer but doesn't lock the table
```

**Large table backfill (batched):**
```sql
-- Don't: UPDATE millions of rows in one transaction
-- Do: batch it
DO $$
DECLARE
    batch_size INT := 5000;
    affected INT;
BEGIN
    LOOP
        UPDATE users SET normalized_email = LOWER(email)
        WHERE normalized_email IS NULL AND id IN (
            SELECT id FROM users WHERE normalized_email IS NULL LIMIT batch_size
        );
        GET DIAGNOSTICS affected = ROW_COUNT;
        RAISE NOTICE 'Updated % rows', affected;
        EXIT WHEN affected = 0;
        COMMIT;
    END LOOP;
END $$;
```

### Migration File Template

```sql
-- Migration: YYYYMMDDHHMMSS_description.sql
-- Author: [name]
-- Ticket: [JIRA/Linear ID]
-- Risk: low|medium|high
-- Rollback: see DOWN section
-- Estimated time: [for production data volume]
-- Requires: [prerequisite migrations]

-- ========== UP ==========
BEGIN;

-- [DDL/DML here]

COMMIT;

-- ========== DOWN ==========
-- BEGIN;
-- [Rollback DDL/DML here]
-- COMMIT;

-- ========== VERIFY ==========
-- [Queries to confirm migration succeeded]
-- SELECT COUNT(*) FROM ... WHERE ...;
```

---

## Phase 5 — Performance Monitoring

### Key Metrics Dashboard

```yaml
health_metrics:
  connections:
    active: "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
    idle: "SELECT count(*) FROM pg_stat_activity WHERE state = 'idle'"
    max: "SHOW max_connections"
    threshold: "active > 80% of max = ALERT"
    
  cache_hit_ratio:
    query: |
      SELECT ROUND(100.0 * sum(heap_blks_hit) / 
             NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0), 2) as ratio
      FROM pg_statio_user_tables
    healthy: "> 99%"
    warning: "< 95%"
    critical: "< 90%"
    
  index_hit_ratio:
    query: |
      SELECT ROUND(100.0 * sum(idx_blks_hit) / 
             NULLIF(sum(idx_blks_hit) + sum(idx_blks_read), 0), 2) as ratio
      FROM pg_statio_user_indexes
    healthy: "> 99%"
    
  table_bloat:
    query: |
      SELECT relname, n_dead_tup, n_live_tup,
             ROUND(100.0 * n_dead_tup / NULLIF(n_live_tup, 0), 2) as dead_pct
      FROM pg_stat_user_tables WHERE n_dead_tup > 10000
      ORDER BY n_dead_tup DESC LIMIT 10
    action: "VACUUM ANALYZE {table} when dead_pct > 20%"
    
  slow_queries:
    query: |
      SELECT query, calls, mean_exec_time, total_exec_time
      FROM pg_stat_statements
      ORDER BY mean_exec_time DESC LIMIT 20
    action: "Optimize top 5 by total_exec_time first"
    
  replication_lag:
    query: |
      SELECT EXTRACT(EPOCH FROM replay_lag) as lag_seconds
      FROM pg_stat_replication
    warning: "> 5 seconds"
    critical: "> 30 seconds"
```

### Table Size Analysis

```sql
SELECT 
    relname as table,
    pg_size_pretty(pg_total_relation_size(relid)) as total_size,
    pg_size_pretty(pg_relation_size(relid)) as table_size,
    pg_size_pretty(pg_total_relation_size(relid) - pg_relation_size(relid)) as index_size,
    n_live_tup as row_count
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC
LIMIT 20;
```

### Lock Monitoring

```sql
-- Find blocking queries
SELECT 
    blocked.pid as blocked_pid,
    blocked.query as blocked_query,
    blocking.pid as blocking_pid,
    blocking.query as blocking_query,
    NOW() - blocked.query_start as blocked_duration
FROM pg_stat_activity blocked
JOIN pg_locks bl ON bl.pid = blocked.pid
JOIN pg_locks kl ON kl.locktype = bl.locktype AND kl.relation = bl.relation AND kl.pid != bl.pid
JOIN pg_stat_activity blocking ON blocking.pid = kl.pid
WHERE NOT bl.granted;
```

---

## Phase 6 — Backup & Recovery

### Backup Strategy Decision

| Method | RPO | Speed | Use When |
|--------|-----|-------|----------|
| pg_dump (logical) | Point-in-time | Slow for >50GB | Small-medium DBs, cross-version migration |
| pg_basebackup (physical) | Continuous (with WAL) | Fast | Large DBs, same-version restore |
| WAL archiving (PITR) | Seconds | N/A (continuous) | Production with near-zero RPO |
| Replica promotion | Seconds | Instant | HA failover |

### Backup Commands

```bash
# Logical backup (compressed)
pg_dump -Fc -Z 9 -j 4 -d mydb -f backup_$(date +%Y%m%d_%H%M%S).dump

# Restore
pg_restore -d mydb -j 4 --clean --if-exists backup_20260216.dump

# Schema only
pg_dump -s -d mydb -f schema.sql

# Single table
pg_dump -t orders -d mydb -f orders_backup.dump

# Physical backup
pg_basebackup -D /backup/base -Ft -z -P -X stream
```

### Backup Verification Checklist

- [ ] Backup completes without errors
- [ ] Backup file size is within expected range (not suspiciously small)
- [ ] Restore to a test database succeeds
- [ ] Row counts match production (spot check 5 tables)
- [ ] Application can connect and query the restored database
- [ ] Run automated test suite against restored backup
- [ ] Backup encryption verified (if required)
- [ ] Offsite copy confirmed

---

## Phase 7 — Security

### Access Control Checklist

```sql
-- Create application role (least privilege)
CREATE ROLE app_user LOGIN PASSWORD 'use-vault-not-plaintext';
GRANT CONNECT ON DATABASE mydb TO app_user;
GRANT USAGE ON SCHEMA public TO app_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO app_user;
-- NO: GRANT ALL, superuser, CREATE, DROP

-- Read-only role for analytics
CREATE ROLE analyst LOGIN PASSWORD 'use-vault';
GRANT CONNECT ON DATABASE mydb TO analyst;
GRANT USAGE ON SCHEMA public TO analyst;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO analyst;

-- Row-Level Security (multi-tenant)
ALTER TABLE orders ENABLE ROW LEVEL SECURITY;
CREATE POLICY tenant_isolation ON orders
    USING (tenant_id = current_setting('app.tenant_id')::bigint);
```

### SQL Injection Prevention

```
RULE 1: NEVER concatenate user input into SQL strings
RULE 2: Always use parameterized queries / prepared statements
RULE 3: Validate and whitelist table/column names if dynamic
RULE 4: Use ORMs for CRUD, raw SQL only for complex queries
RULE 5: Audit logs for unusual query patterns (UNION, DROP, --)
```

### Data Protection

```sql
-- Encrypt sensitive columns (application-level)
-- Store: pgp_sym_encrypt(data, key) 
-- Read: pgp_sym_decrypt(encrypted_col, key)

-- Audit trail table
CREATE TABLE audit_log (
    id BIGSERIAL PRIMARY KEY,
    table_name VARCHAR(100) NOT NULL,
    record_id BIGINT NOT NULL,
    action VARCHAR(10) NOT NULL, -- INSERT, UPDATE, DELETE
    old_data JSONB,
    new_data JSONB,
    changed_by BIGINT REFERENCES users(id),
    changed_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    ip_address INET
);

-- Generic audit trigger
CREATE OR REPLACE FUNCTION audit_trigger() RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO audit_log (table_name, record_id, action, old_data, new_data, changed_by)
    VALUES (
        TG_TABLE_NAME,
        COALESCE(NEW.id, OLD.id),
        TG_OP,
        CASE WHEN TG_OP != 'INSERT' THEN to_jsonb(OLD) END,
        CASE WHEN TG_OP != 'DELETE' THEN to_jsonb(NEW) END,
        current_setting('app.user_id', true)::bigint
    );
    RETURN COALESCE(NEW, OLD);
END;
$$ LANGUAGE plpgsql;
```

---

## Phase 8 — PostgreSQL Configuration Tuning

### Essential Settings by Server Size

| Setting | Small (4GB RAM) | Medium (16GB) | Large (64GB+) |
|---------|-----------------|---------------|---------------|
| shared_buffers | 1GB | 4GB | 16GB |
| effective_cache_size | 3GB | 12GB | 48GB |
| work_mem | 16MB | 64MB | 256MB |
| maintenance_work_mem | 256MB | 1GB | 2GB |
| max_connections | 100 | 200 | 300 |
| wal_buffers | 64MB | 128MB | 256MB |
| random_page_cost | 1.1 (SSD) | 1.1 (SSD) | 1.1 (SSD) |
| effective_io_concurrency | 200 (SSD) | 200 (SSD) | 200 (SSD) |
| max_parallel_workers_per_gather | 2 | 4 | 8 |

### Connection Pooling (PgBouncer)

```ini
[databases]
mydb = host=127.0.0.1 port=5432 dbname=mydb

[pgbouncer]
pool_mode = transaction          # transaction pooling (best for most apps)
max_client_conn = 1000           # accept up to 1000 app connections
default_pool_size = 25           # 25 actual DB connections per database
reserve_pool_size = 5            # extra connections for burst
reserve_pool_timeout = 3         # seconds before using reserve
server_idle_timeout = 300        # close idle server connections after 5 min
```

---

## Phase 9 — Common Patterns

### Soft Delete

```sql
-- Add to table
ALTER TABLE users ADD COLUMN deleted_at TIMESTAMPTZ;
CREATE INDEX idx_users_active ON users(id) WHERE deleted_at IS NULL;

-- Application queries always filter
SELECT * FROM users WHERE deleted_at IS NULL AND ...;

-- Or use a view
CREATE VIEW active_users AS SELECT * FROM users WHERE deleted_at IS NULL;
```

### Optimistic Locking

```sql
UPDATE products SET 
    price = 29.99, 
    version = version + 1, 
    updated_at = NOW()
WHERE id = 123 AND version = 5;  -- expected version
-- If 0 rows affected → concurrent modification → retry or error
```

### Event Sourcing Table

```sql
CREATE TABLE events (
    id BIGSERIAL PRIMARY KEY,
    aggregate_type VARCHAR(50) NOT NULL,
    aggregate_id UUID NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    event_data JSONB NOT NULL,
    metadata JSONB DEFAULT '{}',
    version INTEGER NOT NULL,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (aggregate_id, version)
);
CREATE INDEX idx_events_aggregate ON events(aggregate_id, version);
CREATE INDEX idx_events_type ON events(event_type, created_at);
```

### Time-Series Optimization

```sql
-- Partitioned by month
CREATE TABLE metrics (
    id BIGSERIAL,
    sensor_id INTEGER NOT NULL,
    value NUMERIC(12,4) NOT NULL,
    recorded_at TIMESTAMPTZ NOT NULL
) PARTITION BY RANGE (recorded_at);

CREATE TABLE metrics_2026_01 PARTITION OF metrics
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE metrics_2026_02 PARTITION OF metrics
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

-- Auto-create future partitions via cron or pg_partman
-- Use BRIN index for time-series
CREATE INDEX idx_metrics_time ON metrics USING brin(recorded_at);
```

### Full-Text Search (PostgreSQL)

```sql
-- Add search column
ALTER TABLE articles ADD COLUMN search_vector tsvector;
CREATE INDEX idx_articles_search ON articles USING gin(search_vector);

-- Populate
UPDATE articles SET search_vector = 
    setweight(to_tsvector('english', COALESCE(title, '')), 'A') ||
    setweight(to_tsvector('english', COALESCE(body, '')), 'B');

-- Search with ranking
SELECT id, title, ts_rank(search_vector, query) as rank
FROM articles, plainto_tsquery('english', 'database optimization') query
WHERE search_vector @@ query
ORDER BY rank DESC LIMIT 20;
```

### JSONB Patterns

```sql
-- Store flexible attributes
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    attributes JSONB NOT NULL DEFAULT '{}',
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Index specific JSON paths
CREATE INDEX idx_products_color ON products((attributes->>'color'));
-- Or GIN for any key lookups
CREATE INDEX idx_products_attrs ON products USING gin(attributes);

-- Query patterns
SELECT * FROM products WHERE attributes->>'color' = 'red';
SELECT * FROM products WHERE attributes @> '{"size": "large"}';
SELECT * FROM products WHERE attributes ? 'warranty';
```

---

## Phase 10 — Operational Runbooks

### Emergency: Database Overloaded

```sql
-- 1. Find and kill long-running queries
SELECT pid, NOW() - query_start as duration, query 
FROM pg_stat_activity WHERE state = 'active' AND query_start < NOW() - INTERVAL '5 minutes'
ORDER BY duration DESC;

-- Kill a specific query
SELECT pg_cancel_backend(pid);    -- graceful
SELECT pg_terminate_backend(pid); -- force

-- 2. Check for lock contention (see Phase 5)

-- 3. Reduce max connections temporarily
-- In pgbouncer: pause database, reduce pool, resume

-- 4. Check if VACUUM is needed
SELECT relname, n_dead_tup, last_autovacuum FROM pg_stat_user_tables 
WHERE n_dead_tup > 100000 ORDER BY n_dead_tup DESC;
```

### Emergency: Disk Full

```bash
# 1. Check what's consuming space
du -sh /var/lib/postgresql/*/main/ 2>/dev/null || du -sh /var/lib/mysql/

# 2. Clean up WAL files (PostgreSQL) — CAREFUL
# Check replication slot status first
SELECT slot_name, active FROM pg_replication_slots;
# Drop inactive slots consuming WAL
SELECT pg_drop_replication_slot('unused_slot');

# 3. VACUUM FULL largest tables (locks table!)
VACUUM FULL large_table;

# 4. Remove old backups / logs
find /backups -name "*.dump" -mtime +7 -delete
```

### Weekly Maintenance Checklist

- [ ] Review slow query log (top 10 by total time)
- [ ] Check index usage stats — drop unused, add missing
- [ ] Verify backup success and test restore
- [ ] Check table bloat — schedule VACUUM where needed
- [ ] Review connection count trends
- [ ] Check disk space trajectory
- [ ] Review replication lag
- [ ] Update table statistics: `ANALYZE;`

---

## Phase 11 — Database Comparison Quick Reference

| Feature | PostgreSQL | MySQL (InnoDB) | SQLite |
|---------|-----------|----------------|--------|
| Best for | Complex queries, extensions | Web apps, read-heavy | Embedded, dev, small apps |
| Max size | Unlimited (practical) | Unlimited (practical) | 281 TB (practical ~1TB) |
| JSON support | JSONB (indexable, fast) | JSON (limited indexing) | JSON1 extension |
| Full-text search | Built-in (tsvector) | Built-in (FULLTEXT) | FTS5 extension |
| Window functions | Full support | Full support (8.0+) | Full support (3.25+) |
| CTEs | Recursive + materialized | Recursive (8.0+) | Recursive (3.8+) |
| Partitioning | Declarative + list/range/hash | Range/list/hash/key | None |
| Row-level security | Yes | No (use views) | No |
| Replication | Streaming + logical | Binary log | None (use Litestream) |
| Connection model | Process per connection | Thread per connection | In-process |

---

## Quality Scoring Rubric (0-100)

| Dimension | Weight | 0 (Poor) | 5 (Good) | 10 (Excellent) |
|-----------|--------|----------|----------|-----------------|
| Schema Design | 20% | No normalization, no constraints | 3NF, FKs, proper types | Optimal normal form, all constraints, audit fields |
| Indexing | 15% | No indexes beyond PK | Indexes on FKs and common queries | Covering indexes, partials, no unused indexes |
| Query Quality | 20% | SELECT *, N+1, no EXPLAIN | Specific columns, JOINs, basic optimization | Keyset pagination, window functions, optimized plans |
| Migration Safety | 10% | Raw DDL, no rollback | Versioned files, up/down | Zero-downtime, batched backfills, concurrent indexes |
| Security | 15% | Superuser access, no audit | Least privilege, parameterized queries | RLS, encryption, audit triggers, regular access review |
| Monitoring | 10% | No monitoring | Basic alerts on connections/disk | Full dashboard, slow query analysis, proactive tuning |
| Backup/Recovery | 10% | No backups | Daily dumps | PITR, tested restores, offsite copies |

**Score interpretation:** <40 = Critical risk | 40-60 = Needs work | 60-80 = Solid | 80-90 = Professional | 90+ = Expert

---

## Natural Language Commands

- "Design a schema for [domain]" → Phase 1 full design process
- "Optimize this query: [SQL]" → EXPLAIN analysis + rewrite
- "Add an index for [query pattern]" → Index type selection + creation
- "Write a migration to [change]" → Safe migration with rollback
- "Audit this database" → Full scoring across all dimensions
- "Set up monitoring for [database]" → Phase 5 dashboard queries
- "Review this schema" → Naming, types, constraints, relationships check
- "Help me with [PostgreSQL/MySQL/SQLite] [topic]" → Platform-specific guidance
- "Troubleshoot slow queries" → pg_stat_statements analysis + top fixes
- "Plan a backup strategy" → Phase 6 decision framework
- "Make this table multi-tenant" → RLS + tenant_id pattern
- "Convert this to use partitioning" → Phase 9 time-series pattern
