---
name: memory-bench-pioneer
description: "Be one of the first to benchmark your agent's memory — and help shape how AI remembers. Runs a peer-review-grade evaluation suite (LLM-as-judge, nDCG/MAP/MRR with 95% CIs, ablation studies) against your live memory system and submits anonymized results to the ENGRAM/CORTEX research papers. Your data stays private; only aggregate stats leave. Works with agent-memory-ultimate. For the bold few who believe AI memory should be measured, not guessed at."
---

# Memory Bench

Collect, assess, and submit anonymized memory system statistics for the ENGRAM and CORTEX research papers.

## Three-Step Pipeline

### 1. Assess Retrieval Quality

Run the standard test set (30 queries across 4 types × 3 difficulty levels) with LLM-as-judge:

```bash
# Full assessment with GPT-4o-mini judge + ablation (recommended)
python3 scripts/rate.py --queries 30 --judge openai --ablation

# Without OpenAI key: local embedding judge (weaker, marked in output)
python3 scripts/rate.py --queries 30 --judge local --ablation

# Custom test set
python3 scripts/rate.py --testset path/to/queries.json --judge openai
```

**What it measures:**

- **RAR** (Recall Accuracy Ratio), **MRR** (Mean Reciprocal Rank)
- **nDCG@5**, **MAP@5**, **Precision@5**, **Hit Rate**
- All metrics include **95% bootstrap confidence intervals**
- **Ablation**: runs with AND without spreading activation to isolate its contribution

**Judge methods:**

- `openai` — GPT-4o-mini rates each (query, result) pair 1-5. Independent from retrieval system. ~$0.01 per run.
- `local` — Embedding cosine similarity. Weaker, marked as such in output. Zero cost.

**Standard test set** (`scripts/testset.json`): 30 queries stratified across semantic/episodic/procedural/strategic types and easy/medium/hard difficulty. No lexical overlap with stored memories. All deployments run the same queries for cross-site comparability.

### 2. Collect Statistics

```bash
python3 scripts/collect.py --contributor GITHUB_USER --days 14 --output /tmp/memory-bench-report.json
```

**Collected (anonymized):** Memory counts/types/ages, strength/importance histograms, association graph size, hierarchy levels, consolidation history, retrieval metrics (RAR/MRR/nDCG/MAP with CIs), ablation results, judge method, algorithm version, embedding coverage. Instance ID is a random UUID (not reversible).

**Never collected:** Memory content, queries, file paths, usernames, hostnames.

### 3. Submit as PR

```bash
scripts/submit.sh /tmp/memory-bench-report.json GITHUB_USERNAME
```

Forks, branches, places report, updates INDEX.json, opens PR. Requires `gh` CLI.

## Validation Protocol

For peer-review-ready data, contributors should:

1. Run `rate.py --ablation --judge openai` (minimum N=30 queries)
2. Collect at least 2 reports from the same instance, ≥7 days apart (longitudinal)
3. Report the algorithm version (auto-captured from git)

## Test Set Format

Custom test sets are JSON arrays:

```json
[
  {
    "id": "T01",
    "query": "...",
    "category": "semantic|episodic|procedural|strategic",
    "difficulty": "easy|medium|hard"
  }
]
```

## Agent Workflow

When asked to submit benchmarks: run `rate.py --ablation --judge openai`, then `collect.py`, review summary, then `submit.sh`. Share the PR link.
