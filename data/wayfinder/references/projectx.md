# ProjectX (HyperEVM)

## Overview

ProjectX is a Uniswap V3-style concentrated-liquidity DEX on HyperEVM. The ProjectX adapter supports:
- Pool overview reads (tick/price/liquidity + token metadata)
- Listing positions for a specific pool
- Minting/increasing liquidity using wallet balances (with optional balancing swaps)
- Fee collection / burning positions
- Exact-in swaps via the ProjectX router

- **Type**: `PROJECTX`
- **Module**: `wayfinder_paths.adapters.projectx_adapter.adapter.ProjectXLiquidityAdapter`
- **Capabilities**: `projectx.pool.overview`, `projectx.positions.list`, `projectx.liquidity.mint`, `projectx.liquidity.increase`, `projectx.liquidity.decrease`, `projectx.fees.collect`, `projectx.position.burn`, `projectx.swap.exact_in`

## Usage (via custom scripts)

The adapter requires:
- A signing wallet (`strategy_wallet.address` + `private_key_hex`)
- A `pool_address` in config (or `config_overrides`)

```python
from wayfinder_paths.mcp.scripting import get_adapter
from wayfinder_paths.adapters.projectx_adapter import ProjectXLiquidityAdapter

POOL = "0x..."  # ProjectX pool address (required)
adapter = get_adapter(ProjectXLiquidityAdapter, "main", config_overrides={"pool_address": POOL})

ok, overview = await adapter.pool_overview()
ok, positions = await adapter.list_positions()
```

### High-value methods

| Method | Purpose | Notes |
|--------|---------|-------|
| `pool_overview()` | Pool state + token metadata | Read-only |
| `list_positions(owner?)` | Positions in the configured pool | Read-only |
| `mint_from_balances(tick_lower, tick_upper, slippage_bps=...)` | Mint new LP position using balances | Fund-moving |
| `increase_liquidity_balanced(token_id, tick_lower, tick_upper, slippage_bps=...)` | Add liquidity after balancing | Fund-moving |
| `burn_position(token_id)` | Remove liquidity + collect + burn | Fund-moving |
| `swap_exact_in(from_token, to_token, amount_in, slippage_bps=...)` | Swap tokens (exact-in) | Fund-moving |

## Strategy Note

The `projectx_thbill_usdc_strategy` strategy uses this adapter for concentrated-liquidity market making on the THBILL/USDC stable pair.

## Gotchas

- **`pool_address` is required:** The adapter is pool-scoped; it will error without a configured pool.
- **ERC20-only swaps:** `swap_exact_in(...)` currently supports ERC20 tokens (no native token swaps).
- **Tick spacing:** When minting or adjusting ranges, ticks are rounded to the pool’s tick spacing.
