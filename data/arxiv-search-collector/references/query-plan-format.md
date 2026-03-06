# Query Plan Format

`fetch_queries_batch.py` accepts either:

- a JSON list of query items, or
- a JSON object with a `queries` list.

## Minimal Plan (Recommended)

Only `label` and `query` are required.

```json
[
  {
    "label": "lean4",
    "query": "all:\"Lean 4\""
  },
  {
    "label": "theorem-proving",
    "query": "all:\"interactive theorem proving\""
  },
  {
    "label": "llm-formalization",
    "query": "all:\"LLM formalization\""
  }
]
```

With this minimal plan, batch fetch auto-fills:

- `max_results` (derived from `target_range` and query count)
  - default rule: `target_per_query * 2`, capped by `--max-results-cap` (default `60`)
- language and categories from `task_meta.json`
- conservative rate-limit controls and retries
- run-local throttle state (per-run cooldown/throttling)

## Query Design Recommendation

- Build synonym groups with `OR` to improve recall.
  - Example model group: `(all:"LLM" OR all:"large language model" OR all:"AI")`
  - Example Lean group: `(all:"Lean 4" OR all:"Lean" OR all:"formal language")`
- Combine different groups with `AND` to keep topical relevance.
  - Example combined query:
    - `(all:"Lean 4" OR all:"Lean" OR all:"formal language") AND (all:"LLM" OR all:"large language model" OR all:"AI")`
- Keep one query close to original user wording, then add 2-3 expanded queries using this pattern.

## Iterative Retry Pattern

When first-round relevance is weak or final count is insufficient:

1. Add a new query plan file (for example `query_plan_round2.json`) with new labels.
2. Run `fetch_queries_batch.py` again for this run directory.
3. Update merge selection using `--incremental` and `selection-json`.
   - Set a label to `[]` to explicitly drop that query output (`keep 0`).
   - Keep previous good labels, and add new better labels.

Example update:

```json
{
  "lean4-round1": [0, 2, 4],
  "lean4-round2-broad": [],
  "lean-round2-refined": [1, 3, 5]
}
```

## Optional Per-query Overrides

```json
{
  "queries": [
    {
      "label": "lean4",
      "query": "all:\"Lean 4\"",
      "max_results": 20
    },
    {
      "label": "llm-formalization",
      "query": "all:\"LLM formalization\"",
      "categories": "cs.AI,cs.LO"
    }
  ]
}
```

Supported optional keys per item:

- `max_results`
- `categories`
- `from_date`, `to_date`
- `sort_by`, `sort_order`
- `start`
- `request_timeout`
- `user_agent`
- `language`

Global rate-state path is configured on the command line (not per item):

- `fetch_queries_batch.py --rate-state-path /path/to/arxiv_api_state.json`
