# Boros

## Overview

Boros provides fixed-rate markets on Arbitrum. It allows locking in a fixed funding rate for delta-neutral strategies, removing variable rate risk.

- **Type**: `BOROS`
- **Module**: `wayfinder_paths.adapters.boros_adapter.adapter.BorosAdapter`
- **Capabilities**: `market.read`, `market.quote`, `position.open`, `position.close`, `collateral.deposit`, `collateral.withdraw`

## Market Data

```bash
# Describe Boros adapter
poetry run wayfinder resource wayfinder://adapters/boros_adapter

# Discover positions
poetry run wayfinder wallets --action discover_portfolio --wallet_label main --protocols '["boros"]'
```

## Execution

Boros operations are executed via one-off scripts:

```bash
# Run a Boros script (dry run)
poetry run wayfinder run_script --script_path .wayfinder_runs/boros_lock_rate.py --wallet_label main

# Run live
poetry run wayfinder run_script --script_path .wayfinder_runs/boros_lock_rate.py --wallet_label main --force
```

### Script Example

```python
from wayfinder_paths.mcp.scripting import get_adapter
from wayfinder_paths.adapters.boros_adapter import BorosAdapter

adapter = get_adapter(BorosAdapter, "main")
markets = await adapter.discover_markets()
```

## Key Concepts

- **Yield Units (YU)**: The core trading unit. 1 YU ≈ $1 for USDT collateral; 1 YU = 1 HYPE (at unit price) for HYPE collateral. YU sizing is determined by margin formula, not 1:1 with collateral.
- **Implied APR**: The orderbook price — what the market expects the rate to be.
- **Underlying APR**: The actual funding rate that settles (e.g., Hyperliquid hourly funding).
- **Settlement cadence**: Mirrors the underlying venue — hourly for Hyperliquid, 8-hour for Binance/OKX. Must sample funding and rates on the same cadence.
- **Margin types**: **Cross** (shared across all positions) vs **Isolated** (locked to a specific market).
- **Collateral types**: WBTC (1), WETH (2), USDT (3), BNB (4), HYPE (5).
- **Funding sign convention**: Negative = shorts pay longs (longs receive). Positive = longs pay shorts.

### Rate Locking Recipes

