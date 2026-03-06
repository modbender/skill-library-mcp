# Model Selection and Routing

## Routing Strategy

Select models by workload profile, not by a single default:

| Workload | Primary Goal | Routing Guidance |
|----------|--------------|------------------|
| Interactive chat | Lowest latency | Choose a fast text model and short prompts |
| Agent reasoning | Higher reliability | Choose a stronger reasoning model with tighter output checks |
| Summarization | Throughput | Batch requests and cap context size |
| Transcription | Accuracy + speed | Use a speech model and validate noisy inputs |

## Practical Selection Loop

1. Fetch live model list from `/models`.
2. Keep a short candidate set per workload.
3. Run the same prompt across candidates.
4. Compare latency, output quality, and failure rate.
5. Save winner + fallback in memory.

## Fallback Policy

Use a primary model and one fallback per workload:
- If timeout or repeated `5xx`, switch to fallback.
- If `429`, retry first, then fallback.
- Log the switch reason so routing can be improved later.

## Prompt Sizing Rules

- Keep system prompts compact and explicit.
- Split long context into summarized chunks.
- Avoid unnecessary history replay in every request.
- Use deterministic settings when output must be parsed.

## Production Checklist

- Primary and fallback model IDs are valid now.
- Retry policy is capped and observable.
- Output parsing fails closed, not open.
- P95 latency and error rate are tracked per route.
