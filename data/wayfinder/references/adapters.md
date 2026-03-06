# Adapters

## Overview

Adapters are protocol integrations that provide read and write capabilities. Strategies compose adapters to build trading logic.

## Discovering Adapters

```bash
# List all adapters with capabilities
poetry run wayfinder resource wayfinder://adapters

# Describe a specific adapter
poetry run wayfinder resource wayfinder://adapters/moonwell_adapter
```

## Adapter Reference

### Balance Adapter (`balance_adapter`)

- **Type**: `BALANCE`
- **Module**: `wayfinder_paths.adapters.balance_adapter.adapter.BalanceAdapter`
- **Protocol**: EVM wallets (Base, Arbitrum, Ethereum, HyperEVM)
- **Capabilities**: `balance.read`, `transfer.main_to_strategy`, `transfer.strategy_to_main`, `transfer.send`

Provides token balance queries for any wallet, cross-wallet transfers between main and strategy wallets, and automatic ledger recording for deposits/withdrawals.

```bash
poetry run wayfinder resource wayfinder://balances/main
poetry run wayfinder resource wayfinder://tokens/resolve/usd-coin-base
poetry run wayfinder resource wayfinder://activity/main
```

### BRAP Adapter (`brap_adapter`)

- **Type**: `BRAP`
- **Module**: `wayfinder_paths.adapters.brap_adapter.adapter.BRAPAdapter`
- **Protocol**: Cross-chain swap aggregator (Bridge/Router/Adapter Protocol)
- **Capabilities**: `swap.quote`, `swap.execute`, `swap.compare_routes`, `bridge.quote`, `gas.estimate`

Handles cross-chain swaps and bridges with quote fetching, route optimization, and execution.

```bash
poetry run wayfinder quote_swap --wallet_label main --from_token usd-coin-base --to_token ethereum-base --amount 100
poetry run wayfinder execute --kind swap --wallet_label main --from_token usd-coin-base --to_token ethereum-base --amount 100
```

**Key Methods:**
- `BRAPClient.get_quote(from_token, to_token, from_chain, to_chain, from_wallet, from_amount, slippage?)` — Low-level quote (amount in **raw base units** as string)
- `BRAPAdapter.best_quote(...)` — Returns single best route; supports `preferred_providers`
- `BRAPAdapter.swap_from_token_ids(from_token_id, to_token_id, from_address, amount, slippage, ...)` — Execute swap by token IDs
- `BRAPAdapter.swap_from_quote(from_token, to_token, from_address, quote, ...)` — Execute from a pre-fetched quote

**Recommended Quote Loop:**
1. Call `quote_swap` (does token lookup + human→raw conversion + returns preview)
2. Inspect `from_token`/`to_token` in response to verify correct asset + chain
3. Pass `suggested_execute_request` directly into `execute`

**BRAP Gotchas:**
- **Broadcast ≠ success**: A tx hash does not mean the swap succeeded. The SDK waits for receipt and raises `TransactionRevertedError` on `status=0`.
- **Units**: Quote input `from_amount` is **raw base units**. Resolve decimals via TokenClient first.
- **Slippage formats**: BRAP adapter uses **decimal fraction** (`0.005` = 0.5%). MCP may use bps (`50` = 0.5%). Don't mix.
- **Approvals**: Some tokens are "strict approve" and require setting allowance to 0 before increasing — the adapter has a built-in allowlist.
- **Recipient safety**: Treat `recipient != sender` as high-risk; require explicit user confirmation.
- **USD enrichment is best-effort**: USD fields in quotes may fail; rely on raw amounts for correctness.
- **Native token sends**: For tiny amounts use scientific notation (`"1e-18"`); long decimal strings may cause serialization errors.
- **Native sends**: Require `token: "native"` and `chain_id` in the request.

### CCXT Adapter (`ccxt_adapter`)

