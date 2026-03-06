# Search & Retrieval

## Similarity Metrics

| Metric | Formula | When to Use |
|--------|---------|-------------|
| Cosine | 1 - cos(θ) | Normalized vectors, most common |
| Dot Product | a · b | Unnormalized, magnitude matters |
| Euclidean (L2) | \|\|a - b\|\| | Dense clusters, outlier-sensitive |

**Rule:** If vectors are normalized, cosine = dot product. Most providers normalize.

## Query Optimization

### Pre-filter vs Post-filter

```python
# PRE-FILTER (faster): Filter metadata before vector search
results = index.query(
    vector=query_embedding,
    top_k=10,
    filter={"category": "technical"}  # Applied BEFORE similarity
)

# POST-FILTER (slower): Filter after retrieving more
results = index.query(
    vector=query_embedding,
    top_k=100  # Get more to ensure enough after filter
)
results = [r for r in results if r.metadata["category"] == "technical"][:10]
```

### Hybrid Search

Combine vector similarity with keyword matching:

```python
# Weaviate hybrid search
results = client.query.get(
    "Document",
    ["content"]
).with_hybrid(
    query="machine learning",
    alpha=0.5  # 0=keyword, 1=vector
).with_limit(10).do()

# Manual hybrid (any DB)
def hybrid_search(query, top_k=10, alpha=0.5):
    vector_results = vector_search(query, top_k * 2)
    keyword_results = keyword_search(query, top_k * 2)
    
    combined = {}
    for i, r in enumerate(vector_results):
        combined[r.id] = combined.get(r.id, 0) + alpha * (1 / (i + 1))
    for i, r in enumerate(keyword_results):
        combined[r.id] = combined.get(r.id, 0) + (1 - alpha) * (1 / (i + 1))
    
    return sorted(combined.items(), key=lambda x: -x[1])[:top_k]
```

### Reranking

Two-stage: fast retrieval then precise reranking:

```python
import cohere

co = cohere.Client()

# Stage 1: Fast vector search
candidates = index.query(vector=query_embedding, top_k=100)

# Stage 2: Rerank with cross-encoder
reranked = co.rerank(
    query="user question",
    documents=[c.content for c in candidates],
    model="rerank-english-v3.0",
    top_n=10
)
```

## Query Expansion

Improve recall by expanding the query:

```python
def expand_query(query):
    # Generate variations
    prompt = f"Generate 3 alternative phrasings of: {query}"
    variations = llm.generate(prompt)
    
    # Embed all variations
    all_queries = [query] + variations
    embeddings = embed_batch(all_queries)
    
    # Average or search with all
    avg_embedding = np.mean(embeddings, axis=0)
    return avg_embedding

# Or: Multi-query retrieval
def multi_query_search(query, top_k=10):
    variations = generate_variations(query)
    all_results = []
    for q in [query] + variations:
        results = index.query(embed(q), top_k=top_k)
        all_results.extend(results)
    return deduplicate_and_rank(all_results)[:top_k]
```

## Threshold Tuning

Don't return everything—filter by similarity:

```python
SIMILARITY_THRESHOLD = 0.75

def search_with_threshold(query, top_k=10):
    results = index.query(embed(query), top_k=top_k)
    return [r for r in results if r.score >= SIMILARITY_THRESHOLD]
```

**Calibration:**
1. Run queries with known good matches
2. Record similarity scores
3. Set threshold at 90th percentile of good matches

## MMR (Maximal Marginal Relevance)

Avoid redundant results:

```python
def mmr_search(query_embedding, top_k=10, lambda_param=0.5):
    candidates = index.query(query_embedding, top_k=top_k * 3)
    selected = []
    
    while len(selected) < top_k and candidates:
        # Score: relevance - redundancy
        scores = []
        for c in candidates:
            relevance = cosine_similarity(query_embedding, c.embedding)
            redundancy = max(
                cosine_similarity(c.embedding, s.embedding) 
                for s in selected
            ) if selected else 0
            score = lambda_param * relevance - (1 - lambda_param) * redundancy
            scores.append((c, score))
        
        best = max(scores, key=lambda x: x[1])[0]
        selected.append(best)
        candidates.remove(best)
    
    return selected
```

## Debugging Poor Results

| Symptom | Likely Cause | Fix |
|---------|--------------|-----|
| Wrong documents | Query too vague | Query expansion, be specific |
| Misses relevant docs | Chunk too large | Smaller chunks, more overlap |
| Same doc repeatedly | No diversity | MMR, dedupe by source |
| Low scores everywhere | Model mismatch | Same model for query/docs |
| Slow queries | No index | Add HNSW/IVF index |
