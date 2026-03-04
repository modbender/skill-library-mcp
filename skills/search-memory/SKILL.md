---
name: search-memory
description: Local-first memory search and indexing for Openclaw. Use when you need to (1) index memory files, (2) search memory from the CLI, or (3) wire a slash command for memory lookup.
---

# Search Memory

## Overview

Index local memory files and run fast keyword search with recency boost.

## Quick Start

1) Build/update index (incremental cache):
```bash
scripts/index-memory.py
```

2) Search the index:
```bash
scripts/search-memory.py "your query" --top 5
```

## Notes

- Index includes `MEMORY.md` plus `memory/**/*.md`.
- Cache lives under `memory/cache/`.
- Search uses keyword scoring + recency boost (last 30/90 days).
