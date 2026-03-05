# claw-memory-lite Skill

> Lightweight Long-Term Memory for OpenClaw — SQLite-Powered, Zero External Dependencies, Millisecond Queries.

This skill provides an automated way to manage your agent's long-term memory by extracting distilled insights from daily logs into a queryable SQLite database.

## Installation

```bash
npx skills add timothysong0w0/claw-memory-lite --agent openclaw
```

## Tools

### db_query
Query the long-term memory database by keyword or category.

**Usage**: `python scripts/db_query.py [SEARCH_TERM] [--category CATEGORY]`

### extract_memory
Extract memory snippets from daily log files (`memory/YYYY-MM-DD.md`) into the database.

**Usage**: `python scripts/extract_memory.py [--review]`

## Automation

To enable automatic daily extraction, add the following to your `HEARTBEAT.md`:

```bash
python ~/.openclaw/extensions/claw-memory-lite/scripts/extract_memory.py
```

## Configuration

The database is stored at `~/.openclaw/database/insight.db` by default.

## Credits

Inspired by **鸿蒙小张** and ByteDance's **OpenViking** hierarchy.

---

**Built with 🐯 for OpenClaw users.**
