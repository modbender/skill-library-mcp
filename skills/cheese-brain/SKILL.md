---
name: cheese-brain
description: DuckDB-powered knowledge management system for fast retrieval across 22+ entity types (projects, contacts, tools, workflows, decisions, etc.). Use when you need to recall context about past projects, look up configuration details, find tool documentation, retrieve contact information, search workflows/procedures, or query any tracked knowledge. Supports sub-millisecond keyword search and BM25 full-text search with relevance ranking.
---

# Cheese Brain

Fast, persistent knowledge base for AI agents and humans. Store and retrieve entities (projects, contacts, tools, workflows, decisions) with sub-millisecond search.

## Installation

Cheese Brain is a Python package that requires installation before use:

```bash
# Clone the repository
git clone https://github.com/mhugo22/cheese-brain.git
cd cheese-brain

# Create virtual environment and install
python3 -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
pip install -e .
```

**Verify installation:**

```bash
cheese-brain stats
```

If this shows statistics (entity counts, database size), the installation is successful.

## When to Use This Skill

Use Cheese Brain when you need to:

- **Recall project context** - "What's the email monitor project?" → instant project details with repo, path, schedule
- **Look up tools** - "Where's the backup script?" → tool location, usage, related workflows
- **Find contact info** - "Scout calendar feed?" → contact with calendar URL, location, timezone
- **Search workflows** - "How do I restore config?" → step-by-step workflow + related tools
- **Retrieve decisions** - "Why did we choose DuckDB?" → past decision with rationale + date
- **Query infrastructure** - "What's the Telegram channel ID?" → integration details with tokens, config

**Key advantage:** Persistent memory across sessions. You don't "remember" things — you query Cheese Brain and get instant context.

## Common Usage Patterns

### Quick Search (Most Common)

```bash
# Keyword search (fast, loose matching)
cheese-brain search "email monitor"
cheese-brain search "backup config"
cheese-brain search "calendar feed"

# Full-text search (BM25 relevance ranking)
cheese-brain fts "email monitoring"
cheese-brain fts "backup config" --category tool
```

**Output:** Table with title, category, tags + full entity details for matches.

### Get Specific Entity

When search returns multiple results, get the exact one by ID:

```bash
cheese-brain get <entity-id>
```

**Output:** Full entity details including JSON data field (paths, URLs, schedules, etc.).

### Add New Entity

When you learn something new worth persisting:

```bash
cheese-brain add \
  --title "New Project Name" \
  --category project \
  --tags "tag1,tag2,tag3" \
  --data '{"repo": "https://github.com/...", "status": "active"}'
```

**Categories:** project, tool, workflow, contact, decision, bookmark, infrastructure, habit, idea, etc.

**Data field:** Freeform JSON for entity-specific details (paths, URLs, schedules, credentials, etc.).

### Update Entity

```bash
cheese-brain update <entity-id> --title "New Title" --tags "new,tags"
cheese-brain update <entity-id> --data '{"status": "shipped", "deployed": "2026-02-17"}'
```

### List & Browse

```bash
cheese-brain list                     # All entities (most recent first)
cheese-brain list --category project  # Filter by category
cheese-brain list --tag shipped       # Filter by tag
cheese-brain list --limit 10          # Limit results
```

### Stats & Tags

```bash
cheese-brain stats                    # Database statistics
cheese-brain tags                     # Tag usage analysis
```

## Query Examples by Use Case

### "What's the email monitor project?"
```bash
cheese-brain search "email monitor"
# Returns: Email Monitor project with repo, path, cron schedule, run command
```

### "How do I backup the config?"
```bash
cheese-brain search "backup config"
# Returns: 5 entities (backup script, restore script, workflow, recovery guide, gateway)
```

### "Calendar feed URL?"
```bash
cheese-brain search "calendar feed"
# Returns: Contact entity with ICS feed URL + location details
```

### "What projects are shipped?"
```bash
cheese-brain list --category project --tag shipped
# Returns: SketchySkills, Gabby Gmail, Cheese Brain, etc.
```

### "Find anything about monitoring"
```bash
cheese-brain fts "monitoring"
# Returns: BM25-ranked results (Gabby Gmail, news monitor, cost monitor, etc.)
```

