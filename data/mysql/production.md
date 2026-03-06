# Production Configuration

## Buffer Pool

`innodb_buffer_pool_size` is the single most important setting. For dedicated DB server: 70-80% of RAM.

Too small = constant disk reads. Too large = OS swapping, which is worse.

## Connections

`max_connections` default is 151. Calculate what you need:
```
(app_servers × pool_size) + monitoring + buffer
```

Each connection uses memory. Don't set to 10000 "just in case".

`wait_timeout` (default 8 hours) kills idle connections—connection poolers may not notice the disconnect until next query.

## Slow Query Log

Enable it. Always.

```ini
slow_query_log = ON
long_query_time = 0.5  # Default 10s is way too high
log_queries_not_using_indexes = ON
```

Use `pt-query-digest` to analyze. It groups similar queries and ranks by total time.

## Schema Changes on Large Tables

`ALTER TABLE` rebuilds the table. On a 100GB table, this takes hours and locks writes.

Solutions:
- `pt-online-schema-change` (Percona)
- `gh-ost` (GitHub)
- MySQL 8.0 instant DDL (for some changes only)

Test on production-size copy first.

## Backups

`mysqldump` locks tables by default. Use `--single-transaction` for InnoDB to get consistent snapshot without locking.

Binary logs enable point-in-time recovery. Enable them:
```ini
log_bin = ON
expire_logs_days = 7
```

Test your restores. A backup you can't restore is not a backup.

## Replication Lag

Check `Seconds_Behind_Master` but don't trust it completely. It can show 0 while actually behind (if IO thread is behind but SQL thread caught up to what it has).

For critical reads after write, read from primary.
