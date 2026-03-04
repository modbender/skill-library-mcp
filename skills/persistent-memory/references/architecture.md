# Memory Architecture

## Why Three Layers?

MEMORY.md alone is insufficient — the agent "forgets" to check it, or the file grows too large for effective context injection. Each layer solves a different problem:

- **L1 (Markdown):** Human-readable, editable, version-controllable. The source of truth.
- **L2 (Vector/ChromaDB):** Semantic search. The agent doesn't need to know which file contains a fact — it searches by meaning and gets the answer.
- **L3 (Graph/NetworkX):** Relationship traversal. Understands that "Tesseract" is connected to "OCR" which is connected to "Visual Core." Enables chain-of-thought over the knowledge base.

## How They Sync

L1 is the source. The indexer reads all markdown files, chunks them by header, generates embeddings (L2), and extracts nodes/edges (L3). Running the indexer updates both L2 and L3 from L1.

```
MEMORY.md + reference/*.md + memory/*.md
         ↓ indexer.py
    ChromaDB (L2) + NetworkX graph (L3)
```

## Knowledge Graph Extraction

The graph builder automatically extracts:
- **Nodes:** Section headers become "section" nodes. `**Bolded terms**` become "concept" nodes.
- **Edges:** Structural (section → concept via "contains"), semantic (cross-references via keyword matching: "depends on", "enables", "replaces", etc.)

## Embedding Model

Uses `sentence-transformers/all-MiniLM-L6-v2`:
- 384-dimensional embeddings
- Fast inference on CPU (~0.03s per chunk)
- Good semantic similarity for English text
- ~80MB model size

## Design Decisions

- **ChromaDB over FAISS:** Persistent by default, no server needed, built-in metadata filtering
- **NetworkX over Neo4j:** Pure Python, no daemon, persists to JSON, sufficient for workspace-scale graphs
- **Lazy loading:** Heavy ML dependencies load on-demand to avoid startup crashes in constrained environments
- **all-MiniLM-L6-v2 over larger models:** Best speed/quality tradeoff for frequent indexing on CPU-only machines
