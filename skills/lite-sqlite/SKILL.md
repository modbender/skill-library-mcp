---
name: lite-sqlite
description: Fast lightweight local SQLite database for OpenClaw agents with minimal RAM and storage usage. Use when creating or managing SQLite databases for storing agent data efficiently. Ideal for local data persistence quick agent data storage low-memory databases small-scale applications and agent memo and caching storage.
---

# Lite SQLite - Lightweight Local Database

Ultra-lightweight SQLite database management optimized for OpenClaw agents with minimal RAM (~2-5MB) and storage overhead.

## Why SQLite?

✅ **Zero setup** - No server, no configuration, file-based
✅ **Minimal RAM** - 2-5MB typical usage
✅ **Fast** - Millions of queries/second
✅ **Portable** - Single .db file
✅ **Reliable** - ACID compliant, crash-proof
✅ **Cross-platform** - Works everywhere Python works

## Core Features

- In-memory mode for temporary data (even faster!)
- WAL mode for concurrent access
- Connection pooling
- Automatic schema migration
- Built-in backup/restore
- Query optimization hints

## Quick Start

### Basic Database Operations

```python
from sqlite_connector import SQLiteDB

# Create database (auto-wal mode enabled)
db = SQLiteDB("agent_data.db")

# Create table
db.create_table("memos", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "title": "TEXT NOT NULL",
    "content": "TEXT",
    "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
    "tags": "TEXT"
})

# Insert data
db.insert("memos", [title="First memo", content="Hello world", tags="test"])

# Query data
results = db.query("SELECT * FROM memos WHERE tags = ?", ("test",))

# Update data
db.update("memos", "id = ?", [content="Updated content"], (1,))

# Delete data
db.delete("memos", "id = ?", (1,))

# Close connection
db.close()
```

### In-Memory Database (Fastest)

```python
# Fastest mode - RAM only, no disk I/O
db = SQLiteDB(":memory:")

# Perfect for temporary operations
db.create_table("temp", {...})

# Data persists only during session
# Use for caching, computations, temporary storage
```

---

## Performance Optimization

### Essential Settings

```python
import sqlite3

# WAL mode (Write-Ahead Logging) - 3-4x faster
conn = sqlite3.connect("agent_data.db")
conn.execute("PRAGMA journal_mode=WAL")

# Sync OFF (faster writes, crash-safe with proper shutdown)
conn.execute("PRAGMA synchronous=NORMAL")

# Memory optimization
conn.execute("PRAGMA cache_size=-64000")  # 64MB cache
conn.execute("PRAGMA page_size=4096")

# Temp store in RAM
conn.execute("PRAGMA temp_store=MEMORY")
```

### Query Optimization

```python
# Use indexes for frequent queries
db.create_index("memos", "tags")
db.create_index("memos", "created_at")

# Use prepared statements (automatic in our wrapper)
db.query("SELECT * FROM memos WHERE id = ?", (id,))

# Batch inserts for large datasets
db.batch_insert("memos", rows_data)
```

---

## Predefined Schemas

### Agent Memo Schema (Memory Store)

```python
db.create_table("agent_memos", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "agent_id": "TEXT NOT NULL",           # Which agent created it
    "key": "TEXT NOT NULL",               # Lookup key
    "value": "TEXT",                      # Stored value
    "priority": "INTEGER DEFAULT 0",       # For retrieval ordering
    "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
    "expires_at": "TEXT"                  # Optional TTL
})

# Create indexes
db.create_index("agent_memos", "agent_id")
db.create_index("agent_memos", "key")
db.create_index("agent_memos", "expires_at")
```

### Session Log Schema

```python
db.create_table("session_logs", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "session_id": "TEXT NOT NULL",
    "agent": "TEXT NOT NULL",
    "message": "TEXT",
    "metadata": "TEXT",                   # JSON
    "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP"
})

db.create_index("session_logs", "session_id")
db.create_index("session_logs", "created_at")
```

