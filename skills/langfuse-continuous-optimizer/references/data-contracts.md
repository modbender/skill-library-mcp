# Data Contracts

## Inputs

### OpenRouter activity CSV

Expected columns (current export format):

- `generation_id`
- `created_at`
- `cost_total`
- `tokens_prompt`
- `tokens_completion`
- `tokens_reasoning`
- `tokens_cached`
- `model_permaslug`
- `provider_name`
- `finish_reason_normalized`
- `generation_time_ms`
- `time_to_first_token_ms`
- `app_name`

### LangFuse JSON export

The script accepts:

- JSON array of observations/generations.
- JSON object with `data` array.
- JSONL (one JSON object per line).

Important fields used when present:

- top-level: `id`, `name`, `startTime`, `endTime`, `input`, `output`, `metadata`.
- `output.usage`: token fields.
- `metadata.attributes`: model/cost/usage details.
- `metadata.attributes.langfuse.trace.tags`: task tagging support.

### Evaluator scores file

Optional score files can be CSV or JSON and should include:

- ID key (any one): `event_id`, `observation_id`, `generation_id`, `id`, `trace_id`.
- score key (any one): `score`, `value`, `numeric_score`.
- metric key (optional): `metric`, `name`, `score_name`.

Scores are interpreted as:

- `0..1`: used directly.
- `1..100`: normalized by dividing by 100.

## Normalized Event JSONL

Each line in `normalized_events.jsonl` is a JSON object with keys like:

- identity: `source`, `source_file`, `source_row`, `event_id`, `trace_id`.
- segmentation: `task_key`, `name`, `model`, `provider`, `operation`, `app_name`, `tags`.
- timing: `started_at`, `ended_at`, `latency_ms`, `ttft_ms`.
- usage/cost: `prompt_tokens`, `completion_tokens`, `reasoning_tokens`, `cached_prompt_tokens`, `total_tokens`, `input_cost`, `output_cost`, `total_cost`.
- prompt lineage: `prompt_name`, `prompt_version`, `input_sha256`, `prompt_char_count`.
- quality: `eval_score` (optional).

## Outputs

### `routing_policy.json`

Contains:

- selection settings (`min_samples`, floor, weights, optional hard caps),
- defaults (`model`, `fallback_model`),
- task-level routes:
  - `task_key`
  - `selected_model`
  - `fallback_model`
  - observed stats
  - token limits
  - prompt action recommendations
  - full candidate ranking

### `model_stats.csv`

One row per `(task_key, model)` with aggregate metrics:

- quality, cost, latency,
- prompt/completion token stats,
- evaluator coverage.

### Continuous runner artifacts

When using `langfuse_openclaw_optimizer.py`:

- `config.json` (default `~/.openclaw/optimizer/config.json`): persisted runtime settings.
- `raw/<timestamp>/langfuse_observations.json`: API snapshot of observations.
- `raw/<timestamp>/langfuse_scores.csv`: normalized evaluator score rows.
- `cycles/<timestamp>/routing_policy.json`: staged policy for that cycle.
- `optimizer_memory.json`: persistent cycle history and promotion decisions.
