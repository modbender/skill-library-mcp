# Query Optimization

## EXPLAIN First

Never ship a query without checking EXPLAIN. Key columns:
- `type`: ALL = full scan (bad), range = index range (ok), ref = index lookup (good), const = single row (best)
- `rows`: estimated rows examined—multiply across joins
- `Extra`: "Using filesort" = sorting without index, "Using temporary" = temp table

## EXPLAIN ANALYZE

Only in MySQL 8.0.18+. Shows actual execution time, not just estimates. Use it.

## Pagination That Scales

`LIMIT 10000, 10` still reads 10010 rows then throws away 10000. Offset pagination breaks at scale.

Cursor pagination:
```sql
WHERE id > :last_seen_id ORDER BY id LIMIT 10
```
Reads exactly 10 rows. Works at any depth.

## COUNT(*) on InnoDB

There's no magic row counter. `SELECT COUNT(*) FROM big_table` scans the entire table or an index.

For dashboards, pre-aggregate counts. For "is there any?", use `SELECT 1 ... LIMIT 1`.

## JOINs

MySQL uses nested loop joins. The smaller table should drive the join—optimizer usually gets this right.

Implicit vs explicit JOIN: Always use `JOIN ... ON`, never comma joins with WHERE. Same result, explicit is clearer and less error-prone.

## Subqueries vs JOINs

Modern MySQL (5.6+) optimizes both well. Use what's clearer. But know that correlated subqueries run once per outer row—can be slow.

`EXISTS` stops at first match, often faster than `IN` with large result sets.

## Date Ranges

```sql
-- Bad: function prevents index
WHERE DATE(created_at) = '2024-01-15'

-- Good: range uses index
WHERE created_at >= '2024-01-15' AND created_at < '2024-01-16'
```
