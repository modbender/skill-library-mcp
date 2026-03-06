---
name: infinite-memory
version: 1.0.0
description: High-precision memory with 100% recall accuracy for long contexts.
emoji: 🦞
metadata:
  clawdbot:
    requires:
      bins: 
        - python
        - curl
    files:
      - scripts/recall.py
      - scripts/ingest.py
      - engine/memory_engine_parallel_lms.py
      - references/AUTO_INTEGRATION.md
      - memory_service.py
      - requirements.txt
---

# Infinite Memory 🦞

High-precision RAG engine for deep context retrieval (Phase 16 Architecture).

## Tools

### recall_facts
- **Cmd:** `python scripts/recall.py "{{query}}"`
- **Goal:** Search for facts in the historical database.

### memorize_data
- **Cmd:** `python scripts/ingest.py "{{filename}}" "{{text}}"`
- **Goal:** Store new data into the long-term memory.