- **Type**: `CCXT`
- **Module**: `wayfinder_paths.adapters.ccxt_adapter.adapter.CCXTAdapter`
- **Protocol**: Centralized exchanges (CEXes) via CCXT
- **Capabilities**: `exchange.factory`

Use this only when the user explicitly wants CEX data/trading and has API credentials configured in `config.json` under `ccxt`. For Hyperliquid, prefer the native Hyperliquid tools/adapters unless the user explicitly asks for CCXT.

See [ccxt.md](ccxt.md) for setup + examples.

### Boros Adapter (`boros_adapter`)

- **Type**: `BOROS`
- **Module**: `wayfinder_paths.adapters.boros_adapter.adapter.BorosAdapter`
- **Protocol**: Boros (Arbitrum) - Fixed-rate funding markets
- **Capabilities**: `market.read`, `market.quote`, `position.open`, `position.close`, `collateral.deposit`, `collateral.withdraw`

Provides fixed-rate market discovery, quoting, orderbook data, deposits, withdrawals, and position management on Boros.

See [boros.md](boros.md) for details.

### HyperLend Adapter (`hyperlend_adapter`)

- **Type**: `HYPERLEND`
- **Module**: `wayfinder_paths.adapters.hyperlend_adapter.adapter.HyperlendAdapter`
- **Protocol**: HyperLend (HyperEVM)
- **Capabilities**: `market.stable_markets`, `market.assets_view`, `market.rate_history`, `lending.lend`, `lending.unlend`

Provides stable market snapshots, rate history time series, and stablecoin supply/withdraw operations on HyperLend.

See [hyperlend.md](hyperlend.md) for details.

### Hyperliquid Adapter (`hyperliquid_adapter`)

- **Type**: `HYPERLIQUID`
- **Module**: `wayfinder_paths.adapters.hyperliquid_adapter.adapter.HyperliquidAdapter`
- **Protocol**: Hyperliquid DEX
- **Capabilities**: `market.read`, `market.meta`, `market.funding`, `market.candles`, `market.orderbook`, `order.execute`, `order.cancel`, `position.manage`, `transfer`, `withdraw`

Comprehensive Hyperliquid integration for perp/spot state, funding rates, mid prices, order books, candles, market/limit orders, leverage, deposits, and withdrawals.

See [hyperliquid.md](hyperliquid.md) for details.

### Polymarket Adapter (`polymarket_adapter`)

- **Type**: `POLYMARKET`
- **Module**: `wayfinder_paths.adapters.polymarket_adapter.adapter.PolymarketAdapter`
- **Protocol**: Polymarket (prediction markets)
- **Capabilities**: `market.read`, `market.search`, `market.orderbook`, `market.candles`, `position.read`, `order.execute`, `order.cancel`, `bridge.deposit`, `bridge.withdraw`

Read Polymarket markets/events, prices and order books, and (with a signing key) place trades and bridge collateral.

**Read-only examples:**

```bash
poetry run wayfinder polymarket --action search --query "bitcoin above" --limit 5
poetry run wayfinder polymarket --action status --wallet_label main
```

**Execution examples (live):**

```bash
poetry run wayfinder polymarket_execute --action bridge_deposit --wallet_label main --amount 10
poetry run wayfinder polymarket_execute --action buy --wallet_label main --market_slug "some-market" --outcome YES --amount_usdc 2
```

See [polymarket.md](polymarket.md) for details.

### Ledger Adapter (`ledger_adapter`)

- **Type**: `LEDGER`
- **Module**: `wayfinder_paths.adapters.ledger_adapter.adapter.LedgerAdapter`
- **Protocol**: Local bookkeeping
- **Capabilities**: `ledger.read`, `ledger.record`, `ledger.snapshot`

Provides transaction history tracking, net deposit calculations, deposit/withdrawal recording, and strategy operation logging.

### Moonwell Adapter (`moonwell_adapter`)

