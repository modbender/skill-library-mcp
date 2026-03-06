---
name: 🐾 Knowledge Base (RAG) — Your Second Brain
description: Save anything, recall it semantically. Personal RAG-powered
  knowledge base with SQLite + embeddings.
---

# 🐾 Knowledge Base (RAG) — Your Second Brain

> by Odin's Eye Enterprises — Ancient Wisdom. Modern Intelligence.

Save anything, recall it semantically. Personal RAG-powered knowledge base with SQLite + embeddings.

## What It Does

1. **Ingest** — Save text, URLs, files, notes into your knowledge base
2. **Query** — Semantic search across everything you've saved
3. **Retrieve** — Get relevant context for any question

## Trigger Phrases

- "remember this"
- "save this to the knowledge base"
- "what do I know about"
- "search my notes"
- "KB query"

## Usage

```bash
# Ingest text
python ingest.py "The key insight from today's meeting was..."

# Ingest from a file
python ingest.py --file notes.md

# Query the knowledge base
python query.py "What did we discuss about pricing?"

# Full KB management
python kb.py stats
python kb.py search "topic"
```

## Files

- `kb.py` — core KB engine (embeddings, storage, retrieval)
- `ingest.py` — CLI for adding content
- `query.py` — CLI for searching
- `kb.db` — SQLite database (auto-created)

## Requirements

- Python 3.10+
- `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` for embeddings

## For Agents

Save context: `python ingest.py "TEXT"`
Retrieve context: `python query.py "QUESTION"`

<!-- 🐾 Muninn never forgets -->
