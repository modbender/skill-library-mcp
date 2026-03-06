# Billing + Ledger notes

## Ledger model
Store **cents** (integers). Never floats.

Tables (conceptual):
- `api_keys(id, secret, created_at, disabled_at)`
- `balances(api_key_id, balance_cents)` (or compute from ledger)
- `usage(id, api_key_id, route, request_hash, cost_cents, created_at)`
- `credits(id, api_key_id, provider, event_id, gross_cents, fee_cents, net_cents, created_at)`

## Pricing
Keep it simple first:
- fixed `COST_CENTS_PER_CALL` per call (flat pricing across all transformers)

Later:
- tiered pricing by plan
- dynamic pricing by payload size
- model/token based pricing

## Platform fee (2.5%)
When a top-up is credited:
- `fee_cents = round(gross_cents * 0.025)`
- `net_cents = gross_cents - fee_cents`
- credit user balance by `net_cents`

Fee destination addresses (accounting targets):
- ETH: `FEE_ETH_ADDRESS`
- BTC: `FEE_BTC_ADDRESS`

**Important:** the reference server only accounts for the fee. Actual on-chain splitting/sweeps should be handled by your payment processor/wallet ops.

## Idempotency
- usage: accept optional `request_id` and/or compute `request_hash` (raw body sha256)
- credits: require provider `event_id` unique constraint

## Anti-abuse defaults
- per-key rate limits
- timestamp skew checks
- payload size limits
- denylist/allowlist by key
