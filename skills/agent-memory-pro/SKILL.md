---
name: agent-memory
description: Full AI agent memory stack — Mem0 unified memory engine with vector search (Qdrant) and knowledge graph (Neo4j), plus SQLite for structured data. Complete setup script and tools. Give your OpenClaw agent a real brain with semantic recall, entity relationships, and structured storage.
homepage: https://www.agxntsix.ai
license: MIT
compatibility: Python 3.10+, Docker (Qdrant + Neo4j), OpenRouter API key
metadata: {"openclaw": {"emoji": "\ud83e\udde0", "requires": {"env": ["OPENROUTER_API_KEY"]}, "primaryEnv": "OPENROUTER_API_KEY", "homepage": "https://www.agxntsix.ai"}}
---

# Agent Memory 🧠

Full intelligence layer: vector memory + knowledge graph + structured database.

## When to Use

- Storing and recalling facts semantically ("remember that Abidi prefers...")
- Managing structured data: projects, contacts, tasks, bookmarks
- Setting up the brain stack after container rebuild
- Batch seeding memory with key facts

## Usage

### Memory Engine (Mem0 — vectors + graph)
```bash
# Store a fact
python3 {baseDir}/scripts/memory_engine.py add "Abidi's business focuses on Voice AI"

# Semantic recall
python3 {baseDir}/scripts/memory_engine.py search "what does Abidi's business do"

# List all memories
python3 {baseDir}/scripts/memory_engine.py get-all

# Test connections (Qdrant, Neo4j, Langfuse)
python3 {baseDir}/scripts/memory_engine.py test
```

### Structured Database (SQLite)
```bash
# List tables
python3 {baseDir}/scripts/structured_db.py tables

# Insert data
python3 {baseDir}/scripts/structured_db.py insert projects '{"name":"MyProject","status":"active"}'

# Query
python3 {baseDir}/scripts/structured_db.py query "SELECT * FROM projects"
```

### Setup & Seeding
```bash
# Install Python deps after container rebuild
bash {baseDir}/scripts/setup_brain.sh

# Batch seed with key facts
python3 {baseDir}/scripts/seed_mem0.py
```

## Architecture

- **Mem0** — Unified AI memory (auto fact extraction, dedup, multi-level recall)
- **Qdrant** — Vector database for semantic search
- **Neo4j** — Knowledge graph for entities & relationships
- **SQLite** — Structured data (projects, contacts, tasks, bookmarks)
- **Langfuse** — Observability tracing on all operations

## Credits
Built by [M. Abidi](https://www.linkedin.com/in/mohammad-ali-abidi) | [agxntsix.ai](https://www.agxntsix.ai)
[YouTube](https://youtube.com/@aiwithabidi) | [GitHub](https://github.com/aiwithabidi)
Part of the **AgxntSix Skill Suite** for OpenClaw agents.

📅 **Need help setting up OpenClaw for your business?** [Book a free consultation](https://cal.com/agxntsix/abidi-openclaw)
