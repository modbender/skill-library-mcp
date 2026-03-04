---
name: enhanced-memory
description: Enhanced memory search with hybrid vector+keyword scoring, temporal routing, filepath scoring, adaptive weighting, pseudo-relevance feedback, salience scoring, and knowledge graph cross-references. Replaces the default memory search with a 4-signal fusion retrieval system. Use when searching memories, indexing memory files, building cross-references, or scoring memory salience. Requires Ollama with nomic-embed-text model.
---

# Enhanced Memory

Drop-in enhancement for OpenClaw's memory system. Replaces flat vector search with a 4-signal hybrid retrieval pipeline that achieved **0.782 MRR** (vs ~0.45 baseline vector-only).

## Setup

```bash
# Install Ollama and pull the embedding model
ollama pull nomic-embed-text

# Index your memory files (run from workspace root)
python3 skills/enhanced-memory/scripts/embed_memories.py

# Optional: build cross-reference graph
python3 skills/enhanced-memory/scripts/crossref_memories.py build
```

Re-run `embed_memories.py` whenever memory files change significantly.

## Scripts

### `scripts/search_memory.py` — Primary Search

Hybrid 4-signal retrieval with automatic adaptation:

```bash
python3 skills/enhanced-memory/scripts/search_memory.py "query" [top_n]
```

**Signals fused:**
1. **Vector similarity** (0.4) — cosine similarity via nomic-embed-text embeddings
2. **Keyword matching** (0.25) — query term overlap with chunk text
3. **Header matching** (0.1) — query terms in section headers
4. **Filepath scoring** (0.25) — query terms matching file/directory names

**Automatic behaviors:**
- **Temporal routing** — date references ("yesterday", "Feb 8", "last Monday") get 3x boost on matching files
- **Adaptive weighting** — when keyword overlap is low, shifts to 85% vector weight
- **Pseudo-relevance feedback (PRF)** — when top score < 0.45, expands query with terms from initial results and re-scores

### `scripts/enhanced_memory_search.py` — JSON-Compatible Search

Same pipeline with JSON output format compatible with OpenClaw's memory_search tool:

```bash
python3 skills/enhanced-memory/scripts/enhanced_memory_search.py --json "query"
```

Returns `{results: [{path, startLine, endLine, score, snippet, header}], ...}`.

### `scripts/embed_memories.py` — Indexing

Chunks all `.md` files in `memory/` plus core workspace files (MEMORY.md, AGENTS.md, etc.) by markdown headers and embeds them:

```bash
python3 skills/enhanced-memory/scripts/embed_memories.py
```

Outputs `memory/vectors.json`. Batches embeddings in groups of 20, truncates chunks to 2000 chars.

### `scripts/memory_salience.py` — Salience Scoring

Surfaces stale/important memory items for heartbeat self-prompting:

```bash
python3 skills/enhanced-memory/scripts/memory_salience.py          # Human-readable prompts
python3 skills/enhanced-memory/scripts/memory_salience.py --json   # Programmatic output
python3 skills/enhanced-memory/scripts/memory_salience.py --top 5  # More items
```

Scores `importance × staleness` considering: file type (topic > core > daily), size, access frequency, and query gap correlation.

### `scripts/crossref_memories.py` — Knowledge Graph

Builds cross-reference links between memory chunks using embedding similarity:

```bash
python3 skills/enhanced-memory/scripts/crossref_memories.py build          # Build index
python3 skills/enhanced-memory/scripts/crossref_memories.py show <file>    # Show refs for file
python3 skills/enhanced-memory/scripts/crossref_memories.py graph          # Graph statistics
```

Uses file-representative approach (top 5 chunks per file) to reduce O(n²) to manageable comparisons. Threshold: 0.75 cosine similarity.

## Configuration

All tunable constants are at the top of each script. Key parameters:

| Parameter | Default | Script | Purpose |
|-----------|---------|--------|---------|
| `VECTOR_WEIGHT` | 0.4 | search_memory.py | Weight for vector similarity |
| `KEYWORD_WEIGHT` | 0.25 | search_memory.py | Weight for keyword overlap |
| `FILEPATH_WEIGHT` | 0.25 | search_memory.py | Weight for filepath matching |
| `TEMPORAL_BOOST` | 3.0 | search_memory.py | Multiplier for date-matching files |
| `PRF_THRESHOLD` | 0.45 | search_memory.py | Score below which PRF activates |
| `SIMILARITY_THRESHOLD` | 0.75 | crossref_memories.py | Min similarity for cross-ref links |
| `MODEL` | nomic-embed-text | all | Ollama embedding model |

To use a different embedding model (e.g., `mxbai-embed-large`), change `MODEL` in each script and re-run `embed_memories.py`.

## Integration

To replace the default memory search, point your agent's search tool at these scripts. The scripts expect:
- `memory/` directory relative to workspace root containing `.md` files
- `memory/vectors.json` (created by `embed_memories.py`)
- Ollama running locally on port 11434

All scripts use only Python stdlib + Ollama HTTP API. No pip dependencies.
