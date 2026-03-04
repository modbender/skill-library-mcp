# Performance Tuning — Qdrant

## Batch Insertion

```python
from qdrant_client.models import PointStruct

# Good: batch insert
client.upsert(
    collection_name="my_collection",
    points=[
        PointStruct(id=i, vector=vec, payload=pay)
        for i, (vec, pay) in enumerate(data_batch)
    ],
    wait=False  # async insert
)

# Bad: one by one
for i, (vec, pay) in enumerate(data):
    client.upsert(...)  # N round trips
```

## Payload Indexing

```python
# Index fields used in filters
client.create_payload_index(
    collection_name="my_collection",
    field_name="category",
    field_schema="keyword"  # or "integer", "float", "geo", "text"
)
```

| Schema | Use For |
|--------|---------|
| keyword | exact match (status, category) |
| integer | numeric IDs, counts |
| float | prices, scores, ranges |
| text | full-text search within payload |
| geo | location-based filtering |

## HNSW Tuning

```python
from qdrant_client.models import HnswConfigDiff

client.update_collection(
    collection_name="my_collection",
    hnsw_config=HnswConfigDiff(
        m=32,             # connections per node (default 16)
        ef_construct=200  # build quality (default 100)
    )
)
```

| Parameter | Higher = | Trade-off |
|-----------|----------|-----------|
| m | better recall | more memory, slower insert |
| ef_construct | better index quality | slower index build |

## Quantization (Memory Reduction)

```python
from qdrant_client.models import ScalarQuantization, ScalarQuantizationConfig

# Scalar: 4x memory reduction
client.update_collection(
    collection_name="my_collection",
    quantization_config=ScalarQuantization(
        scalar=ScalarQuantizationConfig(type="int8")
    )
)
```

| Type | Memory | Quality |
|------|--------|---------|
| None | 100% | Best |
| Scalar (int8) | ~25% | Good |
| Product | ~12% | Acceptable |

## On-Disk Storage

```python
from qdrant_client.models import VectorParams, Distance

# For large collections
client.create_collection(
    collection_name="large_collection",
    vectors_config=VectorParams(
        size=1536,
        distance=Distance.COSINE,
        on_disk=True  # store vectors on disk
    )
)
```

## Search Optimization

```python
client.search(
    collection_name="my_collection",
    query_vector=embedding,
    limit=10,
    search_params={
        "hnsw_ef": 128  # search quality (default 100)
    }
)
```

Higher `hnsw_ef` = better recall, slower search.

## Collection Sharding

For 10M+ vectors:
```python
client.create_collection(
    collection_name="huge_collection",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
    shard_number=4  # distribute across nodes
)
```
