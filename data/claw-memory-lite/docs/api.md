# API Reference

Technical documentation for claw-memory-lite database schema and functions.

---

## Database Schema

### Table: `long_term_memory`

Stores all extracted long-term memories.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| `id` | INTEGER | PRIMARY KEY, AUTOINCREMENT | Unique record ID |
| `category` | TEXT | NOT NULL | Category (System/Environment/Skill/Project/Comm/Security) |
| `content` | TEXT | NOT NULL | Memory content/fact |
| `keywords` | TEXT | - | Space-separated keywords for search |
| `source_file` | TEXT | - | Source daily memory filename |
| `created_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation time |
| `updated_at` | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Last update time |

### Indexes

```sql
-- Category index (fast filtering)
CREATE INDEX idx_category ON long_term_memory(category);

-- Keyword index (fast search)
CREATE INDEX idx_keywords ON long_term_memory(keywords);

-- Timestamp index (fast ordering)
CREATE INDEX idx_created_at ON long_term_memory(created_at);
```

---

## SQL Queries

### Get All Records by Category

```sql
SELECT category, content, created_at 
FROM long_term_memory 
WHERE category = 'Skill' 
ORDER BY created_at DESC;
```

### Search by Keyword

```sql
SELECT category, content, created_at 
FROM long_term_memory 
WHERE content LIKE '%backup%' 
   OR keywords LIKE '%backup%' 
ORDER BY created_at DESC;
```

### Combined Query

```sql
SELECT category, content, created_at 
FROM long_term_memory 
WHERE category = 'Environment' 
  AND (content LIKE '%uv%' OR keywords LIKE '%uv%') 
ORDER BY created_at DESC;
```

### Get Statistics

```sql
-- Total records
SELECT COUNT(*) FROM long_term_memory;

-- Records by category
SELECT category, COUNT(*) as count 
FROM long_term_memory 
GROUP BY category 
ORDER BY count DESC;

-- Date range
SELECT MIN(created_at), MAX(created_at) FROM long_term_memory;
```

### Get Recent Records

```sql
SELECT category, content, created_at 
FROM long_term_memory 
ORDER BY created_at DESC 
LIMIT 10;
```

---

## Python Functions

### Initialize Database

```python
import sqlite3
import os

DB_PATH = "/home/node/.openclaw/database/insight.db"

def init_db():
    """Create database schema if not exists."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS long_term_memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT NOT NULL,
            content TEXT NOT NULL,
            keywords TEXT,
            source_file TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON long_term_memory(category)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_keywords ON long_term_memory(keywords)")
    
    conn.commit()
    conn.close()
```

### Insert Record

```python
def insert_memory(category, content, keywords="", source_file=""):
    """Insert a new memory record."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO long_term_memory (category, content, keywords, source_file)
        VALUES (?, ?, ?, ?)
    """, (category, content, keywords, source_file))
    
    conn.commit()
    last_id = cursor.lastrowid
    conn.close()
    
    return last_id
```

### Query Records

```python
def query_memories(search_term=None, category=None, limit=None):
    """Query memory records with optional filters."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT category, content, created_at FROM long_term_memory WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if search_term:
        query += " AND (content LIKE ? OR keywords LIKE ?)"
        params.extend([f'%{search_term}%', f'%{search_term}%'])
    
    query += " ORDER BY created_at DESC"
    
    if limit:
        query += f" LIMIT {limit}"
    
    cursor.execute(query, params)
    results = cursor.fetchall()
    conn.close()
    
    return results
```

### Get Statistics

```python
def get_stats():
    """Get database statistics."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Total
    cursor.execute("SELECT COUNT(*) FROM long_term_memory")
    total = cursor.fetchone()[0]
    
    # By category
    cursor.execute("""
        SELECT category, COUNT(*) as count 
        FROM long_term_memory 
        GROUP BY category 
        ORDER BY count DESC
    """)
    by_category = cursor.fetchall()
    
    # Date range
    cursor.execute("SELECT MIN(created_at), MAX(created_at) FROM long_term_memory")
    date_range = cursor.fetchone()
    
    conn.close()
    
    return {
        "total": total,
        "by_category": dict(by_category),
        "date_range": date_range
    }
```

### Delete Record

```python
def delete_memory(record_id):
    """Delete a memory record by ID."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM long_term_memory WHERE id = ?", (record_id,))
    
    conn.commit()
    deleted = cursor.rowcount
    conn.close()
    
    return deleted > 0
```

### Export to JSON

```python
import json

def export_to_json(output_path):
    """Export all memories to JSON file."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM long_term_memory ORDER BY created_at DESC")
    columns = [desc[0] for desc in cursor.description]
    rows = cursor.fetchall()
    
    records = [dict(zip(columns, row)) for row in rows]
    
    with open(output_path, 'w') as f:
        json.dump(records, f, indent=2, default=str)
    
    conn.close()
    
    return len(records)
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CLAW_MEMORY_DB_PATH` | `/home/node/.openclaw/database/insight.db` | Database file path |
| `CLAW_MEMORY_WORKSPACE` | `/home/node/.openclaw/workspace` | Workspace root directory |

### Usage

```bash
# Custom database path
export CLAW_MEMORY_DB_PATH="/custom/path/memory.db"
python3 scripts/db_query.py backup

# Custom workspace
export CLAW_MEMORY_WORKSPACE="/custom/workspace"
python3 scripts/extract_memory.py
```

---

## Error Handling

### Database Not Found

```python
if not os.path.exists(DB_PATH):
    print(f"Error: Database not found at {DB_PATH}")
    print("Run 'python3 extract_memory.py' to initialize.")
    return []
```

### Query Errors

```python
try:
    cursor.execute(query, params)
    results = cursor.fetchall()
except sqlite3.Error as e:
    print(f"Database error: {e}")
    return []
finally:
    conn.close()
```

---

## Performance Notes

### Query Optimization

- Use `--category` filter when possible (indexed)
- Avoid leading wildcards in search: `backup%` is faster than `%backup%`
- Limit results for large datasets: add `LIMIT 100`

### Index Maintenance

```sql
-- Rebuild all indexes
REINDEX;

-- Analyze for query optimization
ANALYZE;
```

### Vacuum Database

```sql
-- Reclaim space after deletions
VACUUM;
```

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | 2026-02-18 | Initial release |

---

## Support

For issues or feature requests, open a GitHub issue at:
https://github.com/timothysong0w0/claw-memory-lite/issues
