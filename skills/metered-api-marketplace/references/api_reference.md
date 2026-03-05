# API reference (metered-api-marketplace)

## Auth

All billable endpoints require:
- `x-api-key: <public key id>`
- `x-timestamp: <unix ms>`
- `x-signature: <hex hmac>`

Signature:
- `message = `${timestamp}.${rawBody}``
- `signature = HMAC_SHA256(api_secret, message)` (hex)

Rules:
- reject if timestamp skew > `MAX_SKEW_MS` (default 5 min)
- reject if signature mismatch

## Endpoints

### POST /v1/transform/:name
**Purpose:** call any transformer (pure-function input → output) behind metering.

Available transformers are listed in `GET /v1/balance` and include:
- revenue-amplifier
- ad-copy-optimizer
- lead-scoring-engine
- landing-page-generator
- competitor-price-monitor
- contract-risk-analyzer
- market-trend-signal-generator
- outbound-personalization-writer
- seo-brief-content-plan
- arbitrage-spread-detector
- churn-risk-retention-playbook
- support-triage-refund-risk

Plus high-frequency conversion/math endpoints:
- pricing-anchor
- objection-crush
- offer-stack
- cta-boost
- headline-power-scorer
- competitive-undercut
- scarcity-clock
- risk-reversal
- upsell-ladder
- authority-positioning
- simple-arbitrage-signal
- funnel-leak-detector

Request JSON:
```json
{
  "request_id": "optional-client-idempotency-key",
  "product": {"name": "...", "url": "..."},
  "market": {"niche": "...", "customer": "..."},
  "constraints": {"tone": "direct", "channel": "landing-page"}
}
```

Response JSON:
```json
{
  "ok": true,
  "data": {
    "positioning": "...",
    "offer_stack": ["..."],
    "pricing": {"strategy": "...", "numbers": [99, 299]},
    "headlines": ["..."],
    "risks": ["..."],
    "next_steps": ["..."]
  },
  "billing": {
    "cost_cents": 250,
    "balance_before_cents": 10000,
    "balance_after_cents": 9750,
    "usage_id": "..."
  }
}
```

Errors:
- 401/403 auth
- 402 insufficient balance
- 429 rate limit
- 500 transformer failure

### GET /v1/balance
Returns current balance and recent usage summary.

### POST /v1/payments/webhook/:provider
Provider webhook endpoint.

The server verifies provider signatures (shared secret) and applies credits idempotently.

Expected normalized payload (provider adapters should map to this):
```json
{
  "event_id": "provider-event-id",
  "api_key": "key_id",
  "gross_cents": 10000,
  "currency": "USD",
  "chain": "ETH",
  "txid": "0x...",
  "confirmations": 1
}
```
