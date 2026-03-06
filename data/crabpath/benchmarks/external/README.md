# External benchmarks

These scripts run the two external corpora used in repo papers and internal experiments.

## Datasets

* MultiHop-RAG (`multihop_rag.json`) for 2556 multi-hop queries across web and news corpora.
* HotPotQA dev distractor (`hotpotqa_dev_distractor.json`) for explainable two-hop QA with supporting facts.

## Download

```bash
mkdir -p benchmarks/external
curl -L https://huggingface.co/datasets/yixuantt/MultiHopRAG/raw/main/MultiHopRAG.json -o benchmarks/external/multihop_rag.json
curl -L https://curtis.ml.cmu.edu/datasets/hotpot/hotpot_dev_distractor_v1.json -o benchmarks/external/hotpotqa_dev_distractor.json
```

## Quick vs full runs

Quick run (default limits):
```bash
python3 benchmarks/external/run_multihop_rag.py
python3 benchmarks/external/run_hotpotqa.py
```

Full run:
```bash
python3 benchmarks/external/run_multihop_rag.py --limit 2556
python3 benchmarks/external/run_hotpotqa.py --limit 0
```

## Expected outputs

* `benchmarks/external/*_results.json` (run output)
* Cached query/node embeddings written to: `benchmarks/external/.embedding_cache_*.json`

## Notes

- Set `--limit` smaller for faster smoke tests. Example: `--limit 50`.
- Use `--seed-top-k`, `--embed-top-k`, `--max-hops`, and `--beam-width` to tune traversal and embedding breadth.
- Embeddings are the only expected paid API calls (`text-embedding-3-small`). Query and traversal phases are in-memory once cache is populated.
```
