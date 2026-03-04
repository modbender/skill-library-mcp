# RAG Engineering — Complete Retrieval-Augmented Generation System

> Build production RAG systems that actually work. From chunking strategy to evaluation — the complete methodology.

You are an expert RAG engineer. When the user needs to build, optimize, or debug a RAG system, follow this complete methodology.

---

## Phase 1: RAG Architecture Assessment

### Quick Health Check (Existing Systems)

| Signal | Healthy | Warning | Critical |
|--------|---------|---------|----------|
| Answer relevance | >85% users satisfied | 60-85% | <60% |
| Retrieval precision@5 | >70% relevant chunks | 40-70% | <40% |
| Hallucination rate | <5% | 5-15% | >15% |
| Latency (P95) | <3s | 3-8s | >8s |
| Context utilization | >60% of retrieved used | 30-60% | <30% |
| Cost per query | <$0.05 | $0.05-0.20 | >$0.20 |

### RAG Project Brief

```yaml
rag_brief:
  project: "[name]"
  date: "YYYY-MM-DD"

  # What problem are we solving?
  use_case: "[customer support / code search / document Q&A / research / legal / medical]"
  user_persona: "[who asks questions]"
  query_types:
    - factual: "[percentage] — direct fact lookup"
    - analytical: "[percentage] — synthesis across documents"
    - procedural: "[percentage] — how-to, step-by-step"
    - comparative: "[percentage] — compare X vs Y"
    - conversational: "[percentage] — multi-turn follow-ups"

  # What data do we have?
  corpus:
    total_documents: "[count]"
    total_size: "[GB/TB]"
    document_types:
      - type: "[PDF/HTML/markdown/code/JSON/CSV]"
        count: "[count]"
        avg_length: "[pages/tokens]"
    update_frequency: "[static / daily / real-time]"
    languages: ["en", "..."]
    quality: "[curated / mixed / noisy]"

  # Requirements
  accuracy_target: "[% — start with 85%]"
  latency_target: "[ms P95]"
    max_cost_per_query: "[$]"
  scale: "[queries/day]"
  multi_turn: "[yes/no]"
  citations_required: "[yes/no]"

  # Constraints
  deployment: "[cloud / on-prem / hybrid]"
  data_sensitivity: "[public / internal / PII / regulated]"
  budget: "[$/month for infrastructure]"
```

### RAG Architecture Decision Tree

```
Is your corpus < 100 documents AND < 50 pages each?
├─ YES → Consider full-context stuffing (no RAG needed)
│        Use: Long-context model (Gemini 1M, Claude 200K)
│        When: Static docs, low query volume, budget allows
│
└─ NO → RAG is appropriate
         │
         Is real-time freshness critical?
         ├─ YES → Streaming RAG with incremental indexing
         └─ NO → Batch-indexed RAG
                  │
                  Do queries need multi-step reasoning?
                  ├─ YES → Agentic RAG (query planning + tool use)
                  └─ NO → Standard retrieval pipeline
                           │
                           Single document type?
                           ├─ YES → Single-index RAG
                           └─ NO → Multi-index with routing
```

### Architecture Patterns

| Pattern | Use Case | Complexity | Quality |
|---------|----------|------------|---------|
| **Naive RAG** | Simple Q&A, prototypes | Low | Medium |
| **Advanced RAG** | Production systems | Medium | High |
| **Modular RAG** | Complex multi-source | High | Highest |
| **Agentic RAG** | Multi-step research | Highest | Highest |
| **Graph RAG** | Entity-heavy domains | High | High for relational queries |
| **Hybrid RAG** | Mixed query types | Medium-High | High |

---

## Phase 2: Data Ingestion & Preprocessing

### Document Processing Pipeline

```
Raw Documents → Extraction → Cleaning → Enrichment → Chunking → Embedding → Indexing
```

### Extraction Strategy by Document Type

| Document Type | Extraction Tool | Key Challenges | Quality Tips |
|--------------|----------------|----------------|--------------|
| **PDF** | PyMuPDF, Unstructured, Docling | Tables, images, multi-column | Use layout-aware parser; OCR for scanned |
| **HTML** | BeautifulSoup, Trafilatura | Boilerplate, navigation | Extract main content only; preserve headers |
| **Markdown** | Direct parse | Minimal | Preserve structure; handle frontmatter |
| **Code** | Tree-sitter, AST | Context loss | Include file path + imports as metadata |
| **CSV/JSON** | pandas, jq | Schema understanding | Convert rows to natural language |
| **DOCX/PPTX** | python-docx, python-pptx | Formatting, embedded media | Extract text + table structure |
| **Images** | GPT-4V, Claude Vision | OCR accuracy | Generate text descriptions; store as metadata |
| **Audio/Video** | Whisper, Assembly | Timestamps, speakers | Chunk by speaker turn or topic segment |

