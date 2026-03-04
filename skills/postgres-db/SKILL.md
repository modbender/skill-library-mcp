---
name: postgres-db
description: PostgreSQL 数据库操作技能。用于执行SQL查询、表管理、备份恢复、性能监控等数据库操作。触发条件：用户提到 PostgreSQL、postgres、数据库查询、SQL查询、表结构、数据库备份等。
---

# PostgreSQL Database Skill

## Overview

This skill provides comprehensive PostgreSQL database operations including query execution, schema management, backup/restore, and performance monitoring.

## Capabilities

### 1. SQL Query Execution (`scripts/query.py`)
Execute SQL queries against PostgreSQL databases with support for:
- SELECT queries with result formatting
- INSERT/UPDATE/DELETE operations
- Transaction support
- Query result export (JSON, CSV)

### 2. Schema Export (`scripts/schema_export.py`)
Export database schema information:
- Table structures (columns, types, constraints)
- Indexes and foreign keys
- Views and triggers
- Export to JSON/Markdown format

### 3. Database Backup (`scripts/backup.py`)
Database backup and restore operations:
- Full database backup using pg_dump
- Table-specific backup
- Point-in-time recovery support
- Backup rotation management

### 4. Performance Monitoring
Monitor database performance:
- Query execution plans (EXPLAIN ANALYZE)
- Index usage statistics
- Table size and row counts
- Connection pool status

## Usage

### Query Database
```bash
python scripts/query.py --dbname mydb --query "SELECT * FROM users LIMIT 10"
```

### Export Schema
```bash
python scripts/schema_export.py --dbname mydb --output schema.json
```

### Backup Database
```bash
python scripts/backup.py --dbname mydb --backup-dir /backups
```

## Requirements

- PostgreSQL client tools (psql, pg_dump)
- Python 3.7+
- psycopg2 or asyncpg library

## Configuration

Set environment variables:
- `PGHOST` - Database host
- `PGPORT` - Database port (default: 5432)
- `PGDATABASE` - Database name
- `PGUSER` - Database user
- `PGPASSWORD` - Database password
