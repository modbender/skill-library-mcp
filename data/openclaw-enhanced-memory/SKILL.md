---
name: enhanced-memory
description: >
  An enhanced memory system for OpenClaw agents that replaces the default
  single-file MEMORY.md with a complete memory architecture: hierarchical
  directory organization by category, [category:value] tag indexing with
  multi-tag AND search, automatic lifecycle management (active → archive,
  never delete), and intelligent cross-category retrieval that auto-routes
  queries to the right memory module. Gives your agent structured, searchable,
  long-lived memory out of the box.
---

# Enhanced Memory

A structured memory system that gives your OpenClaw agent **organized, searchable, long-lived memory** instead of a single monolithic `MEMORY.md`.

## Why?

The default `MEMORY.md` approach hits a wall fast:

- One file grows endlessly → slow to read, expensive on tokens
- No categorization → food logs mixed with project notes mixed with relationship context
- No retrieval strategy → agent re-reads everything or misses what matters
- No lifecycle → old entries clutter active memory forever

Tagged Memory fixes all of this.

## Core Features

### 1. Hierarchical Directory Organization

Memories are stored in purpose-built directories:

```
memory/
├── current/          # Active memories (last 6 months)
├── archived/         # Auto-archived older memories (permanent, never deleted)
│   └── YYYY-MM/      # Organized by month
├── RELATION/         # One file per person (relationship context)
├── food/             # Meal and food logs
├── training/         # Exercise and workout records
├── connections.md    # Global relationship graph
├── system/           # System config and logs
└── misc/             # Everything else
```

### 2. Tag-Based Indexing

Tag any line in any memory file with `[category:value]` markers:

```markdown
## 2026-02-20

- Had lunch with Zhang Hao [人物:张浩东] [类型:聚餐] [地点:campus]
- Discussed the new project deadline [项目:openclaw] [类型:会议]
- Yoyo learned a new trick today [宠物:悠悠] [类型:milestone]
```

Tags support multi-tag AND search — find the exact memory you need:

```bash
# Single tag search
python3 scripts/memory_tag_search.py "人物:张浩东"

# Multi-tag AND search (all tags must match)
python3 scripts/memory_tag_search.py "人物:王隆哲" "类型:开票信息"

# List all tags in the system
python3 scripts/memory_tag_search.py --list-tags

# List tags under a specific category
python3 scripts/memory_tag_search.py --list-tags --category 人物
```

### 3. Lifecycle Management

Memories age gracefully — never lost, always accessible:

| Age | Location | Status |
|-----|----------|--------|
| 0–6 months | `memory/current/` | Active, auto-retrieved |
| 6–12 months | `memory/archived/YYYY-MM/` | Archived, searchable on demand |
| 12+ months | `memory/archived/` | Permanent archive, manual query |

Run the lifecycle manager manually or via cron:

```bash
# Default: archive memories older than 6 months
python3 scripts/memory_lifecycle_manager.py

# Custom threshold (e.g., 90 days)
python3 scripts/memory_lifecycle_manager.py 90
```

### 4. Smart Cross-Category Retrieval

The retrieval strategy script auto-classifies queries and searches the right directories:

```bash
python3 scripts/memory_retrieval_strategy.py "What did I eat yesterday?"
# → Searches memory/food/ + memory/current/

python3 scripts/memory_retrieval_strategy.py "How is Yoyo doing?"
# → Searches memory/RELATION/悠悠.md + memory/connections.md

python3 scripts/memory_retrieval_strategy.py "Yang Lingxiao"
# → Searches memory/RELATION/ + memory/connections.md
```

Query type detection covers: food, training, relationships, pets, system, mood, projects, and more.

## Scripts

| Script | Purpose |
|--------|---------|
| `scripts/memory_tag_search.py` | Tag-based indexing and search (single/multi-tag AND queries, tag listing) |
| `scripts/memory_retrieval_strategy.py` | Smart retrieval — auto-classifies queries and routes to relevant memory directories |
| `scripts/memory_lifecycle_manager.py` | Automatic archival of old memories (configurable threshold, never deletes) |

## Integration

### AGENTS.md

Add the following to your `AGENTS.md` memory section:

```markdown
## Memory

### Directory Structure
- `memory/current/` — active memories (6 months)
- `memory/archived/` — permanent archive
- `memory/RELATION/` — per-person relationship files
- `memory/food/` — meal logs
- `memory/training/` — workout logs

### Retrieval Strategy
- Exact queries (names, dates, codes) → `grep` the file system
- Fuzzy/semantic queries → `python3 scripts/memory_retrieval_strategy.py "<query>"`
- Tag search → `python3 scripts/memory_tag_search.py "<category>:<value>"`

### Tagging Convention
When writing memory entries, tag important lines:
  [人物:name] [类型:type] [地点:place] [项目:project] [情绪:mood]
```

### HEARTBEAT.md

Add periodic memory maintenance to your heartbeat checklist:

```markdown
## Memory Maintenance (every few days)
- [ ] Run `python3 scripts/memory_lifecycle_manager.py` to archive old memories
- [ ] Run `python3 scripts/memory_tag_search.py --list-tags` to review tag health
- [ ] Check `memory/current/` file count — if growing large, verify archival is running
```

### Cron (optional)

Set up monthly auto-archival:

```bash
# Run on the 1st of every month at 03:00
0 3 1 * * cd /path/to/workspace && python3 scripts/memory_lifecycle_manager.py
```

## Customization

- **Archive threshold**: Edit `ARCHIVE_THRESHOLD_DAYS` in `memory_lifecycle_manager.py` (default: 180 days)
- **Query patterns**: Add new regex patterns to `QUERY_TYPES` in `memory_retrieval_strategy.py`
- **Memory directories**: Add new modules to `MODULES_TO_ARCHIVE` in `memory_lifecycle_manager.py`
- **Tag categories**: Tags are freeform — just use `[category:value]` in any `.md` file

## Requirements

- Python 3.8+
- No external dependencies (stdlib only)