- **Short hedge** (you're short a perp with positive funding): Open a **SHORT YU** on Boros to lock fixed funding you're paying.
- **Long hedge** (you're long a perp with positive funding): Open a **LONG YU** on Boros to lock fixed funding payment.
- "Current rate" = `BorosMarketQuote.mid_apr` — always fetch fresh via adapter.

## High-Value Reads

All BorosAdapter methods return `tuple[bool, result]` — always unpack. All fields use **snake_case** (not camelCase).

| Method | Purpose | Best For |
|--------|---------|----------|
| `list_tenor_quotes(underlying_symbol, platform)` | Fast market+rate snapshot (no orderbooks) | Quick tenor-level APR scan |
| `quote_market(market)` / `quote_market_by_id(market_id)` | Detailed APR quote with orderbook data | Single market analysis |
| `quote_markets_for_underlying(underlying_symbol)` | Quotes across all tenors for an underlying | Tenor curve building |
| `list_markets()` / `list_markets_all()` | Discover all markets (auto-paginates) | Market discovery |
| `get_orderbook(market_id, tick_size)` | Raw orderbook snapshot | Slippage estimation |
| `get_assets()` / `get_asset_by_token_id(token_id)` | Collateral asset addresses and metadata | Token address lookups |
| `list_available_underlyings(active_only)` | Unique underlying symbols with market counts | What's tradeable |
| `list_markets_by_collateral(token_id)` | Filter markets by collateral type | Collateral-specific queries |
| `get_enriched_market(market_id)` | Single market with all metadata joined | Full market context |
| `get_market_history(market_id, time_frame)` | OHLCV + rate history (`5m`, `1h`, `1d`, `1w`) | Historical analysis |

### Quote Fields (BorosMarketQuote)

- `mid_apr`, `best_bid_apr`, `best_ask_apr` — current implied fixed rates
- `mark_apr`, `floating_apr`, `long_yield_apr` — mark and floating rates
- `funding_7d_ma_apr`, `funding_30d_ma_apr` — moving averages
- `volume_24h`, `notional_oi`, `asset_mark_price` — market data

### Account State Reads (MUST check before trading)

**Always fetch current state before suggesting or executing any Boros trade:**

| Method | Purpose |
|--------|---------|
| `get_active_positions()` | Existing rate positions |
| `get_account_balances(token_id)` | Collateral summary (isolated/cross/total) |
| `get_collaterals()` | Full raw collateral data |
| `get_open_limit_orders()` | Pending limit orders |
| `get_withdrawal_status()` / `get_pending_withdrawal_amount()` | Withdrawal state |

**Why check first:** Avoid duplicate positions, unnecessary deposits, or trading with pending withdrawals.

## Collateral Types

| token_id | Token | Decimals | How to acquire on Arbitrum |
|----------|-------|----------|---------------------------|
| 1 | WBTC | 8 | BRAP swap |
| 2 | WETH | 18 | BRAP swap |
| 3 | USDT | 6 | BRAP swap to `usdt0-arbitrum` |
| 4 | BNB | 18 | BRAP swap |
| 5 | HYPE | 18 | OFT bridge from HyperEVM |

Each market accepts a specific collateral — check `market["tokenId"]` to know which one. Use `get_assets()` or `get_asset_by_token_id()` to get token addresses dynamically.

## YU Sizing (critical for order placement)

| Collateral | YU Meaning | $50 Position |
|------------|------------|--------------|
| USDT (token_id=3) | 1 YU ≈ $1 | `size_yu = 50` |
| HYPE (token_id=5) | 1 YU = 1 HYPE | `size_yu = 50 / hype_price` |

**Do NOT** set `target_yu = deposit_amount` — collateral does not cap YU 1:1. Max YU is determined by the margin formula. Apply a safety buffer (e.g., 50-70% of theoretical max) to avoid liquidation.

## Rate Locking Flow

1. **Pre-trade check** — Always fetch positions, balances, and collateral state first
2. **Discover markets** — Find available markets and tenors
3. **Get quote** — Check current fixed rates for your desired size (`mid_apr`)
4. **Check market collateral type** → acquire collateral if needed
5. **Deposit collateral** — Fund your Boros margin account
6. **Sweep isolated→cross** — If deposits land in isolated, sweep with `cash_transfer`
7. **Place order** — `place_rate_order(market_id, token_id, size_yu_wei, side, ...)`
8. **Monitor** — Track position until expiry or early close

## Gotchas

- **Units are not uniform**: Different calls use different decimals — native decimals vs 1e18 cash units vs YU. Always check what each method expects.
- **Collateral vs YU sizing**: Deposited collateral does NOT cap YU 1:1. Max YU is determined by margin formula.
- **Withdrawal cooldowns**: Withdrawals are two-step — request → cooldown period → finalize. Monitor withdrawal status.
- **Isolated cash issue**: Deposits can land in isolated margin even when requesting cross. Sweep with `cash_transfer`.
- **Min cross cash**: Some actions require minimum cross cash (`MMInsufficientMinCash` error).
- **Calldata sequencing**: Multi-tx payloads must execute sequentially (approve → deposit → place). Never parallelize.
- **Tick math**: Use adapter helpers for tick↔rate conversions. Don't compute manually.
- **Chain**: Boros operates on Arbitrum (42161). Ensure your wallet has Arbitrum ETH for gas.
- **HYPE acquisition paths**: Either BRAP→HyperEVM HYPE→OFT bridge, or Hyperliquid spot→HyperEVM→OFT bridge. OFT bridge requires `msg.value = amount + fee`, amounts rounded to `decimalConversionRate()`.
- **Markets endpoint**: `marketId` queries return lists. Underlying symbol lives at `metadata.assetSymbol`.
- **Funding sign convention**: Negative = shorts pay longs. Positive = longs pay shorts. Get this wrong and your hedge is backwards.
