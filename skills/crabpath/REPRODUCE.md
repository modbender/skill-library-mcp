# Reproduce CrabPath Results

All paper claims are verified by deterministic simulations and one benchmark harness. No API keys are needed for simulation.

## Quick Start

```bash
git clone https://github.com/jonathangu/crabpath.git
cd crabpath
pip install -e .
python sims/run_all.py
```

## Expected Output

```
simulation                 claim        summary
-------------------------------------------------------------------------------
deploy_pipeline            PASS         final=1.000
negation                   PASS         bad=-0.940
context_reduction          PASS         30.0->2.6
forgetting                 PASS         dormant=0.933
edge_damping               PASS         dr=True ur=False
domain_separation          PASS         cross=5
brain_death                PASS         dormant=0.975
individuation              PASS         diff_edges=27
```

All eight simulations are deterministic and all PASS.

## Table: Simulations → Paper Claims

| Sim | Paper Claim | What It Tests |
|-----|-------------|---------------|
| `deploy_pipeline` | Repeated edges compile to reflex | 50 queries, 4 pipeline edges, reflex-tier convergence |
| `negation` | Corrective negatives suppress bad guidance | Inhibitory learning (`-0.940`) on stale edge |
| `context_reduction` | Context becomes focused over time | 30→2.6 fired nodes |
| `forgetting` | Selective dormancy is learned | Dormant shares reach 93.3% |
| `edge_damping` | Damped traversal avoids loops | `λ=0.3` reaches target; `λ=1.0` loops |
| `domain_separation` | Sparse bridges while preserving clusters | 5 cross-file edges emerge |
| `brain_death` | Health checks surface recovery pressure | Dormancy and recovery control behavior |
| `individuation` | Same topology with workload-specific weights | 27 edges differ by >0.05 after divergent workloads |

## Run Tests

```bash
pip install -e .
python3 -m pytest tests/ -x -q
```

Expected: 204 passed.

## Benchmarks

CrabPath includes a deterministic benchmark harness at `benchmarks/run_benchmark.py`.

### Run

```bash
python3 benchmarks/run_benchmark.py
python3 -m pytest tests/ -x -q
```

Benchmark output compares:

1. keyword overlap
2. hash embedding
3. CrabPath traversal
4. CrabPath traversal + session replay

Run `python3 benchmarks/run_benchmark.py` to see current deterministic results for this commit.

## External benchmarks (optional, dataset downloads required)

Benchmarks for external corpora are documented in `benchmarks/external/README.md`.
The external datasets are optional and are **not included** in this repository.

Download the datasets and run a quick end-to-end check:

```bash
mkdir -p benchmarks/external
curl -L https://huggingface.co/datasets/yixuantt/MultiHopRAG/raw/main/MultiHopRAG.json -o benchmarks/external/multihop_rag.json
curl -L https://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json -o benchmarks/external/hotpotqa_dev_distractor.json
python3 benchmarks/external/run_multihop_rag.py --limit 50
python3 benchmarks/external/run_hotpotqa.py --limit 50
```

For full benchmark runs and tuning options, see `benchmarks/external/README.md`.

## Live Injection Verification

Live injection is covered by `tests/test_inject.py` and can also be exercised directly with a simple state payload.

```bash
python3 -m pytest tests/test_inject.py -x -q
```

Run an end-to-end CLI smoke test:

```bash
python3 - <<'PY'
from pathlib import Path

from crabpath import VectorIndex, save_state, HashEmbedder, inject_node
from crabpath.graph import Graph, Node

graph = Graph()
index = VectorIndex()
graph.add_node(Node("seed", "Seed policy guidance", metadata={"file": "seed.md"}))
index.upsert("seed", HashEmbedder().embed("Seed policy guidance"))

state_path = Path("/tmp/crabpath_live_inject_state.json")
save_state(graph=graph, index=index, path=state_path)

result = inject_node(
    graph=graph,
    index=index,
    node_id="learning::manual",
    content="Prefer deterministic tests over assumptions.",
    connect_top_k=1,
    connect_min_sim=0.0,
)

save_state(graph=graph, index=index, path=state_path)
print(result)
print(f"node_count={graph.node_count()}")
print(f"edges={graph.edge_count()}")
PY

crabpath inject \
  --state /tmp/crabpath_live_inject_state.json \
  --id learning::manual2 \
  --content "Never expose secrets in plain text." \
  --type TEACHING \
  --json \
  --connect-min-sim 0.0
```
