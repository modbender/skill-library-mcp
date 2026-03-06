# CrabPath Architecture: two-timescale operation

CrabPath runs on two timescales.

For production setup and runbooks, see [CrabPath Operator Setup Guide](setup-guide.md).

## 1) Overview

CrabPath stores a learned retrieval policy as a graph of **nodes** and directed **edges** in `state.json`.
It separates:

- **Online learning (fast loop)**: cheap updates while serving queries.
- **Maintenance (slow loop)**: periodic structural operations to keep the graph healthy.

The core library is pure and does not assume any scheduler.

## 2) Online Learning (fast loop)

### What happens

```text
query -> traverse -> log trace -> feedback -> learn
```

1. The query is embedded and used as seeds for `traverse()`.
2. `traverse()` walks the graph, producing fired nodes and context.
3. A query trace is logged with `log_query()`.
4. Feedback arrives as `outcome` and is applied with:
   - `apply_outcome()` for local credit assignment, or
   - `apply_outcome_pg()` for full-policy updates.
5. New material can be added with `inject()`.

## 2-b) Persistent Worker (`crabpathd`)

CrabPath now supports a persistent worker process (`crabpath daemon`) that keeps
`Graph` and `VectorIndex` in memory for the lifetime of the process.

- Starts once and loads `state.json` at startup.
- Accepts NDJSON requests over stdin and writes one-line JSON responses to stdout.
- Avoids per-call reload overhead in the fast path, often saving ~100–800ms per query-heavy call path.
- Supports periodic and explicit save behavior.

Command:

```bash
python3 -m crabpath daemon --state PATH [--embed-model text-embedding-3-small] [--auto-save-interval 10]
```

Example request/response:

```json
{"id":"req-1","method":"query","params":{"query":"how to deploy","top_k":4,"chat_id":"telegram:123"}}
```

```json
{"id":"req-1","result":{"fired_nodes":["a"],"context":"...","seeds":[["a",0.96]],"embed_query_ms":1.1,"traverse_ms":2.4,"total_ms":3.5}}
```

Supported methods:

- `query`: returns `fired_nodes`, `context`, `seeds`, timing (`embed_query_ms`, `traverse_ms`, `total_ms`)
- `learn`: returns `edges_updated`
- `maintain`: returns `health_before`, `health_after`, `merges_applied`
- `health`: returns health metrics
- `info`: returns node/edge counts and `embedder`
- `save`: persists state immediately
- `reload`: reloads `state.json` from disk
- `shutdown`: persists pending writes and exits

Auto-save behavior:

- `write_count` increments after write operations (`learn`, `maintain`).
- On every `N` writes, where `N` is `--auto-save-interval`, the daemon saves state.
- `shutdown` persists pending state before exit.

### Vocabulary

- **Brain**: persisted `state.json` plus associated artifacts.
- **Query trace**: ordered fired nodes + metadata from one query.
- **Feedback signal**: scalar outcome (`+1`, `-1`, or intermediate).
- **Online learning**: edge-weight updates plus injection in response to each interaction.

## 3) Maintenance (slow loop)

### What happens

```text
health -> decay -> merge -> prune -> connect
```

1. **Health snapshot**: measure graph structure and quality with `measure_health()`.
2. **Decay**: weaken dormant edges with `apply_decay()`.
3. **Merge**: propose and apply structural merges with `suggest_merges()` and `apply_merge()`.
4. **Prune**: remove weak edges and orphaned nodes.
5. **Connect**: connect learning nodes to workspace neighborhoods.

### Functions used

- `run_maintenance()` (new)
- or directly: `measure_health()`, `apply_decay()`, `suggest_merges()`, `apply_merge()`, `prune_edges()`, `prune_orphan_nodes()`, `connect_learning_nodes()`

## 4) Constitutional Anchors

CrabPath uses node metadata to mark maintenance authority:

- `authority="constitutional"`: immutable anchors (`SOUL.md`, `AGENTS.md`, `USER.md`-style hard rules).
  - never decay
  - never prune nodes or edges
  - never merge
- `authority="canonical"`: stable long-lived anchors (`MEMORY.md`, `TOOLS.md`-style references).
  - decay at half speed (2x half-life)
  - never prune if the node is still weighted
  - merge only with LLM confirmation
- `authority="overlay"` (default): normal maintenance policy for session and working nodes (`TEACHING`, `CORRECTION`, derived nodes).

Maintenance behavior:

- `prune_edges()` skips any edge touching a constitutional node.
- `prune_orphan_nodes()` keeps constitutional and canonical nodes even if disconnected.
- `run_maintenance()` merge candidates are filtered to exclude constitutional nodes, and canonical nodes only merge when LLM is enabled.
- `run_maintenance()` decay skips constitutional sources and applies 2x half-life to canonical sources.

### When it runs

Maintenance is **not** part of request path.
Run it periodically (cron, timer, CI job, custom workflow) or after meaningful events (re-index, large workspace changes, etc.).

## 5) Integration Contract

### Framework provides

- Paths:
  - `state_path`
  - optional `journal_path`
- Callbacks:
  - `embed_fn(text) -> vector` (optional)
  - `llm_fn(system, user) -> str` (optional)
- Scheduling and lock strategy.

#### Callback Construction

CrabPath requires callbacks only. Core code does not import provider SDKs.

```python
from examples.ops.callbacks import make_embed_fn, make_llm_fn

embed_fn = make_embed_fn("openai")  # defaults to text-embedding-3-small
llm_fn = make_llm_fn("gpt-5-mini")

run_maintenance(
    state_path="...",
    embed_fn=embed_fn,
    llm_fn=llm_fn,
)

apply_outcome(...)

```

