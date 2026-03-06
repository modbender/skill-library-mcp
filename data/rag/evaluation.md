# RAG Evaluation & Debugging

## Retrieval Metrics

| Metric | What It Measures | Target |
|--------|------------------|--------|
| Recall@K | % of relevant docs in top-K | >0.8 |
| MRR | Reciprocal rank of first relevant | >0.5 |
| NDCG | Ranked relevance quality | >0.7 |
| Precision@K | % of top-K that are relevant | >0.6 |

## Generation Metrics

| Metric | What It Measures | How to Evaluate |
|--------|------------------|-----------------|
| Faithfulness | Answer supported by context | LLM-as-judge or human |
| Relevance | Answer addresses query | LLM-as-judge |
| Correctness | Factually accurate | Ground truth comparison |
| Coherence | Well-structured response | Human evaluation |

## Evaluation Dataset Creation

### Synthetic Generation
```python
# For each document chunk:
# 1. Generate questions the chunk answers
# 2. Create variations (paraphrase, specificity)
# 3. Add negative examples (unanswerable)
```

### From Production Logs
```python
# Capture: query, retrieved_chunks, user_feedback
# Label: thumbs up/down, corrections, reformulations
```

### Gold Standard Set
- 50-100 curated query-answer-source triples
- Cover edge cases and common queries
- Update quarterly as corpus evolves

## Debugging Retrieval Issues

### "Wrong documents retrieved"
1. Check query embedding quality (is query too vague?)
2. Examine chunk content (was source poorly chunked?)
3. Try hybrid search (add keyword matching)
4. Consider query expansion

### "Relevant doc exists but not retrieved"
1. Check if chunk contains key terms
2. Verify document was indexed (hash check)
3. Increase top_k and rerank
4. Examine embedding similarity scores

### "Low similarity scores across the board"
1. Embedding model mismatch? (query vs doc models)
2. Domain-specific vocabulary not captured?
3. Consider fine-tuning embeddings

## Production Monitoring

### Key Metrics to Track
```yaml
retrieval:
  - avg_similarity_score
  - retrieval_latency_p50/p95
  - empty_result_rate
  - chunks_per_query

generation:
  - response_latency
  - token_usage
  - error_rate
  - user_feedback_rate
```

### Alerting Rules
- Empty retrieval > 5% of queries
- Avg similarity < 0.5 (possible drift)
- Latency p95 > 3s
- Error rate > 1%

## A/B Testing RAG Configs

### What to Test
- Chunk size (256 vs 512 vs 1024)
- Overlap percentage (0%, 10%, 20%)
- Top-K values
- Reranker vs no reranker
- Hybrid alpha weighting

### Minimum Sample Size
- 1000+ queries for statistical significance
- Segment by query type if heterogeneous

### Success Metrics
- User satisfaction (feedback, reformulation rate)
- Task completion rate
- Engagement (follow-up questions)
