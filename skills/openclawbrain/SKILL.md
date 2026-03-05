---
name: openclawbrain
description: Learned memory graph for AI agents. Policy-gradient routing over document chunks with self-learning, self-regulation, and autonomous correction. Pure Python core with optional OpenAI embeddings.
metadata:
  openclaw:
    emoji: "🧠"
    requires:
      python: ">=3.10"
---

# OpenClawBrain v12.2.1

Learned retrieval graph for AI agents. Nodes are document chunks, edges are mutable weighted pointers. The graph learns from outcomes using policy-gradient updates (REINFORCE) and self-regulates via homeostatic decay, synaptic scaling, and tier hysteresis.

## Install

```bash
pip install openclawbrain              # core (pure Python, zero deps)
pip install "openclawbrain[openai]"    # with OpenAI embeddings
```

## Quick Start

```bash
# Build a brain from workspace files
openclawbrain init --workspace ./my-workspace --output ./brain --embedder openai

# Query
openclawbrain query "how do I deploy" --state ./brain/state.json --json

# Learn from outcome (+1 good, -1 bad)
openclawbrain learn --state ./brain/state.json --outcome 1.0 --fired-ids "node1,node2"

# Self-learn (agent-initiated, no human needed)
openclawbrain self-learn --state ./brain/state.json \
  --content "Always download artifacts before terminating instances" \
  --fired-ids "node1,node2" --outcome -1.0 --type CORRECTION

# Health check
openclawbrain doctor --state ./brain/state.json
```

## Core Concepts

### Learning Rule: Policy Gradient (default)
Default is `apply_outcome_pg` (REINFORCE). At each node, updates redistribute probability mass across ALL outgoing edges (sum ≈ 0). The chosen edge goes up, all alternatives go down. No inflation.

`apply_outcome` (heuristic) is available as fallback — only updates traversed edges, inflationary.

### Self-Learning
Agents learn from their own observed outcomes without human feedback (`self-correct` available as CLI/API alias):

```python
from openclawbrain.socket_client import OCBClient

with OCBClient('~/.openclawbrain/main/daemon.sock') as client:
    # Agent detected failure
    client.self_learn(
        content='Always download artifacts before terminating',
        fired_ids=['node1', 'node2'],
        outcome=-1.0,
        node_type='CORRECTION',   # penalize + inhibitory edges
    )

    # Agent observed success
    client.self_learn(
        content='Download-then-terminate works reliably',
        fired_ids=['node1', 'node2'],
        outcome=1.0,
        node_type='TEACHING',     # reinforce + positive knowledge
    )
```

| Situation | outcome | type | Effect |
|-----------|---------|------|--------|
| Mistake | -1.0 | CORRECTION | Penalize path + inhibitory edges |
| Fact learned | 0.0 | TEACHING | Inject knowledge only |
| Success | +1.0 | TEACHING | Reinforce path + inject knowledge |

### Self-Regulation (automatic, no tuning needed)
- **Homeostatic decay**: half-life auto-adjusts to maintain 5-15% reflex edge ratio. Bounded 60-300 cycles.
- **Synaptic scaling**: soft per-node weight budget (5.0) prevents hub domination.
- **Tier hysteresis**: habitual band 0.15-0.6 prevents threshold thrashing.
- **Synaptic scaling (maintenance detail)**: soft per-node weight budget (5.0) with fourth-root scaling.

### Edge Tiers
| Tier | Weight | Behavior |
|------|--------|----------|
| Reflex | ≥ 0.6 | Auto-follow |
| Habitual | 0.15 – 0.6 | Follow by weight |
| Dormant | < 0.15 | Skipped |
| Inhibitory | < -0.01 | Actively suppresses target |

### Maintenance Pipeline
Runs every 30 min via daemon: `health → decay → scale → split → merge → prune → connect`

- **Decay**: exponential edge weight decay (adaptive half-life)
- **Scale**: synaptic scaling on hub nodes
- **Split**: runtime node splitting (inverse of merge) for bloated multi-topic nodes
- **Merge**: consolidate co-firing nodes (bidirectional weight ≥ 0.8)
- **Prune**: remove dead edges (|w| < 0.01) and orphan nodes

### Maintenance

- `split_node`: splits bloated nodes into focused children with embedding-based edge rewiring
- `suggest_splits`: detects candidates by content length, hub degree, merge origin, edge variance

