# Query Cookbook (Read-Only)

## PostgreSQL / MySQL common

### Show tables

- Postgres: `SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema NOT IN ('pg_catalog','information_schema') ORDER BY 1,2;`
- MySQL: `SELECT table_schema, table_name FROM information_schema.tables WHERE table_schema = DATABASE() ORDER BY 1,2;`

### Count rows

`SELECT COUNT(*) FROM your_table;`

### Sample rows

`SELECT * FROM your_table ORDER BY 1 DESC LIMIT 20;`

### Top values

`SELECT status, COUNT(*) cnt FROM your_table GROUP BY status ORDER BY cnt DESC LIMIT 20;`

### Date trend

`SELECT DATE(created_at) d, COUNT(*) cnt FROM your_table GROUP BY DATE(created_at) ORDER BY d DESC LIMIT 30;`

## Safety checklist

1. Start with `LIMIT`.
2. Avoid `SELECT *` on huge tables.
3. Use indexed columns in filters when possible.
4. Never run write SQL in this skill.