### Cleaning Checklist

- [ ] Remove headers/footers/page numbers (PDF artifacts)
- [ ] Normalize whitespace (collapse multiple spaces/newlines)
- [ ] Fix encoding issues (UTF-8 normalize)
- [ ] Remove boilerplate (disclaimers, repeated navigation)
- [ ] Preserve meaningful formatting (tables, lists, code blocks)
- [ ] Handle special characters and Unicode consistently
- [ ] Detect and flag low-quality documents (OCR confidence < 80%)
- [ ] Deduplicate (exact + near-duplicate detection)

### Metadata Enrichment

Always extract and store:

```yaml
document_metadata:
  source_id: "[unique document identifier]"
  source_url: "[original URL or file path]"
  title: "[document title]"
  author: "[if available]"
  created_date: "[ISO 8601]"
  modified_date: "[ISO 8601]"
  document_type: "[pdf/html/md/code/...]"
  language: "[ISO 639-1]"
  section_hierarchy: ["Chapter", "Section", "Subsection"]
  tags: ["auto-generated", "topic", "tags"]
  access_level: "[public/internal/restricted]"
  quality_score: "[0-100 from cleaning pipeline]"
```

**Enrichment strategies:**
- Auto-generate summaries per document (for hybrid search)
- Extract entities (people, companies, products, dates)
- Classify by topic/category
- Generate hypothetical questions (HyDE technique at index time)

---

## Phase 3: Chunking Strategy

### The Chunking Decision Is Critical

Bad chunking is the #1 cause of poor RAG quality. No amount of model sophistication fixes bad chunks.

### Chunking Method Selection

| Method | Best For | Chunk Quality | Implementation |
|--------|----------|---------------|----------------|
| **Fixed-size** | Homogeneous text, quick prototype | Medium | Simple |
| **Recursive character** | General purpose, structured docs | Good | LangChain default |
| **Semantic** | Varied content, topic shifts | High | Embedding-based |
| **Document-structure** | Technical docs, legal, academic | Highest | Custom per doc type |
| **Agentic/LLM** | High-value docs, complex structure | Highest | Expensive |
| **Sentence-window** | Dense factual content | Good | Sentence + context |
| **Parent-child** | Hierarchical docs, manuals | High | Two-level index |

### Chunking Decision Tree

```
Is your content highly structured (headers, sections, numbered)?
├─ YES → Document-structure chunking
│        Split on: H1 > H2 > H3 > paragraph boundaries
│        Keep: section title chain as metadata
│
└─ NO → Is content topically diverse within documents?
         ├─ YES → Semantic chunking
         │        Split when: embedding similarity drops below threshold
         │        Typical threshold: cosine similarity < 0.75
         │
         └─ NO → Recursive character splitting
                  With: chunk_size=512, overlap=64 (tokens)
                  Separators: ["\n\n", "\n", ". ", " "]
```

### Chunk Size Guidelines

| Use Case | Target Tokens | Overlap | Rationale |
|----------|--------------|---------|-----------|
| **Factual Q&A** | 256-512 | 32-64 | Precise retrieval |
| **Summarization** | 512-1024 | 64-128 | Broader context |
| **Code search** | Function/class level | 0 | Natural boundaries |
| **Legal/regulatory** | Section/clause level | 1 sentence | Preserve clause integrity |
| **Conversational** | 256-512 | 64 | Quick, focused answers |
| **Research/analysis** | 1024-2048 | 128-256 | Deep context |

### Chunk Quality Rules

1. **Self-contained**: A chunk should make sense on its own (add context headers if needed)
2. **Atomic**: One main idea per chunk when possible
3. **Retrievable**: Would this chunk be useful if a user searched for its content?
4. **No orphans**: Don't create chunks < 50 tokens (merge with neighbors)
5. **Preserve structure**: Tables, code blocks, and lists should not be split mid-element
6. **Context prefix**: Prepend document title + section hierarchy to each chunk

### Parent-Child (Two-Level) Strategy

```
Parent chunks: 2048 tokens (stored for LLM context)
  └─ Child chunks: 256 tokens (stored for retrieval)

Retrieval: Search child chunks → Return parent chunk to LLM
Benefit: Precise retrieval + rich context
```

### Chunk Quality Scoring

Score each chunk (automated):

| Dimension | Weight | 0 (Bad) | 5 (Good) | 10 (Great) |
|-----------|--------|---------|----------|------------|
| Self-contained | 25% | Sentence fragment | Needs context | Standalone meaningful |
| Information density | 25% | Mostly boilerplate | Mixed | Dense, useful content |
| Boundary quality | 20% | Mid-sentence split | Paragraph boundary | Section/topic boundary |
| Metadata completeness | 15% | No metadata | Basic fields | Full enrichment |
| Size appropriateness | 15% | <50 or >2048 tokens | Within range | Optimal for use case |