- **Type**: `MOONWELL`
- **Module**: `wayfinder_paths.adapters.moonwell_adapter.adapter.MoonwellAdapter`
- **Protocol**: Moonwell (Base)
- **Capabilities**: `lending.lend`, `lending.unlend`, `lending.borrow`, `lending.repay`, `collateral.set`, `collateral.remove`, `rewards.claim`, `position.read`, `market.apy`, `market.collateral_factor`

Full Moonwell integration including lending (supply/withdraw), borrowing (borrow/repay), collateral management, WELL rewards claiming, and position/market queries.

**Supported Markets (Base)**:

| Token | mToken Address | Underlying Address |
|-------|----------------|-------------------|
| USDC | `0xEdc817A28E8B93B03976FBd4a3dDBc9f7D176c22` | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| WETH | `0x628ff693426583D9a7FB391E54366292F509D457` | `0x4200000000000000000000000000000000000006` |
| wstETH | `0x627Fe393Bc6EdDA28e99AE648fD6fF362514304b` | `0xc1CBa3fCea344f92D9239c08C0568f6F2F0ee452` |

See [moonwell.md](moonwell.md) for details.

### Multicall Adapter (`multicall_adapter`)

- **Type**: `MULTICALL`
- **Module**: `wayfinder_paths.adapters.multicall_adapter.adapter.MulticallAdapter`
- **Protocol**: EVM batch calls
- **Capabilities**: `multicall.aggregate`

Batches multiple on-chain read calls into a single RPC request for efficiency.

### Pendle Adapter (`pendle_adapter`)

- **Type**: `PENDLE`
- **Module**: `wayfinder_paths.adapters.pendle_adapter.adapter.PendleAdapter`
- **Protocol**: Pendle
- **Capabilities**: `pendle.markets.read`, `pendle.market.snapshot`, `pendle.market.history`, `pendle.prices.ohlcv`, `pendle.prices.assets`, `pendle.swap.quote`, `pendle.swap.best_pt`, `pendle.swap.execute`, `pendle.convert.quote`, `pendle.convert.best_pt`, `pendle.convert.execute`, `pendle.positions.database`, `pendle.limit_orders.taker.read`, `pendle.limit_orders.maker.read`, `pendle.limit_orders.maker.write`, `pendle.deployments.read`, `pendle.router_static.rates`

Comprehensive Pendle integration for PT/YT market discovery, historical metrics, execution planning, swap quotes, and limit orders via the Pendle Hosted SDK.

See [pendle.md](pendle.md) for details.

### Uniswap Adapter (`uniswap_adapter`)

- **Type**: `UNISWAP`
- **Module**: `wayfinder_paths.adapters.uniswap_adapter.adapter.UniswapAdapter`
- **Protocol**: Uniswap V3 (concentrated liquidity)
- **Capabilities**: `uniswap.liquidity.add`, `uniswap.liquidity.increase`, `uniswap.liquidity.remove`, `uniswap.fees.collect`, `uniswap.position.get`, `uniswap.positions.list`, `uniswap.fees.uncollected`, `uniswap.pool.get`

Provides Uniswap V3 LP position reads and liquidity/fee management.

See [uniswap.md](uniswap.md) for details.

### ProjectX Adapter (`projectx_adapter`)

- **Type**: `PROJECTX`
- **Module**: `wayfinder_paths.adapters.projectx_adapter.adapter.ProjectXLiquidityAdapter`
- **Protocol**: ProjectX (Uniswap V3 fork on HyperEVM)
- **Capabilities**: `projectx.pool.overview`, `projectx.positions.list`, `projectx.liquidity.mint`, `projectx.liquidity.increase`, `projectx.liquidity.decrease`, `projectx.fees.collect`, `projectx.position.burn`, `projectx.swap.exact_in`

Provides concentrated liquidity reads and execution on ProjectX, plus exact-in swaps.

See [projectx.md](projectx.md) for details.

### Pool Adapter (`pool_adapter`)

