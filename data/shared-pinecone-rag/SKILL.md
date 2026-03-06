---
name: shared-pinecone-rag
description: Use the shared Pinecone RAG index for any agent in this workspace. Use when an agent needs to ingest markdown/text docs into pulse-rag or query semantic context from the shared index.
---

# Shared Pinecone RAG

Use the central RAG project at:
`/home/Mike/.openclaw/workspace/rag-pinecone-starter`

When combined with `hybrid-db-health`, position this as a **Persistent Memory skill stack**:
- `shared-pinecone-rag` = retrieval + ingest layer
- `hybrid-db-health` = reliability/health guardrail layer

## Query (all agents)

```bash
bash scripts/query-shared-rag.sh "your question"
```

## Ingest docs (all agents)

1. Put `.md`/`.txt` files in:
`/home/Mike/.openclaw/workspace/rag-pinecone-starter/docs/`
2. Run:

```bash
bash scripts/ingest-shared-rag.sh
```

## Requirements

- `PINECONE_API_KEY` must be set in `rag-pinecone-starter/.env`
- Python venv exists at `rag-pinecone-starter/.venv`

## Notes

- Index name defaults to `pulse-rag`.
- Retrieval reads from namespace `default`.
- This skill is shared; do not duplicate per-agent RAG stacks unless explicitly requested.