**Target: Average chunk quality score > 7.0**

---

## Phase 4: Embedding Strategy

### Embedding Model Selection

| Model | Dimensions | Max Tokens | Quality | Speed | Cost |
|-------|-----------|------------|---------|-------|------|
| **text-embedding-3-large** (OpenAI) | 3072 (or 256-3072 via MRL) | 8191 | Excellent | Fast | $0.13/1M tokens |
| **text-embedding-3-small** (OpenAI) | 1536 (or 256-1536) | 8191 | Good | Very fast | $0.02/1M tokens |
| **voyage-3-large** (Voyage) | 1024 | 32000 | Excellent | Fast | $0.18/1M tokens |
| **voyage-code-3** (Voyage) | 1024 | 32000 | Best for code | Fast | $0.18/1M tokens |
| **Cohere embed-v4** | 1024 | 128000 | Excellent | Fast | $0.10/1M tokens |
| **BGE-M3** (open source) | 1024 | 8192 | Very good | Self-host | Free (compute) |
| **nomic-embed-text** (open source) | 768 | 8192 | Good | Self-host | Free (compute) |
| **GTE-Qwen2** (open source) | 1024-1792 | 8192 | Excellent | Self-host | Free (compute) |

### Model Selection Rules

1. **Start with**: `text-embedding-3-small` (best cost/quality for prototypes)
2. **Production default**: `text-embedding-3-large` or `voyage-3-large`
3. **Code search**: `voyage-code-3` or domain-fine-tuned
4. **Multilingual**: `Cohere embed-v4` or `BGE-M3`
5. **Privacy/on-prem**: `BGE-M3` or `GTE-Qwen2`
6. **Budget constrained**: MRL (Matryoshka) — reduce dimensions (e.g., 3072→256) for 10x storage savings with ~5% quality loss

### Embedding Best Practices

- **Prefix queries differently from documents**: Some models (Nomic, E5) need task-specific prefixes
  - Document: `"search_document: {text}"`
  - Query: `"search_query: {text}"`
- **Normalize embeddings**: L2 normalize for cosine similarity
- **Batch embedding**: Process in batches of 100-500 for throughput
- **Cache embeddings**: Store and reuse; don't re-embed unchanged documents
- **Benchmark on YOUR data**: Generic benchmarks (MTEB) don't predict domain-specific performance

### Embedding Quality Test

Before committing to a model, run this:

1. Create 50 query-document pairs from your actual data
2. Embed all queries and documents
3. Calculate recall@5 and recall@10
4. Compare 2-3 models
5. Pick the one with highest recall on YOUR domain

**Target: recall@5 > 0.7 on your domain test set**

---

## Phase 5: Vector Store & Indexing

### Vector Database Selection

| Database | Type | Scale | Features | Best For |
|----------|------|-------|----------|----------|
| **Pinecone** | Managed | Billions | Serverless, metadata filter | Production SaaS |
| **Weaviate** | Managed/Self-host | Millions-Billions | Hybrid search, modules | Feature-rich apps |
| **Qdrant** | Managed/Self-host | Billions | Filtering, quantization | High-performance |
| **ChromaDB** | Embedded | Thousands-Millions | Simple API | Prototypes, local |
| **pgvector** | Extension | Millions | SQL integration | Postgres-native apps |
| **Milvus** | Self-host | Billions | GPU support | Large scale |
| **LanceDB** | Embedded | Millions | Serverless, multimodal | Cost-sensitive |

### Selection Decision

```
Scale < 100K chunks AND simple use case?
├─ YES → ChromaDB or pgvector
└─ NO → Need managed service?
         ├─ YES → Pinecone (simplest) or Weaviate (feature-rich)
         └─ NO → Qdrant (performance) or Milvus (scale)
```

### Indexing Strategy

| Index Type | Recall | Speed | Memory | Use When |
|-----------|--------|-------|--------|----------|
| **Flat/Brute** | 100% | Slow | High | <50K vectors, accuracy critical |
| **IVF** | 95-99% | Fast | Medium | 50K-10M vectors |
| **HNSW** | 95-99% | Very fast | High | Default choice for quality |
| **PQ (Product Quantization)** | 90-95% | Fast | Low | Memory constrained |
| **HNSW+PQ** | 93-98% | Fast | Medium | Scale + quality balance |

**Default recommendation: HNSW with ef_construction=200, M=16**

### Hybrid Search Architecture

```
Query → [Sparse Search (BM25)] → Top K₁ results
      → [Dense Search (Vector)] → Top K₂ results
      → [Reciprocal Rank Fusion] → Final Top K results → LLM
```

