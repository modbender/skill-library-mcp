# Hyperliquid

## Overview

Hyperliquid is a decentralized perpetuals exchange with spot trading. The Hyperliquid adapter provides comprehensive trading capabilities.

- **Type**: `HYPERLIQUID`
- **Module**: `wayfinder_paths.adapters.hyperliquid_adapter.adapter.HyperliquidAdapter`
- **Capabilities**: `market.read`, `market.meta`, `market.funding`, `market.candles`, `market.orderbook`, `order.execute`, `order.cancel`, `position.manage`, `transfer`, `withdraw`

## Market Data (via Resources)

```bash
# For any of the commands make sure you are in the SDK dir
cd "${WAYFINDER_SDK_PATH:-$HOME/wayfinder-paths-sdk}"

# Perp positions + PnL
poetry run wayfinder resource wayfinder://hyperliquid/main/state

# Spot balances on Hyperliquid
poetry run wayfinder resource wayfinder://hyperliquid/main/spot

# All mid prices
poetry run wayfinder resource wayfinder://hyperliquid/prices

# Single coin price
poetry run wayfinder resource wayfinder://hyperliquid/prices/ETH

# Funding rates + metadata for all assets
poetry run wayfinder resource wayfinder://hyperliquid/markets

# Spot asset metadata
poetry run wayfinder resource wayfinder://hyperliquid/spot-assets

# Order book
poetry run wayfinder resource wayfinder://hyperliquid/book/ETH
```

### High-Value Read Methods

| Method | Purpose |
|--------|---------|
| `get_meta_and_asset_ctxs()` | Perp market metadata + contexts (enumerate markets, map asset_id↔coin) |
| `get_spot_meta()` | Spot metadata (tokens + universe pairs) |
| `get_spot_assets()` | Spot asset mapping (e.g. `{"HYPE/USDC": 10107}`) |
| `get_l2_book(coin)` | Perp/spot order book by coin string |
| `get_spot_l2_book(spot_asset_id)` | Spot order book by asset ID |
| `get_user_state(address)` | Perp account state |
| `get_spot_user_state(address)` | Spot balances |
| `get_open_orders(address)` | Open orders |
| `get_frontend_open_orders(address)` | Open + trigger orders |
| `get_user_fills(address)` | Recent fills |
| `get_order_status(address, order_id)` | Single order status |

### Funding History

There is **no** `HyperliquidAdapter.get_funding_history()` method. Use one of:
- **Wayfinder API** (preferred): `HyperliquidDataClient.get_funding_history(coin, start_ms, end_ms)`
- **SDK direct**: `adapter.info.funding_history(name, startTime, endTime)` (milliseconds, not async)

### Hyperliquid deposits + withdrawals (Bridge2)

This repo uses Hyperliquid’s **Bridge2** deposit/withdraw flow and assumes **Arbitrum (chain_id = 42161)** as the EVM side.

**TL;DR:** To deposit to Hyperliquid, you send **native USDC on Arbitrum** to the Hyperliquid Bridge2 address. Do **not** send USDC from other chains or other assets.

Primary reference:
- Hyperliquid docs: https://hyperliquid.gitbook.io/hyperliquid-docs/for-developers/api/bridge2
- Funding cadence (hourly): https://hyperliquid.gitbook.io/hyperliquid-docs/trading/funding

## What you can deposit/withdraw

- **Deposit asset:** native **USDC on Arbitrum**
  - This repo’s constant: `ARBITRUM_USDC_ADDRESS = 0xaf88d065e77c8cC2239327C5EDb3A432268e5831`
- **Deposit target:** Bridge2 address on Arbitrum
  - This repo’s constant: `HYPERLIQUID_BRIDGE_ADDRESS = 0x2Df1c51E09aECF9cacB7bc98cB1742757f163dF7`

## Minimums, fees + timing (operational expectations)

From Hyperliquid's Bridge2 docs:
- **Minimum deposit is 5 USDC**; deposits below that are **lost**.
- Deposits are typically credited **in < 1 minute**.
- Withdrawals typically arrive **in several minutes** (often longer than deposits).
- **Withdrawal fee is $1 USDC** — deducted from the withdrawn amount (e.g., withdraw $6.93 → receive $5.93).

Treat these as *best-effort expectations*, not guarantees. In orchestration code, always:
- poll for confirmation
- time out safely
- avoid taking downstream risk (hedges/allocations) until funds are confirmed

## Who gets credited (common pitfall)

Baseline Bridge2 deposit behavior:
- **The Hyperliquid account credited is the sender** of the Arbitrum USDC transfer to the bridge address.

Bridge2 also supports “deposit on behalf” via a permit flow (`batchedDepositWithPermit`) per the docs, but this repo’s strategy patterns assume the simple “send USDC to bridge” path.

## How to monitor deposits/withdrawals