## Advanced Features

### Full-Text Search (FTS)

For relevance-ranked results when you have many entities:

```bash
# First-time setup (one-time only)
cheese-brain create-fts-index

# Search with relevance ranking
cheese-brain fts "backup automation"
cheese-brain fts "email calendar" --category tool
cheese-brain fts "security logging" --limit 10
```

**When to use FTS vs keyword search:**
- **FTS:** Large knowledge base (>100 entities), multi-word queries, need best matches first
- **Keyword:** Quick lookups, exact matches, small knowledge base

### Export & Backup

```bash
# JSON export (human-readable)
cheese-brain export backup.json

# Parquet export (2-9x smaller, columnar format)
cheese-brain export backup.parquet --format parquet

# Restore from backup
cheese-brain restore-backup backup.json  # Auto-detects format
```

**Note:** Automated daily backups may already be configured via OpenClaw cron (check `~/.cheese-brain/backups/`).

## Data Model

Each entity has:

- **id** (UUID) - Unique identifier
- **title** (string) - Entity name
- **category** (string) - Entity type (project, tool, contact, etc.)
- **tags** (array) - Searchable tags
- **data** (JSON) - Freeform structured data (paths, URLs, schedules, etc.)
- **created_at** / **updated_at** / **deleted_at** (timestamps)

**Example entity:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Email Monitor Project",
  "category": "project",
  "tags": ["automation", "nodejs", "gmail", "calendar", "telegram", "shipped"],
  "data": {
    "repo": "https://github.com/username/email-monitor",
    "path": "/path/to/workspace/email-monitor/",
    "schedule": "7am, 1pm, 5pm, 9pm CST",
    "run_command": "node process.js",
    "telegram_channel": "-100XXXXXXXXXX"
  },
  "created_at": "2026-02-17T06:55:00Z",
  "updated_at": "2026-02-17T08:30:00Z"
}
```

## Performance

- **Search:** <1ms keyword search, ~5ms FTS
- **Database size:** ~0.3 MB per entity (varies with data field)
- **Scales to:** 100k+ entities (constant-time FTS, linear keyword scan)

## Troubleshooting

**Command not found:**
- Ensure virtual environment is activated: `source /path/to/cheese-brain/venv/bin/activate`
- Or use full path: `/path/to/cheese-brain/venv/bin/cheese-brain`

**Database locked:**
- Close other Cheese Brain processes
- Check `~/.cheese-brain/` for stale lock files

**Slow queries:**
- Create FTS index if not already done: `cheese-brain create-fts-index`
- Check database size: `cheese-brain stats`
- Consider archiving old entities (soft delete with `--deleted` flag)

## Documentation

- **Full documentation:** https://github.com/mhugo22/cheese-brain
- **Backup/recovery guide:** `BACKUP_RECOVERY.md` in repo
- **FTS guide:** `FTS.md` in repo
- **Performance analysis:** `PERFORMANCE_ANALYSIS.md` in repo
- **Security:** `SECURITY.md` in repo

## Security Features

- **File permissions:** Database/backups auto-secured (`0600` owner-only)
- **Sensitive redaction:** `api_key`, `token`, `password` auto-hidden (use `--reveal` to show)
- **Encrypted exports:** `cheese-brain export --encrypt` for password-protected backups
- **Data validation:** Max 1MB per entity, max 10 nesting levels, SQL injection protection

**Best practice:** Don't store secrets in plain text. Use password managers (1Password, Bitwarden) and reference them:
```json
{"api_key_location": "1Password: OpenAI API", "notes": "Retrieve from vault"}
```

## Tips for Effective Use

1. **Tag consistently** - Use lowercase, hyphenated tags (e.g., `email-monitoring`, not `Email Monitoring`)
2. **Use data field** - Store structured info (paths, URLs, schedules) in JSON data field for easy retrieval
3. **Search first, then get** - Use search to find candidates, then `get <id>` for full details
4. **FTS for discovery** - Use full-text search when you're not sure what you're looking for
5. **Update frequently** - Keep entity status current (active → shipped, urls, paths)
6. **Soft delete** - Don't hard delete; use `--deleted` flag to mark inactive (recoverable)
