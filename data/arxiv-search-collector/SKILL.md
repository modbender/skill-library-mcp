---
name: arxiv-search-collector
description: "Model-driven arXiv retrieval workflow for building a paper set with a manual language parameter: initialize a run, fetch metadata for each model-designed query, let the model filter irrelevant items per query by keep indexes, then merge and dedupe into per-paper metadata directories. Use when query planning and relevance filtering should be done by the model, not rule-based heuristics."
---

# ArXiv Search Collector

Use this skill when you want model-led query planning and model-led relevance filtering.

## Core Principle

Scripts are tools. The model performs the reasoning and decisions:

1. Expand the original topic into multiple focused queries.
2. Run one fetch command per query.
3. Read each query result list and decide keep indexes.
4. Merge kept items and dedupe with one script.

## Step 1: Initialize Run

```bash
python3 scripts/init_collection_run.py \
  --output-root /path/to/data \
  --topic "LLM applications in Lean 4 formalization" \
  --keywords "Lean 4,LLM,formalization" \
  --categories "cs.AI,cs.LO" \
  --target-range 5-10 \
  --lookback 30d \
  --language English
```

This creates a run directory with `task_meta.json`, `task_meta.md`, `query_results/`, and `query_selection/`.

## Language Parameter

- `--language` must be set manually for each collection run.
- Use the same language value across all collector scripts for consistency.
- If `--language` is non-English (for example `Chinese`), generated markdown files are written in that language:
  - `task_meta.md`
  - `query_results/<label>.md`
  - `<arxiv_id>/metadata.md`
  - `papers_index.md`

## Query Writing Requirements

Follow these rules before running per-query fetch:

1. Determine query count from final target range.
- Prefer `3` queries for small/medium targets (`2-5`, `5-10`).
- Prefer `4` queries for larger targets (`10-50` or above).
- Avoid writing too many low-quality queries.

2. Allocate target budget to each query, then oversample.
- Let `target_max` be the upper bound in target range.
- Compute `target_per_query = ceil(target_max / query_count)`.
- Fetch each query with `max_results = target_per_query * 2` (or `* 3` when recall is more important).
- Example: target `5-10`, query count `3` -> `target_per_query=4` -> each query fetches `8-12`.

3. Keep one original-theme query, then add normalized/synonym expansions.
- Query 1 keeps original topic wording.
- Remaining queries use normalized terms and close synonyms.
- Prefer concise noun phrases that match arXiv indexing behavior.

4. Use `OR` inside the same semantic group (synonyms), and `AND` across groups.
- Same-group synonyms should be connected with `OR` to increase recall.
  - Example group A (model terms): `LLM OR "large language model" OR AI`.
  - Example group B (Lean terms): `"Lean 4" OR Lean OR "formal language"`.
- Different semantic groups should be connected with `AND` to keep relevance.
  - Example: `(LLM-group) AND (Lean-group)`.
- Recommended pattern:
  - `(<domain terms with OR>) AND (<method/model terms with OR>) [AND <optional constraint terms>]`

### Query Examples (arXiv API-ready)

Theme A: `LLM applications in Lean 4 formalization`
- `all:"LLM applications in Lean 4 formalization"`
- `(all:"Lean 4" OR all:"Lean" OR all:"formal language") AND (all:"LLM" OR all:"large language model" OR all:"AI")`
- `(all:"Lean" OR all:"formalization") AND (all:"LLM" OR all:"large language model") AND all:"theorem proving"`
- `(all:"Lean" OR all:"proof assistant") AND (all:"AI" OR all:"LLM")`

Theme B: `agentic tool use for code generation`
- `all:"agentic tool use code generation"`
- `(all:"agentic" OR all:"autonomous agent") AND (all:"LLM" OR all:"large language model")`
- `(all:"tool use" OR all:"function calling") AND (all:"coding assistant" OR all:"code generation")`

Theme C: `multimodal reasoning with retrieval`
- `all:"multimodal reasoning retrieval"`
- `(all:"multimodal" OR all:"vision language") AND (all:"retrieval" OR all:"RAG")`
- `(all:"multimodal model" OR all:"vision language model") AND (all:"reasoning" OR all:"tool use")`

## Step 2: Fetch One Query at a Time

Model defines queries manually, for example:

- `all:"Lean 4"`
- `all:"LLM formalization"`
- `all:"AI formal verification"`

Recommended batch mode (safe defaults, serial execution):

```bash
python3 scripts/fetch_queries_batch.py \
  --run-dir /path/to/run-dir \
  --plan-json /path/to/query_plan.json
```

