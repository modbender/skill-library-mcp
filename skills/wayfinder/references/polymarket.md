# Polymarket

## Overview

Polymarket is a prediction market platform. The Polymarket adapter supports:
- Market discovery (search/trending)
- Market/event details
- Prices, order books, and price history
- User status (balances, positions, orders)
- Collateral bridging and trade execution (requires signing wallet)

- **Type**: `POLYMARKET`
- **Module**: `wayfinder_paths.adapters.polymarket_adapter.adapter.PolymarketAdapter`
- **Capabilities**: `market.read`, `market.search`, `market.orderbook`, `market.candles`, `position.read`, `order.execute`, `order.cancel`, `bridge.deposit`, `bridge.withdraw`

## Read-Only Actions (CLI)

Polymarket reads use the `polymarket` tool (not `resource` URIs):

```bash
# Search markets
poetry run wayfinder polymarket --action search --query "bitcoin above" --limit 5

# Trending markets (by 24h volume)
poetry run wayfinder polymarket --action trending --limit 10

# Market details
poetry run wayfinder polymarket --action get_market --market_slug "some-market-slug"

# Account status (positions + balances; provide wallet_label or account)
poetry run wayfinder polymarket --action status --wallet_label main

# CLOB order book + price for a specific token_id
poetry run wayfinder polymarket --action order_book --token_id 123456
poetry run wayfinder polymarket --action price --token_id 123456 --side BUY
```

## Execution (CLI) — Live

Polymarket execution uses `polymarket_execute` and is **always live** (no dry-run flag).

**Wallet requirement:** `wallet_label` must resolve to a wallet in `config.json` that includes **both** `address` and `private_key_hex` (local dev only).

```bash
# Bridge USDC -> USDC.e collateral (Polymarket)
poetry run wayfinder polymarket_execute --action bridge_deposit --wallet_label main --amount 10

# Buy shares by market slug + outcome
poetry run wayfinder polymarket_execute --action buy --wallet_label main --market_slug "some-market-slug" --outcome YES --amount_usdc 2

# Close position (convenience: sells full size for the resolved token_id)
poetry run wayfinder polymarket_execute --action close_position --wallet_label main --market_slug "some-market-slug" --outcome YES
```

## Gotchas

- **USDC vs USDC.e (collateral mismatch):** Polymarket trading collateral is **USDC.e** on Polygon (`0x2791Bca1f2de4661ED88A30C99A7a9449Aa84174`, 6 decimals), not native Polygon USDC (`0x3c499c542cEF5E3811e1192ce70d8cC03d5c3359`). Use `bridge_deposit` / `bridge_withdraw` to convert.
- **Bridge utilities (BRAP vs bridge service):** `bridge_deposit` (USDC → USDC.e) and `bridge_withdraw` (USDC.e → USDC/destination token) prefer a fast on-chain BRAP swap on Polygon when possible (sender == recipient). Otherwise they fall back to the Polymarket Bridge service; the result includes `method: "polymarket_bridge"` and you may need to poll `polymarket --action bridge_status` until it clears.
- **`market_slug` vs `token_id`:** You can trade using `market_slug`+`outcome` or directly via the CLOB `token_id`. Prefer `market_slug` when possible.
- **Market found but not tradable:** Filter for `enableOrderBook`, `acceptingOrders`, `active`, `closed != true`, and non-empty `clobTokenIds`. Fallback to `trending` when fuzzy search returns stale/closed items.
- **Outcomes are not always YES/NO:** Some markets are multi-outcome. If `YES` doesn’t exist, retry with `outcome=0` (first outcome) or pick the exact outcome string from the market’s outcomes list.
- **Approvals:** Trading requires on-chain approvals on Polygon. These are handled automatically before order placement (idempotent).
- **Bridging:** Collateral flows may involve USDC/USDC.e conversions. Always verify balances via `polymarket --action status` after bridge operations.
- **Open orders:** `polymarket --action open_orders` requires a signing wallet (private key) due to Level-2 auth. Optional: pass `--token_id` to filter.
- **Buy then immediately sell can fail:** CLOB settlement/match can lag; you may not have shares available to sell instantly. If chaining BUY → SELL, wait for the buy confirmation first.
- **Rate limiting:** Avoid large concurrent scans of `price_history`. Use a semaphore (e.g. 4–8 concurrent calls) and retry/backoff on 429s.
- **Token IDs aren’t ERC20 addresses:** `clobTokenIds` are CLOB identifiers. Outcome shares are ERC1155 positions under ConditionalTokens.
- **Redemption requires `conditionId`:** Resolved markets redeem via ConditionalTokens `redeemPositions()` using the market’s `conditionId`.
