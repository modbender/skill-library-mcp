---
name: fred-navigator
description: Navigate FRED categories and series using fredapi, supporting natural-language queries with intent recognition and double validation.
metadata:
  short-description: FRED navigation and lookup
---

# FRED Navigator

## Purpose

Provide a reliable workflow to navigate FRED categories and series, with support for:
1. Direct `category_id`
2. Direct `series_id`
3. Natural-language `query` → intent recognition → double validation

## Inputs

- `category_id`: FRED category id
- `series_id`: FRED series id
- `query`: natural language request
- `limit`: number of candidates to return (default 5)
- `api_key`: read from environment `FRED_API_KEY` only

## Required Resources

- `references/fred_categories_tree.json`
- `references/fred_categories_flat.json`
- Optional: `references/category_paths.json` (precomputed)
- Optional: `references/synonyms.json`
- Helper script: `scripts/fred_query.py`
- Path builder: `scripts/build_paths.py`

### Optional Resource Structure Notes

- `references/category_paths.json` format:
  - `{ "category_id": { "id": <int>, "name": "<str>", "path": "<str>" }, ... }`
- `references/synonyms.json` format:
  - `{ "concept": ["alias1", "alias2", ...], ... }`

## Workflow

### 1. Category Exploration

1. Load `fred_categories_tree.json` for hierarchical browsing.
2. If user provides `category_id`, validate it exists.
3. If user provides `category_name`, fuzzy match against `flat` names and return candidates.

### 2. Series Discovery

1. Use `search_by_category(category_id)` to list available series.
2. Prefer `scripts/fred_query.py category <id>` for consistent output.
2. Return key columns:
   - `id`, `title`, `frequency`, `units`, `seasonal_adjustment`, `last_updated`.

### 3. Series Retrieval

1. Use `get_series(series_id)` for time series.
2. Use `get_series_info(series_id)` for metadata.
3. Prefer `scripts/fred_query.py series <id>` and `scripts/fred_query.py series-info <id>`.
3. Provide:
   - data head/tail
   - missing counts
   - latest value and date

### 4. Natural Language Query

#### 4.1 Intent Identification (Top-K)

1. Use the IDE agent (Codex) to interpret the natural-language intent.
2. Select the single best-matching category.
3. If confidence is low, ask the user to confirm the category before proceeding.
4. Use `references/category_paths.json` and `references/synonyms.json` as supporting context if available.

#### 4.2 Double Validation

**Structural validation**
- Candidate must exist in `fred_categories_tree.json`.
- Pass if at least one:
  - `children` non-empty
  - `search_by_category(id)` returns >= 1 series
  - Prefer `scripts/fred_query.py check-category <id>` for a quick check

**Semantic validation (agent)**
- Compare `query` with candidate `name/path`.
- Return `pass/fail` or numeric relevance score.

#### 4.3 Decision

- If structural + semantic validation both pass → accept category.
- Otherwise:
  - return Top-5 candidates
  - ask user to choose one explicitly

## Failure Handling

- Always provide Top-5 candidates when uncertain.
- Never proceed to series retrieval if category validation fails.

## Notes

- Do not hardcode API keys.
- Keep heavy reference data in `references/`, not in this file.
- When running Python functions for querying, execute them inside the sandbox environment.

## Maintenance

- Update workflow or constraints: edit `SKILL.md`.
- Update category data: replace files in `references/`.
- Improve natural-language matching: add or edit `references/synonyms.json` (key → list of related terms).
- Regenerate precomputed paths (optional): run `scripts/build_paths.py`.
- Add helper scripts (optional): place in `scripts/` and document usage here.
