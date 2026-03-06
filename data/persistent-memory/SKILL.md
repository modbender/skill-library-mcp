---
name: persistent-memory
version: 3.0.0
description: Three-layer persistent memory system (Markdown + ChromaDB vectors + NetworkX knowledge graph) for long-term agent recall across sessions. One-command setup with automatic OpenClaw integration. Use when the agent needs to remember decisions, facts, context, or institutional knowledge between sessions.
---

# Persistent Memory

Adds persistent three-layer memory to any OpenClaw workspace. The agent gains semantic recall across sessions — decisions, facts, lessons, and institutional knowledge survive restarts.

## Architecture

| Layer | Technology | Purpose |
|-------|-----------|---------|
| L1: Markdown | MEMORY.md + daily logs + reference/ | Human-readable curated knowledge |
| L2: Vector | ChromaDB + all-MiniLM-L6-v2 | Semantic search across all memories |
| L3: Graph | NetworkX | Relationship traversal between concepts |

All three layers sync together. The indexer updates L2 and L3 from L1 automatically.

## ⚠️ Critical Integration: OpenClaw Memory Configuration

**Problem:** OpenClaw has its own built-in memory search system, but by default it only indexes `MEMORY.md` and `memory/*.md` files. Critical workspace files like `SOUL.md` (agent directives), `AGENTS.md` (behavior rules), and `PROJECTS.md` (active work) are **ignored**.

**Impact:** Agents can violate explicit directives because they're not found in memory searches. This causes operational failures where agents ignore their own rules.

**Solution:** The `configure_openclaw.py` script adds a `memorySearch` configuration block to OpenClaw that indexes all critical workspace files. This makes directive compliance **automatic** rather than optional.

## Setup

**One command from workspace root:**

```bash
bash skills/persistent-memory/scripts/unified_setup.sh
```

This automatically:
- ✅ Creates 3-layer memory system (Markdown + Vector + Graph)
- ✅ Installs all Python dependencies (ChromaDB, NetworkX, sentence-transformers)
- ✅ Configures OpenClaw memorySearch integration (directive compliance)
- ✅ Indexes existing MEMORY.md if present
- ✅ Sets up daily maintenance automation

**No manual configuration needed.** The script handles everything including OpenClaw integration that prevents agents from ignoring workspace directives (SOUL.md, AGENTS.md, etc.).

## Daily Usage

### Writing Memories

- **MEMORY.md** — Curated long-term knowledge (decisions, architecture, lessons learned). Update after significant events.
- **memory/YYYY-MM-DD.md** — Daily logs. Raw notes of what happened each day.
- **reference/*.md** — Institutional facts (people, repos, infrastructure, business rules). The agent's encyclopedia.

### Indexing (after editing any memory file)

```bash
vector_memory/venv/bin/python vector_memory/indexer.py
```

The indexer parses MEMORY.md, reference/*.md, and memory/*.md into vector embeddings and rebuilds the knowledge graph. Run after every edit to keep layers in sync.

### Searching

```bash
vector_memory/venv/bin/python vector_memory/search.py "your query"
```

Returns top-3 semantically similar chunks with source file and section.

### Sync Status Check

```bash
vector_memory/venv/bin/python vector_memory/auto_retrieve.py --status
```

Reports sync health: MEMORY.md hash vs indexed state, chunk count, graph size. Use in heartbeats to detect drift.

## Agent Behavior Rules

Add these to AGENTS.md or SOUL.md:

### Pre-Response (mandatory)
Before answering questions about prior work, decisions, dates, people, or preferences — search memory first. Use `memory_search` or run `auto_retrieve.py` with the query. Never say "I don't remember" without checking.

**CRITICAL:** OpenClaw's built-in memory search should now automatically find directive files (SOUL.md, AGENTS.md) if `configure_openclaw.py` was run. If memory searches are not finding agent rules or workspace directives, the OpenClaw integration is missing or broken.

### Pre-Action (mandatory)
Before executing any action that references an external identifier (URL, handle, email, repo name, address) — query `reference/` files for the exact value. If not found, query vector memory. If still not found, ask the user. **Never fabricate identifiers.**

### Post-Edit (mandatory)
After editing MEMORY.md or any file in reference/ or memory/ — re-index:
```bash
vector_memory/venv/bin/python vector_memory/indexer.py
```

### Heartbeat Integration
Add to HEARTBEAT.md:
```
## Memory Sync Check
Run `vector_memory/venv/bin/python vector_memory/auto_retrieve.py --status` and if status is OUT_OF_SYNC, re-index with `vector_memory/venv/bin/python vector_memory/indexer.py`.
```

## Reference Directory (Optional but Recommended)

Create `reference/` in the workspace root as the agent's institutional knowledge base:

```
reference/
├── people.md          — Contacts, roles, communication details
├── repos.md           — GitHub repositories, URLs, status
├── infrastructure.md  — Hosts, IPs, ports, services
├── business.md        — Company info, strategies, rules
└── properties.md      — Domain-specific entities (deals, products, etc.)
```

These files are vector-indexed alongside MEMORY.md. The agent queries them before any action involving external identifiers. Facts accumulate over time — the agent that never forgets.

## File Structure After Setup

```
workspace/
├── MEMORY.md              — Curated long-term memory (L1)
├── memory/
│   ├── 2026-02-17.md      — Daily log
│   └── heartbeat-state.json — Sync tracking
├── reference/             — Institutional knowledge (optional)
│   ├── people.md
│   └── ...
└── vector_memory/
    ├── indexer.py          — Index all markdown into vectors + graph
    ├── search.py           — Semantic search CLI
    ├── graph.py            — NetworkX knowledge graph
    ├── auto_retrieve.py    — Status checker + auto-retrieval
    ├── chroma_db/          — Vector database (gitignored)
    ├── memory_graph.json   — Knowledge graph (auto-generated)
    └── venv/               — Python venv (gitignored)
```

## Troubleshooting

- **"No module named chromadb"** — Run setup.sh again or activate the venv: `source vector_memory/venv/bin/activate`
- **OUT_OF_SYNC status** — Run the indexer: `vector_memory/venv/bin/python vector_memory/indexer.py`
- **Empty search results** — Check that MEMORY.md has content and the indexer has been run at least once
- **SIGSEGV on indexing** — Usually caused by incompatible ML libs. The setup script pins known-good versions.
- **Agent ignoring SOUL.md/AGENTS.md directives** — OpenClaw integration missing. Run `python skills/persistent-memory/scripts/configure_openclaw.py` to fix.
- **Memory searches not finding workspace files** — Check OpenClaw configuration: `openclaw config get | grep memorySearch`
- **"Configuration verification failed"** — Restart OpenClaw manually: `openclaw gateway restart`
