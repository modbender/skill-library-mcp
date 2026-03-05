# Query Patterns — Qdrant

## Basic Search

```python
client.search(
    collection_name="my_collection",
    query_vector=[0.1, 0.2, ...],  # embedding
    limit=10
)
```

## Filtered Search

```python
from qdrant_client.models import Filter, FieldCondition, MatchValue

client.search(
    collection_name="my_collection",
    query_vector=embedding,
    query_filter=Filter(
        must=[
            FieldCondition(key="category", match=MatchValue(value="tech"))
        ]
    ),
    limit=10
)
```

## Complex Filters

```python
Filter(
    must=[
        FieldCondition(key="status", match=MatchValue(value="active"))
    ],
    should=[
        FieldCondition(key="priority", match=MatchValue(value="high")),
        FieldCondition(key="priority", match=MatchValue(value="critical"))
    ],
    must_not=[
        FieldCondition(key="archived", match=MatchValue(value=True))
    ]
)
```

- `must`: all conditions required (AND)
- `should`: at least one required (OR)
- `must_not`: exclude matches (NOT)

## Range Filters

```python
from qdrant_client.models import Range

FieldCondition(
    key="price",
    range=Range(gte=10.0, lte=100.0)
)
```

## Scroll (Pagination)

```python
# First page
results, next_offset = client.scroll(
    collection_name="my_collection",
    scroll_filter=filter,
    limit=100
)

# Next pages
while next_offset:
    results, next_offset = client.scroll(
        collection_name="my_collection",
        scroll_filter=filter,
        limit=100,
        offset=next_offset
    )
```

## Search with Score Threshold

```python
client.search(
    collection_name="my_collection",
    query_vector=embedding,
    score_threshold=0.8,  # only return if similarity >= 0.8
    limit=10
)
```

## Batch Search

```python
from qdrant_client.models import SearchRequest

client.search_batch(
    collection_name="my_collection",
    requests=[
        SearchRequest(vector=emb1, limit=5),
        SearchRequest(vector=emb2, limit=5, filter=my_filter),
    ]
)
```

## Recommend (Find Similar to Existing Points)

```python
client.recommend(
    collection_name="my_collection",
    positive=[point_id_1, point_id_2],  # find similar to these
    negative=[point_id_3],              # avoid similar to this
    limit=10
)
```
