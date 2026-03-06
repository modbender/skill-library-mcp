---
name: Weaviate
slug: weaviate
version: 1.0.0
description: Build vector search with Weaviate using v4 syntax, proper module configuration, and production-ready patterns.
metadata: {"clawdbot":{"emoji":"🔷","requires":{"bins":[]},"os":["linux","darwin","win32"]}}
---

## Critical: v4 Only (Dec 2024+)

v3 syntax is DEPRECATED. Before generating ANY Weaviate code:

1. **Verify client version** — must be `weaviate-client>=4.0`
2. **Use context managers** — `with weaviate.connect_to_*() as client:` or explicit `client.close()`
3. **New imports** — `from weaviate.classes.config import Configure, Property`

If you see v3 patterns (`weaviate.Client()`, `client.schema.create_class()`, `path=[...]` filters), **stop and rewrite**.

## Quick Reference

| Topic | File |
|-------|------|
| v3→v4 migration table | `v4-syntax.md` |
| Module configuration | `modules.md` |
| Batch, hybrid, HNSW | `operations.md` |

## v4 Syntax Essentials

```python
# Connection (ALWAYS close)
with weaviate.connect_to_local() as client:
    # Collections (not classes)
    collection = client.collections.get("Article")
    
    # Queries
    response = collection.query.hybrid("search term", alpha=0.7)
    
    # Vector access
    vector = obj.vector["default"]  # Dict, not List
    
    # Filters
    Filter.by_property("category").equal("tech")
```

## Scope

This skill covers:
- Schema design for RAG and semantic search
- Vectorizer and reranker module configuration
- Batch imports with error handling
- Hybrid search tuning (alpha parameter)
- HNSW index configuration for scale

## Core Rules

### 1. Always Verify Modules
Before using `text2vec-openai`, `generative-openai`, or rerankers, verify they're enabled:
```yaml
# docker-compose.yml
ENABLE_MODULES: 'text2vec-openai,generative-openai,reranker-cohere'
```

### 2. API Keys in Headers
```python
client = weaviate.connect_to_local(
    headers={"X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]}
)
```

### 3. Batch with Context Manager
```python
with client.batch.dynamic() as batch:
    for item in data:
        batch.add_object(properties=item, collection="Name")
```

### 4. Hybrid Search Alpha
- `alpha=0` → BM25 only (keyword)
- `alpha=1` → Vector only (semantic)
- `alpha=0.5-0.75` → Balanced (typical for RAG)

### 5. Apply Filters BEFORE Vector Search
Filters in `where` reduce the search space first — always filter before `near_text`/`near_vector`.

### 6. Named Vectors vs Single Vector
Choose one pattern per collection:
```python
# Single vector (simpler)
vectorizer_config=Configure.Vectorizer.text2vec_openai()

# Named vectors (multiple embeddings per object)
vector_config=[
    Configure.Vectors.text2vec_openai(name="content", source_properties=["body"]),
]
```

### 7. Debug Empty Results
Check in order: schema exists → vectorizer ran → distance threshold → filter syntax.
Use `_additional { vector }` to verify vectors were generated.