In batch mode, the script auto-applies:

- serial API calls
- `--min-interval-sec 5`
- `--retry-max 4`
- `--retry-base-sec 5`
- `--retry-max-sec 120`
- `--retry-jitter-sec 1`
- per-run rate-state file (`<run_dir>/.runtime/arxiv_api_state.json`) for throttling
- auto `max_results` from `target_range` and query count (default oversample `x2`, cap `60`)
- default language/categories from `task_meta.json`

Minimal `query_plan.json` only needs `label` and `query`.
See `references/query-plan-format.md`.
You normally do not need to set fetch-control args manually.

If you need one-by-one manual fetch, run each query:

```bash
python3 scripts/fetch_query_metadata.py \
  --run-dir /path/to/run-dir \
  --label lean4 \
  --query 'all:"Lean 4"' \
  --max-results 30 \
  --min-interval-sec 5 \
  --retry-max 4 \
  --language English
```

Output files:

- `query_results/<label>.json` (indexed full metadata list)
- `query_results/<label>.md` (human-readable preview)

Date range is applied directly in arXiv API `search_query` via `submittedDate:[... TO ...]`.
No second local date-filter pass is performed.

Rate-limit controls in `fetch_query_metadata.py`:

- `--min-interval-sec` (default `5.0`)
- `--retry-max` (default `4`)
- `--retry-base-sec` (default `5.0`)
- `--retry-max-sec` (default `120.0`)
- `--retry-jitter-sec` (default `1.0`)
- `--rate-state-path` (optional override; default is `<run_dir>/.runtime/arxiv_api_state.json`)
- `--force` to bypass cache and re-fetch

## Step 3: Model Filters Relevance

For each query list, the model reads indexed results and decides what to keep.

Use keep specs by index and/or arXiv ID when merging.
To explicitly drop one weak query in later iterations, set that label to an empty keep list in `selection-json`.

## Step 4: Merge and Dedupe

```bash
python3 scripts/merge_selected_papers.py \
  --run-dir /path/to/run-dir \
  --keep lean4:0,2,4 \
  --keep llm-formalization:1,3 \
  --language English
```

or with `selection-json`:

```json
{
  "lean4-round1": [0, 2, 4],
  "lean4-round2": [],
  "formalization-round2": [1, 3, 5]
}
```

An empty list means this query label is intentionally dropped (`keep 0`).

This writes final outputs:

- `<arxiv_id>/metadata.json`
- `<arxiv_id>/metadata.md`
- `papers_index.json`
- `papers_index.md`

## Step 5: Iterative Retry Loop (Incremental)

If relevance is weak or final count is insufficient after Step 4, iterate:

1. Review `papers_index.md` and per-paper metadata quality.
2. Adjust query plan (usually broaden with additional synonym `OR` terms, keep cross-group `AND` constraints).
3. Fetch additional query results with new labels.
4. Re-run merge in incremental mode:

```bash
python3 scripts/merge_selected_papers.py \
  --run-dir /path/to/run-dir \
  --incremental \
  --selection-json /path/to/updated_selection.json \
  --language English
```

Incremental behavior:

- Previous label selections are loaded from `query_selection/selected_by_query.json`.
- Labels provided in the new `selection-json` override previous selections for those labels.
- New labels can be added.
- Old labels can be dropped by setting `[]`.

Stop retrying when:

- relevance is acceptable, or
- additional broadened queries mainly add low-relevance papers.

If relevant papers are genuinely scarce, it is valid to finish below the original minimum target range.

## Notes

- Keep API concurrency conservative by controlling query count and `--max-results`.
- Keep per-query fetch serial (no parallel API calls in Stage A).
- Reuse cache by default for identical query/date/request settings; only use `--force` when necessary.
- Prefer default run-local rate-state so all steps in the same run share one cooldown/throttling state.
- If arXiv API returns `429 Too Many Requests`, retry later and/or increase `--min-interval-sec`.
- Prefer explicit, narrow queries and let the model filter aggressively.
- Use `references/io-contract.md` for exact files and schema.

## Related Skills

This skill is a sub-skill of `arxiv-summarizer-orchestrator`.

Pipeline position:

1. Step 1 (collection): `arxiv-search-collector` (this skill)
2. Step 2 (per-paper processing): `arxiv-paper-processor`
3. Step 3 (batch reporting): `arxiv-batch-reporter`

This skill produces the initial paper-set structure and metadata that Stage B and Stage C depend on.
