---
name: brain-cms
description: Continuum Memory System (CMS) for OpenClaw agents. Replaces flat MEMORY.md with a brain-inspired multi-layer memory architecture — semantic schemas, a hippocampal router (INDEX.md), vector store (LanceDB + nomic-embed-text), and automated NREM/REM sleep cycles for consolidation. Based on neuroscience research (LTP, spreading activation, CMS theory). Use when setting up persistent agent memory, improving context efficiency, or reducing token cost on long-running agents. Triggers: brain, memory system, CMS, long-term memory, vector store, sleep cycle, NREM, REM, memory architecture, semantic memory, context efficiency.
metadata:
  openclaw:
    emoji: 🧠
    requires:
      bins: ["python3", "ollama"]
    install:
      - id: python-deps
        kind: shell
        label: "Install Python dependencies"
        command: "cd ~/.openclaw/workspace/memory_brain && python3 -m venv .venv && .venv/bin/pip install lancedb numpy pyarrow requests --quiet"
      - id: ollama-models
        kind: shell
        label: "Pull Ollama models (nomic-embed-text + llama3.2:3b)"
        command: "ollama pull nomic-embed-text && ollama pull llama3.2:3b"
---

# Brain CMS 🧠

A neuroscience-inspired memory architecture for OpenClaw agents.
Replaces flat file injection with sparse, semantic, frequency-gated memory loading.

## What This Installs

```
memory/
├── INDEX.md          ← Hippocampus: topic router + cross-links
├── ANCHORS.md        ← Permanent high-significance event store
└── schemas/          ← Domain-specific semantic schemas (you create these)

memory_brain/
├── index_memory.py   ← Embeds schemas into LanceDB vector store
├── query_memory.py   ← Semantic similarity search
├── nrem.py           ← NREM sleep cycle (compression + anchor promotion)
├── rem.py            ← REM sleep cycle (LLM consolidation via Ollama)
└── vectorstore/      ← LanceDB database (auto-created)
```

## Setup (one-time)

```bash
# 1. Run the installer
python3 ~/.openclaw/workspace/skills/brain-cms/install.py

# 2. Index your schemas
cd ~/.openclaw/workspace/memory_brain
.venv/bin/python3 index_memory.py

# 3. Test retrieval
.venv/bin/python3 query_memory.py "your topic here" --sources-only
```

## How It Works

**Boot sequence:** Load MEMORY.md (lean core) + today's daily log. Nothing else.

**When a topic appears:** Read `memory/INDEX.md` → load only the relevant schemas (spreading activation). Check `memory/ANCHORS.md` for high-significance events.

**For ambiguous topics:** Run semantic search:
```bash
memory_brain/.venv/bin/python3 memory_brain/query_memory.py "message text" --sources-only
```

**Auto-schema creation:** When a new significant project or domain appears:
1. Create `memory/<topic>.md`
2. Add to INDEX.md with triggers + priority + cross-links
3. Re-index: `memory_brain/.venv/bin/python3 memory_brain/index_memory.py`

**Sleep cycles:**
```bash
# NREM — run on shutdown (~30s, no LLM)
cd ~/.openclaw/workspace/memory_brain && .venv/bin/python3 nrem.py

# REM — run weekly (2-5 min, uses local llama3.2:3b, free)
cd ~/.openclaw/workspace/memory_brain && .venv/bin/python3 rem.py
```

## Memory Layers (CMS)

| Layer | Files | When loaded | Purpose |
|-------|-------|-------------|---------|
| Working | `MEMORY.md` + today log | Every session | Core context |
| Episodic | `memory/YYYY-MM-DD.md` | Session boot | Recent events |
| Semantic | `memory/*.md` schemas | On trigger | Domain knowledge |
| Anchors | `memory/ANCHORS.md` | On CRITICAL topics | Permanent ground truth |
| Vector | `memory_brain/vectorstore/` | On demand | Semantic search |

## Tagging Anchors
In any daily log, tag high-significance events:
```
[ANCHOR] Major demo success — full pipeline working end-to-end
```
NREM auto-promotes these to ANCHORS.md on next shutdown.

## Token Savings
Typical MEMORY.md: 150-300 lines injected every session.
With Brain CMS: ~50-line core + schemas loaded only when relevant.
Estimated savings: 40-60% reduction in context tokens per session.

## Requirements
- Python 3.10+
- Ollama (for embeddings + REM consolidation)
- 500MB+ storage for vector store and models
- `lancedb`, `numpy`, `pyarrow`, `requests` (auto-installed)
