# Vector Search — kNN, dense_vector, Hybrid Search (RRF)

## dense_vector Mapping (ES 9.x)

```json
PUT my-index
{
  "mappings": {
    "properties": {
      "text": { "type": "text" },
      "embedding": {
        "type": "dense_vector",
        "dims": 1024,
        "index": true,
        "similarity": "cosine",
        "index_options": {
          "type": "bbq_hnsw",
          "m": 16,
          "ef_construction": 100,
          "rescore_vector": { "oversample": 3.0 }
        }
      }
    }
  }
}
```

### bbq_hnsw (ES 9.x — recommended)
- **bbq** = Binary Quantization — compresses vectors, 4-32x memory reduction
- `rescore_vector.oversample: 3.0` — fetches 3x candidates then re-ranks with full precision
- Better than plain `hnsw` for production: same recall, much less memory
- Use `similarity: "cosine"` for normalized embeddings (most models)

### Similarity options
| | Use when |
|---|---|
| `cosine` | Normalized vectors (most embedding models) — default choice |
| `dot_product` | Already normalized, slightly faster |
| `l2_norm` | Euclidean distance, image/spatial search |

## kNN Query

### On-the-fly inference (via inference endpoint)
```json
POST my-index/_search
{
  "knn": {
    "field": "embedding",
    "query_vector_builder": {
      "text_embedding": {
        "model_id": "jina-embeddings-v3",
        "model_text": "healthy leafy greens"
      }
    },
    "k": 10,
    "num_candidates": 100
  },
  "_source": ["title", "category", "price"]
}
```

### Pre-computed vector
```json
POST my-index/_search
{
  "knn": {
    "field": "embedding",
    "query_vector": [0.23, -0.87, 0.14, ...],
    "k": 10,
    "num_candidates": 100
  }
}
```

### Tuning
- `k` — number of results to return (final)
- `num_candidates` — candidates evaluated per shard before ranking (trade recall vs speed)
- Rule of thumb: `num_candidates` = 5-10x `k`, min 100
- For better recall: increase `num_candidates` (slower but more accurate)

## Hybrid Search — BM25 + kNN with RRF

Best of both worlds: exact keyword matching + semantic understanding.
RRF (Reciprocal Rank Fusion) merges rankings without needing score normalization.

```json
POST my-index/_search
{
  "sub_searches": [
    {
      "query": {
        "multi_match": {
          "query": "healthy leafy greens",
          "fields": ["title^3", "description^2", "category"]
        }
      }
    },
    {
      "knn": {
        "field": "embedding",
        "query_vector_builder": {
          "text_embedding": {
            "model_id": "jina-embeddings-v3",
            "model_text": "healthy leafy greens"
          }
        },
        "k": 10,
        "num_candidates": 100
      }
    }
  ],
  "rank": {
    "rrf": {
      "rank_constant": 60,
      "window_size": 100
    }
  }
}
```

### RRF Parameters
- `rank_constant` (default 60) — smoothing factor; higher = less aggressive re-ranking
- `window_size` (default 100) — number of top docs from each sub_search to merge
- No score normalization needed — RRF uses rank positions, not raw scores

### When to use hybrid vs pure semantic
| | Pure semantic | Hybrid (RRF) |
|---|---|---|
| Intent-based queries | ✅ Best | ✅ Good |
| Exact term/ID lookups | ❌ Can miss | ✅ Catches |
| Multilingual | ✅ | ✅ |
| Very small index (<100 docs) | Overkill | Overkill |
| Production default | Consider | ✅ Recommended |

## Hybrid with Filters

Add filters without affecting scoring:
```json
POST my-index/_search
{
  "sub_searches": [ ... ],
  "rank": { "rrf": {} },
  "post_filter": {
    "bool": {
      "filter": [
        { "term": { "on_sale": true } },
        { "range": { "price": { "lte": 20 } } }
      ]
    }
  }
}
```

## Ingest Pipeline for Auto-Embedding

Generate embeddings at index time without changing application code:

```json
PUT _ingest/pipeline/jina-embedding-pipeline
{
  "processors": [
    {
      "inference": {
        "model_id": "jina-embeddings-v3",
        "input_output": {
          "input_field": "text_for_embedding",
          "output_field": "embedding"
        }
      }
    }
  ]
}

POST my-index/_doc?pipeline=jina-embedding-pipeline
{
  "title": "Fresh Broccoli",
  "text_for_embedding": "Fresh Broccoli Nutritious green broccoli. vegetables"
}
```