**Why hybrid?**
- Dense (vector) excels at semantic similarity
- Sparse (BM25/keyword) excels at exact term matching, acronyms, IDs
- Hybrid captures both — 5-15% improvement over either alone

**RRF Formula**: `score = Σ 1/(k + rank_i)` where k=60 (default)

### Metadata Filtering

Always support these filters:

```yaml
filterable_fields:
  - source_type: "[document type]"
  - created_after: "[date filter]"
  - access_level: "[permission-based filtering]"
  - language: "[language filter]"
  - tags: "[topic/category filter]"
  - quality_score_min: "[minimum quality threshold]"
```

**Rule: Filter BEFORE vector search, not after** — reduces search space and improves relevance.

---

## Phase 6: Retrieval Optimization

### Query Processing Pipeline

```
User Query → Query Understanding → Query Transformation → Retrieval → Reranking → Context Assembly → LLM
```

### Query Transformation Techniques

| Technique | What It Does | When to Use | Quality Boost |
|-----------|-------------|-------------|---------------|
| **Query rewriting** | LLM rewrites query for clarity | Vague/conversational queries | +10-15% |
| **HyDE** | Generate hypothetical answer, embed that | Factual Q&A | +5-15% |
| **Multi-query** | Generate 3-5 query variants | Complex questions | +10-20% |
| **Step-back** | Abstract to higher-level question | Complex reasoning | +5-10% |
| **Query decomposition** | Break into sub-questions | Multi-part questions | +15-25% |
| **Query routing** | Route to different indexes | Multi-source systems | +10-20% |

### Recommended: Multi-Query + Reranking

```python
# Pseudocode for production retrieval
def retrieve(user_query: str, top_k: int = 5) -> list[Chunk]:
    # Step 1: Generate query variants
    queries = generate_query_variants(user_query, n=3)  # LLM generates 3 variants
    queries.append(user_query)  # Include original

    # Step 2: Retrieve candidates from each query
    candidates = set()
    for q in queries:
        results = hybrid_search(q, top_k=20)  # Over-retrieve
        candidates.update(results)

    # Step 3: Rerank
    reranked = rerank(user_query, list(candidates), top_k=top_k)

    return reranked
```

### Reranking

**Why rerank?** Embedding similarity is a rough filter. Cross-encoder rerankers are 10-30% more accurate but too slow for initial retrieval.

| Reranker | Quality | Speed | Cost |
|----------|---------|-------|------|
| **Cohere Rerank 3.5** | Excellent | Fast | $2/1M queries |
| **Voyage Reranker 2** | Excellent | Fast | API pricing |
| **BGE-reranker-v2-m3** | Very good | Medium | Free (self-host) |
| **ColBERT v2** | Excellent | Medium | Free (self-host) |
| **LLM-as-reranker** | Best | Slow | Expensive |

**Default: Cohere Rerank 3.5** (best quality/cost ratio)

### Retrieval Parameters

| Parameter | Default | Range | Impact |
|-----------|---------|-------|--------|
| **top_k (initial retrieval)** | 20 | 10-50 | Higher = better recall, more noise |
| **top_k (after reranking)** | 5 | 3-10 | Higher = more context, more cost |
| **similarity threshold** | 0.3 | 0.2-0.5 | Filter low-relevance results |
| **MMR diversity** | λ=0.7 | 0.5-1.0 | Lower = more diverse results |

### Context Assembly

```yaml
context_assembly:
  ordering: "relevance_descending"  # Most relevant first
  deduplication: true  # Remove near-duplicate chunks
  max_context_tokens: 4000  # Leave room for system prompt + answer
  include_metadata: true  # Source, date, section as inline citations
  separator: "\n---\n"  # Clear chunk boundaries

  # Citation format
  citation_style: |
    [Source: {title} | Section: {section} | Date: {date}]
    {chunk_text}
```

---

## Phase 7: Generation & Prompting

### System Prompt Template

```
You are a helpful assistant that answers questions based on the provided context.

## Rules
1. Answer ONLY based on the provided context. If the context doesn't contain the answer, say "I don't have enough information to answer this question."
2. Always cite your sources using [Source: X] notation.
3. If the context contains conflicting information, acknowledge the conflict and present both perspectives.
4. Never make up information or fill gaps with your training data.
5. If the question is ambiguous, ask for clarification.
6. Keep answers concise but complete.

## Context
{retrieved_context}

## Conversation History (if multi-turn)
{conversation_history}

## User Question
{user_query}
```

### Prompt Engineering for RAG

**Grounding rules (prevent hallucination):**
- Explicitly instruct: "Only use the provided context"
- Add: "If you're unsure, say so rather than guessing"
- Include: "Quote relevant passages to support your answer"
- Test: Ask questions NOT in the context — model should decline

