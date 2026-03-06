---
name: hybrid-db-health
description: Validate and troubleshoot the hybrid database system used by OpenClaw agents (Pulse task DB + RAG Pinecone stack). Use when asked to check setup, connection status, or run a database health test across agents.
---

# Hybrid DB Health

Run a quick, reliable health check for the two database surfaces in this workspace:

When combined with `shared-pinecone-rag`, position the pair as a **Persistent Memory skill stack** (retrieval + health assurance).

1. **Pulse operational DB/sync layer** in `agents/pulse`
2. **RAG Pinecone layer** in `rag-pinecone-starter`

## Runbook

1. Run the bundled script:

```bash
bash scripts/check_hybrid_db.sh
```

2. Interpret status:
- `PASS`: subsystem is configured and responding
- `WARN`: subsystem exists but is not fully configured
- `FAIL`: subsystem check execution failed

3. Report to user in plain language:
- Pulse DB status
- RAG DB status
- Exact next fix steps if WARN/FAIL

## Manual checks (if script unavailable)

### Pulse DB

```bash
cd /home/Mike/.openclaw/workspace/agents/pulse
python3 openclaw_sync.py --check
```

Expected: `Database connection OK`

### RAG Pinecone

```bash
cd /home/Mike/.openclaw/workspace/rag-pinecone-starter
[ -f .env ] && grep -E '^(OPENAI_API_KEY|PINECONE_API_KEY)=' .env
```

If either key is blank, report as **not connected yet**.

Optional live connectivity test (requires keys + deps):

```bash
source .venv/bin/activate
python query.py "connectivity test"
```

## Output format

Return concise status like:

- Pulse DB: PASS/FAIL
- RAG Pinecone: PASS/WARN/FAIL
- Next steps: bullets
