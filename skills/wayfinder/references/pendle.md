# Pendle

## Overview

Pendle splits yield-bearing assets into Principal Tokens (PTs) and Yield Tokens (YTs). PTs offer fixed yield at a discount; YTs offer leveraged exposure to variable yield.

- **Type**: `PENDLE`
- **Module**: `wayfinder_paths.adapters.pendle_adapter.adapter.PendleAdapter`
- **Capabilities**: `pendle.markets.read`, `pendle.market.snapshot`, `pendle.market.history`, `pendle.prices.ohlcv`, `pendle.prices.assets`, `pendle.swap.quote`, `pendle.swap.best_pt`, `pendle.swap.execute`, `pendle.convert.quote`, `pendle.convert.best_pt`, `pendle.convert.execute`, `pendle.positions.database`, `pendle.limit_orders.taker.read`, `pendle.limit_orders.maker.read`, `pendle.limit_orders.maker.write`, `pendle.deployments.read`, `pendle.router_static.rates`

## PT vs YT Mental Model

- **PT (Principal Token)**: "Fixed yield" leg. `fixedApy` = Pendle's `impliedApy`. Buy PT to lock in a fixed rate at a discount.
- **YT (Yield Token)**: "Floating yield" leg. `floatingApy` = `underlyingApy - impliedApy`. Leveraged exposure to variable yield.

## Market Discovery

```bash
# Describe Pendle adapter capabilities
poetry run wayfinder resource wayfinder://adapters/pendle_adapter

# Discover via wallet positions
poetry run wayfinder wallets --action discover_portfolio --wallet_label main --protocols '["pendle"]'
```

### Discovery Methods

| Method | Returns | Best for |
|--------|---------|----------|
| `list_active_pt_yt_markets(chain)` | Flattened list with `fixedApy`, `underlyingApy`, `liquidityUsd`, `daysToExpiry` | Market discovery, scanners (RECOMMENDED) |
| `fetch_markets(chain_id)` | Raw API (data **nested under `details`**) | When you need all raw fields |
| `fetch_market_snapshot(chain_id, market)` | Single market state | Point-in-time checks |
| `fetch_market_history(chain_id, market)` | Time series | Historical analysis |

### Chain IDs

Pendle-supported chain strings in this SDK:

`ethereum` → `1`, `bsc` → `56`, `arbitrum` → `42161`, `base` → `8453`, `plasma` → `9745`, `hyperevm` → `999`

## Execution

Pendle swaps are executed via one-off scripts using the Pendle Hosted SDK:

```bash
# Run a Pendle script (dry run)
poetry run wayfinder run_script --script_path .wayfinder_runs/pendle_buy_pt.py --wallet_label main

# Run live
poetry run wayfinder run_script --script_path .wayfinder_runs/pendle_buy_pt.py --wallet_label main --force
```

### Execution Methods

| Method | Purpose |
|--------|---------|
| `execute_swap(chain, market_address, token_in, token_out, amount_in, slippage, ...)` | Full execution: quote → approvals → broadcast. Returns `(True, {"tx_hash": ..., "quote": ...})`. Requires `strategy_wallet_signing_callback`. |
| `sdk_swap_v2(...)` | Quote only — returns `tx`, `tokenApprovals`, and quote metadata (`amountOut`, `priceImpact`, `impliedApy`) |
| `build_best_pt_swap_tx(...)` | Auto-selects best PT by `effectiveApy`, filters by liquidity/volume/expiry, quotes up to `max_markets_to_quote` |

**`execute_swap` inputs:**
- `amount_in` — **string in raw base units** (convert using token decimals)
- `slippage` — **decimal fraction** (`0.01` = 1%)
- `token_in` / `token_out` — ERC20 addresses (PTs and YTs are both valid `token_out` targets)

### Script Example (swap USDC into PT)

```python
from wayfinder_paths.mcp.scripting import get_adapter
from wayfinder_paths.adapters.pendle_adapter import PendleAdapter

adapter = get_adapter(PendleAdapter, "main")

# Discover best markets
markets = await adapter.list_active_pt_yt_markets(chain="base", min_liquidity_usd=250_000, sort_by="fixed_apy", descending=True)
market = markets[0]

# Execute swap into PT (amount_in is STRING in raw base units)
success, result = await adapter.execute_swap(
    chain="base",
    market_address=market["marketAddress"],
    token_in="0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913",  # USDC
    token_out=market["ptAddress"],
    amount_in="1000000",  # 1 USDC (6 decimals)
    slippage=0.01,  # 1% as decimal fraction
)
```

## Gotchas

- **`fetch_markets()` vs `list_active_pt_yt_markets()` (CRITICAL)**: `fetch_markets()` nests data under `details` — `m.get("impliedApy")` returns 0! Use `m.get("details", {}).get("impliedApy")`. `list_active_pt_yt_markets()` returns **flattened** data with renamed fields (e.g. `fixedApy`). **Always prefer `list_active_pt_yt_markets()` for discovery.**
- **Units are raw strings**: Hosted SDK expects `amountIn` in **raw base units as a string**. Resolve token decimals and convert explicitly.
- **Address formats**: `fetch_markets()` returns IDs like `"42161-0xabc..."`. `list_active_pt_yt_markets()` normalizes to plain `0x...` addresses.
- **Chain IDs**: Accepts both `chain=42161` and `chain="arbitrum"`.
- **Expiry**: PTs have fixed expiry dates. After expiry, PTs can be redeemed 1:1 for the underlying.
- **Liquidity**: Check pool liquidity and volume before large trades — thin pools have high slippage.
- **Approvals**: `execute_swap()` handles approvals automatically. For `sdk_swap_v2()`, you must execute `tokenApprovals` yourself before broadcasting.
- **Quote fields optional**: Hosted SDK may omit `effectiveApy`/`impliedApy` depending on market state. Always use `.get()` with defaults.
- **Receiver vs signer**: If `receiver != signer`, treat as high-risk and require explicit user confirmation.
