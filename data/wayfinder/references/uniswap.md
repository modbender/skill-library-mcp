# Uniswap V3

## Overview

Uniswap V3 is a concentrated-liquidity AMM. The Uniswap adapter provides LP position reads and liquidity/fee management on supported EVM chains (defaults to Base).

- **Type**: `UNISWAP`
- **Module**: `wayfinder_paths.adapters.uniswap_adapter.adapter.UniswapAdapter`
- **Capabilities**: `uniswap.liquidity.add`, `uniswap.liquidity.increase`, `uniswap.liquidity.remove`, `uniswap.fees.collect`, `uniswap.position.get`, `uniswap.positions.list`, `uniswap.fees.uncollected`, `uniswap.pool.get`

## Usage (via custom scripts)

Uniswap operations are executed via one-off scripts under `.wayfinder_runs/` using `get_adapter()`:

```python
from wayfinder_paths.mcp.scripting import get_adapter
from wayfinder_paths.adapters.uniswap_adapter import UniswapAdapter

# Default chain_id is Base (8453). Override via config_overrides if needed.
adapter = get_adapter(UniswapAdapter, "main", config_overrides={"chain_id": 8453})

ok, positions = await adapter.get_positions()  # list all positions owned by the wallet
```

### High-value read methods

| Method | Purpose |
|--------|---------|
| `get_positions(owner?)` | List all Uniswap V3 positions for an owner |
| `get_position(token_id)` | Read a single position by NFT token id |
| `get_pool(token_a, token_b, fee)` | Resolve the pool address for a pair + fee tier |
| `get_uncollected_fees(token_id)` | Estimate uncollected fees for a position |

### Execution methods (fund-moving)

| Method | Purpose | Notes |
|--------|---------|-------|
| `add_liquidity(token0, token1, fee, tick_lower, tick_upper, amount0_desired, amount1_desired, slippage_bps=...)` | Mint a new LP position | Amounts are **raw units** |
| `increase_liquidity(token_id, amount0_desired, amount1_desired, slippage_bps=...)` | Add liquidity to an existing position | Amounts are **raw units** |
| `remove_liquidity(token_id, liquidity?, collect=True, burn=False)` | Decrease liquidity and optionally collect/burn | Uses NPM multicall |
| `collect_fees(token_id)` | Collect fees | — |

## Gotchas

- **Requires signing wallet:** Uniswap write methods require a wallet with `private_key_hex` and sufficient gas on the target chain.
- **Chain selection:** `UniswapAdapter` reads `chain_id` from config (default 8453). Make sure you’re on the intended chain.
- **Raw units:** Liquidity amounts and token amounts are in **raw integer units** (respect decimals).