### Cache Schema (TTL-based)

```python
db.create_table("cache", {
    "id": "INTEGER PRIMARY KEY AUTOINCREMENT",
    "key": "TEXT UNIQUE NOT NULL",
    "value": "BLOB",                      # Supports binary data
    "created_at": "TEXT DEFAULT CURRENT_TIMESTAMP",
    "expires_at": "TEXT NOT NULL"
})

# Auto-cleanup expired entries
db.query("DELETE FROM cache WHERE expires_at < ?", (datetime.now().isoformat(),))

db.create_index("cache", "key")
db.create_index("cache", "expires_at")
```

---

## Advanced Features

### Connection Pooling

```python
from sqlite_connector import ConnectionPool

# Pool of connections for concurrent access
pool = ConnectionPool("agent_data.db", max_connections=5)

# Get connection
conn = pool.get_connection()
# Use conn...
pool.release_connection(conn)
```

### Automatic Backup

```python
# Backup database
db.backup("agent_data_backup.db")

# Automatic daily backup
db.auto_backup("backups/", "daily")
```

### Schema Migration

```python
# Add column if not exists
db.add_column("memos", "updated_at", "TEXT DEFAULT CURRENT_TIMESTAMP")

# Migrate data
db.migrate("memos", {
    "old_column": "new_column"
})
```

---

## Performance Benchmarks

### Typical Performance

| Operation | Rows | Time (In-Memory) | Time (Disk) |
|-----------|------|------------------|-------------|
| Insert | 10,000 | 0.05s | 0.3s |
| Select (indexed) | 10,000 | 0.001s | 0.01s |
| Select (full scan) | 10,000 | 0.05s | 0.5s |
| Update | 1,000 | 0.01s | 0.1s |
| Delete | 1,000 | 0.01s | 0.1s |

### Memory Usage

- Base Memory: 2-5MB
- With 100K rows: ~10-15MB
- With 1M rows: ~50-100MB
- In-memory mode: Same as data size + overhead

---

## Best Practices for OpenClaw Agents

### 1. Choose the Right Mode

```python
# Use :memory: for temporary operations
temp_db = SQLiteDB(":memory:")

# Use file DB for persistent storage
persist_db = SQLiteDB("agent_storage.db")
```

### 2. Use Proper Indexes

```python
# Always index columns used in WHERE clauses
db.create_index("table", "column_name")

# Index multiple columns for composite queries
db.create_index("table", "col1, col2")
```

### 3. Batch Operations

```python
# Instead of individual inserts:
for row in rows:
    db.insert("table", row)  # Slow!

# Use batch insert:
db.batch_insert("table", rows)  # Fast!
```

### 4. Use TTL for Expiring Data

```python
# Auto-cleanup old data
db.cleanup_expired("cache", "expires_at")
db.cleanup_old("logs", "created_at", days=7)
```

### 5. Compact Database Periodically

```python
# Reclaim space after many deletes
db.vacuum()  # Should be run during downtime
```

---

## DuckDB Alternative (Analytics)

For analytical queries (aggregations, joins on large datasets), consider DuckDB:

```python
import duckdb

conn = duckdb.connect(":memory:")

# Faster than SQLite for complex analytics
conn.execute("""
    SELECT COUNT(*) as rows,
           AVG(value) as avg_value
    FROM large_table
""").fetchall()
```

**When to use DuckDB:**
- Analytics on large datasets (>100M rows)
- Complex aggregations and joins
- Columnar data operations
- Statistical analysis

**When to use SQLite:**
- Transactional operations
- Small to medium datasets (<100M rows)
- Point queries and updates
- General-purpose storage

---

## Common Patterns

### 1. Memo Storage

```python
def save_memo(db, agent_id, key, value, ttl_hours=24):
    expires_at = (datetime.now() + timedelta(hours=ttl_hours)).isoformat()
    db.insert("agent_memos", {
        "agent_id": agent_id,
        "key": key,
        "value": json.dumps(value),
        "expires_at": expires_at
    })
```

