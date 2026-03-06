# I/O Contract

## Scripts

- `scripts/init_collection_run.py`
- `scripts/fetch_queries_batch.py`
- `scripts/fetch_query_metadata.py`
- `scripts/merge_selected_papers.py`

## Query Planning Policy (Model-side)

- Choose `3-4` total queries based on final target size.
- Split `target_max` across queries: `target_per_query = ceil(target_max / query_count)`.
- Set per-query fetch size as `target_per_query * 2` or `target_per_query * 3`.
- Keep one query close to original topic text.
- Use the remaining queries for normalized and synonym-expanded wording.
- Use `OR` for synonyms in the same semantic group.
  - Example model group: `(all:"LLM" OR all:"large language model" OR all:"AI")`.
  - Example domain group: `(all:"Lean 4" OR all:"Lean" OR all:"formal language")`.
- Use `AND` across different semantic groups to preserve relevance.
  - Example: `(model-group) AND (domain-group) AND all:"theorem proving"`.
- Allow iterative retry rounds:
  - If relevance is low, generate new query labels and fetch again.
  - If count is low, slightly broaden synonym groups with `OR`.
  - If new results are low quality, do not force low-quality additions; finishing below target minimum is acceptable.

## 1) init_collection_run.py

Creates a new run directory under `--output-root`.

Inputs:

- `--topic` and optional `--keywords`, `--categories`
- `--target-range`
- `--lookback` or `--from-date` + `--to-date`
- `--language` (markdown output language, default English)

Outputs:

- `task_meta.json`
- `task_meta.md`
- `query_results/`
- `query_selection/`

Notes:

- All generated markdown files follow the selected `--language` / `params.language`.

`task_meta.json` includes workflow logs:

- `query_plan`: executed query descriptors
- `query_fetch_logs`: per-query fetch stats
- `selection_logs`: merge/selection records

### `task_meta.json` full schema

Top-level fields (current implementation):

- `generated_at`: run creation timestamp (ISO 8601)
- `run_dir`: absolute run directory path
- `params`: request parameters captured at initialization
- `notes`: optional free-text notes from `init_collection_run.py`
- `query_plan`: query descriptors appended by `fetch_query_metadata.py`
- `query_fetch_logs`: per-query fetch logs appended by `fetch_query_metadata.py`
- `selection_logs`: merge logs appended by `merge_selected_papers.py`
- `execution` (optional): merge summary appended by `merge_selected_papers.py`

`params` object:

- `topic`
- `keywords` (list of strings)
- `categories` (list of strings)
- `target_range`
- `lookback`
- `from_date`
- `to_date`
- `language`
- `language_normalized`

`execution` object (added after merge):

- `selected_count`
- `candidate_after_merge`

Minimal initialization example (before merge):

```json
{
  "generated_at": "2026-02-14T00:00:00+00:00",
  "run_dir": "/.../topic-20260214-000000-30d",
  "params": {
    "topic": "LLM applications in Lean 4 formalization",
    "keywords": ["Lean 4", "LLM", "formalization"],
    "categories": ["cs.AI", "cs.LO"],
    "target_range": "5-10",
    "lookback": "30d",
    "from_date": "2026-01-15",
    "to_date": "2026-02-14",
    "language": "English",
    "language_normalized": "en"
  },
  "notes": "",
  "query_plan": [],
  "query_fetch_logs": [],
  "selection_logs": []
}
```

Post-merge, an `execution` object is added:

```json
{
  "execution": {
    "selected_count": 8,
    "candidate_after_merge": 8
  }
}
```

## 2) fetch_queries_batch.py

Runs `fetch_query_metadata.py` serially over a query plan JSON and applies safe defaults.

Inputs:

- `--run-dir`
- `--plan-json` (list or `{ "queries": [...] }`)
- optional:
  - `--language`
  - `--rate-state-path` (throttle state path; optional override)
  - `--default-max-results` (global override)
  - `--oversample-factor` (default `2`, used when auto-deriving per-query `max_results`)
  - `--max-results-cap` (default `60`)
  - `--min-interval-sec` / retry args (forwarded to each query fetch)
  - `--continue-on-error`
  - `--print-commands`
  - `--fetch-script`, `--python-bin`

