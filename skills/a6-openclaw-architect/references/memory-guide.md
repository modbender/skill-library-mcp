# OpenClaw Memory System Guide

## Overview

OpenClaw has a multi-layer memory system that gives agents persistent knowledge across sessions.

## Memory Layers

### Layer 1: Workspace Files (Always Loaded)
These files are injected into every session's context:
- **MEMORY.md** — Long-term strategic knowledge (main sessions only)
- **AGENTS.md** — System architecture rules
- **SOUL.md** — Identity and personality
- **TOOLS.md** — API notes and tool usage

**Key rule:** Keep these files focused. Every byte counts against context window.

### Layer 2: Memory Search (On-Demand)
Files in `memory/*.md` are indexed and searched via embeddings:
- Agent auto-searches when a query might benefit from memory
- Configured in `agents.defaults.memorySearch`
- Uses OpenRouter embeddings by default

```json
{
  "memorySearch": {
    "enabled": true,
    "provider": "openai",
    "remote": {
      "baseUrl": "https://openrouter.ai/api/v1",
      "apiKey": "sk-or-v1-..."
    }
  }
}
```

### Layer 3: Compaction Memory Flush
Before context compaction (when conversation gets too long):
1. Agent scans for unstored important info
2. Writes to memory files and/or brain_engine.py
3. Then context is summarized

```json
{
  "compaction": {
    "mode": "safeguard",
    "memoryFlush": {
      "enabled": true,
      "softThresholdTokens": 4000,
      "prompt": "Scan conversation for unstored important info..."
    }
  }
}
```

### Layer 4: Brain Stack (External DBs)
For deployments with Mem0/Qdrant/Neo4j/SQLite:
- **Mem0 → Qdrant** — Semantic vector search
- **Mem0 → Neo4j** — Entity relationships and knowledge graph
- **SQLite** — Structured decisions, contacts, metrics

```bash
$PY tools/brain_engine.py remember "Important fact"
$PY tools/brain_engine.py recall "query about the fact"
$PY tools/brain_engine.py decide '{"title":"Decision","summary":"..."}'
```

## File Organization

### MEMORY.md — Core Knowledge
```markdown
# MEMORY.md — Long-Term Memory

## Who I Am
- Identity, purpose, capabilities

## Key People
- Names, preferences, relationships

## Active Projects
- Current work, status, context

## Server Setup
- Infrastructure details

## API Keys
- Key locations and notes
```

**Rules:**
- Keep under ~4000 tokens (it's loaded every session)
- Only strategic/permanent info
- Update when facts change, don't let it grow unbounded

### memory/*.md — Daily/Topical Files
```
memory/
├── 2026-02-18.md           # Daily log
├── 2026-02-19.md           # Daily log
├── errors-and-fixes-*.md   # Error documentation
├── founder-journal/        # Daily journals
├── voice-notes/            # Transcribed audio
└── brain-stack-plan.md     # Topical reference
```

**Naming conventions:**
- Daily: `YYYY-MM-DD.md`
- Topical: `descriptive-name.md`
- Errors: `errors-and-fixes-YYYY-MM-DD.md`

### What Goes Where

| Content | Storage | Why |
|---------|---------|-----|
| Identity, preferences | MEMORY.md | Needed every session |
| Today's events | memory/YYYY-MM-DD.md | Searchable, archival |
| Strategic decisions | brain_engine.py → SQLite | Structured, queryable |
| Relationships | brain_engine.py → Neo4j | Graph traversal |
| Semantic facts | brain_engine.py → Mem0 | Vector search |
| System rules | AGENTS.md | Loaded every session |
| Tool configs | TOOLS.md | Quick reference |

## CLI Commands

```bash
openclaw memory search "query"    # Search across memory files
openclaw memory reindex           # Rebuild memory index
```

## Common Issues

### Memory not being found
- Check `memorySearch.enabled: true` in config
- Run `openclaw memory reindex`
- Verify the memory file has enough content to be indexed

### MEMORY.md too large
- Move historical info to `memory/` files
- Keep only current, essential info in MEMORY.md
- Use brain_engine.py for structured data

### Compaction losing information
- Enable `memoryFlush` in compaction config
- Set `softThresholdTokens` high enough for the flush to complete
- Check that flush prompt instructs saving to both files AND brain

### Memory search returning irrelevant results
- Embedding model quality matters — use a good one via OpenRouter
- More specific file content = better retrieval
- Split large files into focused topics
