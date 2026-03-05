# CrabPath — learned retrieval routing for AI agents

> Your retrieval routes become the prompt — assembled by learned routing, not top-k similarity.

**Current release: v11.2.0**

**Setup:** [Setup Guide](docs/setup-guide.md)

**CrabPath learns from your agent feedback, so wrong answers get suppressed instead of resurfacing.** It builds a memory graph over your workspace, remembers what worked, and routes future answers through learned paths.

- Zero dependencies. Pure Python 3.10+.
- Works offline with built-in hash embeddings.
- Builds a **`state.json`** brain from your workspace.
- Queries follow learned routes instead of only similarity matches.
- Positive feedback (`+1`) strengthens routes, negative (`-1`) creates inhibitory edges.
- Over time, less noise appears and recurring mistakes are less likely.

- CrabPath integrates with your agent's file-based workspace through incremental sync, constitutional anchors, and automatic compaction.
- See the [context lifecycle](docs/architecture.md) for details.

## Install

```bash
pip install crabpath
```

See also: [Setup Guide](docs/setup-guide.md) for a complete local configuration walkthrough.

## Why CrabPath

- Static retrieval vs learned routing: CrabPath continuously updates node-to-node edges so good routes strengthen and bad routes decay.
- No correction propagation vs inhibitory edges: incorrect context can be actively suppressed and forgotten less often than in similarity-only systems.
- Bulk context load vs targeted traversal: context windows stay focused (roughly 52KB → 3-13KB in typical sessions) by following likely retrieval routes.
- No structural maintenance vs prune/merge/compact: CrabPath includes scheduled maintenance commands to keep the graph healthy and compact.
- No protection vs constitutional anchors: anchor critical nodes with authority so operational instructions do not drift.

## 5-minute quickstart (A→B learning story)

```bash
# 1. Build a brain from the sample workspace
crabpath init --workspace examples/sample_workspace --output /tmp/brain

# 2. Check state health
crabpath doctor --state /tmp/brain/state.json
# output
# PASS: python_version
# PASS: state_file_exists
# PASS: state_json_valid
# Summary: 8/9 checks passed

# 3. Query (text output includes node IDs)
crabpath query "how do I deploy" --state /tmp/brain/state.json --top 3 --json
# output (abbrev.)
# {"fired": ["deploy.md::0", "deploy.md::1", "deploy.md::2"], ...}

# 4. Teach it (good path)
crabpath learn --state /tmp/brain/state.json --outcome 1.0 --fired-ids "deploy.md::0,deploy.md::1"
# output
# {"edges_updated": 2, "max_weight_delta": 0.155}

# 5. Inject a correction
crabpath inject --state /tmp/brain/state.json \
  --id "fix::1" --content "Never skip CI for hotfixes" --type CORRECTION

# 5b. Add new knowledge (no correction needed, just a new fact)
crabpath inject --state /tmp/brain/state.json \
  --id "teaching::monitoring-tip" \
  --content "Check Grafana dashboards before every deploy" \
  --type TEACHING

# 6. Query again and see the route change
crabpath query "can I skip CI" --state /tmp/brain/state.json --top 3
# output
# fix::1
# ~~~~~~
# Never skip CI for hotfixes
# ...

# 7. Re-check health for a quick signal
crabpath health --state /tmp/brain/state.json
```

## Correcting mistakes (the main workflow)

When your agent retrieves wrong context, teach CrabPath in one command:

```bash
crabpath inject --state brain/state.json \
  --id "correction::42" \
  --content "Never show API keys in chat messages" \
  --type CORRECTION
```

What happens:
1. CrabPath creates a new node with your correction text
2. It connects that node to the most related workspace chunks
3. It adds **inhibitory edges** — negative-weight links that suppress those chunks
4. Next query touching that topic: the correction appears, the bad route is dampened

To add knowledge without suppressing anything, use `--type TEACHING` instead.

## Adding new knowledge (no rebuild needed)

When you learn something that isn't in any workspace file, inject it directly:

