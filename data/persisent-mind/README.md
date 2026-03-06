# PersistentMind

> Persistent, searchable memory for AI agents. Never repeat yourself again.

[![Version](https://img.shields.io/badge/version-1.0.0-blue)](https://github.com/vedantsingh60/persistentmind/releases)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE.md)
[![VirusTotal](https://img.shields.io/badge/VirusTotal-0%2F77-brightgreen)](https://github.com/vedantsingh60/persistentmind)
[![ClawhHub](https://img.shields.io/badge/ClawhHub-Memory%20Manager-orange)](https://clawhub.ai/unisai/persistentmind)

Give your AI agent a persistent memory across sessions and projects. Store facts, preferences, corrections, and procedures — then inject them directly into prompts so your agent always has the right context.

---

## What It Does

- **Persistent Memory** — Survives across sessions, projects, and restarts
- **7 Memory Types** — facts, preferences, procedures, corrections, context, relationships, reminders
- **3 Scopes** — global (cross-project), project, or session
- **Smart Search** — Full-text search with relevance scoring and importance boosting
- **Prompt Injection** — `get_context()` returns a formatted block ready for AI prompts
- **Auto-Tagging** — Extracts tags from content automatically
- **Deduplication** — `consolidate()` merges near-duplicate memories
- **Export/Import** — Share memory sets with teammates

---

## Quick Start

No installation needed — pure Python, zero dependencies.

```python
from persistentmind import PersistentMind, MemoryType, MemoryScope

mm = PersistentMind(project="my-app")

# Store a correction (highest priority in context)
mm.remember(
    "Never use wildcard imports — the linter will fail CI",
    memory_type=MemoryType.CORRECTION,
    scope=MemoryScope.PROJECT,
    importance=10.0,
    tags=["linting", "ci"]
)

# Store a user preference
mm.remember(
    "User prefers concise responses under 200 words",
    memory_type=MemoryType.PREFERENCE,
    scope=MemoryScope.GLOBAL,
    importance=8.0
)

# Store a procedure
mm.remember(
    "To run migrations: poetry run alembic upgrade head",
    memory_type=MemoryType.PROCEDURE,
    scope=MemoryScope.PROJECT,
    importance=7.0,
    tags=["alembic", "migrations"]
)

# Search memories
results = mm.recall("database migrations")
for r in results:
    print(f"[{r.relevance_score:.2f}] {r.memory.content}")

# Inject context into an AI prompt
context = mm.get_context()
prompt = f"{context}\n\nUser request: {user_input}"
```

---

## Memory Types

| Type | Use For |
|------|---------|
| `fact` | Factual information about the project or domain |
| `preference` | User preferences and communication style |
| `procedure` | Step-by-step instructions for recurring tasks |
| `correction` | Mistakes made + the correct approach |
| `context` | Background information agents need |
| `relationship` | How things relate to each other |
| `reminder` | Time-sensitive or important notes |

## Memory Scopes

| Scope | Persistence |
|-------|-------------|
| `global` | Across all projects and sessions |
| `project` | Within a specific named project |
| `session` | Current session only (auto-archived when stale) |

---

## Example Output

```
# Relevant Memory Context

⚠️ [CORRECTION] Never use wildcard imports — the linter will fail CI (tags: linting, ci)
⚙️ [PREFERENCE] User prefers concise responses under 200 words (tags: response-style)
📋 [PROCEDURE] To run migrations: poetry run alembic upgrade head (tags: alembic, migrations)
📌 [FACT] Database uses PostgreSQL 16. Connection string in .env as DATABASE_URL
```

---

## API Reference

| Method | Description |
|--------|-------------|
| `remember(content, type, scope, tags, importance)` | Store a new memory |
| `recall(query, scope_filter, type_filter, limit)` | Search memories by relevance |
| `recall_by_type(memory_type)` | Get all memories of a type |
| `recall_by_tag(tag)` | Get all memories with a tag |
| `get_context(project, max_tokens_estimate)` | Get prompt-ready context block |
| `update_memory(id, content, importance, tags)` | Update an existing memory |
| `forget(id, permanent)` | Archive or delete a memory |
| `consolidate(dry_run)` | Find and merge duplicates |
| `export_memories(output_file)` | Export to JSON |
| `import_memories(input_file)` | Import from JSON |
| `get_stats()` | Memory statistics |

---

## Privacy & Security

- **Local-only** — all memory stored in `.persistentmind/` on your machine
- **No external calls** — works completely offline
- **No API keys required** — zero credentials needed
- **Full transparency** — MIT licensed, source code included

---

## Available on ClawhHub

Install directly via [ClawhHub](https://clawhub.ai/unisai/persistentmind) for integration with Claude Code and OpenClaw.

---

## License

MIT License — see [LICENSE.md](LICENSE.md) for details.

© 2026 UnisAI Community
