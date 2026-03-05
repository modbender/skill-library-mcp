---
name: volcengine-ai-search-rag
description: Retrieval and RAG workflow on Volcengine AI stack. Use when users need embedding search, document indexing, top-k retrieval, grounding prompts, or search relevance tuning.
---

# volcengine-ai-search-rag

Implement retrieval-first answering with explicit indexing, retrieval, and grounding stages.

## Execution Checklist

1. Confirm corpus source and chunking strategy.
2. Generate embeddings and build/update index.
3. Retrieve top-k context with filters.
4. Build grounded answer with citations to retrieved chunks.

## Quality Rules

- Separate retrieval prompt from generation prompt.
- Keep chunk metadata (source, timestamp, id).
- Return confidence and fallback path if no hits.

## References

- `references/sources.md`
