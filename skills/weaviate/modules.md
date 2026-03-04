# Weaviate Module Configuration

## Enabling Modules

Modules must be enabled at server startup:

```yaml
# docker-compose.yml
services:
  weaviate:
    environment:
      ENABLE_MODULES: 'text2vec-openai,generative-openai,reranker-cohere'
      # Or enable ALL API-based modules (v1.33+):
      ENABLE_API_BASED_MODULES: 'true'
```

## Vectorizers

### text2vec-openai

```python
from weaviate.classes.config import Configure

client.collections.create(
    "Article",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(
        model="text-embedding-3-small",  # or "text-embedding-3-large"
        dimensions=1536,  # 1536 for small, 3072 for large
    ),
    properties=[...]
)
```

Headers required:
```python
client = weaviate.connect_to_local(
    headers={"X-OpenAI-Api-Key": os.environ["OPENAI_API_KEY"]}
)
```

### text2vec-cohere

```python
vectorizer_config=Configure.Vectorizer.text2vec_cohere(
    model="embed-multilingual-v3.0"
)
```

Headers: `{"X-Cohere-Api-Key": ...}`

### Local Transformers

```python
vectorizer_config=Configure.Vectorizer.text2vec_transformers()
```

No API key needed — runs locally. Add to docker-compose:
```yaml
ENABLE_MODULES: 'text2vec-transformers'
```

## Named Vectors (Multiple Embeddings)

For different embeddings per property:

```python
from weaviate.classes.config import Configure

client.collections.create(
    "Document",
    vector_config=[
        Configure.Vectors.text2vec_openai(
            name="title_vector",
            source_properties=["title"],
            model="text-embedding-3-small"
        ),
        Configure.Vectors.text2vec_openai(
            name="content_vector", 
            source_properties=["body", "summary"],
            model="text-embedding-3-large"
        ),
    ],
    properties=[...]
)
```

Query specific vector:
```python
collection.query.near_text(
    query="search",
    target_vectors=["content_vector"]
)
```

## Generative Modules

```python
from weaviate.classes.config import Configure

client.collections.create(
    "Article",
    vectorizer_config=Configure.Vectorizer.text2vec_openai(),
    generative_config=Configure.Generative.openai(model="gpt-4"),
)
```

Usage:
```python
response = collection.generate.near_text(
    query="AI trends",
    grouped_task="Summarize these articles"
)
print(response.generated)
```

## Rerankers

```python
reranker_config=Configure.Reranker.cohere(model="rerank-english-v3.0")
# or
reranker_config=Configure.Reranker.voyageai()
```

Usage:
```python
response = collection.query.near_text(
    query="search",
    rerank=Rerank(prop="content", query="rerank query")
)
```

## Common Errors

### "no module with name 'X' present"
Module not enabled in docker-compose. Add to `ENABLE_MODULES`.

### "API key not provided"
Missing header. Add `X-{Provider}-Api-Key` to connection.

### "vectorizer not configured"
Collection created without `vectorizer_config`. Either:
1. Add vectorizer config when creating collection
2. Bring your own vectors with `vector=` parameter