```bash
crabpath inject --state brain/state.json \
  --id "teaching::codex-spark" \
  --content "Use Codex CLI with gpt-5.3-codex-spark for coding tasks — free on Pro plan" \
  --type TEACHING
```

TEACHING nodes connect to related workspace chunks just like CORRECTION nodes,
but without inhibitory edges — they add knowledge instead of suppressing it.

Three injection types:
- **CORRECTION** — creates inhibitory edges that suppress related wrong paths
- **TEACHING** — adds knowledge with normal positive connections
- **DIRECTIVE** — same as TEACHING (use for standing instructions)

For agent frameworks that need to correlate corrections with earlier queries,
see `examples/correction_flow/` for the fired-node logging pattern.

You can also reinforce good retrievals:

```bash
# After a query returns helpful context, strengthen those paths
crabpath learn --state brain/state.json --outcome 1.0 \
  --fired-ids "deploy.md::0,deploy.md::1"
```

Or weaken bad ones:

```bash
crabpath learn --state brain/state.json --outcome -1.0 \
  --fired-ids "monitoring.md::2"
```

## What it looks like in practice

```bash
# Before learning
crabpath query "how do we handle incidents" --state /tmp/brain/state.json --top 3

# After one good learn on the best route
crabpath learn --state /tmp/brain/state.json --outcome 1.0 --fired-ids "incidents.md::0,deploy.md::1"

# After one negative learn on a bad route
crabpath learn --state /tmp/brain/state.json --outcome -1.0 --fired-ids "monitoring.md::2,incidents.md::0"

# Query again to observe new routing
crabpath query "incident runbook for deploy failures" --state /tmp/brain/state.json --top 4
```

## How it compares

| | Plain RAG | CrabPath |
|---|-----------|----------|
| Retrieval | Similarity search | Learned graph traversal |
| Feedback | None | `learn +1/-1` updates edge weights |
| Wrong answers | Can keep resurfacing | Inhibitory edges suppress them |
| Adding knowledge | Re-index/re-embed | `inject --type TEACHING` (no rebuild) |
| Over time | Same results for same query | Routes become habitual behavior |
| Dependencies | Vector DB or service | Zero dependencies |

## How CrabPath differs from related tools

| | CrabPath | Plain RAG | Reflexion | MemGPT |
|---|----------|-----------|-----------|--------|
| What it learns | Retrieval routes | Nothing | Reasoning via self-reflection text | Memory read/write policies |
| Negative feedback | Inhibitory edges suppress bad paths | None | None (additive only) | None |
| New knowledge | `inject` node (no rebuild) | Re-embed corpus | Add to reflection prompt | Update tier config |
| Integration | Standalone library, any agent | Vector DB required | Tied to agent loop | Tied to agent architecture |
| Cold start | Hash embeddings, no API key | Needs embedding service | Needs prior episodes | Needs configured tiers |
| State | Single `state.json` file | External DB | Prompt history | Multi-tier storage |

## Real embeddings + LLM routing (OpenAI)

Offline hash embeddings work for trying the product, but real deployments generally use:

- **Embeddings:** `text-embedding-3-small` (1536-dim)
- **LLM routing/scoring:** `gpt-5-mini`

```python
from openai import OpenAI
from crabpath import split_workspace, VectorIndex

client = OpenAI()


def embed(text):
    return client.embeddings.create(
        model="text-embedding-3-small", input=[text]
    ).data[0].embedding


def llm(system, user):
    return client.chat.completions.create(
        model="gpt-5-mini",
        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
    ).choices[0].message.content

graph, texts = split_workspace("./workspace", llm_fn=llm)
index = VectorIndex()
for nid, content in texts.items():
    index.upsert(nid, embed(content))
```

See `examples/openai_embedder/` for a complete example.

## CLI Reference