### Text Chunking
`split_workspace` chunks files by type (.py → functions, .md → headers, .json → keys) then `_rechunk_oversized` ensures no chunk exceeds 12K chars. Large texts are split on blank lines → newlines → hard cut. **No content is ever skipped or truncated.**

## Daemon (production use)

The daemon keeps state hot in memory behind a Unix socket (~500ms queries vs 5-8s from disk).

```bash
# Start daemon (usually via launchd)
openclawbrain daemon --state ./brain/state.json --embed-model text-embedding-3-small
```

### Daemon Methods (NDJSON over Unix socket)
| Method | Purpose |
|--------|---------|
| `query` | Traverse graph, return fired nodes + context |
| `learn` | Apply outcome to fired nodes |
| `self_learn` | Agent-initiated learning (CORRECTION or TEACHING) |
| `self_correct` | Alias for self_learn (self-correct available as CLI/API alias) |
| `correction` | Human-initiated correction (uses chat_id lookback) |
| `inject` | Add TEACHING/CORRECTION/DIRECTIVE node |
| `maintain` | Run maintenance tasks |
| `health` | Graph health metrics |
| `info` | Daemon info |
| `save` | Force state write |
| `reload` | Reload state from disk |
| `shutdown` | Clean shutdown |

### Socket Client
```python
from openclawbrain.socket_client import OCBClient

with OCBClient('/path/to/daemon.sock') as c:
    result = c.query('how do I deploy', chat_id='session-123')
    c.learn(fired_nodes=['node1', 'node2'], outcome=1.0)
    c.self_learn(content='lesson', outcome=-1.0, node_type='CORRECTION')
    c.health()
    c.maintain(tasks=['decay', 'prune'])
```

## CLI Reference

```bash
openclawbrain init --workspace W --output O [--embedder openai] [--llm openai]
openclawbrain query TEXT --state S [--top N] [--json] [--chat-id CID]
openclawbrain learn --state S --outcome N --fired-ids a,b,c [--json]
openclawbrain self-learn --state S --content TEXT [--fired-ids a,b] [--outcome -1] [--type CORRECTION|TEACHING]
openclawbrain inject --state S --id ID --content TEXT [--type CORRECTION|TEACHING|DIRECTIVE]
openclawbrain health --state S
openclawbrain doctor --state S
openclawbrain info --state S
openclawbrain maintain --state S [--tasks decay,scale,split,merge,prune,connect]
openclawbrain status --state S [--json]
openclawbrain replay --state S --sessions S
openclawbrain merge --state S [--llm openai]
openclawbrain connect --state S
openclawbrain compact --state S
openclawbrain sync --workspace W --state S [--embedder openai]
openclawbrain daemon --state S [--embed-model text-embedding-3-small]
```

## Traversal Defaults

| Parameter | Default |
|-----------|---------|
| beam_width | 8 |
| max_hops | 30 |
| fire_threshold | 0.01 |
| reflex_threshold | 0.6 |
| habitual_range | (0.15, 0.6) |
| inhibitory_threshold | -0.01 |
| max_context_chars | 20000 (in query_brain.py) |

## State Persistence

- Atomic writes: temp → fsync → rename. Keeps `.bak` backup. Crash-safe.
- State format: `state.json` (graph + index + metadata)
- Embedder identity stored in metadata; dimension mismatches are errors.

## Integration with OpenClaw Agents

Add to your agent's `AGENTS.md`:

```markdown
## OpenClawBrain Memory Graph

**Query:**
python3 ~/openclawbrain/examples/openclaw_adapter/query_brain.py \
  ~/.openclawbrain/<brain>/state.json '<query>' --chat-id '<chat_id>' --json

**Learn:** openclawbrain learn --state ~/.openclawbrain/<brain>/state.json --outcome 1.0 --fired-ids <ids>

**Self-learn:** openclawbrain self-learn --state ~/.openclawbrain/<brain>/state.json \
  --content "lesson" --fired-ids <ids> --outcome -1.0 --type CORRECTION
  # (self-correct available as CLI/API alias)

**Health:** openclawbrain health --state ~/.openclawbrain/<brain>/state.json
```

## Links

- Paper: https://jonathangu.com/openclawbrain/
- Blog: https://jonathangu.com/openclawbrain/blog/v12.2.1/
- Derivation: https://jonathangu.com/openclawbrain/gu2016/
- GitHub: https://github.com/jonathangu/openclawbrain
- PyPI: `pip install openclawbrain==12.2.1`
