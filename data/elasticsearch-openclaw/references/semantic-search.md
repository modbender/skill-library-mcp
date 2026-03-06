# Semantic Search — JINA & semantic_text

## semantic_text Field Type (ES 8.11+, recommended)

The simplest way to add semantic search. ES handles embedding generation automatically
at index time and query time via the Inference API — no manual vector management needed.

```json
PUT my-index
{
  "mappings": {
    "properties": {
      "title":   { "type": "text" },
      "content": { "type": "text" },
      "semantic_content": {
        "type": "semantic_text",
        "inference_id": "my-inference-endpoint"
      }
    }
  }
}
```

Index a document — embedding generated automatically:
```json
POST my-index/_doc
{
  "title": "Fresh Broccoli",
  "content": "Nutritious green broccoli, rich in vitamins.",
  "semantic_content": "Fresh Broccoli Nutritious green broccoli, rich in vitamins. vegetables"
}
```

Query:
```json
POST my-index/_search
{
  "query": {
    "semantic": {
      "field": "semantic_content",
      "query": "healthy leafy greens"
    }
  }
}
```

## Inference Endpoints — Setup

### JINA v3 Inference Endpoint

```json
PUT _inference/text_embedding/jina-embeddings-v3
{
  "service": "jinaai",
  "service_settings": {
    "api_key": "jina_xxxxxx",
    "model_id": "jina-embeddings-v3"
  }
}
```

**Model details:**
- `jina-embeddings-v3` — 1024 dimensions, multilingual (100+ languages)
- Requires JINA API key: https://jina.ai/embeddings (free tier available)
- Dense vector embeddings via External Inference API
- ⚠️ Every query and indexing operation calls api.jina.ai

**Check existing inference endpoints:**
```bash
GET _inference
```

## semantic_text vs manual dense_vector

| | semantic_text | dense_vector (manual) |
|---|---|---|
| Embedding generation | Automatic | Manual (you call the API) |
| Complexity | Low | High |
| Flexibility | Less | More |
| Recommended | ✅ Yes, default choice | Only if you need custom control |

## Troubleshooting

- `inference_not_found` → inference endpoint doesn't exist, check with `GET _inference` or create it first
- Slow first query after idle → external API cold start, normal on free tier
- Embeddings not updating → re-index document, semantic_text does not auto-update on inference model change
- `unauthorized` → check JINA API key validity and quotas