- **Type**: `POOL`
- **Module**: `wayfinder_paths.adapters.pool_adapter.adapter.PoolAdapter`
- **Protocol**: DeFi Llama pool data
- **Capabilities**: `pool.read`, `pool.discover`

Provides pool information, yield analytics via DeFi Llama integration, and pool discovery with filtering.

```bash
poetry run wayfinder resource wayfinder://adapters/pool_adapter
```

### Token Adapter (`token_adapter`)

- **Type**: `TOKEN`
- **Module**: `wayfinder_paths.adapters.token_adapter.adapter.TokenAdapter`
- **Protocol**: Token metadata service
- **Capabilities**: `token.read`, `token.price`, `token.gas`

Provides token metadata (address, decimals, symbol), live price data, and gas token lookups by chain.

```bash
poetry run wayfinder resource wayfinder://tokens/resolve/usd-coin-base
poetry run wayfinder resource wayfinder://tokens/search/base/usdc
poetry run wayfinder resource wayfinder://tokens/gas/base
```

---

## Presenting Adapter Data to Users

Adapters return raw JSON results. When presenting this data to users, follow these patterns to make the information clear and actionable.

### Balance Presentation

When showing `resource wayfinder://balances/{label}` results:

- **Group by chain** — show Base tokens, Arbitrum tokens, etc. as separate sections
- **Lead with USD value** — users care about dollar amounts first, then token quantities
- **Hide dust** — tokens worth less than $0.01 are noise; mention their count but don't list them
- **Show totals** — always include a total portfolio value across all chains

Example format:
```
Base ($2,450.32)
  1,200.00 USDC     $1,200.00
  0.5123   ETH      $1,230.32
  150.00   USDbC    $20.00

Arbitrum ($500.00)
  500.00   USDC     $500.00

Total: $2,950.32 across 2 chains (3 dust tokens hidden)
```

### Token Resolution Presentation

When showing `resource wayfinder://tokens/search/{chain}/{query}` results:

- **Show top 3-5 matches** with their full token ID, chain, and contract address
- **Highlight the best match** if the score is significantly higher than others
- **Always show the canonical ID** that the user should use in subsequent commands

### Swap Quote Presentation

When showing `quote_swap` results:

- **Show the exchange rate** — e.g., "1 ETH = 2,460.50 USDC"
- **Show price impact** — if available in the quote response
- **Show fees** — gas cost estimate, protocol fees, bridge fees (if cross-chain)
- **Show the net amount received** — this is what the user ultimately cares about
- **Compare to mid price** — if you have `mid_prices` data, show how the quote compares

### Strategy Status Presentation

When showing `run_strategy --action status` results:

- **Show current positions** — what's deployed and where
- **Show P&L** — unrealized gains/losses if available
- **Show APY** — current yield rate
- **Show health** — any warnings (low health factor, approaching liquidation, etc.)

### Hyperliquid State Presentation

When showing `resource wayfinder://hyperliquid/{label}/state` results:

- **Separate perp positions from account summary** — show margin, equity, and unrealized PnL at the top, then list positions
- **Per-position details** — coin, side, size, entry price, mark price, unrealized PnL, leverage
- **Funding rate context** — if showing positions, include current funding rate so the user knows their carry cost/income

### Error Presentation

See the Error Handling section in the main SKILL.md for how to translate error codes into user-friendly messages with actionable recovery steps.

### General Principles

1. **Numbers need context** — raw wei amounts or 18-decimal values are useless. Always convert to human-readable amounts.
2. **Currency formatting** — use commas for thousands, 2 decimal places for USD, appropriate decimals for crypto (4 for ETH, 2 for stablecoins, 6+ for micro-cap).
3. **Timestamps** — convert Unix timestamps to relative time ("2 hours ago") or readable dates.
4. **Addresses** — truncate to `0x1234...abcd` unless the user needs the full address.
5. **Status indicators** — use clear labels: "Active", "Pending", "Failed" rather than numeric status codes.
6. **Chain labels** — always include the chain name next to token amounts when showing multi-chain data.
