# WhenToMeet Troubleshooting (v1)

## Script checks first

Show script interface:

```bash
python3 scripts/w2m_events.py --help
```

Validate command shape quickly:

```bash
python3 scripts/w2m_events.py create --help
python3 scripts/w2m_events.py delete --help
```

If script output is non-JSON, treat command as failed and read stderr.

## Common failures

### 400 BAD_REQUEST

Likely causes:

- Missing top-level wrapper (`{"json": ...}`)
- Wrong field names
- Invalid timestamps
- `endTime <= startTime`

Checks:

- Confirm payload shape matches procedure exactly.
- Confirm timestamps are ISO-8601 UTC strings.

### 401 UNAUTHORIZED / 403 FORBIDDEN

Likely causes:

- Missing or invalid API key
- Key does not have required access

Checks:

- Ensure header is exactly `Authorization: Bearer $WHENTOMEET_API_KEY`.
- Ensure env var is set in runtime.

Script check:

```bash
python3 scripts/w2m_events.py list
```

If stderr shows `WHENTOMEET_API_KEY is required`, set the env var first.

### 404 NOT_FOUND

Likely causes:

- Wrong `eventId`
- Event not accessible for this key

Checks:

- Call list first and copy id directly from response.

### 429 TOO_MANY_REQUESTS

Use response headers:

- `X-RateLimit-Limit`
- `X-RateLimit-Remaining`
- `X-RateLimit-Reset`

Retry policy:

1. Wait until reset time.
2. Retry once.
3. If still throttled, stop and report rate-limit state.

## Response parsing guardrails

- Read success payload at `result.data.json`.
- Treat missing `result` as failure.
- For writes, only report success if API confirms it.
- `scripts/w2m_events.py` wraps this in:
  - `ok` (boolean)
  - `status` (HTTP)
  - `rateLimit` (limit/remaining/reset)
  - `body` (raw API response)

## Safety checklist

- Never print raw API keys.
- Never fabricate ids or URLs.
- Never delete without explicit user confirmation.
- Prefer list/get before destructive actions.