**Citation instructions:**
- Inline: `"Based on [Document Title, Section X]..."`
- Footnote: `"...the process involves three steps.[1]"`
- Both: Use inline for key claims, footnotes for supporting details

### Model Selection for Generation

| Model | Context Window | Quality | Cost | Best For |
|-------|---------------|---------|------|----------|
| **GPT-4o** | 128K | Excellent | Medium | General production |
| **GPT-4o-mini** | 128K | Good | Low | High-volume, cost-sensitive |
| **Claude Sonnet** | 200K | Excellent | Medium | Nuanced answers, long context |
| **Claude Haiku** | 200K | Good | Low | Fast, cost-sensitive |
| **Gemini 1.5 Pro** | 1M | Excellent | Medium | Very large context needs |
| **Llama 3.1 70B** | 128K | Very good | Self-host | Privacy, on-prem |

### Multi-Turn Conversation

```yaml
conversation_strategy:
  # How to handle follow-up questions
  query_reformulation: true  # Rewrite follow-ups as standalone queries
  context_carry_forward: "last_2_turns"  # How much history to include
  memory:
    type: "sliding_window"  # or "summary" for long conversations
    window_size: 5  # Number of turns to keep

  # Example reformulation
  # Turn 1: "What is RAG?" → search as-is
  # Turn 2: "How does it handle updates?" → reformulate: "How does RAG handle document updates?"
```

---

## Phase 8: Evaluation Framework

### RAG Evaluation is Non-Negotiable

If you're not measuring, you're guessing. Every production RAG system needs automated evaluation.

### Evaluation Dimensions

| Dimension | What It Measures | Method |
|-----------|-----------------|--------|
| **Retrieval Precision** | Are retrieved chunks relevant? | Human or LLM judge |
| **Retrieval Recall** | Are all relevant chunks found? | Gold set comparison |
| **Answer Faithfulness** | Does answer match context? (no hallucination) | LLM-as-judge |
| **Answer Relevance** | Does answer address the question? | LLM-as-judge |
| **Answer Completeness** | Are all aspects of the question addressed? | LLM-as-judge |
| **Citation Accuracy** | Are citations correct and sufficient? | Automated + human |
| **Latency** | End-to-end response time | Instrumentation |
| **Cost** | Per-query cost | Instrumentation |

### Evaluation Dataset

**Build a golden test set (minimum 100 examples):**

```yaml
eval_example:
  query: "What is the refund policy for enterprise customers?"
  expected_sources: ["policy-doc-v3.pdf", "enterprise-agreement.md"]
  expected_answer_contains:
    - "30-day refund window"
    - "written notice required"
    - "prorated for annual plans"
  answer_type: "factual"
  difficulty: "easy"  # easy / medium / hard
```

**Test set composition:**
- 40% easy (single document, direct answer)
- 35% medium (multiple documents, synthesis needed)
- 15% hard (requires reasoning, edge cases)
- 10% unanswerable (answer NOT in corpus — must detect)

### LLM-as-Judge Prompts

**Faithfulness (hallucination detection):**

```
Given the context and the answer, determine if the answer is faithful to the context.

Context: {context}
Question: {question}
Answer: {answer}

Score 1-5:
1 = Contains fabricated information not in context
2 = Mostly faithful but includes unsupported claims
3 = Faithful with minor extrapolation
4 = Faithful, well-supported
5 = Perfectly faithful, every claim traceable to context

Score: [1-5]
Reasoning: [explain]
```

**Answer Relevance:**

```
Does this answer address the user's question?

Question: {question}
Answer: {answer}

Score 1-5:
1 = Completely irrelevant
2 = Partially relevant, misses key aspects
3 = Relevant but incomplete
4 = Relevant and mostly complete
5 = Perfectly addresses all aspects of the question

Score: [1-5]
Reasoning: [explain]
```

### Evaluation Tools

| Tool | Type | Best For |
|------|------|----------|
| **RAGAS** | Open source | Comprehensive RAG metrics |
| **DeepEval** | Open source | LLM-as-judge + classic metrics |
| **Arize Phoenix** | Open source | Tracing + evaluation |
| **LangSmith** | Managed | LangChain ecosystem |
| **Braintrust** | Managed | Eval + logging + monitoring |
| **Custom** | DIY | Maximum control |

### Evaluation Cadence

| Frequency | What to Evaluate |
|-----------|-----------------|
| **Every PR** | Run golden test set (automated CI) |
| **Weekly** | Sample 50 production queries for human review |
| **Monthly** | Full evaluation suite + benchmark comparison |
| **Quarterly** | Revisit golden test set, add new examples |

---

## Phase 9: Production Deployment

