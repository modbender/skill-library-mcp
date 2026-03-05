# Query Patterns — SQL

## Pagination

### Offset-based (simple but slow for large offsets)

```sql
SELECT * FROM posts ORDER BY created_at DESC LIMIT 20 OFFSET 100;
```

### Keyset pagination (efficient for any page)

```sql
-- First page
SELECT * FROM posts ORDER BY created_at DESC, id DESC LIMIT 20;

-- Next page (using last row's values)
SELECT * FROM posts 
WHERE (created_at, id) < ('2026-01-15 10:00:00', 12345)
ORDER BY created_at DESC, id DESC LIMIT 20;
```

---

## Deduplication

### Keep first occurrence

```sql
-- PostgreSQL: DISTINCT ON
SELECT DISTINCT ON (user_id) * FROM orders ORDER BY user_id, created_at;

-- Standard SQL
DELETE FROM orders a
USING orders b
WHERE a.id < b.id AND a.email = b.email;

-- Find duplicates
SELECT email, COUNT(*) FROM users GROUP BY email HAVING COUNT(*) > 1;
```

---

## Conditional Aggregation

```sql
SELECT 
    COUNT(*) AS total,
    COUNT(*) FILTER (WHERE status = 'paid') AS paid,
    COUNT(*) FILTER (WHERE status = 'pending') AS pending,
    SUM(total) FILTER (WHERE status = 'paid') AS revenue
FROM orders;

-- MySQL syntax (no FILTER)
SELECT 
    COUNT(*) AS total,
    SUM(CASE WHEN status = 'paid' THEN 1 ELSE 0 END) AS paid,
    SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending
FROM orders;
```

---

## Gap Analysis (Missing IDs)

```sql
WITH all_ids AS (
    SELECT generate_series(1, (SELECT MAX(id) FROM products)) AS id
)
SELECT a.id FROM all_ids a
LEFT JOIN products p ON a.id = p.id
WHERE p.id IS NULL;
```

---

## Running Totals and Differences

```sql
-- Cumulative sum
SELECT date, amount,
       SUM(amount) OVER (ORDER BY date) AS running_total
FROM transactions;

-- Day-over-day change
SELECT date, amount,
       amount - LAG(amount) OVER (ORDER BY date) AS change
FROM daily_metrics;

-- Percentage of total
SELECT category, amount,
       ROUND(amount * 100.0 / SUM(amount) OVER (), 2) AS pct
FROM category_totals;
```

---

## Pivoting Data

### PostgreSQL (crosstab)

```sql
CREATE EXTENSION IF NOT EXISTS tablefunc;

SELECT * FROM crosstab(
    'SELECT month, category, total FROM sales ORDER BY 1, 2',
    'SELECT DISTINCT category FROM sales ORDER BY 1'
) AS ct(month TEXT, electronics NUMERIC, clothing NUMERIC, food NUMERIC);
```

### Standard SQL (CASE)

```sql
SELECT month,
       SUM(CASE WHEN category = 'electronics' THEN total END) AS electronics,
       SUM(CASE WHEN category = 'clothing' THEN total END) AS clothing,
       SUM(CASE WHEN category = 'food' THEN total END) AS food
FROM sales
GROUP BY month;
```

---

## Unpivoting Data

```sql
-- PostgreSQL
SELECT id, key, value
FROM metrics,
LATERAL (VALUES 
    ('metric_a', metric_a),
    ('metric_b', metric_b),
    ('metric_c', metric_c)
) AS t(key, value);

-- SQL Server
SELECT id, metric_name, metric_value
FROM metrics
UNPIVOT (metric_value FOR metric_name IN (metric_a, metric_b, metric_c)) AS u;
```

---

## Hierarchical Data

### Adjacency List (simple)

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    parent_id INTEGER REFERENCES categories(id)
);

-- Get all ancestors
WITH RECURSIVE ancestors AS (
    SELECT * FROM categories WHERE id = 5
    UNION ALL
    SELECT c.* FROM categories c
    JOIN ancestors a ON c.id = a.parent_id
)
SELECT * FROM ancestors;

-- Get all descendants
WITH RECURSIVE descendants AS (
    SELECT * FROM categories WHERE id = 1
    UNION ALL
    SELECT c.* FROM categories c
    JOIN descendants d ON c.parent_id = d.id
)
SELECT * FROM descendants;
```

### Materialized Path (faster reads)

```sql
CREATE TABLE categories (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    path TEXT NOT NULL  -- e.g., '1/3/7/15'
);

-- All descendants of category 3
SELECT * FROM categories WHERE path LIKE '1/3/%';

-- All ancestors of category 15
SELECT * FROM categories 
WHERE '1/3/7/15' LIKE path || '/%' OR id = ANY(string_to_array('1/3/7/15', '/')::int[]);
```

---

## Temporal Queries

### Date ranges that overlap

```sql
SELECT * FROM bookings
WHERE daterange(start_date, end_date, '[]') && daterange('2026-01-01', '2026-01-31', '[]');
```

### Date series generation

```sql
-- PostgreSQL
SELECT generate_series('2026-01-01'::date, '2026-12-31'::date, '1 day')::date AS date;

-- Fill missing dates
SELECT d.date, COALESCE(s.revenue, 0) AS revenue
FROM generate_series('2026-01-01'::date, '2026-01-31'::date, '1 day') AS d(date)
LEFT JOIN daily_sales s ON s.date = d.date;
```

---

## Sampling

```sql
-- PostgreSQL: truly random sample (slow)
SELECT * FROM large_table ORDER BY random() LIMIT 100;

-- PostgreSQL: block-level sampling (fast, approximate)
SELECT * FROM large_table TABLESAMPLE SYSTEM(1);  -- ~1% of rows

-- MySQL
SELECT * FROM large_table ORDER BY RAND() LIMIT 100;
```

---

## Locking

```sql
-- Row-level lock (prevent concurrent updates)
SELECT * FROM inventory WHERE product_id = 5 FOR UPDATE;

-- Skip locked rows (for job queues)
SELECT * FROM jobs WHERE status = 'pending' 
ORDER BY created_at LIMIT 1 FOR UPDATE SKIP LOCKED;
```

---

## Bulk Operations

```sql
-- Bulk insert
INSERT INTO users (email, name) VALUES
    ('a@example.com', 'Alice'),
    ('b@example.com', 'Bob'),
    ('c@example.com', 'Carol');

-- Bulk upsert (PostgreSQL)
INSERT INTO users (email, name) VALUES
    ('a@example.com', 'Alice Updated'),
    ('d@example.com', 'Dave')
ON CONFLICT (email) DO UPDATE SET name = EXCLUDED.name;

-- Bulk delete with subquery
DELETE FROM orders WHERE user_id IN (
    SELECT id FROM users WHERE deleted_at IS NOT NULL
);
```
