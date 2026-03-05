# Operations — SQL

## Migrations

### File Convention

```
migrations/
├── 001_create_users.sql
├── 002_create_orders.sql
├── 003_add_users_phone.sql
├── 004_add_orders_index.sql
```

### Migration Tracking Table

```sql
CREATE TABLE IF NOT EXISTS schema_migrations (
    version TEXT PRIMARY KEY,
    applied_at TIMESTAMPTZ DEFAULT NOW()
);
```

### Migration Script

For production, use established tools:
- **PostgreSQL**: golang-migrate, Flyway, sqitch
- **MySQL**: Flyway, Liquibase
- **SQLite**: golang-migrate, custom scripts
- **Any**: Alembic (Python), Prisma Migrate, TypeORM

These tools handle edge cases (transactions, rollbacks, concurrent runs) that simple scripts miss.

### Safe Schema Changes

```sql
-- Add column (safe, allows NULL)
ALTER TABLE users ADD COLUMN phone TEXT;

-- Add NOT NULL column (requires default or backfill)
ALTER TABLE users ADD COLUMN status TEXT NOT NULL DEFAULT 'active';

-- Add index concurrently (PostgreSQL, doesn't block writes)
CREATE INDEX CONCURRENTLY idx_users_email ON users(email);

-- Drop column (careful, data loss)
ALTER TABLE users DROP COLUMN deprecated_field;

-- Rename table (update code first)
ALTER TABLE old_name RENAME TO new_name;
```

---

## Backup & Restore

### PostgreSQL

```bash
# Full dump (custom format, compressed)
pg_dump -Fc -h localhost -U myuser mydb > backup.dump

# Specific tables
pg_dump -Fc -t users -t orders mydb > partial.dump

# Schema only (no data)
pg_dump -Fc --schema-only mydb > schema.dump

# Restore (drop existing objects)
pg_restore -h localhost -U myuser -d mydb --clean --if-exists backup.dump

# Restore to different database
createdb newdb
pg_restore -d newdb backup.dump

# Plain SQL dump (portable)
pg_dump mydb > backup.sql
psql newdb < backup.sql

# Copy table to CSV
psql -c "\copy (SELECT * FROM users) TO 'users.csv' CSV HEADER"
```

### SQLite

```bash
# Backup (use .backup for consistency during writes)
sqlite3 mydb.sqlite ".backup backup.sqlite"

# Dump to SQL
sqlite3 mydb.sqlite .dump > backup.sql

# Restore
sqlite3 newdb.sqlite < backup.sql

# Vacuum (reclaim space, defragment)
sqlite3 mydb.sqlite "VACUUM;"
```

### MySQL

```bash
# Full dump
mysqldump -h localhost -u root -p mydb > backup.sql

# Specific tables
mysqldump -h localhost -u root -p mydb users orders > partial.sql

# Restore
mysql -h localhost -u root -p mydb < backup.sql

# Dump all databases
mysqldump --all-databases > all_databases.sql
```

### SQL Server

```bash
# Backup
sqlcmd -S localhost -U sa -Q "BACKUP DATABASE mydb TO DISK='backup.bak'"

# Restore
sqlcmd -S localhost -U sa -Q "RESTORE DATABASE mydb FROM DISK='backup.bak'"
```

---

## Maintenance

### PostgreSQL

```sql
-- Update statistics (helps query planner)
ANALYZE users;
ANALYZE;  -- all tables

-- Reclaim space from deleted rows
VACUUM users;
VACUUM FULL users;  -- more aggressive, locks table

-- Reindex (after bulk deletes or major changes)
REINDEX INDEX idx_users_email;
REINDEX TABLE users;

-- Check table sizes
SELECT relname, pg_size_pretty(pg_total_relation_size(relid))
FROM pg_stat_user_tables
ORDER BY pg_total_relation_size(relid) DESC;

-- Check index sizes
SELECT indexname, pg_size_pretty(pg_relation_size(indexrelid))
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;

-- Kill long-running queries
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'active' AND query_start < NOW() - INTERVAL '1 hour';
```