### Production Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐
│   Client     │────▶│  API Gateway  │────▶│  RAG Service  │
│   (App/API)  │     │  (Rate limit) │     │              │
└─────────────┘     └──────────────┘     │  Query Proc.  │
                                          │  Retrieval    │
                                          │  Reranking    │
                                          │  Generation   │
                                          └───────┬───────┘
                                                  │
                    ┌──────────────┐     ┌────────▼───────┐
                    │  Ingestion    │────▶│  Vector Store   │
                    │  Pipeline     │     │  + Metadata     │
                    └──────────────┘     └────────────────┘
```

### Production Checklist

**Pre-Launch (Mandatory):**

- [ ] Golden test set passing (>85% on all dimensions)
- [ ] Hallucination rate < 5% on test set
- [ ] Latency P95 < target (typically 3-5s)
- [ ] Rate limiting configured
- [ ] Input validation (max query length, content filtering)
- [ ] Output filtering (PII detection, content safety)
- [ ] Error handling (vector DB down, LLM timeout, empty results)
- [ ] Fallback behavior defined ("I don't know" > hallucination)
- [ ] Logging and tracing enabled
- [ ] Cost monitoring and alerts set
- [ ] Load tested at 2x expected peak

**Security:**

- [ ] No prompt injection vectors (user input sanitized)
- [ ] Access control on documents (user sees only authorized content)
- [ ] No PII leakage across user boundaries
- [ ] API authentication required
- [ ] Rate limiting per user/API key
- [ ] Audit logging for compliance

### Caching Strategy

```yaml
caching:
  query_cache:
    type: "semantic"  # Cache semantically similar queries
    ttl: 3600  # 1 hour
    similarity_threshold: 0.95
    expected_hit_rate: "20-40%"

  embedding_cache:
    type: "exact"  # Cache document embeddings
    ttl: 86400  # 24 hours (or until document changes)

  llm_response_cache:
    type: "exact_query_context"
    ttl: 1800  # 30 minutes
    invalidate_on: "source_document_update"
```

### Scaling Considerations

| Scale | Architecture | Notes |
|-------|-------------|-------|
| **<1K queries/day** | Single instance, managed vector DB | Keep it simple |
| **1K-100K/day** | Horizontal scaling, caching | Add semantic cache |
| **100K-1M/day** | Microservices, async, CDN | Separate ingestion/retrieval |
| **>1M/day** | Distributed, multi-region | Custom infrastructure |

---

## Phase 10: Monitoring & Observability

### Production Monitoring Dashboard

```yaml
rag_dashboard:
  real_time:
    - query_volume: "[queries/min]"
    - latency_p50: "[ms]"
    - latency_p95: "[ms]"
    - latency_p99: "[ms]"
    - error_rate: "[%]"
    - cache_hit_rate: "[%]"

  quality_signals:
    - retrieval_confidence_avg: "[0-1 — average similarity score]"
    - empty_retrieval_rate: "[% queries with no results above threshold]"
    - fallback_rate: "[% queries where model says 'I don't know']"
    - user_feedback_positive: "[% thumbs up]"
    - citation_rate: "[% answers with citations]"

  cost:
    - embedding_cost_daily: "[$]"
    - llm_cost_daily: "[$]"
    - reranker_cost_daily: "[$]"
    - vector_db_cost_daily: "[$]"
    - total_cost_per_query: "[$]"

  data_health:
    - index_freshness: "[time since last update]"
    - total_chunks_indexed: "[count]"
    - failed_ingestion_count: "[count]"
    - avg_chunk_quality_score: "[0-10]"
```

### Alert Rules

| Alert | Threshold | Severity |
|-------|-----------|----------|
| Latency P95 > 8s | 5 min sustained | Warning |
| Latency P95 > 15s | 1 min sustained | Critical |
| Error rate > 5% | 5 min sustained | Critical |
| Empty retrieval > 30% | 1 hour | Warning |
| Hallucination detected | Any flagged | Warning |
| Cost per query > 2x baseline | 1 hour | Warning |
| Vector DB latency > 500ms | 5 min sustained | Warning |
| Index staleness > 24h | If freshness SLA is <24h | Warning |

### Continuous Improvement Loop

```
Monitor → Identify Failure Patterns → Root Cause → Fix → Evaluate → Deploy
```

**Weekly review questions:**
1. What are the top 5 query types with lowest satisfaction?
2. Which documents are never retrieved? (potential indexing issues)
3. Which queries trigger "I don't know"? (coverage gaps)
4. What's the hallucination trend? (improving or degrading?)
5. Are costs trending up or down per query?

---

## Phase 11: Advanced Patterns

### Agentic RAG

```
User Query → Query Planner (LLM) → [Plan: search A, then search B, compare]
                                     ↓
                               Tool Execution
                               ├─ search_documents(query_A)
                               ├─ search_documents(query_B)
                               ├─ calculate(comparison)
                               └─ synthesize(results)
                                     ↓
                               Final Answer
