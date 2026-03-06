---
name: Embeddings
slug: embeddings
description: Generate, store, and search vector embeddings with provider selection, chunking strategies, and similarity search optimization.
---

## When to Use

User wants to convert text/images to vectors, build semantic search, or integrate embeddings into applications.

## Quick Reference

| Topic | File |
|-------|------|
| Provider comparison & selection | `providers.md` |
| Chunking strategies & code | `chunking.md` |
| Vector database patterns | `storage.md` |
| Search & retrieval tuning | `search.md` |

## Core Capabilities

1. **Generate embeddings** — Call provider APIs (OpenAI, Cohere, Voyage, local models)
2. **Chunk content** — Split documents with overlap, semantic boundaries, token limits
3. **Store vectors** — Insert into Pinecone, Weaviate, Qdrant, pgvector, Chroma
4. **Similarity search** — Query with top-k, filters, hybrid search
5. **Batch processing** — Handle large datasets with rate limiting and retries
6. **Model comparison** — Evaluate embedding quality for specific use cases

## Decision Checklist

Before recommending approach, ask:
- [ ] What content type? (text, code, images, multimodal)
- [ ] Volume and update frequency?
- [ ] Latency requirements? (real-time vs batch)
- [ ] Budget constraints? (API costs vs self-hosted)
- [ ] Existing infrastructure? (cloud provider, database)

## Critical Rules

- **Same model everywhere** — Query embeddings MUST use identical model as document embeddings
- **Normalize before storage** — Most similarity metrics assume unit vectors
- **Chunk with overlap** — 10-20% overlap prevents context loss at boundaries
- **Batch API calls** — Never embed one item at a time in production
- **Cache embeddings** — Regenerating is expensive; store with source hash
- **Monitor dimensions** — Higher isn't always better; 768-1536 is usually optimal

## Provider Quick Selection

| Need | Provider | Why |
|------|----------|-----|
| Best quality, any cost | OpenAI `text-embedding-3-large` | Top benchmarks |
| Cost-sensitive | OpenAI `text-embedding-3-small` | 5x cheaper, 80% quality |
| Multilingual | Cohere `embed-multilingual-v3` | 100+ languages |
| Code/technical | Voyage `voyage-code-2` | Optimized for code |
| Privacy/offline | Local (e5, bge, nomic) | No data leaves machine |
| Images | OpenAI CLIP, Cohere multimodal | Cross-modal search |

## Common Patterns

```python
# Batch embedding with retry
def embed_batch(texts, model="text-embedding-3-small"):
    results = []
    for chunk in batched(texts, 100):  # API limit
        response = client.embeddings.create(input=chunk, model=model)
        results.extend([e.embedding for e in response.data])
    return results

# Similarity search with filter
results = index.query(
    vector=query_embedding,
    top_k=10,
    filter={"category": "technical"},
    include_metadata=True
)
```
