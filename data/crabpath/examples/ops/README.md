# Framework-agnostic operations examples

`examples/ops/` contains generic, minimal scripts that demonstrate both loops.

- `query_and_learn.py`: fast-loop interaction (`query -> traverse -> outcome`)
- `run_maintenance.py`: slow-loop maintenance run (`health,decay,merge,prune`)
- `compact_notes.py`: compact old daily notes into teaching summaries before graph updates

By default, examples use OpenAI callbacks as the production path:

- `OPENAI_API_KEY` is expected in the environment.
- Embeddings use `text-embedding-3-small`.
- LLM decisions use `gpt-5-mini`.
- If `OPENAI_API_KEY` is missing, examples automatically fall back to `--embedder hash`
  via `HashEmbedder` for zero-dependency testing.

## Callback construction

CrabPath core is callback-only and does not import `openai`:

```python
from examples.ops.callbacks import make_embed_fn, make_llm_fn

embedder = make_embed_fn("openai")  # or "hash"
llm = make_llm_fn("gpt-5-mini")

run_maintenance(..., embed_fn=embedder, llm_fn=llm)
```

Use `--embedder hash` explicitly when you want deterministic, zero-API testing.