| Command | Description |
|---------|-------------|
| `init` | Build a brain from workspace files |
| `query` | Traverse graph and return context |
| `learn` | Apply outcome feedback to fired edges |
| `merge` | Suggest and apply node merges |
| `anchor` | Set/list/remove constitutional authority on nodes |
| `connect` | Connect learning nodes to workspace neighborhoods |
| `maintain` | Run structural maintenance (health, decay, prune, merge) |
| `compact` | Compact old daily notes into graph nodes |
| `sync` | Incremental re-embed after file changes |
| `inject` | Add CORRECTION/TEACHING/DIRECTIVE nodes |
| `replay` | Replay session queries into brain |
| `health` | Show graph health metrics |
| `journal` | Show event journal |
| `doctor` | Run diagnostic checks |
| `info` | Show brain info (nodes, edges, embedder) |
| `daemon` | Start persistent worker (JSON-RPC over stdio, state loaded once) |

## Persistent Worker (`crabpath daemon`)

For production use, run CrabPath as a long-lived daemon that keeps state hot in memory:

```bash
crabpath daemon --state ~/.crabpath/main/state.json
```

- Loads `state.json` once at startup (~100-800ms saved per call)
- Accepts NDJSON requests over stdin, responds on stdout
- Methods: `query`, `learn`, `maintain`, `health`, `info`, `save`, `reload`, `shutdown`
- Query responses include timing: `embed_query_ms`, `traverse_ms`, `total_ms`
- Auto-saves after N write operations; graceful SIGTERM/SIGINT shutdown

Production timing (Mac Mini M4 Pro, OpenAI embeddings):
- MAIN (1,158 nodes): 397ms embed + 107ms traverse = **504ms total**
- PELICAN (582 nodes): 634ms embed + 51ms traverse = **685ms total**
- BOUNTIFUL (285 nodes): 404ms embed + 27ms traverse = **431ms total**

See `examples/ops/client_example.py` for a Python client and `docs/architecture.md` for protocol details.

## True Policy Gradient (apply_outcome_pg)

`apply_outcome_pg` implements a full REINFORCE policy-gradient update.

- It updates **all outgoing edges** for each visited node on the fired trajectory, not only traversed edges.
- It uses the update:
  `Δw = (η(z-b)γ^ℓ)/τ · (𝟙[j=a] - π(j|i))`
  where:
  - `η` = learning rate
  - `z` = outcome reward
  - `b` = baseline
  - `γ` = discount
  - `ℓ` = trajectory depth
  - `τ` = temperature
  - `π(j|i)` = action probability from softmax (including STOP)
  - `𝟙[j=a]` = 1 for the taken action, else 0
- Conservation property: for each source node `i`, outgoing updates sum to zero, so total outgoing mass is preserved.
- Use `apply_outcome_pg` when you want smoother, probability-based updates across alternatives; use `apply_outcome` for a simpler sparse update that only touches traversed edges.

```python
from crabpath import apply_outcome_pg, LearningConfig

config = LearningConfig(learning_rate=0.1, temperature=1.0, baseline=0.0)
updates = apply_outcome_pg(graph, fired_nodes=["a", "b", "c"], outcome=1.0, config=config)
```

Full derivation: https://jonathangu.com/crabpath/gu2016/

## Write policy summary

| Situation | Action |
|-----------|--------|
| Durable fact | Edit file → sync re-embeds |
| Correction | Edit file + learn_correction.py |
| Soft teaching | crabpath inject --type TEACHING |
| Wrong retrieval | learn_correction.py (graph-only) |
| New rule | Edit AGENTS.md or SOUL.md |

## Production stats (current)

- MAIN: 1,160 nodes, 2,551 edges, 43 learnings
- PELICAN: 555 nodes, 2,211 edges, 181 learnings
- BOUNTIFUL: 289 nodes, 1,101 edges, 35 learnings
- CORMORANT: 1,672 nodes, ~7,100 edges, 22 learnings (first external user!)

## Traversal defaults

| Setting | Default | Purpose |
|---------|---------|---------|
| `beam_width` | `8` | Frontier size per hop (wider = reaches farther routes) |
| `max_hops` | `30` | Safety ceiling; damping controls convergence |
| `fire_threshold` | `0.01` | Minimum score required to fire a candidate node |
| `reflex_threshold` | `0.6` | Edges with weight `>= 0.6` auto-follow (no route function) |
| `habitual_range` | `0.2 - 0.6` | Edges in this band run through route function |
| `inhibitory_threshold` | `-0.01` | Edges at or below suppress targets |
| `max_fired_nodes` | `None` | Hard stop on fired node count |
| `max_context_chars` | `None` | Hard stop on rendered traversal context |
| `edge_damping` | `0.3` | Per-reuse decay (`weight × 0.3^k`) |

