---
name: openclaw-memories
description: Agent memory with ALMA meta-learning, LLM fact extraction, and full-text search. Observer calls remote LLM APIs (OpenAI/Anthropic/Gemini). ALMA and Indexer work offline.
---

# OpenClaw Memory System

Three components for agent memory:

1. **ALMA** — Evolves memory designs through mutation + evaluation (offline)
2. **Observer** — Extracts structured facts from conversations via LLM API (requires API key)
3. **Indexer** — Full-text search over workspace Markdown files (offline)

## Environment Variables

Observer requires one of:
- `OPENAI_API_KEY`
- `ANTHROPIC_API_KEY`
- Or pass `apiKey` in config

ALMA and Indexer require no keys or network access.

## How It Works

### ALMA (Algorithm Learning via Meta-learning Agents)
Proposes memory system designs, evaluates them, keeps the best. Uses gaussian mutation and simulated annealing to explore the design space.

```
alma.propose() → design
alma.evaluate(design.id, metrics) → score  
alma.best() → top design
alma.top(5) → leaderboard
```

### Observer
Sends conversation history to an LLM, gets back structured facts:
- Kind: world fact / biographical / opinion / observation
- Priority: high / medium / low
- Entities: mentioned people/places
- Confidence: 0.0–1.0 for opinions

Fails gracefully — returns empty array if LLM is unavailable.

### Indexer
Chunks workspace Markdown files and indexes them for search:
- `MEMORY.md` — core facts
- `memory/YYYY-MM-DD.md` — daily logs
- `bank/entities/*.md` — entity summaries
- `bank/opinions.md` — beliefs with confidence

```
indexer.index() → count of chunks indexed
indexer.search('query') → ranked results
indexer.rebuild() → re-index from scratch
```

## Install

```bash
npm install @artale/openclaw-memory
```

## Limitations

- Indexer uses an in-memory mock database, not real SQLite FTS5. Search works but ranking is simplified.
- Observer calls remote APIs — not offline. Only ALMA and Indexer work without network.
- No dashboard — removed in v2 for simplicity.

## Source

5 files, 578 lines, 0 runtime dependencies.

https://github.com/arosstale/openclaw-memory
