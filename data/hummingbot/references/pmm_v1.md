# PMM V1 Controller

A faithful clone of the legacy Hummingbot Pure Market Making (PMM) V1 strategy, implemented as a V2 controller.

## Overview

PMM V1 places limit orders on both sides of the order book at configurable spreads from the mid price. It's the classic market making strategy that Hummingbot is known for, now available as a V2 controller.

**Best for:**
- Simple market making on CEX spot markets
- Users familiar with legacy Hummingbot PMM
- Strategies that don't require position tracking or leverage

## Strategy Logic

1. **Order Placement:** Places buy orders below mid price and sell orders above mid price at configured spread levels
2. **Inventory Management:** Adjusts order sizes based on current inventory vs target to maintain balance
3. **Order Refresh:** Periodically cancels and replaces orders to stay competitive
4. **Price Bands:** Optionally stops buying above ceiling or selling below floor

## Configuration Parameters

### Core Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `connector_name` | string | `binance` | Exchange connector (e.g., binance, kucoin) |
| `trading_pair` | string | `BTC-USDT` | Trading pair in BASE-QUOTE format |
| `order_amount` | decimal | `1` | Order size in **base asset** (e.g., 0.01 BTC) |

### Spread Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `buy_spreads` | list | `0.01` | Comma-separated buy spreads as decimals (0.01 = 1%) |
| `sell_spreads` | list | `0.01` | Comma-separated sell spreads as decimals |

**Multi-level example:** `buy_spreads: 0.005,0.01,0.015` creates 3 buy orders at 0.5%, 1%, and 1.5% below mid price.

### Timing Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `order_refresh_time` | int | `30` | Seconds between order refresh cycles |
| `order_refresh_tolerance_pct` | decimal | `-1` | Price change % to trigger early refresh (-1 = disabled) |
| `filled_order_delay` | int | `60` | Seconds to wait after a fill before replacing that level |

### Inventory Skew

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `inventory_skew_enabled` | bool | `false` | Enable inventory-based order size adjustment |
| `target_base_pct` | decimal | `0.5` | Target base asset percentage (0.5 = 50/50 split) |
| `inventory_range_multiplier` | decimal | `1.0` | Controls how aggressively skew is applied |

**How skew works:**
- If you hold more base than target: buy orders shrink, sell orders grow
- If you hold less base than target: buy orders grow, sell orders shrink
- Skew multipliers range from 0 (skip order) to 2 (double size)

### Price Bands

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `price_ceiling` | decimal | `-1` | Stop buying if price >= ceiling (-1 = disabled) |
| `price_floor` | decimal | `-1` | Stop selling if price <= floor (-1 = disabled) |

## Example Configurations

### Basic Market Making

```yaml
id: btc_usdt_basic
controller_name: pmm_v1
connector_name: binance
trading_pair: BTC-USDT
order_amount: 0.001
buy_spreads: "0.002"
sell_spreads: "0.002"
order_refresh_time: 30
```

### Multi-Level with Inventory Skew

```yaml
id: eth_usdt_multi
controller_name: pmm_v1
connector_name: binance
trading_pair: ETH-USDT
order_amount: 0.1
buy_spreads: "0.001,0.002,0.003"
sell_spreads: "0.001,0.002,0.003"
order_refresh_time: 15
inventory_skew_enabled: true
target_base_pct: 0.5
inventory_range_multiplier: 1.5
```

### With Price Bands

```yaml
id: sol_usdt_bands
controller_name: pmm_v1
connector_name: binance
trading_pair: SOL-USDT
order_amount: 1
buy_spreads: "0.005"
sell_spreads: "0.005"
price_ceiling: 200
price_floor: 100
```

## Status Display

The controller shows:
- Current inventory percentage vs target
- Buy/sell skew multipliers
- Reference price and active order counts
- Price band status
- Visual inventory bar

```
=========================================================================
|                    PMM V1 | binance:BTC-USDT                          |
=========================================================================
| INVENTORY                           | SETTINGS                        |
-------------------------------------------------------------------------
| Base %: 45.00% (target 50.00%)      | Order Amount: 0.001 base        |
| Buy Skew: 1.20x | Sell Skew: 0.80x  | Spreads B: [0.002] S: [0.002]   |
-------------------------------------------------------------------------
| Inventory: [######X..........:..........] |
=========================================================================
```

## Differences from Legacy PMM

| Feature | Legacy PMM | PMM V1 Controller |
|---------|-----------|-------------------|
| Order type | Direct order submission | Uses OrderExecutor |
| State management | Strategy class | Controller + processed_data |
| Multi-pair | Single pair | Single pair (use multiple controllers) |
| Hanging orders | Separate feature | Use pmm_mister instead |

## When to Use

**Use PMM V1 when:**
- You want simple, proven market making logic
- Trading spot markets without leverage
- You don't need position tracking or take-profit/stop-loss
- Migrating from legacy Hummingbot PMM

**Consider pmm_mister instead when:**
- Trading perpetuals with leverage
- You need position profit protection
- You want hanging executors and cooldowns
- You need more sophisticated risk management