```python
from crabpath import traverse, TraversalConfig

result = traverse(
    graph,
    seeds,
    config=TraversalConfig(max_context_chars=20000, max_fired_nodes=30),
)
```

`query` and `query_brain.py` honor these budgets and stop as soon as any termination condition is met.

## External benchmarks

External retrieval benchmarks are optional and use separately downloaded datasets.
CrabPath ships a quick-start workflow for MultiHop-RAG and HotPotQA in
`benchmarks/external/README.md`, but the datasets are not in the repository.

Quick run (from project root):

```bash
mkdir -p benchmarks/external
curl -L https://huggingface.co/datasets/yixuantt/MultiHopRAG/raw/main/MultiHopRAG.json -o benchmarks/external/multihop_rag.json
curl -L https://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json -o benchmarks/external/hotpotqa_dev_distractor.json
python3 benchmarks/external/run_multihop_rag.py --limit 50
python3 benchmarks/external/run_hotpotqa.py --limit 50
```

## Python API

```python
from crabpath import (
    split_workspace,
    traverse,
    apply_outcome,
    inject_node,
    inject_correction,
    inject_batch,
    VectorIndex,
    HashEmbedder,
    TraversalConfig,
    save_state,
    load_state,
    ManagedState,
    measure_health,
    replay_queries,
    score_retrieval,
)
```

## State lifecycle

- **Where it lives:** a single `state.json` file (portable, version-controllable)
- **How big:** ~180KB for 20 nodes (hash), ~60MB for 1,600 nodes (OpenAI embeddings)
- **When to rebuild:** after major workspace restructuring or embedder changes
- **Embedder changes:** CrabPath stores the embedder name + dimension in state metadata and hard-fails on mismatch — no silent corruption
- **Merging:** use `crabpath merge` to consolidate similar nodes as the graph grows

## Cost control

- **Free tier:** hash embeddings work offline with zero API calls. Good for trying CrabPath and small workspaces.
- **Budget tier:** use OpenAI `text-embedding-3-small` (~$0.02/1M tokens). Embed once at init, cache in state.json.
- **LLM routing:** optional. `gpt-5-mini` for routing/scoring decisions. Only called during query, not at rest.
- **Batch init:** `crabpath init` embeds all workspace files in one batch call. Subsequent queries reuse cached vectors.
- **Upgrade path:** start with hash, switch to real embeddings later by rebuilding state with `crabpath init`.

## Optional: warm start from sessions

If you have prior conversation logs, replay them:

```bash
crabpath replay --state /tmp/brain/state.json --sessions ./sessions/
```

Skip this if you are just getting started.

## Production experience

Three brains run in production on a Mac Mini M4 Pro:

| Brain | Nodes | Edges | Learning Corrections | Sessions Replayed |
|-------|-------|-------|---------------------|-------------------|
| MAIN | 1,142 | 2,814 | 43 | 215 |
| PELICAN | 512 | 1,984 | 181 | 183 |
| BOUNTIFUL | 273 | 1,073 | 35 | 300 |

## Design Tenets

- No network calls in core.
- No secret discovery (no dotfiles, no keychain lookup).
- Embedder identity stored in state metadata; hard-fail on dimension mismatch.
- One canonical state format (`state.json`).
- Traversal defaults are budget-first for safety: `beam_width=8`, `max_hops=30`, `fire_threshold=0.01`.

## Paper + links

[jonathangu.com/crabpath](https://jonathangu.com/crabpath/) — 8 deterministic simulations + production deployment data.

- PyPI: `pip install crabpath`
- GitHub: [jonathangu/crabpath](https://github.com/jonathangu/crabpath)
- ClawHub: `clawhub install crabpath`
- Benchmarks: `python3 benchmarks/run_benchmark.py` (deterministic per commit; timings vary by machine)
