# PersistentMind

**Persistent, searchable, context-aware memory for AI agents. Store what matters. Never lose context again.**

Free and open-source (MIT License) • Zero dependencies • Works locally • No API keys required

---

## Why This Skill?

AI agents forget everything between sessions. Every time you start a new conversation, you repeat the same context: your preferences, your project setup, corrections to previous mistakes, procedures you've documented. This skill solves that permanently.

### Problems it solves:
- Agents forget user preferences between sessions
- Same mistakes repeated because corrections aren't persisted
- Project context has to be re-explained every time
- No way to build up a team knowledge base over time

---

## Core Concepts

### Memory Types

| Type | Use For | Example |
|------|---------|---------|
| `fact` | Factual information | "Database is PostgreSQL 16" |
| `preference` | User preferences | "User prefers concise responses" |
| `procedure` | How-to steps | "Run migrations with: poetry run alembic upgrade head" |
| `correction` | Mistakes + fixes | "Never use wildcard imports — CI will fail" |
| `context` | Background info | "This is a B2B SaaS product for HR teams" |
| `relationship` | How things relate | "AuthService depends on UserRepository" |
| `reminder` | Notes for later | "Check with team before changing DB schema" |

### Memory Scopes

| Scope | Persists | Use For |
|-------|----------|---------|
| `global` | Always | Cross-project preferences, universal rules |
| `project` | Within project | Project-specific facts, procedures, corrections |
| `session` | Current session only | Temporary working notes |

---

## Features

### 1. Store Memories

```python
from persistentmind import PersistentMind, MemoryType, MemoryScope

mm = PersistentMind(project="my-app")

# Critical correction — will always surface first in context
mm.remember(
    "Never use wildcard imports — the linter will fail CI",
    memory_type=MemoryType.CORRECTION,
    scope=MemoryScope.PROJECT,
    importance=10.0,
    tags=["linting", "ci", "imports"]
)

# Global preference — applies everywhere
mm.remember(
    "User prefers code examples over long explanations",
    memory_type=MemoryType.PREFERENCE,
    scope=MemoryScope.GLOBAL,
    importance=8.0
)

# Auto-tags extracted from content automatically if you don't specify
mm.remember(
    "The Stripe API key is in .env as STRIPE_SECRET_KEY",
    memory_type=MemoryType.FACT,
    scope=MemoryScope.PROJECT,
    importance=9.0
)
```

### 2. Search Memories

```python
# Full-text search with relevance scoring
results = mm.recall("database migrations")
for r in results:
    print(f"[{r.relevance_score:.2f}] [{r.memory.memory_type}] {r.memory.content}")

# Search with filters
results = mm.recall("imports", type_filter="correction", min_importance=7.0)

# Get by type
corrections = mm.recall_by_type(MemoryType.CORRECTION)

# Get by tag
db_memories = mm.recall_by_tag("database")
```

### 3. Inject Context Into Prompts

```python
# Get a formatted context block to prepend to any prompt
context = mm.get_context(project="my-app", max_tokens_estimate=1500)

prompt = f"""
{context}

---

User request: {user_input}
"""
```

Output:
```
# Relevant Memory Context

⚠️ [CORRECTION] Never use wildcard imports — the linter will fail CI
⚙️ [PREFERENCE] User prefers code examples over long explanations
📌 [FACT] The Stripe API key is in .env as STRIPE_SECRET_KEY
📋 [PROCEDURE] Run migrations with: poetry run alembic upgrade head
```

Corrections always surface first. Importance score determines ranking.

### 4. Memory Management

```python
# Update an existing memory
mm.update_memory(memory_id="mem_abc123", importance=9.0, tags=["critical"])

# Archive a memory (soft delete)
mm.forget("mem_abc123")

# Permanently delete
mm.forget("mem_abc123", permanent=True)

# Expire automatically after N days
mm.remember("Temp token: abc...", expires_in_days=7)
```

### 5. Deduplication

```python
# Find near-duplicate memories (dry run — just report)
groups = mm.consolidate(dry_run=True)
for g in groups:
    print(f"Found {g['count']} similar memories:")
    for m in g['memories']:
        print(f"  - {m['content']}")

# Actually merge them
mm.consolidate(dry_run=False)
```

### 6. Team Sharing

```python
# Export your memory set
mm.export_memories("team_memories.json")

# Import a colleague's memories
mm.import_memories("team_memories.json")
```

### 7. Summary & Stats

```python
print(mm.format_summary())
```

```
🧠 Total Active Memories: 24  |  Archived: 3
   Avg Importance: 7.4/10

📊 BY TYPE
  • correction             4
  • fact                   8
  • preference             5
  • procedure              4
  • context                3
```

---

## Importance Scoring Guide

| Score | Use When |
|-------|----------|
| 10 | Critical — never violate (e.g. security rules, CI requirements) |
| 8-9 | Important — strong preference or key fact |
| 5-7 | Useful but not critical |
| 1-4 | Nice to know, low priority |

---

## API Reference

### `PersistentMind(storage_path, project, session_id, auto_cleanup_days)`
Initialize. Data stored in `.persistentmind/` by default.

### `remember(content, memory_type, scope, tags, importance, project, expires_in_days, source)`
Store a new memory. Returns `Memory` object.

### `recall(query, scope_filter, type_filter, project_filter, limit, min_importance)`
Search memories. Returns `List[MemorySearchResult]` sorted by relevance.

### `recall_by_type(memory_type, limit)`
Get all memories of a specific type, sorted by importance.

### `recall_by_tag(tag, limit)`
Get all memories with a specific tag.

### `get_context(project, max_tokens_estimate)`
Get formatted context block for prompt injection. Corrections surfaced first.

### `update_memory(memory_id, content, importance, tags)`
Update an existing memory's fields.

### `forget(memory_id, permanent)`
Archive (default) or permanently delete a memory.

### `consolidate(dry_run)`
Find near-duplicate memories. Set `dry_run=False` to merge them.

### `get_stats()`
Return memory statistics dictionary.

### `format_summary()`
Human-readable memory summary.

### `export_memories(output_file, include_archived)`
Export to JSON for backup or team sharing.

### `import_memories(input_file, overwrite_duplicates)`
Import from JSON export file.

---

## Privacy & Security

- ✅ **Zero telemetry** — No data sent anywhere
- ✅ **Local-only storage** — Everything in `.persistentmind/` on your machine
- ✅ **No API keys required** — Zero credentials needed
- ✅ **No authentication** — No accounts or logins
- ✅ **Full transparency** — MIT licensed, source code included

---

## Changelog

### [1.0.0] - 2026-02-16

- ✨ Initial release — PersistentMind
- ✨ 7 memory types: fact, preference, procedure, context, correction, relationship, reminder
- ✨ 3 scopes: global, project, session
- ✨ Full-text search with relevance scoring, importance boosting, recency decay
- ✨ Prompt context injection via `get_context()`
- ✨ Automatic tag extraction from content
- ✨ Memory consolidation for deduplication
- ✨ Export/import for team sharing
- ✨ Auto-expiry and stale session cleanup
- ✨ Zero dependencies, local-only storage, MIT licensed

---

**Last Updated**: February 16, 2026
**Current Version**: 1.0.0
**Status**: Active & Community-Maintained

© 2026 UnisAI Community
