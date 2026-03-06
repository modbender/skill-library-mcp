# PMM Mister Controller

An advanced Pure Market Making controller with sophisticated position management, designed for both spot and perpetual futures markets.

## Overview

PMM Mister extends basic market making with features critical for serious trading: hanging executors, position tracking, breakeven awareness, cooldowns, and dynamic risk management.

**Best for:**
- Spot and perpetual futures market making
- Strategies requiring position-aware decisions
- Advanced users who need fine-grained control over order timing and risk

## Key Features

| Feature | Description |
|---------|-------------|
| **Hanging Executors** | Filled orders become "hanging" positions that can be effectivized or closed |
| **Position Tracking** | Tracks aggregate position, breakeven price, and unrealized PnL |
| **Cooldown System** | Separate buy/sell cooldowns after fills to prevent over-trading |
| **Price Distance Control** | Prevents placing orders too close to existing positions |
| **Profit Protection** | Option to never sell below breakeven price |
| **Level-Specific Tolerances** | Tolerances scale with level for tiered order management |

## Strategy Logic

1. **Order Placement:** Places orders at spread levels, adjusted by position skew
2. **Fill Handling:** Filled orders become hanging executors awaiting effectivization
3. **Cooldown:** After a fill, that side enters cooldown before new orders
4. **Effectivization:** After effectivization time, hanging positions are "realized"
5. **Position Management:** Skews order sizes to rebalance toward target position
6. **Profit Protection:** Optionally prevents selling below breakeven

## Configuration Parameters

### Core Settings

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `connector_name` | string | `binance` | Exchange connector |
| `trading_pair` | string | `BTC-FDUSD` | Trading pair |
| `portfolio_allocation` | decimal | `0.1` | Fraction of total_amount_quote to use (0.1 = 10%) |
| `leverage` | int | `20` | Leverage for perpetual contracts |
| `position_mode` | enum | `ONEWAY` | ONEWAY or HEDGE position mode |

### Position Management

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `target_base_pct` | decimal | `0.5` | Target position as % of allocation |
| `min_base_pct` | decimal | `0.3` | Minimum position % (stops selling below this) |
| `max_base_pct` | decimal | `0.7` | Maximum position % (stops buying above this) |
| `min_skew` | decimal | `1.0` | Minimum skew multiplier (prevents tiny orders) |

### Spread & Amount Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `buy_spreads` | list | `0.0005` | Comma-separated buy spreads (0.0005 = 0.05%) |
| `sell_spreads` | list | `0.0005` | Comma-separated sell spreads |
| `buy_amounts_pct` | list | `1` | Amount weights per buy level |
| `sell_amounts_pct` | list | `1` | Amount weights per sell level |

**Amount weights:** If you have 3 levels with amounts `1,2,1`, the middle level gets 50% of the allocation.

### Timing Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `executor_refresh_time` | int | `30` | Seconds before refreshing unfilled orders |
| `buy_cooldown_time` | int | `60` | Seconds to wait after a buy fill |
| `sell_cooldown_time` | int | `60` | Seconds to wait after a sell fill |
| `buy_position_effectivization_time` | int | `120` | Seconds before buy position is effectivized |
| `sell_position_effectivization_time` | int | `120` | Seconds before sell position is effectivized |

### Tolerance Configuration

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `price_distance_tolerance` | decimal | `0.0005` | Min distance from existing orders (0.05%) |
| `refresh_tolerance` | decimal | `0.0005` | Price deviation to trigger order refresh |
| `tolerance_scaling` | decimal | `1.2` | Multiplier for level-specific tolerances |

**Level scaling:** Level 0 uses base tolerance, Level 1 uses `tolerance * 1.2`, Level 2 uses `tolerance * 1.2^2`, etc.

### Risk Management

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `take_profit` | decimal | `0.0001` | Take profit % per position (0.01%) |
| `global_take_profit` | decimal | `0.03` | Overall take profit % (3%) |
| `global_stop_loss` | decimal | `0.05` | Overall stop loss % (5%) |
| `position_profit_protection` | bool | `false` | Never sell below breakeven |
| `max_active_executors_by_level` | int | `4` | Max hanging executors per level |

### Order Types

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `open_order_type` | enum | `LIMIT_MAKER` | Order type for entry |
| `take_profit_order_type` | enum | `LIMIT_MAKER` | Order type for TP |
| `tick_mode` | bool | `false` | Use tick-based spread calculation |

## Example Configurations

### Conservative Perpetual MM

