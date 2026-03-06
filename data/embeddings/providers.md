# Embedding Providers

## OpenAI

| Model | Dimensions | Cost/1M tokens | Best for |
|-------|------------|----------------|----------|
| text-embedding-3-large | 3072 (or 256-3072) | $0.13 | Maximum quality |
| text-embedding-3-small | 1536 (or 256-1536) | $0.02 | Cost-effective |
| text-embedding-ada-002 | 1536 | $0.10 | Legacy, avoid |

**Features:**
- Dimension reduction via `dimensions` parameter
- 8191 token input limit
- Batch up to 2048 inputs

```python
from openai import OpenAI
client = OpenAI()

response = client.embeddings.create(
    input=["text to embed"],
    model="text-embedding-3-small",
    dimensions=512  # optional reduction
)
embedding = response.data[0].embedding
```

## Cohere

| Model | Dimensions | Cost/1M tokens | Best for |
|-------|------------|----------------|----------|
| embed-english-v3.0 | 1024 | $0.10 | English text |
| embed-multilingual-v3.0 | 1024 | $0.10 | 100+ languages |
| embed-english-light-v3.0 | 384 | $0.10 | Faster, smaller |

**Features:**
- `input_type` parameter: `search_document`, `search_query`, `classification`, `clustering`
- 512 token limit per input
- Batch up to 96 inputs

```python
import cohere
co = cohere.Client()

response = co.embed(
    texts=["text to embed"],
    model="embed-english-v3.0",
    input_type="search_document"
)
embedding = response.embeddings[0]
```

## Voyage AI

| Model | Dimensions | Cost/1M tokens | Best for |
|-------|------------|----------------|----------|
| voyage-large-2 | 1536 | $0.12 | General purpose |
| voyage-code-2 | 1536 | $0.12 | Code & technical |
| voyage-lite-02-instruct | 1024 | $0.02 | Cost-effective |

**Features:**
- Optimized for retrieval
- 16K token context for voyage-large-2
- Excellent for code search

```python
import voyageai
vo = voyageai.Client()

result = vo.embed(["text to embed"], model="voyage-large-2")
embedding = result.embeddings[0]
```

## Local Models (HuggingFace)

| Model | Dimensions | Memory | Best for |
|-------|------------|--------|----------|
| BAAI/bge-large-en-v1.5 | 1024 | ~1.3GB | Quality + speed |
| BAAI/bge-small-en-v1.5 | 384 | ~130MB | Resource-constrained |
| intfloat/e5-large-v2 | 1024 | ~1.3GB | Multilingual |
| nomic-ai/nomic-embed-text-v1.5 | 768 | ~550MB | Long context (8K) |

**Features:**
- No API costs
- Data stays local
- Requires GPU for speed

```python
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("BAAI/bge-large-en-v1.5")
embeddings = model.encode(["text to embed"], normalize_embeddings=True)
```

## Selection Decision Tree

1. **Need best quality, cost not an issue?** → OpenAI text-embedding-3-large
2. **Need multilingual?** → Cohere embed-multilingual-v3.0
3. **Embedding code/technical docs?** → Voyage voyage-code-2
4. **Need to keep data local?** → BGE or E5 models
5. **Cost-sensitive with good quality?** → OpenAI text-embedding-3-small
6. **Need image embeddings?** → OpenAI CLIP or Cohere multimodal

## Benchmarks (MTEB)

| Model | Average Score | Retrieval | Clustering |
|-------|---------------|-----------|------------|
| text-embedding-3-large | 64.6 | 59.2 | 49.0 |
| voyage-large-2 | 63.9 | 58.4 | 48.1 |
| embed-english-v3.0 | 64.5 | 58.0 | 49.2 |
| bge-large-en-v1.5 | 63.6 | 54.3 | 46.1 |
