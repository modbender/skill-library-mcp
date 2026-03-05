# Boosta API Error Handling

## Response patterns

Expected error payloads:

```json
{ "error": "..." }
```

or

```json
{
  "status": "active_job_exists",
  "job_id": "job_xxx",
  "job_status": "processing"
}
```

## Common cases

### 401 Unauthorized

- Cause: missing/invalid `Authorization` bearer key
- Action: verify `BOOSTA_API_KEY` and header format

### 400 Bad Request

- Cause: malformed payload, missing required field
- Action: include `video_url` and valid `video_type`

### 400 Invalid Video Type

- Cause: invalid `video_type`
- Action: use one of: `conversation`, `solo`, `gaming`, `vlog`, `faceless`, `movies`

### 403 No Credits

- Cause: account credits exhausted
- Action: stop retries and return a clear billing/credits message

### 429 Rate Limited

- Cause: too many requests
- Action: respect `retry_after` seconds, then retry with backoff

### Active Job Exists

- Cause: one-job-at-a-time limit hit
- Action: do not create a second job; continue polling returned `job_id`

## Retry policy

- Retry transient failures (`429`, `5xx`) with bounded attempts.
- Do not retry credential or validation failures (`401`, `400`, `403`) without changes.
- Log status code and body for debugging (redact secrets).
