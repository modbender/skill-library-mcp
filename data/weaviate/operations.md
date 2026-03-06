# Weaviate Operations Guide

## Batch Imports

### Always Use Batch for >100 Objects

```python
# ✅ Correct: dynamic batching with error handling
failed_objects = []

with client.batch.dynamic() as batch:
    for item in data:
        result = batch.add_object(
            properties=item,
            collection="Article"
        )
        
# Check for failures after batch completes
if client.batch.failed_objects:
    for obj in client.batch.failed_objects:
        print(f"Failed: {obj.original_uuid} - {obj.message}")
```

### Batch Strategies

```python
# Dynamic (auto-adjusts batch size)
with client.batch.dynamic() as batch:

# Fixed size (predictable memory)
with client.batch.fixed_size(batch_size=100) as batch:

# Rate limited (for external API vectorizers)
with client.batch.rate_limit(requests_per_minute=600) as batch:
```

### Bring Your Own Vectors

```python
with client.batch.dynamic() as batch:
    batch.add_object(
        properties={"title": "Doc"},
        collection="Article",
        vector=[0.1, 0.2, ...]  # Single vector
        # or
        vector={"title": [...], "content": [...]}  # Named vectors
    )
```

## Hybrid Search

### Alpha Parameter

```python
# alpha controls BM25 vs vector balance
collection.query.hybrid(
    query="machine learning",
    alpha=0.7,  # 0=BM25 only, 1=vector only, 0.5-0.75=balanced
    limit=10
)
```

Guidelines:
- `alpha=0.5` — Equal weight, good starting point
- `alpha=0.7` — Favor semantic (typical for RAG)
- `alpha=0.3` — Favor keyword (when exact terms matter)

### Fusion Types

```python
from weaviate.classes.query import HybridFusion

collection.query.hybrid(
    query="search",
    alpha=0.7,
    fusion_type=HybridFusion.RELATIVE_SCORE,  # or RANKED
)
```

## Filters

### Apply BEFORE Vector Search

```python
# ✅ Correct: filter reduces search space first
from weaviate.classes.query import Filter

collection.query.near_text(
    query="AI",
    filters=Filter.by_property("category").equal("tech"),
    limit=10
)
```

### Common Filter Operations

```python
Filter.by_property("status").equal("published")
Filter.by_property("views").greater_than(1000)
Filter.by_property("tags").contains_any(["ai", "ml"])
Filter.by_property("title").like("*intro*")

# Combine with AND/OR
(Filter.by_property("status").equal("published") & 
 Filter.by_property("views").greater_than(100))
```

## HNSW Index Tuning

### Parameters

| Parameter | Default | Effect |
|-----------|---------|--------|
| `ef` | -1 (dynamic) | Query time quality (higher=better, slower) |
| `efConstruction` | 128 | Build time quality (higher=better index) |
| `maxConnections` | 32 | Graph connectivity (higher for >1M vectors) |

### Configuration

```python
from weaviate.classes.config import Configure

client.collections.create(
    "LargeCollection",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    vector_index_config=Configure.VectorIndex.hnsw(
        ef=100,
        ef_construction=256,  # Higher for large datasets
        max_connections=64,   # Higher for >1M vectors
    )
)
```

### Memory Estimation

~4KB per vector with HNSW index. For 1M vectors ≈ 4GB RAM just for index.

## Debugging Empty Results

Check in order:

1. **Collection exists?**
   ```python
   client.collections.list_all()
   ```

2. **Objects exist?**
   ```python
   collection.aggregate.over_all(total_count=True)
   ```

3. **Vectors generated?**
   ```python
   response = collection.query.fetch_objects(
       limit=1,
       include_vector=True
   )
   print(response.objects[0].vector)  # Should not be None
   ```

4. **Filter syntax correct?**
   ```python
   # Test without filter first
   collection.query.near_text(query="test", limit=5)
   ```

5. **Distance threshold too strict?**
   Default distance metric is cosine. Results with distance > 0.5 may be filtered.
