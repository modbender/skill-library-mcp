# openai_embedder

Requires `openai` package and `OPENAI_API_KEY` in the process environment.

Run:

```bash
OPENAI_API_KEY=... python3 examples/openai_embedder/run.py ./workspace
```

The callback uses real embeddings (for example `text-embedding-3-small`) and persists embedder metadata (`name`, `dim`, `schema_version`) into state.