### 2. Session Persistence

```python
def save_session(db, session_id, agent, message, metadata=None):
    db.insert("session_logs", {
        "session_id": session_id,
        "agent": agent,
        "message": message,
        "metadata": json.dumps(metadata) if metadata else None
    })
```

### 3. Caching Layer

```python
def cache_get(db, key):
    if expired_key := db.query_one(
        "SELECT value FROM cache WHERE key = ? AND expires_at > ?",
        (key, datetime.now().isoformat())
    ):
        return json.loads(expired_key)
    return None

def cache_set(db, key, value, ttl_seconds=3600):
    expires_at = (datetime.now() + timedelta(seconds=ttl_seconds)).isoformat()
    db.insert_or_replace("cache", {
        "key": key,
        "value": json.dumps(value),
        "expires_at": expires_at
    })
```

---

## Error Handling

```python
try:
    db.insert("metrics", {...})
except sqlite3.IntegrityError:
    # Duplicate key violation
    pass
except sqlite3.OperationalError:
    # Table doesn't exist or database locked
    pass
```

---

## Size Optimization Tips

### Reduce Storage

1. **Use appropriate data types:**
   - INTEGER instead of TEXT for numbers
   - REAL instead of TEXT for floats
   - Use CHECK constraints for validation

2. **Normalize data:**
   - Store JSON as TEXT
   - Use TEXT for variable-length strings
   - Avoid storing redundant data

3. **Vacuum regularly:**
   ```python
   db.vacuum()  # Reclaims space after deletes
   ```

4. **Use WAL instead of journal:**
   ```python
   conn.execute("PRAGMA journal_mode=WAL")
   ```

---

## Migration from Other Stores

### From JSON Files

```python
# Load JSON into SQLite
import json

with open("data.json") as f:
    data = json.load(f)

db.create_table("json_data", {key: "TEXT" for key in data[0].keys()})
db.batch_insert("json_data", data)
```

### From CSV Files

```python
import pandas as pd

df = pd.read_csv("data.csv")
df.to_sql("csv_data", conn, if_exists="replace", index=False)
```

---

## Troubleshooting

### Database Locked Error

```python
# Use WAL mode for concurrent access
conn.execute("PRAGMA journal_mode=WAL")

# Or use connection pool
pool = ConnectionPool("db.db", timeout=5.0)
```

### Slow Queries

```python
# Check query plan
plan = conn.execute("EXPLAIN QUERY PLAN SELECT * FROM ...").fetchall()

# Add indexes
db.create_index("table", "column")

# Use ANALYZE
conn.execute("ANALYZE")
```

### Large Database Size

```python
# Check size info
size_info = conn.execute("PRAGMA page_count, page_size").fetchone()
print(f"Size: {(page_count * page_size) / (1024*1024):.2f} MB")

# Vacuum to reclaim space
db.vacuum()
```

---

## CLI Tool

The bundled `sqlite_cli.py` provides command-line access:

```bash
# Create database
python scripts/sqlite_cli.py create agent_data.db

# Add table
python scripts/sqlite_cli.py create-table agent_memos -c id:INTEGER:P -c title:TEXT -c content:TEXT

# Insert data
python scripts/sqlite_cli.py insert agent_memos '{"title": "Test", "content": "Hello"}'

# Query data
python scripts/sqlite_cli.py query "SELECT * FROM agent_memos"

# Optimize
python scripts/sqlite_cli.py optimize agent_data.db
```

---

## Resources

- **SQLite Documentation:** https://www.sqlite.org/docs.html
- **Python sqlite3:** https://docs.python.org/3/library/sqlite3.html
- **DuckDB:** https://duckdb.org/docs/
- **Performance:** https://www.sqlite.org/optoverview.html