Defaults applied automatically:

- serial execution
- rate-limit controls (`min-interval`, retries)
- run-local rate-state (`<run_dir>/.runtime/arxiv_api_state.json`) unless overridden
- default language from `task_meta.json > params.language`
- default categories from `task_meta.json > params.categories`
- per-query `max_results` from `target_range` and query count (unless overridden)

Outputs:

- Per-query outputs created by `fetch_query_metadata.py`
- one stdout summary JSON with per-query statuses

## 3) fetch_query_metadata.py

Runs one arXiv API query and writes indexed results.
Date window is pushed to API-side query using `submittedDate:[YYYYMMDDHHMM TO YYYYMMDDHHMM]`.

Inputs:

- `--run-dir`
- `--label`
- `--query`
- optional: `--max-results`, `--categories`, `--from-date`, `--to-date`, `--language`
- optional rate-limit controls:
  - `--min-interval-sec`
  - `--retry-max`
  - `--retry-base-sec`
  - `--retry-max-sec`
  - `--retry-jitter-sec`
- optional throttle state override: `--rate-state-path`
- default throttle state path (if not overridden): `<run_dir>/.runtime/arxiv_api_state.json`
- optional cache control: `--force`

Outputs:

- `query_results/<label>.json`
- `query_results/<label>.md`

`<label>.json` schema:

- `label`
- `query`
- `effective_query`
- `from_date`, `to_date`
- `results`: list of paper objects with `index`

### `task_meta.json > query_fetch_logs` schema

Each query fetch appends one log object:

- `label`: query label
- `api_returned_count`: number of entries returned by API (already date-filtered by `submittedDate`)
- `date_filter_mode`: currently `api_submittedDate`
- `json_path`: path to `query_results/<label>.json`
- `md_path`: path to `query_results/<label>.md`
- `language`: user language string
- `language_normalized`: normalized language code (`en` or `zh`)
- `cache_hit`: whether outputs came from compatible local cache
- `request_attempts`: number of request attempts to arXiv API (`0` when cache hit)
- `request_wait_seconds`: cumulative wait time from interval control + retry waits
- `rate_state_path`: effective throttle state path used for this fetch

Example:

```json
{
  "label": "lean4",
  "api_returned_count": 2,
  "date_filter_mode": "api_submittedDate",
  "json_path": ".../query_results/lean4.json",
  "md_path": ".../query_results/lean4.md",
  "language": "English",
  "language_normalized": "en",
  "cache_hit": false,
  "request_attempts": 1,
  "request_wait_seconds": 5.1,
  "rate_state_path": "/path/to/run/.runtime/arxiv_api_state.json"
}
```

## 4) merge_selected_papers.py

Merges model selections and dedupes by arXiv ID.

Inputs:

- `--run-dir`
- keep selections by index: `--keep label:0,2,5`
- optional keep by id: `--keep-id label:2601.00001,2601.00002`
- optional `--selection-json`
  - format A: `label -> [indexes_or_ids]`
  - format B: `label -> { keep_indexes: [...], keep_ids: [...] }`
  - empty list/object means explicit `keep 0` for that label
- optional `--incremental`
  - loads previous `query_selection/selected_by_query.json` as base
  - labels present in current `selection-json` override previous values
- optional `--language` (markdown output language)

Outputs:

- `query_selection/selected_by_query.json`
- `query_selection/merged_selected_raw.json`
- `<arxiv_id>/metadata.json`
- `<arxiv_id>/metadata.md`
- `papers_index.json`
- `papers_index.md`

Incremental notes:

- Running merge repeatedly is supported.
- Stale paper directories from previous merge outputs are removed when they are no longer selected.
- A run may end with fewer papers than original target range if relevance constraints require it.

## Per-paper metadata fields

Each `metadata.json` keeps arXiv metadata and selection provenance:

- `id`, `base_id`
- `title`, `summary`, `authors`
- `published`, `updated`
- `primary_category`, `categories`
- `abs_url`, `pdf_url`
- `selected_from_labels`
