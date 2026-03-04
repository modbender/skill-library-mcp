# Vector Storage

## Database Selection

| Database | Type | Best For | Limits |
|----------|------|----------|--------|
| Pinecone | Managed SaaS | Production, zero ops | Vendor lock-in |
| Weaviate | Self-hosted/Cloud | Hybrid search, GraphQL | More complex |
| Qdrant | Self-hosted/Cloud | Performance, Rust | Newer ecosystem |
| pgvector | PostgreSQL extension | Existing Postgres users | Scale limits |
| Chroma | Embedded | Prototyping, local dev | Not for production |
| Milvus | Self-hosted | Massive scale | Heavy infra |

## Pinecone

```python
from pinecone import Pinecone, ServerlessSpec

pc = Pinecone(api_key="...")
index = pc.Index("my-index")

# Upsert
index.upsert(vectors=[
    {"id": "doc1", "values": embedding, "metadata": {"source": "file.pdf"}}
])

# Query
results = index.query(
    vector=query_embedding,
    top_k=5,
    include_metadata=True,
    filter={"source": {"$eq": "file.pdf"}}
)
```

## pgvector (PostgreSQL)

```sql
-- Enable extension
CREATE EXTENSION vector;

-- Create table
CREATE TABLE documents (
    id SERIAL PRIMARY KEY,
    content TEXT,
    embedding vector(1536),
    metadata JSONB
);

-- Create index (HNSW recommended)
CREATE INDEX ON documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Query
SELECT id, content, 1 - (embedding <=> $1) AS similarity
FROM documents
ORDER BY embedding <=> $1
LIMIT 5;
```

```python
import psycopg2
from pgvector.psycopg2 import register_vector

conn = psycopg2.connect(...)
register_vector(conn)

cur = conn.cursor()
cur.execute("""
    SELECT content, 1 - (embedding <=> %s) as similarity
    FROM documents
    ORDER BY embedding <=> %s
    LIMIT 5
""", (embedding, embedding))
```

## Qdrant

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

client = QdrantClient("localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="documents",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE)
)

# Upsert
client.upsert(
    collection_name="documents",
    points=[
        PointStruct(id=1, vector=embedding, payload={"source": "doc.pdf"})
    ]
)

# Query with filter
results = client.search(
    collection_name="documents",
    query_vector=query_embedding,
    limit=5,
    query_filter={"must": [{"key": "source", "match": {"value": "doc.pdf"}}]}
)
```

## Chroma (Local/Prototyping)

```python
import chromadb

client = chromadb.Client()  # In-memory
# Or: chromadb.PersistentClient(path="./chroma_db")

collection = client.create_collection("documents")

# Add documents (auto-embeds with default model)
collection.add(
    documents=["text1", "text2"],
    metadatas=[{"source": "a"}, {"source": "b"}],
    ids=["id1", "id2"]
)

# Query
results = collection.query(
    query_texts=["search query"],
    n_results=5,
    where={"source": "a"}
)
```

## Index Types

| Type | Build Time | Query Time | Memory | When to Use |
|------|------------|------------|--------|-------------|
| Flat | O(1) | O(n) | Low | <10K vectors |
| IVF | O(n) | O(√n) | Medium | 10K-1M vectors |
| HNSW | O(n log n) | O(log n) | High | >100K, need speed |
| PQ | O(n) | O(n/k) | Very low | Memory-constrained |

## Schema Design Tips

1. **Store source hash** — Detect when re-embedding needed
2. **Include chunk position** — Reconstruct document order
3. **Namespace by tenant** — Multi-tenant isolation
4. **Timestamp everything** — Enable incremental updates
5. **Separate metadata** — Filter before vector search when possible

```python
document_schema = {
    "id": "uuid",
    "embedding": "vector(1536)",
    "content": "text",
    "content_hash": "md5",
    "source_file": "string",
    "chunk_index": "int",
    "total_chunks": "int",
    "created_at": "timestamp",
    "tenant_id": "string"
}
```
