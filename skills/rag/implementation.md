# RAG Implementation Guide

## Document Ingestion Pipeline

### Step 1: Parse Documents
```python
# Use appropriate parser per format
# PDF: pypdf, pdfplumber, unstructured
# HTML: beautifulsoup, trafilatura
# Office: python-docx, openpyxl
```

### Step 2: Chunk with Overlap
```python
from langchain.text_splitter import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50,  # 10% overlap
    separators=["\n\n", "\n", ". ", " "]
)
chunks = splitter.split_documents(docs)
```

### Step 3: Generate Embeddings
```python
# Batch for efficiency (100-500 per batch)
# Handle rate limits with exponential backoff
# Store vectors with metadata
```

### Step 4: Upsert to Vector DB
```python
# Include: chunk text, embedding, metadata
# Metadata: source_file, page, section, timestamp
```

## Query Pipeline

### Step 1: Embed Query
- Same model as documents
- Consider query expansion for better recall

### Step 2: Retrieve
```python
# Typical k values: 5-20 for initial retrieval
# Apply metadata filters BEFORE similarity search
results = vector_db.query(
    embedding=query_embedding,
    top_k=10,
    filter={"department": user.department}  # Access control
)
```

### Step 3: Rerank (Optional but Recommended)
```python
# Rerank top-k to top-n (e.g., 20 → 5)
reranked = reranker.rerank(query, results, top_n=5)
```

### Step 4: Format Prompt
```python
context = "\n\n".join([r.text for r in reranked])
prompt = f"""Answer based on the context below.

Context:
{context}

Question: {query}

Answer:"""
```

## Document Updates

### Incremental Update Strategy
1. **Detect changes:** Hash documents, compare to stored hashes
2. **Re-chunk only changed docs**
3. **Delete old vectors:** By document_id metadata
4. **Upsert new vectors**

### Full Re-index
- Required when: embedding model changes, chunking strategy changes
- Schedule during low-traffic windows
- Blue-green deployment pattern recommended

## Common Implementation Patterns

### Conversation Memory
```python
# Include last N turns in query context
# Weight recent messages higher
```

### Source Attribution
```python
# Return source metadata with each answer
# "Based on: doc_name, page X, section Y"
```

### Fallback Handling
```python
# When retrieval scores are low:
# 1. Expand query terms
# 2. Try different retrieval strategy
# 3. Acknowledge uncertainty to user
```

### Streaming Responses
```python
# Stream LLM output while retrieval completes
# Show "searching..." indicator during retrieval
```

## Error Handling Checklist

- [ ] Embedding API timeouts/rate limits
- [ ] Vector DB connection failures
- [ ] Empty retrieval results
- [ ] Context window overflow
- [ ] Malformed documents in ingestion
- [ ] Duplicate document detection
