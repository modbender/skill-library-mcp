# CrabPath Operator Setup Guide

## Prerequisites
- Python 3.10+
- `pip install crabpath`
- `OPENAI_API_KEY` in environment (for OpenAI embeddings; optional if using `hash`)
- A workspace directory with markdown files (your agent's knowledge base)

## Step 1: Build your first brain

```bash
crabpath init --workspace ./my-workspace --state ./brain/state.json --embedder openai
crabpath doctor --state ./brain/state.json
crabpath info --state ./brain/state.json
```

## Step 2: Wire up the fast loop (per-query)

Minimum per-query pattern: **query → log → learn**.  
Reference implementation: `examples/ops/query_and_learn.py`

```python
from examples.ops.callbacks import make_embed_fn, make_llm_fn

embed_fn = make_embed_fn("openai")  # or "hash" for zero-dep
llm_fn = make_llm_fn("gpt-5-mini")  # optional, for LLM-assisted merge
```

Use this when building your query handler:

- Run embeddings with `embed_fn(text)`
- Traverse the graph and return `fired_ids`
- Log query traces and learn outcomes:
  - `+1.0` for good output
  - `-1.0` for bad output
- Persist feedback with `crabpath learn`

For an AGENTS.md drop-in hook, use:

`examples/openclaw_adapter/agents_hook.md`

## Step 3: Wire up the slow loop (maintenance)

Run maintenance manually:

```bash
crabpath maintain --state ./brain/state.json --tasks health,decay,prune,merge
crabpath maintain --state ./brain/state.json --dry-run --json
```

Schedule maintenance:

### Cron one-liner

```cron
0 2 * * * /usr/bin/python3 -m crabpath.cli maintain --state /opt/crabpath/brain/state.json --tasks health,decay,prune,merge
```

### systemd timer snippet

`/etc/systemd/system/crabpath-maintenance.service`

```ini
[Service]
Type=oneshot
ExecStart=/usr/bin/python3 -m crabpath.cli maintain --state /opt/crabpath/brain/state.json --tasks health,decay,prune,merge
```

`/etc/systemd/system/crabpath-maintenance.timer`

```ini
[Timer]
OnCalendar=daily
Persistent=true

[Install]
WantedBy=timers.target
```

### Existing batch pipeline

You can also invoke from your existing batch workflow/job:

```bash
python3 /opt/crabpath/examples/ops/run_maintenance.py --state /opt/crabpath/brain/state.json --tasks health,decay,prune,merge
```

## Step 4: Inject corrections and teachings

```bash
crabpath inject --state ./brain/state.json --id "correction::wrong-deploy" \
  --content "Never deploy on Fridays without notifying ops" --type CORRECTION

crabpath inject --state ./brain/state.json --id "teaching::deploy-window" \
  --content "Deploy window is Tuesday-Thursday 10am-2pm" --type TEACHING
```

- `CORRECTION`: creates inhibitory edges.
- `TEACHING`: creates supportive edges.

## Step 5: Rebuild (when workspace changes significantly)

```bash
python3 examples/openclaw_adapter/rebuild_all_brains.py --agent main
```

## Step 6: Monitor health

```bash
crabpath health --state ./brain/state.json
crabpath info --state ./brain/state.json
```

### Key metrics

- `dormant_pct`: target 70-95% (most edges should be dormant)
- `reflex_pct`: target 0-10% (only proven routes)
- `orphan_nodes`: should be 0

## Step 7: Set up file sync (incremental re-embedding)

```bash
crabpath sync --state ~/.crabpath/main/state.json --workspace ./my-workspace --embedder openai
```

## Step 8: Set constitutional anchors

```bash
crabpath anchor --state ~/.crabpath/main/state.json --node-id "SOUL.md::0" --authority constitutional
crabpath anchor --state ~/.crabpath/main/state.json --list
```

## Step 9: Compact old daily notes

```bash
crabpath compact --state ~/.crabpath/main/state.json --memory-dir ./memory --dry-run
```

## Brain directory layout

```
~/.crabpath/main/
├── state.json                 # Graph + index + metadata
├── journal.jsonl              # Append-only telemetry
├── fired_log.jsonl            # Per-chat fired nodes
└── injected_corrections.jsonl # Dedup ledger
```

## Callback pattern (the core principle)

CrabPath never imports `openai` or any provider package directly. You construct callbacks and pass them in.

- `embed_fn`: `(text) -> vector`
- `llm_fn`: `(system, user) -> str`

Reference: `examples/ops/callbacks.py`