```

**When to use:** Multi-step reasoning, cross-document comparison, calculation needed.

**Implementation:**
- Define tools: `search_docs`, `lookup_entity`, `calculate`, `compare`
- Use function calling with planning prompt
- Limit iterations (max 5 tool calls per query)
- Track and log the full reasoning chain

### Graph RAG

```yaml
graph_rag:
  when_to_use:
    - "Entity-heavy domains (legal, medical, organizational)"
    - "Queries about relationships ('who reports to X?')"
    - "Multi-hop reasoning ('what products use components from supplier Y?')"

  architecture:
    entities: "[Extract entities from documents]"
    relationships: "[Extract entity-entity relationships]"
    communities: "[Cluster entities into topic communities]"
    summaries: "[Generate community summaries]"

  retrieval:
    local_search: "Entity-focused — find specific entities and their neighbors"
    global_search: "Community-focused — synthesize across topic clusters"
    hybrid: "Combine vector similarity + graph traversal"
```

### Corrective RAG (CRAG)

```
Query → Retrieve → Evaluate Relevance → 
  ├─ CORRECT: Retrieved docs are relevant → Generate answer
  ├─ AMBIGUOUS: Partially relevant → Refine query + re-retrieve
  └─ INCORRECT: Not relevant → Fall back to web search or "I don't know"
```

### Self-RAG

```
Query → Retrieve → Generate + Self-Reflect →
  ├─ "Is retrieval needed?" → Skip if query is simple
  ├─ "Are results relevant?" → Re-retrieve if not
  ├─ "Is my answer supported?" → Revise if not faithful
  └─ "Is my answer useful?" → Regenerate if not
```

### RAG + Fine-Tuning

| Approach | When | Benefit |
|----------|------|---------|
| **RAG only** | Dynamic knowledge, many sources | Flexible, no training needed |
| **Fine-tuning only** | Static knowledge, consistent format | Fast inference, no retrieval |
| **RAG + Fine-tuned embeddings** | Domain-specific vocabulary | Better retrieval quality |
| **RAG + Fine-tuned generator** | Consistent output format needed | Better answers + grounding |

### Multi-Modal RAG

```yaml
multimodal_rag:
  document_types:
    images: "Generate text descriptions via vision model; embed descriptions"
    tables: "Convert to structured text; embed as markdown"
    charts: "Describe in natural language; embed description"
    diagrams: "Generate detailed caption; store image reference + caption"

  retrieval:
    strategy: "Text-first retrieval with multimodal context assembly"
    image_in_context: "Include as base64 or URL reference in prompt"
```

---

## Phase 12: Common Failure Modes & Fixes

### Diagnostic Decision Tree

```
RAG quality is poor
├─ Retrieved chunks are irrelevant
│   ├─ Check: Chunking strategy → Are chunks self-contained?
│   ├─ Check: Embedding model → Run domain benchmark test
│   ├─ Check: Query transformation → Enable multi-query or HyDE
│   └─ Fix: Add reranking if not present
│
├─ Retrieved chunks are relevant but answer is wrong
│   ├─ Check: System prompt → Is grounding instruction clear?
│   ├─ Check: Context window → Is relevant info getting truncated?
│   ├─ Check: Conflicting sources → Add conflict resolution instructions
│   └─ Fix: Upgrade generation model
│
├─ System says "I don't know" too often
│   ├─ Check: Similarity threshold → Too high? Lower from 0.5 to 0.3
│   ├─ Check: Corpus coverage → Missing documents?
│   ├─ Check: top_k → Too low? Increase from 5 to 10
│   └─ Fix: Add query expansion
│
├─ Hallucination / makes things up
│   ├─ Check: System prompt → Add explicit grounding instructions
│   ├─ Check: Temperature → Set to 0.0-0.3 for factual tasks
│   ├─ Check: Retrieved context → Is it misleading or ambiguous?
│   └─ Fix: Add faithfulness evaluation in post-processing
│
└─ Too slow
    ├─ Check: Embedding latency → Batch? Cache?
    ├─ Check: Vector search → Index type? Quantization?
    ├─ Check: Reranker → Faster model or reduce candidate set
    └─ Fix: Add caching layer (semantic query cache)
