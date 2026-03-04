---
name: MariaDB
description: Write efficient MariaDB queries with proper indexing, temporal tables, and clustering.
metadata: {"clawdbot":{"emoji":"🦭","requires":{"bins":["mariadb"]},"os":["linux","darwin","win32"]}}
---

## Character Set

- Always use `utf8mb4` for tables and connections—full Unicode including emoji
- `utf8mb4_unicode_ci` for proper linguistic sorting, `utf8mb4_bin` for byte comparison
- Set connection charset: `SET NAMES utf8mb4` or in connection string
- Collation mismatch in JOINs forces conversion—kills index usage

## Indexing

- TEXT/BLOB columns need prefix length: `INDEX (description(100))`
- Composite index order matters—`(a, b)` serves `WHERE a=?` but not `WHERE b=?`
- Foreign keys auto-create index on child table—but verify with `SHOW INDEX`
- Covering indexes: include all SELECT columns to avoid table lookup

## Sequences

- `CREATE SEQUENCE seq_name` for guaranteed unique IDs across tables
- `NEXT VALUE FOR seq_name` to get next—survives transaction rollback
- Better than auto-increment when you need ID before insert
- `SETVAL(seq_name, n)` to reset—useful for migrations

## System Versioning (Temporal Tables)

- `ALTER TABLE t ADD SYSTEM VERSIONING` to track all historical changes
- `FOR SYSTEM_TIME AS OF '2024-01-01 00:00:00'` queries past state
- `FOR SYSTEM_TIME BETWEEN start AND end` for change history
- Invisible columns `row_start` and `row_end` store validity period

## JSON Handling

- `JSON_VALUE(col, '$.key')` extracts scalar, returns NULL if not found
- `JSON_QUERY(col, '$.obj')` extracts object/array with quotes preserved
- `JSON_TABLE()` converts JSON array to rows—powerful for unnesting
- `JSON_VALID()` before insert if column isn't strictly typed

## Galera Cluster

- All nodes writable—but same-row conflicts cause rollback
- `wsrep_sync_wait = 1` before critical reads—ensures node is synced
- Keep transactions small—large transactions increase conflict probability
- `wsrep_cluster_size` should be odd number—avoids split-brain

## Window Functions

- `ROW_NUMBER() OVER (PARTITION BY x ORDER BY y)` for ranking within groups
- `LAG(col, 1) OVER (ORDER BY date)` for previous row value
- `SUM(amount) OVER (ORDER BY date ROWS UNBOUNDED PRECEDING)` for running total
- CTEs with `WITH cte AS (...)` for readable complex queries

## Thread Pool

- Enable with `thread_handling=pool-of-threads`—better than thread-per-connection
- `thread_pool_size` = CPU cores for CPU-bound, higher for I/O-bound
- Reduces context switching with many concurrent connections
- Monitor with `SHOW STATUS LIKE 'Threadpool%'`

## Storage Engines

- InnoDB default—ACID transactions, row locking, crash recovery
- Aria for temporary tables—crash-safe replacement for MyISAM
- MEMORY for caches—data lost on restart, but fast
- Check engine: `SHOW TABLE STATUS WHERE Name='table'`

## Locking

- `SELECT ... FOR UPDATE` locks rows until commit
- `LOCK TABLES t WRITE` for DDL-like exclusive access—blocks all other sessions
- Deadlock detection automatic—one transaction rolled back; must retry
- `innodb_lock_wait_timeout` default 50s—lower for interactive apps

## Query Optimization

- `EXPLAIN ANALYZE` for actual execution times (10.1+)
- `optimizer_trace` for deep dive: `SET optimizer_trace='enabled=on'`
- `FORCE INDEX (idx)` when optimizer chooses wrong index
- `STRAIGHT_JOIN` to force join order—last resort

## Backup and Recovery

- `mariadb-dump --single-transaction` for consistent backup without locks
- `mariadb-backup` for hot InnoDB backup—incremental supported
- Binary logs for point-in-time recovery: `mysqlbinlog binlog.000001 | mariadb`
- Test restores regularly—backups that can't restore aren't backups

## Common Errors

- "Too many connections"—increase `max_connections` or use connection pool
- "Lock wait timeout exceeded"—find blocking query with `SHOW ENGINE INNODB STATUS`
- "Row size too large"—TEXT/BLOB stored off-page, but row pointers have limits
- "Duplicate entry for key"—check unique constraints, use `ON DUPLICATE KEY UPDATE`
