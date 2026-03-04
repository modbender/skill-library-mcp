# Webhooks

- Optional for async transcription or render pipelines.
- Expect events like: job queued, transcript ready, render complete.
- Validate signatures if provided and enforce idempotency.

## Minimal payload fields

- job_id
- status
- output_url
- created_at
