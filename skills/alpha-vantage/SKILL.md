---
name: alpha-vantage
description: Use this skill when users need Alpha Vantage market data or indicators (stocks, ETFs, forex, crypto, commodities, macro, company fundamentals) via the official API. Apply it for ticker lookups, time series pulls, indicator calculations, screening/fundamental analysis, API integration code, and deployment-safe workflows requiring API key handling, throttling retries, and commercial/public-use guardrails.
---

# Alpha Vantage

## Overview

This skill provides a production-ready workflow for Alpha Vantage API usage: selecting the right endpoints, building validated requests, handling throttling/error responses, and preparing safe public/commercial deployment.

## Quick Start

1. Set API key: `export ALPHAVANTAGE_API_KEY=...`
2. For endpoint/params, read `references/api_docs.md`
3. For scriptable calls with retry/backoff, use `scripts/alpha_vantage_client.py`
4. For public deployment, follow the `Deployment Guardrails` section before release

## Workflow

1. Classify request type:
- Price bars or latest price: time series functions
- Indicators (RSI, SMA, MACD, etc.): technical indicator functions
- Company info, earnings, statements: fundamentals
- FX/Crypto/Commodities/Macro: their dedicated function families
2. Resolve mandatory parameters from `references/api_docs.md`.
3. Build request with `function=...` and `apikey=...`.
4. Parse response and branch for:
- HTTP error status
- `Error Message`
- `Note` (usually rate-limit/throttle condition)
- Empty/partial payload
5. If `Note`/throttled, retry using exponential backoff with jitter.
6. Normalize output to a stable schema before downstream use.

## Implementation Guidelines

### Authentication

- Use `ALPHAVANTAGE_API_KEY` environment variable by default.
- Never hardcode keys in source, logs, prompts, or examples.
- Mask keys in debug output (show only short prefix/suffix).

### Reliability and Rate Limits

- Treat responses containing `Note` as retriable throttle events.
- Use bounded retries with exponential backoff and jitter.
- For multi-symbol jobs, queue calls and pace to plan limits.
- Cache stable responses (fundamentals, metadata) to reduce quota burn.

### Response Validation

- Validate both transport and payload success.
- Handle string-encoded numbers safely (`float(...)`/`Decimal` as needed).
- Keep parser logic resilient to minor schema/key ordering changes.

### Data Quality

- Preserve source timestamps/time zones from payload metadata.
- Do not infer adjusted/unadjusted semantics; use explicit functions.
- Record the function and params used for reproducibility/auditability.

## Deployment Guardrails

### Public/Commercial Readiness

- Review Alpha Vantage terms before public/commercial release:
  https://www.alphavantage.co/terms_of_service/
- Ensure your usage tier and traffic profile are aligned with your plan:
  https://www.alphavantage.co/premium/
- Do not redistribute restricted content if terms disallow it.

### Security and Operations

- Store API keys in secret managers (or environment variables for local dev only).
- Add circuit-breaking and queue backpressure for upstream rate spikes.
- Instrument call counts, throttle rate, retry count, and error classes.
- Add alerting for sustained `Note` responses and non-2xx response spikes.

## Resources

### references/

- `references/api_docs.md` contains endpoint selection guidance and required parameters.

### scripts/

- `scripts/alpha_vantage_client.py` provides a reusable request wrapper with:
  - env-based auth
  - timeout and retry logic
  - throttle/error detection
  - optional compact output
