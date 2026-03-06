# HyperLend

## Overview

HyperLend is a lending protocol on HyperEVM. It provides stablecoin lending yield with straightforward supply/withdraw mechanics.

- **Type**: `HYPERLEND`
- **Module**: `wayfinder_paths.adapters.hyperlend_adapter.adapter.HyperlendAdapter`
- **Capabilities**: `market.stable_markets`, `market.assets_view`, `market.rate_history`, `lending.lend`, `lending.unlend`

## Market Data

```bash
# Describe HyperLend adapter
poetry run wayfinder resource wayfinder://adapters/hyperlend_adapter

# Discover positions
poetry run wayfinder wallets --action discover_portfolio --wallet_label main --protocols '["hyperlend"]'
```

### High-Value Reads

| Method | Purpose | Output |
|--------|---------|--------|
| `get_stable_markets(chain_id, ...)` | Opportunity list | `list[StableMarket]` — `chain_id`, `token_address`, `symbol`, liquidity/buffer fields |
| `get_assets_view(chain_id, user_address)` | Portfolio view | `AssetsView` — `assets: list[dict]`, optional `total_value` |
| `get_lend_rate_history(chain_id, token_address, lookback_hours)` | Rate time series | `LendRateHistory` — `rates: list[dict]` (timestamped records) |

### Data Accuracy

- Only report values fetched from HyperLend endpoints (`market_entry`, `lend_rate_history`). Do **not** estimate or invent APYs.
- HyperlendClient methods use `_authed_request(...)` even for `/public/hyperlend/*` routes — auth via `config.json` or env vars is always required.

## Execution

HyperLend operations are executed via one-off scripts:

```bash
# Run a HyperLend script (dry run)
poetry run wayfinder run_script --script_path .wayfinder_runs/hyperlend_supply.py --wallet_label main

# Run live
poetry run wayfinder run_script --script_path .wayfinder_runs/hyperlend_supply.py --wallet_label main --force
```

### Script Example (supply USDT0)

```python
from wayfinder_paths.mcp.scripting import get_adapter
from wayfinder_paths.adapters.hyperlend_adapter import HyperlendAdapter

adapter = get_adapter(HyperlendAdapter, "main")
result = await adapter.supply(token="USDT0", amount=100_000_000)  # raw int units
```

### Execution Methods

| Method | Purpose | Notes |
|--------|---------|-------|
| `lend(underlying_token, qty, chain_id, native=False)` | Supply to HyperLend | `qty` is raw int (wei); handles ERC20 approval automatically |
| `unlend(underlying_token, qty, chain_id, native=False)` | Withdraw from HyperLend | Same unit rules as `lend` |

### Unit Conversion Best Practice

1. Resolve token decimals via TokenClient
2. Convert human-readable → raw int units
3. Call `lend`/`unlend` with raw units

## HyperLend Stable Yield Strategy

For automated yield on HyperLend, use the dedicated strategy:

```bash
poetry run wayfinder run_strategy --strategy hyperlend_stable_yield_strategy --action status
poetry run wayfinder run_strategy --strategy hyperlend_stable_yield_strategy --action analyze --amount_usdc 100
poetry run wayfinder run_strategy --strategy hyperlend_stable_yield_strategy --action deposit --main_token_amount 100 --gas_token_amount 0.1
poetry run wayfinder run_strategy --strategy hyperlend_stable_yield_strategy --action update
```

## Gotchas

- **Chain**: HyperLend runs on HyperEVM. Ensure your wallet has HyperEVM gas tokens.
- **RPC**: HyperEVM RPC endpoints can be slower than Base/Arbitrum. RPC URLs must be configured via `config.json` under `strategy.rpc_urls` or via env vars (fallback `RPC_URL`).
- **Units are raw ints**: `lend`/`unlend` expect **raw integer units** (wei for ERC20). Do not pass floats or human-readable values directly.
- **Supported assets**: Primarily stablecoins (USDT0). Check market snapshots for current offerings.
- **No guessing yields**: Do not claim extra yield sources (e.g. "~3-4% staking APY") unless fetched from a concrete data source. Rates change frequently.