Adapter: `wayfinder_paths/adapters/hyperliquid_adapter/adapter.py`

### Deposit initiation

Bash shortcut:
```bash
poetry run wayfinder execute --kind hyperliquid_deposit --wallet_label main --amount 8
```

This hard-codes:
- token: native Arbitrum USDC (`usd-coin-arbitrum`)
- recipient: `HYPERLIQUID_BRIDGE_ADDRESS`
- chain: Arbitrum (42161)

### Withdrawal initiation

- Call: `HyperliquidAdapter.withdraw(amount, address)` (USDC withdraw to Arbitrum via executor)

Bash shortcut:
```bash
poetry run wayfinder hyperliquid_execute --action withdraw --wallet_label main --amount_usdc 100
```

### Deposit monitoring (recommended)

- Call: `HyperliquidAdapter.wait_for_deposit(address, expected_increase, timeout_s=..., poll_interval_s=...)`
- Mechanism: polls `get_user_state(address)` and checks perp margin increase.

Bash shortcut:
```bash
poetry run wayfinder hyperliquid --action wait_for_deposit --wallet_label main --expected_increase 100 --timeout_s 300
```

### Withdrawal monitoring (best-effort)

- Call: `HyperliquidAdapter.wait_for_withdrawal(address, max_poll_time_s=..., poll_interval_s=...)`
- Mechanism: polls Hyperliquid ledger updates for a `withdraw` record.

Bash shortcut:
```bash
poetry run wayfinder hyperliquid --action wait_for_withdrawal --wallet_label main
```

If you need strict "arrived on Arbitrum" confirmation, add an Arbitrum-side receipt check (RPC/Explorer) for the resulting tx hash.

## Orchestration tips

- **Hyperliquid funding is paid hourly**; if you're rate-locking funding with Boros, align your observations to this cadence.
- Prefer explicit "funding stages" in strategies:
  1) deposit to Hyperliquid
  2) wait for credit
  3) open/adjust hedge
  4) only then deploy spot/yield legs


## Trading

### Market Orders

```bash
# Market buy
poetry run wayfinder hyperliquid_execute --action place_order --wallet_label main \
  --coin ETH --is_buy true --usd_amount 200 --usd_amount_kind margin --leverage 5

# Market sell / short
poetry run wayfinder hyperliquid_execute --action place_order --wallet_label main \
  --coin ETH --is_buy false --usd_amount 200 --usd_amount_kind margin --leverage 5
```

### Limit Orders

```bash
# Limit buy
poetry run wayfinder hyperliquid_execute --action place_order --wallet_label main \
  --coin ETH --is_buy true --size 0.1 --price 3000 --order_type limit

# Limit sell
poetry run wayfinder hyperliquid_execute --action place_order --wallet_label main \
  --coin ETH --is_buy false --size 0.1 --price 4000 --order_type limit
```

### Close Position

```bash
# Close with reduce-only
poetry run wayfinder hyperliquid_execute --action place_order --wallet_label main \
  --coin ETH --is_buy false --size 0.5 --reduce_only
```

### Leverage

```bash
# Update leverage (cross margin)
poetry run wayfinder hyperliquid_execute --action update_leverage --wallet_label main \
  --coin ETH --leverage 5 --is_cross

# Update leverage (isolated margin)
poetry run wayfinder hyperliquid_execute --action update_leverage --wallet_label main \
  --coin ETH --leverage 5 --no-is_cross
```

### Cancel Orders

```bash
# Cancel by order ID
poetry run wayfinder hyperliquid_execute --action cancel_order --wallet_label main \
  --coin ETH --order_id 12345

# Cancel by client order ID
poetry run wayfinder hyperliquid_execute --action cancel_order --wallet_label main \
  --coin ETH --cancel_cloid my-order-1
```

## Transfers

### Internal Transfers

USDC transfers between spot and perp wallets are available via `hyperliquid_execute`:

```bash
# Move USDC from spot wallet to perp wallet
poetry run wayfinder hyperliquid_execute --action spot_to_perp_transfer --wallet_label main --amount_usdc 50

# Move USDC from perp wallet to spot wallet
poetry run wayfinder hyperliquid_execute --action perp_to_spot_transfer --wallet_label main --amount_usdc 50
```

> **Note:** Other internal transfers (HyperCore→HyperEVM, arbitrary spot transfers) require a custom script via the [coding interface](coding-interface.md).

Available adapter methods for scripting: `transfer_spot_to_perp()`, `transfer_perp_to_spot()`, `spot_transfer()`, `hypercore_to_hyperevm()`.


### Deposit USDC to Hyperliquid

```bash
# Deposit
poetry run wayfinder execute --kind hyperliquid_deposit --wallet_label main --amount 100

# Wait for deposit to arrive (polls perp margin increase)
poetry run wayfinder hyperliquid --action wait_for_deposit --wallet_label main \
  --expected_increase 100 --timeout_s 300
```