### CrabPath provides

- `state.json` (graph + index + meta)
- `journal.jsonl` (append-only telemetry)
- `fired_log.jsonl` (per-chat fired IDs when using adapters)
- `injected_corrections.jsonl` (dedup for injected correction nodes)

### In one sentence

CrabPath handles query-time scoring and maintenance operators;
you own orchestration, retries, and scheduler.

## 6) Brain directory layout

A brain directory is the operational unit.

- `state.json` — graph, index, and metadata.
- `journal.jsonl` — query, learn, health events and maintenance traces.
- `fired_log.jsonl` — optional fired-node history (chat/session based).
- `injected_corrections.jsonl` — optional dedup ledger for correction nodes.

## 7) Vocabulary table

| Term | Meaning |
|---|---|
| Brain | Persisted state containing graph, index, and metadata. |
| Query trace | Ordered fired nodes and query context for one interaction. |
| Feedback signal | Scalar outcome for later reinforcement (`+1` good, `-1` bad). |
| Online learning | Per-query weight updates using outcomes. |
| Maintenance | Periodic structural updates over the stored graph. |
| Prune | Remove weak edges and orphaned nodes. |
| Merge | Combine redundant/co-firing nodes. |
| Connect | Attach learning nodes back into workspace neighborhoods. |
| Dormant edge | Low-significance edge from health perspective. |
| Orphan | Node with no incoming and no outgoing edges. |

## 8) Scheduling

Run maintenance with your scheduler of choice. CrabPath has no scheduler dependency.

### cron

```cron
# Nightly graph health + decay + merge + prune
0 3 * * * /usr/bin/python3 -m crabpath.cli maintain --state ~/.crabpath/main/state.json

# Weekly deep sweep
0 4 * * 0 /usr/bin/python3 -m crabpath.cli maintain --state ~/.crabpath/main/state.json --tasks health,decay,prune,merge,connect
```

### systemd timer

- `crabpath-maintenance.service`: run `/usr/bin/python3 -m crabpath.cli maintain --state ...`
- `crabpath-maintenance.timer`: `OnCalendar=daily` (or `OnUnitActiveSec=24h`)

### GitHub Actions

```yaml
name: maintenance
on:
  schedule:
    - cron: '0 3 * * *'
jobs:
  maintain:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - run: pip install crabpath
      - run: python3 examples/ops/run_maintenance.py --state ./brains/main/state.json
```

## 9) Fast vs slow loop (concise)

### Fast loop

- **Query path**: `query -> traverse -> log_query`
- **Learning**: `apply_outcome()` / `apply_outcome_pg()`
- **Insertions**: `inject_*`

### Slow loop

- **Maintenance command**: `crabpath maintain ...`
- **Health metrics**: `measure_health()` and `log_health()`
- **Topology updates**: decay, merge, prune, connect

## 9) ASCII diagram

```text
            (request path)                              (scheduled / batch)
  user ──▶ query ──▶ fired nodes ──▶ response     ──▶   maintenance runner
                │         │                               │
                │         └─▶ log trace (journal/fired)    ├─ health + decay
                │                                         ├─ merge
        feedback (+/-)                                    ├─ prune
                │                                         ├─ connect
                └─▶ learn/inject                           └─ publish new state.json
```

## 10) Practical notes

- Use `run_maintenance()` for a complete slow-loop pass.
- Keep `--tasks` tight when experimenting (`health,decay` first, then add `merge`/`prune`/`connect`).
- Keep telemetry consistent so regressions are diagnosable.

## 11) Context Lifecycle

CrabPath is designed to work with both file-based canonical state and graph-based recall.

The full cycle is:

- Agent edits files (canonical state) → normal OpenClaw behavior
- Harvester runs periodically → ingests file changes + session corrections
- CrabPath sync → re-embeds changed chunks, sets authority levels
- CrabPath learns → online edge updates from outcomes
- CrabPath maintains → structural ops (decay/prune/merge)
- Files get compacted → old daily notes shrink, content migrates to graph

```text
Files (small, current) ──edit──→ Files
  │                                │
  │ harvest + sync                 │ compact
  ▼                                ▼
CrabPath Graph (learned) ◄─────── Harvester
  │
  └── single retrieval engine
```

## 12) Authority Levels

Authority is metadata used by maintenance policy:

- `constitutional`: never decay/prune/merge (`SOUL.md`, `AGENTS.md`)
- `canonical`: slow decay, protected prune (`USER.md`, `TOOLS.md`, `MEMORY.md`)
- `overlay`: normal rules (e.g. `TEACHING`, `CORRECTION`, session-derived signals)

## 13) Write Policy

When should the agent edit a file vs inject into CrabPath?

| Situation | Action |
|---|---|
| New durable fact | Edit file → sync re-embeds it |
| Correction received | Edit file + learn_correction.py |
| Soft teaching | `crabpath inject --type TEACHING` only |
| Wrong retrieval | `learn_correction.py` (graph-only) |
| New rule/contract | Edit `AGENTS.md` or `SOUL.md` |
| Monitoring item | Edit `HEARTBEAT.md` |

## 14) File Compaction

- Daily notes older than 7 days get compacted.
- Key facts are extracted and injected as `TEACHING` nodes.
- Files shrink to ~15 lines (headers + key decisions).
- Full historical content lives in the graph for retrieval and learning.
