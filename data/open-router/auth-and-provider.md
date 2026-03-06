# Auth and Provider — Open Router

## Goal

Connect an OpenAI-compatible workflow to OpenRouter with explicit auth checks and zero secret leakage in notes.

## Verification Flow

1. Confirm `OPENROUTER_API_KEY` is present in the environment.
2. Run a lightweight models request to confirm auth and network path.
3. Record only pass/fail and timestamp in memory.

## Minimal Request Pattern

```bash
curl -sS https://openrouter.ai/api/v1/models \
  -H "Authorization: Bearer ${OPENROUTER_API_KEY}" \
  -H "Content-Type: application/json" | jq '.data | length'
```

## Provider Wiring Checklist

- Endpoint uses `https://openrouter.ai/api/v1`.
- Authorization header uses bearer token from environment variable.
- Client timeout and retry strategy are explicit.
- Default model is set per workload class, not globally for all tasks.

## Common Auth Failures

- Missing key in current shell session -> source environment and retry.
- Wrong header format -> enforce `Authorization: Bearer ...`.
- Silent proxy mismatch -> test direct path before debugging client wrappers.
- Expired or revoked key -> rotate key and re-run minimal verification.
