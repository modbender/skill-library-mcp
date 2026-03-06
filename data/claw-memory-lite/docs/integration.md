# Integration Guide

How to integrate claw-memory-lite with your OpenClaw setup.

---

## Automated Extraction

### Option 1: Heartbeat Integration

Add to your `HEARTBEAT.md`:

```markdown
### 🧠 Memory Extraction (Daily)
```bash
python3 /home/node/.openclaw/workspace/scripts/extract_memory.py
```
```

**Pros**: Simple, runs during regular heartbeat checks
**Cons**: Depends on heartbeat frequency

### Option 2: Cron Job

Add to system crontab:

```bash
# Edit crontab
crontab -e

# Daily extraction at 3 AM UTC
0 3 * * * cd /home/node/.openclaw/workspace && python3 scripts/extract_memory.py >> logs/memory_extraction.log 2>&1
```

**Pros**: Precise timing, independent of OpenClaw
**Cons**: Requires system access

### Option 3: OpenClaw Cron Tool

Use OpenClaw's built-in cron:

```python
# Via OpenClaw cron tool (if available)
{
  "name": "Daily Memory Extraction",
  "schedule": {"kind": "cron", "expr": "0 3 * * *"},
  "payload": {
    "kind": "systemEvent",
    "text": "python3 /home/node/.openclaw/workspace/scripts/extract_memory.py"
  }
}
```

---

## Query Integration

### In Your Skills

Import and use the query function:

```python
import sqlite3
import os

DB_PATH = "/home/node/.openclaw/database/insight.db"

def query_memory(keyword, category=None):
    """Query long-term memory from within a skill."""
    if not os.path.exists(DB_PATH):
        return []
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    query = "SELECT content FROM long_term_memory WHERE 1=1"
    params = []
    
    if category:
        query += " AND category = ?"
        params.append(category)
    
    if keyword:
        query += " AND content LIKE ?"
        params.append(f'%{keyword}%')
    
    cursor.execute(query, params)
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return results
```

### As OpenClaw Tool

Create a wrapper script for OpenClaw tool system:

```bash
#!/bin/bash
# tools/memory_query.sh
python3 /home/node/.openclaw/workspace/scripts/db_query.py "$@"
```

---

## MEMORY.md Synchronization

The extraction script automatically updates `MEMORY.md` with:
- New extraction log entries
- Updated timestamp

To manually refresh MEMORY.md:

```bash
# Re-run extraction (won't duplicate)
python3 scripts/extract_memory.py

# Or force re-process all files
python3 scripts/extract_memory.py --force
```

---

## Backup Strategy

### Database Backup

Include the database in your regular backups:

```bash
# Add to backup_config.sh
BACKUP_TARGETS+=(
    "/home/node/.openclaw/database/insight.db"
)
```

### Export to Portable Format

```bash
# Export to JSON (future feature)
python3 scripts/db_query.py --export json > memory_backup.json

# Export to Markdown
python3 scripts/db_query.py --export markdown > memory_backup.md
```

---

## Migration from Native memory/*.md

If you're switching from OpenClaw's native memory system:

### Step 1: Backup Existing Files

```bash
cp -r memory/ memory.backup/
```

### Step 2: Run Initial Extraction

```bash
python3 scripts/extract_memory.py --force
```

### Step 3: Verify Data

```bash
# Check extraction results
python3 scripts/db_query.py --stats

# Spot-check specific memories
python3 scripts/db_query.py [keyword]
```

### Step 4: Update Workflow

- Continue creating `memory/YYYY-MM-DD.md` files as usual
- Extraction script will auto-process new files daily
- Query database instead of reading all files

---

## Performance Tuning

### Index Optimization

Database indexes are created automatically. To rebuild:

```sql
-- In SQLite
REINDEX;
```

### Query Optimization

For frequent queries, use specific categories:

```bash
# Slower (full table scan)
python3 scripts/db_query.py backup

# Faster (indexed category + keyword)
python3 scripts/db_query.py backup --category System
```

---

## Troubleshooting

### Extraction Not Running

Check if files are already processed:

```bash
python3 scripts/extract_memory.py --review
```

### Query Returns No Results

1. Verify database exists: `ls -lh /home/node/.openclaw/database/insight.db`
2. Check categories: `python3 scripts/db_query.py --categories`
3. Try broader search terms

### MEMORY.md Not Updating

Ensure write permissions:

```bash
chmod u+w MEMORY.md
```

---

## Next Steps

- [API Reference](api.md) - Database schema and functions
- [Examples](../examples/) - Sample usage patterns
- [Contributing](../README.md#contributing) - Extend functionality
