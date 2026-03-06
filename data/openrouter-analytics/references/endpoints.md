# OpenRouter Usage & Troubleshooting Endpoints

## Endpoint Matrix

| Endpoint | Key Type | Purpose |
|---|---|---|
| `GET /api/v1/activity` | Management key | Aggregate activity (last 30 completed UTC days), grouped by endpoint/model/provider |
| `GET /api/v1/credits` | Management key | Total credits and total usage |
| `GET /api/v1/keys` | Management key | Per-key usage stats (daily/weekly/monthly), limits, BYOK usage |
| `GET /api/v1/generation?id=...` | Regular API key | Detailed metadata for one request: provider, latency, tokens, usage, finish reason, provider fallback responses |

## Troubleshooting Notes

- Use `activity` for trend-level monitoring (spikes, expensive models, request volume).
- Use `keys` to identify which API key is consuming credits.
- Use `generation` when debugging one failed/slow/expensive request.
- For `generation`, keep the completion response `id` in your app logs so you can inspect incidents later.

## Useful Fields

### Activity
- `date`
- `model`
- `provider_name`
- `requests`
- `usage`
- `prompt_tokens`
- `completion_tokens`
- `reasoning_tokens`

### Generation
- `model`, `provider_name`
- `usage`, `total_cost`, `upstream_inference_cost`
- `tokens_prompt`, `tokens_completion`, `native_tokens_reasoning`, `native_tokens_cached`
- `latency`, `generation_time`, `finish_reason`, `native_finish_reason`
- `provider_responses[]` (fallback chain, endpoint IDs, status, per-provider latency)