### Withdraw USDC from Hyperliquid

```bash
# Withdraw
poetry run wayfinder hyperliquid_execute --action withdraw --wallet_label main \
  --amount_usdc 100

# Wait for withdrawal to settle (polls ledger for withdraw record)
poetry run wayfinder hyperliquid --action wait_for_withdrawal --wallet_label main
```

### Orchestration Tips

- Always poll for confirmation and time out safely before taking downstream risk.
- Hyperliquid funding is paid hourly — if rate-locking with Boros, align observations to this cadence.
- Prefer explicit funding stages: deposit → wait for credit → open hedge → then deploy other legs.

## Sizing

When a user says "$X at Yx leverage", clarify intent:

| `--usd_amount_kind` | Meaning | Example ($200 at 5x) |
|---------------------|---------|----------------------|
| `margin` | $X is collateral | Notional = $1,000 |
| `notional` | $X is position size | Margin = $40 |

## Execution Architecture

- **Read methods** work with the `Info` client only — no executor needed.
- **Write methods** require a `HyperliquidExecutor` with signing configured. Without it, execution methods raise `NotImplementedError`.

### Execution Methods

| Method | Purpose |
|--------|---------|
| `place_market_order(asset_id, is_buy, slippage, size, ...)` | Market order |
| `place_limit_order(asset_id, is_buy, price, size, ...)` | Limit order |
| `place_stop_loss(asset_id, is_buy, trigger_price, size, ...)` | Stop loss |
| `cancel_order(asset_id, order_id, ...)` | Cancel by order ID |
| `cancel_order_by_cloid(asset_id, cloid, ...)` | Cancel by client order ID |
| `update_leverage(asset_id, leverage, is_cross, ...)` | Set leverage + margin mode |
| `approve_builder_fee(builder, max_fee_rate, ...)` | Approve builder fee |
| `withdraw(amount, address)` | USDC withdraw to Arbitrum |

### Builder Fee

Builder attribution uses a fixed wallet `0xaA1D89f333857eD78F8434CC4f896A9293EFE65c`. Fee value `f` is in **tenths of a basis point** (e.g. `30` = 0.030%). Set in `config.json` under `strategy.builder_fee`. The CLI auto-approves if needed.

## Spot Orders

For spot trading, you **must** set `is_spot` explicitly when using `hyperliquid_execute`:

```bash
# Spot buy
poetry run wayfinder hyperliquid_execute --action place_order --wallet_label main \
  --coin HYPE --is_spot true --is_buy true --usd_amount 20

# Perp buy (default)
poetry run wayfinder hyperliquid_execute --action place_order --wallet_label main \
  --coin HYPE --is_spot false --is_buy true --usd_amount 20 --usd_amount_kind notional
```

**Available spot pairs are limited.** Common assets like BTC and ETH are NOT directly available. Use wrapped versions:
- `UBTC/USDC` for wrapped BTC
- `UETH/USDC` for wrapped ETH
- `HYPE/USDC` is native and available

Spot orders don't use leverage — `usd_amount` is always treated as notional. `leverage` and `reduce_only` are ignored for spot.

**Spot balance location:** Spot tokens live in your spot wallet, separate from perp margin. Use scripts with `transfer_spot_to_perp()` / `transfer_perp_to_spot()` to move USDC between them.

## Gotchas

- **Minimum amounts**: Deposits require **>= $5 USDC** (below $5 is lost). All orders (perp and spot) require a minimum of **$10 USD notional**.
- **Asset IDs**: Perp assets: `asset_id < 10000`. Spot assets: `asset_id >= 10000` (spot_index = asset_id - 10000).
- **Spot naming quirks**: Spot index 0 uses `"PURR/USDC"`, otherwise `"@{spot_index}"`. Use `get_spot_assets()` for the mapping.
- **`is_spot` must be explicit**: When placing orders, `is_spot=True` for spot, `is_spot=False` for perp. Omitting returns an error.
- **Funding**: Funding is paid/received every hour. Use `resource wayfinder://hyperliquid/markets` for current funding rates.
- **Slippage**: Default slippage is applied to market orders. Override with `--slippage` (as a decimal, e.g., 0.01 = 1%).
- **No guessing**: Do not invent funding rates or prices. Always fetch via adapter and label timestamps.
- **USD sizing ambiguity**: When a user says "$X at Yx leverage", always clarify if $X is notional (position size) or margin (collateral). See the Sizing table above.
- **Builder fee approvals**: Builder fees are opt-in per user/builder pair. Fee value `f` is in **tenths of a basis point** (e.g. `30` = 0.030%). The CLI auto-approves if needed.
- **Funding history**: There is no `HyperliquidAdapter.get_funding_history()` — use `HyperliquidDataClient` or the SDK's `Info.funding_history()` directly.
