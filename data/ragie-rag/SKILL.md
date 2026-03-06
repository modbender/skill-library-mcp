---
name: ragie-rag
description: "|"
---


# Ragie.ai RAG Skill (OpenClaw Optimized)

This skill enables grounded question answering using Ragie.ai as a RAG backend.

Ragie handles:
- Document chunking
- Embedding
- Vector indexing
- Retrieval
- Optional reranking

The agent handles:
- Deciding when to ingest
- Triggering retrieval
- Constructing grounded prompts
- Producing final answers

---

# Core Principles

1. Never answer without retrieval.
2. Never hallucinate information not present in retrieved chunks.
3. Always cite the `document_name` when referencing specific facts.
4. If retrieval returns zero relevant chunks, explicitly say:
   > "I don't have that information in the current knowledge base."
5. Do not expose API keys or raw API payloads in final answers.

---

# Deterministic Workflow

## Case A — User Provides a File or URL

IF the user provides:
- A file
- A document path
- A PDF/URL to ingest

THEN:

1. Execute ingestion:
   ```bash
   python `skills/scripts/ingest.py` --file <path> --name "<document_name>"
   ```
   OR
   ```bash
   python `skills/scripts/ingest.py` --url "<url>" --name "<document_name>"
   ```

2. Capture returned `document_id`.

3. Poll document status:
   ```bash
   python `skills/scripts/manage.py` status --id <document_id>
   ```
   Repeat until status == `ready`.

4. Proceed to Retrieval (Case C).

---

## Case B — User Requests Document Management

### List documents
```bash
python `skills/scripts/manage.py` list
```

### Check document status
```bash
python `skills/scripts/manage.py` status --id <document_id>
```

### Delete a document
```bash
python `skills/scripts/manage.py` delete --id <document_id>
```

Return structured results to the user.

---

## Case C — Retrieval (Grounded Question Answering)

Execute:

```bash
python `skills/scripts/retrieve.py` \
  --query "<user_question>" \
  --top-k 6 \
  --rerank
```

Optional flags:
- `--partition <name>`
- `--filter '{"key":"value"}'`

---

# Retrieval Output Format

Expected output:

```json
[
  {
    "text": "...",
    "score": 0.87,
    "document_name": "Policy Handbook",
    "document_id": "doc_abc123"
  }
]
```

---

# Grounded Prompt Construction

After retrieval:

1. Extract all chunk `text`.
2. Concatenate with separators.
3. Construct this prompt:

```
SYSTEM:
You are a helpful assistant.
Answer using ONLY the context provided below.
If the context does not contain the answer, say:
"I don't have that information in the current knowledge base."

CONTEXT:
[chunk 1 text]
---
[chunk 2 text]
---
...

USER QUESTION:
{original user question}
```

4. Generate final answer.
5. Cite `document_name` when referencing information.

---

# Output Contract

The final response MUST:

- Be grounded only in retrieved chunks
- Cite `document_name` for factual claims
- Avoid hallucinations
- Avoid mentioning internal execution steps
- Avoid exposing API keys or raw responses
- Clearly state when information is missing

If no chunks are returned:
```
I don't have that information in the current knowledge base.
```

---

# API Reference

Base URL:
```
https://api.ragie.ai
```

| Operation          | Method | Endpoint                 |
|--------------------|--------|--------------------------|
| Ingest file        | POST   | /documents               |
| Ingest URL         | POST   | /documents/url           |
| Retrieve chunks    | POST   | /retrievals              |
| List documents     | GET    | /documents               |
| Get document       | GET    | /documents/{id}          |
| Delete document    | DELETE | /documents/{id}          |

---

# Error Handling

| HTTP Code | Meaning                | Action                          |
|-----------|------------------------|----------------------------------|
| 404       | Document not found     | Verify document_id              |
| 422       | Invalid payload        | Validate request schema         |
| 429       | Rate limited           | Retry with backoff              |
| 5xx       | Server error           | Retry or check Ragie status     |

If ingestion fails:
- Report failure clearly.
- Do not proceed to retrieval.

If retrieval fails:
- Retry once.
- If still failing, inform user.

---

# Decision Rules Summary

1. If user uploads content → ingest → wait until ready → retrieve.
2. If user asks question → retrieve immediately.
3. If zero chunks → state knowledge gap.
4. Always use reranking unless explicitly disabled.
5. Never answer without retrieval.

---

# Advanced Usage

- Use metadata `filter` to narrow retrieval scope.
- Use partitions to separate tenant data.
- Use `recency_bias` only when time relevance matters.
- Adjust `top_k` depending on query complexity.

---

# Security

- API keys must be loaded from environment variables.
- `.env` must not be committed.
- Do not log sensitive headers.

---

# Summary

This skill provides:

- Deterministic ingestion
- Deterministic retrieval
- Strict grounded answering
- Complete Ragie lifecycle management
- Safe and hallucination-resistant RAG execution

End of Skill.