### SQLite

```sql
-- Reclaim space
VACUUM;

-- Integrity check
PRAGMA integrity_check;

-- Check database size
SELECT page_count * page_size AS size FROM pragma_page_count(), pragma_page_size();
```

### MySQL

```sql
-- Optimize table (reclaims space)
OPTIMIZE TABLE users;

-- Analyze (update statistics)
ANALYZE TABLE users;

-- Check table
CHECK TABLE users;

-- Show table sizes
SELECT table_name, ROUND(data_length/1024/1024, 2) AS size_mb
FROM information_schema.tables
WHERE table_schema = 'mydb'
ORDER BY data_length DESC;
```

---

## Monitoring

### PostgreSQL

```sql
-- Active connections
SELECT count(*) FROM pg_stat_activity;

-- Current queries
SELECT pid, query_start, state, query 
FROM pg_stat_activity 
WHERE state != 'idle';

-- Long-running queries
SELECT pid, NOW() - query_start AS duration, query
FROM pg_stat_activity
WHERE state = 'active' AND query_start < NOW() - INTERVAL '1 minute';

-- Lock waits
SELECT blocked_locks.pid AS blocked_pid,
       blocking_locks.pid AS blocking_pid,
       blocked_activity.query AS blocked_query
FROM pg_locks blocked_locks
JOIN pg_stat_activity blocked_activity ON blocked_activity.pid = blocked_locks.pid
JOIN pg_locks blocking_locks ON blocking_locks.locktype = blocked_locks.locktype
    AND blocking_locks.database = blocked_locks.database
    AND blocking_locks.relation = blocked_locks.relation
    AND blocking_locks.pid != blocked_locks.pid
JOIN pg_stat_activity blocking_activity ON blocking_activity.pid = blocking_locks.pid
WHERE NOT blocked_locks.granted;

-- Cache hit ratio (should be > 99%)
SELECT sum(blks_hit)*100/sum(blks_hit+blks_read) AS cache_hit_ratio
FROM pg_stat_database;

-- Index usage
SELECT relname, seq_scan, idx_scan,
       ROUND(idx_scan::numeric / (seq_scan + idx_scan) * 100, 2) AS idx_pct
FROM pg_stat_user_tables
WHERE seq_scan + idx_scan > 0
ORDER BY seq_scan DESC;
```

### MySQL

```sql
-- Current processes
SHOW PROCESSLIST;

-- InnoDB status
SHOW ENGINE INNODB STATUS;

-- Slow query log
SET GLOBAL slow_query_log = 'ON';
SET GLOBAL long_query_time = 1;
```

---

## Connection Pooling

### PgBouncer (PostgreSQL)

```ini
# pgbouncer.ini
[databases]
mydb = host=localhost dbname=mydb

[pgbouncer]
listen_addr = 0.0.0.0
listen_port = 6432
auth_type = md5
auth_file = /etc/pgbouncer/userlist.txt
pool_mode = transaction
max_client_conn = 1000
default_pool_size = 20
```

### Application-level

Most database libraries support connection pooling. Configure:
- `max_connections`: Total pool size
- `min_idle`: Minimum idle connections
- `max_lifetime`: Time before connection is recycled
- `connection_timeout`: Time to wait for connection

---

## Replication (PostgreSQL)

### Streaming Replication Setup

```bash
# On primary: postgresql.conf
wal_level = replica
max_wal_senders = 5
wal_keep_size = 1GB

# On primary: pg_hba.conf
host replication replicator replica_ip/32 md5

# On replica
pg_basebackup -h primary_ip -U replicator -D /var/lib/postgresql/data -P -R
```

### Check Replication Lag

```sql
-- On primary
SELECT client_addr, state, sent_lsn, write_lsn, flush_lsn, replay_lsn
FROM pg_stat_replication;

-- On replica
SELECT NOW() - pg_last_xact_replay_timestamp() AS replication_lag;
```
