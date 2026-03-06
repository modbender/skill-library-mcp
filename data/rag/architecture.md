# RAG Architecture

## Pipeline Components

```
Documents → Chunking → Embedding → Vector DB → Retrieval → Reranking → LLM
```

### 1. Document Processing
- **Ingestion formats:** PDF, HTML, Markdown, Word, plain text
- **Parsing:** Extract text while preserving structure (headers, tables, lists)
- **Metadata:** Capture source, date, author, section for filtering

### 2. Chunking Strategies

| Strategy | Best For | Chunk Size |
|----------|----------|------------|
| Fixed-size | Simple docs | 256-512 tokens |
| Recursive | Structured content | Varies by delimiter |
| Semantic | Dense technical docs | Based on topic boundaries |
| Sentence | Q&A, chat | 3-5 sentences |

**Critical rules:**
- Overlap 10-20% between chunks to preserve context at boundaries
- Never split mid-sentence or mid-code-block
- Include parent headers in child chunks for context

### 3. Embedding Models

| Model | Dimensions | Speed | Quality | Cost |
|-------|------------|-------|---------|------|
| OpenAI ada-002 | 1536 | Fast | Good | $0.0001/1K |
| OpenAI text-3-small | 1536 | Fast | Better | $0.00002/1K |
| OpenAI text-3-large | 3072 | Medium | Best | $0.00013/1K |
| Cohere embed-v3 | 1024 | Fast | Excellent | $0.0001/1K |
| BGE-large-en | 1024 | Self-hosted | Excellent | Free |

**When to self-host:** Sensitive data, high volume, latency requirements

### 4. Vector Databases

| DB | Hosting | Scale | Best For |
|----|---------|-------|----------|
| Pinecone | Managed | Billions | Production, zero-ops |
| Weaviate | Both | Millions | Hybrid search, filtering |
| Qdrant | Both | Millions | Performance, Rust |
| pgvector | Self | Millions | Postgres ecosystem |
| Chroma | Self | Thousands | Prototyping, local dev |

### 5. Retrieval Strategies

**Basic:** Vector similarity (cosine, dot product)

**Hybrid:** Combine vector + keyword (BM25)
```
final_score = α * vector_score + (1-α) * bm25_score
```
Typical α: 0.5-0.7

**Reranking:** Apply cross-encoder after initial retrieval
- Cohere Rerank
- BGE Reranker
- Cross-encoder models

### 6. RAG Variants

| Type | Description | When to Use |
|------|-------------|-------------|
| Naive RAG | Retrieve → Generate | Simple use cases |
| Advanced RAG | Pre/post-retrieval optimization | Production systems |
| Modular RAG | Swappable components | Experimentation |
| Agentic RAG | Multi-step retrieval | Complex queries |
| Graph RAG | Entity relationships | Knowledge graphs |

## Architecture Decisions Checklist

- [ ] Document types and expected volume?
- [ ] Latency requirements (p95 target)?
- [ ] Update frequency (real-time vs batch)?
- [ ] Multi-tenancy requirements?
- [ ] Compliance constraints (data residency)?
- [ ] Budget (embedding costs, hosting)?
