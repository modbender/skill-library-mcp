---
name: Qdrant
slug: qdrant
version: 1.0.0
description: Build vector search with Qdrant using collections, payloads, filtering, and optimized indexing for semantic similarity.
metadata: {"clawdbot":{"emoji":"🔍","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## When to Use

User needs vector similarity search, semantic search, or recommendation systems. Agent handles collection design, point insertion, filtered queries, and index optimization.

## Quick Reference

| Topic | File |
|-------|------|
| Query patterns | `queries.md` |
| Performance tuning | `performance.md` |

## Core Rules

### 1. Collection Setup
- Set vector dimension to match embedding model (e.g., OpenAI ada-002 = 1536)
- Choose distance metric deliberately: `Cosine` for normalized embeddings, `Dot` for raw scores, `Euclid` for absolute distance
- Wrong dimension = silent failures with zero results

### 2. Payload Strategy
- Store filterable metadata as payload fields
- Index payload fields used in filters: `create_payload_index`
- Don't store large blobs in payloads — use external storage + reference ID

### 3. Batch Operations
- Insert points in batches of 100-1000, not one by one
- Use `upsert` to handle duplicates by ID
- Parallel uploads with `wait=false` then verify with collection info

### 4. Filtering vs Post-Filtering
| When | Use |
|------|-----|
| Known constraints | Filter in query (pre-filter) |
| Score threshold | `score_threshold` parameter |
| Complex logic | Combine `must`, `should`, `must_not` |

- Pre-filtering reduces search space = faster
- Post-filtering on results = slower, may miss relevant items

### 5. Search vs Scroll
| Need | Use |
|------|-----|
| Top-K similar | `search` |
| All matching | `scroll` with filter |
| Paginated results | `scroll` with `offset` |
| Export/backup | `scroll` all with pagination |

### 6. Index Optimization
- HNSW parameters: increase `m` for recall, increase `ef_construct` for index quality
- Default `m=16, ef_construct=100` works for most cases
- For millions of vectors: enable `on_disk` storage
- Use quantization (`scalar` or `product`) to reduce memory 4-8x

### 7. Multi-Tenancy
- Payload field for tenant ID + filter on every query
- Or separate collections per tenant (simpler isolation, harder to manage)
- Never expose one tenant's data to another

## Common Traps

- Creating collection with wrong vector size → all searches return empty
- Forgetting `wait=true` on insert → querying before data indexed
- Using scroll without limit → memory exhaustion on large collections
- Not indexing payload fields → filter queries scan entire collection
- Storing embeddings in payload instead of vector field → defeats purpose