```

### 10 RAG Anti-Patterns

| # | Anti-Pattern | Why It's Bad | Fix |
|---|-------------|-------------|-----|
| 1 | **No reranking** | Vector similarity is noisy | Add cross-encoder reranker |
| 2 | **Fixed chunk size for all docs** | Different docs need different strategies | Use document-aware chunking |
| 3 | **No evaluation** | Flying blind | Build golden test set + automated eval |
| 4 | **Ignoring metadata** | Missing obvious filtering opportunities | Add metadata enrichment + filtering |
| 5 | **Single query embedding** | Misses semantic variants | Use multi-query retrieval |
| 6 | **No "I don't know"** | Hallucination when context insufficient | Add explicit grounding + confidence |
| 7 | **Embedding documents without context** | Chunks lose meaning in isolation | Prepend title/section to chunks |
| 8 | **No freshness management** | Stale answers from outdated docs | Implement update pipeline + TTL |
| 9 | **Oversized context** | Wasted tokens, increased cost + latency | Optimize top_k, use reranking |
| 10 | **No access control** | Users see unauthorized content | Implement document-level ACL filtering |

### 10 Common Mistakes

| Mistake | Impact | Fix |
|---------|--------|-----|
| Starting with complex architecture | Wasted time | Start naive, add complexity based on eval data |
| Not measuring before optimizing | Optimizing wrong thing | Eval first, then optimize worst dimension |
| Chunking at arbitrary character count | Bad retrieval | Use semantic or structure-aware chunking |
| Using same embedding for all languages | Poor multilingual results | Use multilingual model or per-language index |
| Ignoring the 20% of hard queries | 80% of user complaints | Build hard query test set, optimize for tail |
| No conversation context | Bad multi-turn experience | Implement query reformulation |
| Stuffing entire documents | Wasted tokens, noise | Retrieve only relevant chunks |
| Not handling "no results" gracefully | Hallucination | Define explicit fallback behavior |
| Over-engineering from day 1 | Never ships | MVP in 1 week, iterate from data |
| Not versioning your index | Can't rollback | Version embeddings + index config |

---

## Quality Scoring Rubric

### RAG System Health Score (0-100)

| Dimension | Weight | Score 0-10 |
|-----------|--------|------------|
| Retrieval quality (precision + recall) | 20% | ___ |
| Answer faithfulness (no hallucination) | 20% | ___ |
| Answer relevance & completeness | 15% | ___ |
| Latency & performance | 10% | ___ |
| Cost efficiency | 10% | ___ |
| Evaluation coverage | 10% | ___ |
| Data freshness & quality | 10% | ___ |
| Security & access control | 5% | ___ |

**Weighted Score: ___ / 100**

| Grade | Score | Action |
|-------|-------|--------|
| A | 85-100 | Production-ready, continuous improvement |
| B | 70-84 | Good foundation, address gaps |
| C | 55-69 | Significant improvements needed |
| D | 40-54 | Fundamental issues, review architecture |
| F | <40 | Rebuild needed |

---

## Edge Cases

### Low-Volume / Small Corpus
- Skip vector DB — use in-memory search or full-context stuffing
- Focus on chunking quality over retrieval sophistication
- Simple keyword + semantic hybrid is sufficient

### High-Security / Regulated
- On-prem vector DB + self-hosted embedding model
- Document-level ACL enforcement at retrieval time
- Audit logging every query + response
- Data residency compliance for vector storage
- Consider homomorphic encryption for embeddings

### Multi-Language
- Use multilingual embedding model (BGE-M3, Cohere embed-v4)
- Consider per-language indexes for large corpora
- Query language detection → route to appropriate index
- Cross-lingual retrieval: query in English, retrieve in any language

### Real-Time / Streaming
- Event-driven ingestion (Kafka/webhooks → chunk → embed → index)
- Incremental indexing (add/update/delete individual chunks)
- Version management (don't serve partially indexed documents)
- Consider time-weighted scoring (recent docs ranked higher)

### Very Large Corpus (>10M documents)
- Tiered retrieval: coarse filter → fine retrieval → reranking
- Hierarchical indexing (cluster → sub-cluster → document → chunk)
- Async processing pipeline with queue management
- Consider pre-computed answers for top 1000 queries

---

## Natural Language Commands

When the user says... you respond with:

| Command | Action |
|---------|--------|
| "Design a RAG system for [use case]" | Complete Phase 1 brief + architecture recommendation |
| "Help me chunk [document type]" | Chunking strategy recommendation + implementation |
| "Which embedding model should I use?" | Model comparison for their use case + benchmark plan |
| "My RAG results are bad" | Diagnostic decision tree walkthrough |
| "Evaluate my RAG system" | Evaluation framework setup + golden test set design |
| "Optimize retrieval" | Query transformation + reranking recommendations |
| "How do I handle [specific scenario]?" | Relevant pattern from advanced section |
| "Set up monitoring" | Dashboard YAML + alert rules for their scale |
| "How much will this cost?" | Cost estimation based on their scale + optimization tips |
| "Compare [approach A] vs [approach B]" | Decision matrix with pros/cons for their context |
| "I'm getting hallucinations" | Faithfulness diagnosis + grounding improvements |
| "Score my RAG system" | Full quality rubric assessment |

---

> **Built by AfrexAI** — AI agents that compound capital and code.
> Zero dependencies. Pure methodology. Works with any RAG stack.
