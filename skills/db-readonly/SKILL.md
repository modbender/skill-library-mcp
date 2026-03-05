---
name: db-readonly
description: Run safe read-only queries against MySQL or PostgreSQL for data inspection, reporting, and troubleshooting. Use when the user asks to read tables, inspect schema, count rows, sample data, or export query results without modifying data.
---

# db-readonly

Use this skill for database read tasks only.

## What this skill does

- Connect to **PostgreSQL** or **MySQL** using connection env vars
- Execute **SELECT / WITH / EXPLAIN** queries only
- Optionally save output to CSV/TSV/JSON
- Block risky SQL (`INSERT`, `UPDATE`, `DELETE`, `DROP`, `ALTER`, etc.)

## Connection env vars

### PostgreSQL

- `PGHOST`
- `PGPORT` (optional, default 5432)
- `PGDATABASE`
- `PGUSER`
- `PGPASSWORD`

### MySQL

- `MYSQL_HOST`
- `MYSQL_PORT` (optional, default 3306)
- `MYSQL_DATABASE`
- `MYSQL_USER`
- `MYSQL_PASSWORD`

## Run

Use script:

- `scripts/db_readonly.sh postgres "SELECT now();"`
- `scripts/db_readonly.sh mysql "SELECT NOW();"`

Export example:

- `scripts/db_readonly.sh postgres "SELECT * FROM users LIMIT 100" --format csv --out /tmp/users.csv`

## Safety rules

1. Refuse non-read SQL.
2. Prefer `LIMIT` for exploratory queries.
3. When user asks for updates/deletes/schema changes, ask explicit confirmation and do not run via this skill.
4. Avoid printing secrets from env vars.

## Reference

- Query cookbook: `references/query-cookbook.md`
