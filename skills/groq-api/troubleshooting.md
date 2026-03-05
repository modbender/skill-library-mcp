# Troubleshooting Guide

## 401 Unauthorized

Symptoms:
- API returns `401`
- `/models` fails immediately

Checks:
1. Confirm `GROQ_API_KEY` is set in current shell.
2. Remove trailing spaces or quotes in env var value.
3. Re-run the `/models` check request.

## 404 or Model Not Found

Symptoms:
- Request accepted but model ID is rejected

Checks:
1. Fetch `/models` and copy exact model ID.
2. Remove stale IDs from saved defaults.
3. Re-test with a minimal payload.

## 429 Rate Limited

Symptoms:
- Spikes of `429` under burst traffic

Checks:
1. Add exponential backoff with jitter.
2. Reduce parallel requests and prompt size.
3. Route overflow to a fallback model.

## 5xx or Timeout

Symptoms:
- Intermittent server errors
- Long-tail latency increases

Checks:
1. Retry capped attempts before failing.
2. Shorten payload and disable non-essential options.
3. Fail over to fallback route and capture error context.

## JSON Parse Failures

Symptoms:
- Model returns prose when automation expects JSON

Checks:
1. Force strict output contract in system message.
2. Use low temperature for deterministic shape.
3. Validate parse before executing downstream actions.

## Transcription Quality Drops

Symptoms:
- Missing words or unstable output

Checks:
1. Verify input audio format and bitrate.
2. Split long audio into smaller segments.
3. Compare results across available speech models.