```yaml
id: btc_perp_conservative
controller_name: pmm_mister
connector_name: binance_perpetual
trading_pair: BTC-USDT
portfolio_allocation: 0.05
leverage: 10
buy_spreads: "0.001,0.002"
sell_spreads: "0.001,0.002"
buy_cooldown_time: 120
sell_cooldown_time: 120
position_profit_protection: true
global_stop_loss: 0.03
```

### Aggressive Scalping

```yaml
id: eth_perp_scalp
controller_name: pmm_mister
connector_name: binance_perpetual
trading_pair: ETH-USDT
portfolio_allocation: 0.2
leverage: 20
buy_spreads: "0.0003,0.0005,0.0008"
sell_spreads: "0.0003,0.0005,0.0008"
buy_amounts_pct: "1,2,3"
sell_amounts_pct: "1,2,3"
executor_refresh_time: 15
buy_cooldown_time: 30
sell_cooldown_time: 30
take_profit: 0.0002
price_distance_tolerance: 0.0002
```

### Position-Balanced Strategy

```yaml
id: sol_perp_balanced
controller_name: pmm_mister
connector_name: binance_perpetual
trading_pair: SOL-USDT
portfolio_allocation: 0.1
leverage: 15
target_base_pct: 0.5
min_base_pct: 0.2
max_base_pct: 0.8
buy_spreads: "0.0005,0.001"
sell_spreads: "0.0005,0.001"
min_skew: 0.5
position_profit_protection: true
```

## Status Display

PMM Mister provides a comprehensive real-time dashboard:

```
╒══════════════════════════════════════════════════════════════════════════════╕
│ binance_perpetual:BTC-USDT @ 95000.00  Alloc: 10.0%  Pos Protect: ON         │
├──────────────────────────────────────────────────────────────────────────────┤
│ REAL-TIME CONDITIONS DASHBOARD                                                │
├────────────────┬──────────────────┬────────────────┬────────────┬────────────┤
│ COOLDOWNS      │ PRICE DISTANCES  │ EFFECTIVIZATION│ REFRESH    │ EXECUTION  │
├────────────────┼──────────────────┼────────────────┼────────────┼────────────┤
│ BUY: READY     │ L0 Dist: 0.05%   │ Hanging: 2     │ Near: 1    │ BUY: 2/2   │
│ SELL: 45.2s    │ BUY: (0.12%)     │ Ready: 1       │ Ready: 0   │ SELL: 1/2  │
├──────────────────────────────────────────────────────────────────────────────┤
│ LEVEL-BY-LEVEL ANALYSIS                                                       │
│ BUY LEVELS:                                                                   │
│   buy_0: Active:1 Hanging:0                                                  │
│   buy_1: Active:0 Hanging:1 | Blocked: cooldown_active                       │
│ SELL LEVELS:                                                                  │
│   sell_0: Active:1 Hanging:1                                                 │
│   sell_1: Active:0 Hanging:0 | Blocked: price_distance_violation             │
├──────────────────────────────────────────────────────────────────────────────┤
│ POSITION STATUS              │ PROFIT & LOSS                                 │
│ Current: 55.00% (Target: 50%)│ Unrealized: +0.15%                            │
│ Range: 30.00% - 70.00%       │ Take Profit: 3.00% (2.85% to go)             │
│ Buy Skew: 0.75 | Sell: 1.25  │ Breakeven: 94850.00                           │
╘══════════════════════════════════════════════════════════════════════════════╛
```

## Blocking Conditions

Orders for a level are blocked when:

| Condition | Description |
|-----------|-------------|
| `max_active_executors_reached` | Level has max hanging executors |
| `cooldown_active` | Recent fill, waiting for cooldown |
| `price_distance_violation` | Existing order too close to current price |
| `below_min_position` | Position below min, only buy orders |
| `above_max_position` | Position above max, only sell orders |
| `position_profit_protection` | Price below breakeven, sells blocked |

## PMM V1 vs PMM Mister

| Feature | PMM V1 | PMM Mister |
|---------|--------|------------|
| Target market | Spot | Perpetuals/Margin |
| Order executor | OrderExecutor | PositionExecutor |
| Position tracking | Inventory only | Full position with breakeven |
| Leverage support | No | Yes |
| Hanging executors | No | Yes |
| Cooldowns | filled_order_delay only | Separate buy/sell cooldowns |
| Profit protection | No | Yes |
| Take profit | No | Per-position TP |
| Status display | Simple | Comprehensive dashboard |

## When to Use

**Use PMM Mister when:**
- Trading perpetual futures with leverage
- You need position-aware decision making
- You want protection against selling at a loss
- You need fine-grained control over order timing
- You want to see real-time condition analysis

**Consider PMM V1 instead when:**
- Trading spot markets
- You want simpler, legacy-compatible behavior
- You don't need position tracking
- Lower complexity is preferred
