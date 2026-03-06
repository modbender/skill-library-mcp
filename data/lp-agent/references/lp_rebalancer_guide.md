# LP Rebalancer Controller Guide

A concentrated liquidity (CLMM) position manager that automatically rebalances positions based on price movement and configurable price limits.

## Overview

LP Rebalancer maintains a single LP position and automatically rebalances it when price moves out of range. It uses a "grid-like" approach with separate BUY and SELL zones, anchoring positions at price limits to maximize fee collection.

### Key Features

- **Automatic rebalancing** when price exits position range
- **Configurable BUY and SELL price zones** (can overlap)
- **"KEEP" logic** to avoid unnecessary rebalancing when already at optimal position
- **Supports initial BOTH, BUY, or SELL sided positions**
- **Retry logic** for transaction failures due to chain congestion

### Use Cases

- **Range-bound trading**: Collect fees while price oscillates within a range
- **Directional LP**: Position for expected price movements (BUY for dips, SELL for pumps)
- **Grid-like strategies**: Automatically reposition at price limits

## Architecture

### Controller-Executor Pattern

```
┌─────────────────────────────────────────────────────────────────┐
│                        Strategy Layer                            │
│  (v2_with_controllers.py - orchestrates multiple controllers)   │
└─────────────────────────────────────────────────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
        ┌─────────────────────┐  ┌─────────────────────┐
        │   LPRebalancer      │  │   Other Controller  │
        │   (Controller)      │  │                     │
        │                     │  │                     │
        │ - Decides WHEN to   │  │                     │
        │   create/stop       │  │                     │
        │   positions         │  │                     │
        │ - Calculates bounds │  │                     │
        │ - KEEP vs REBALANCE │  │                     │
        └─────────┬───────────┘  └─────────────────────┘
                  │
                  │ CreateExecutorAction / StopExecutorAction
                  ▼
        ┌─────────────────────┐
        │     LPExecutor      │
        │     (Executor)      │
        │                     │
        │ - Manages single    │
        │   position lifecycle│
        │ - Opens/closes via  │
        │   gateway           │
        │ - Tracks state      │
        └─────────┬───────────┘
                  │
                  ▼
        ┌─────────────────────┐
        │   Gateway (LP)      │
        │                     │
        │ - Connector to DEX  │
        │ - Meteora, Raydium  │
        │ - Solana chain ops  │
        └─────────────────────┘
```

### Key Components

| Component | Responsibility |
|-----------|---------------|
| **Controller** (`LPRebalancer`) | Strategy logic - when to create/stop positions, price bounds calculation, KEEP vs REBALANCE decisions |
| **Executor** (`LPExecutor`) | Position lifecycle - opens position, monitors state, closes position on stop |
| **Gateway** (`gateway_lp.py`) | DEX interaction - sends transactions, tracks confirmations |
| **Connector** (`meteora/clmm`) | Protocol-specific implementation |

## Configuration

### Full Configuration Reference

```yaml
# Identity
id: lp_rebalancer_1                    # Unique identifier
controller_name: lp_rebalancer         # Must match controller class
controller_type: generic               # Controller category

# Position sizing
total_amount_quote: '50'               # Total value in quote currency
side: 0                                # Initial side: 0=BOTH, 1=BUY, 2=SELL
position_width_pct: '0.5'              # Position width as percentage (0.5 = 0.5%)
position_offset_pct: '0.1'             # Offset to ensure single-sided positions start out-of-range

# Connection
connector_name: meteora/clmm           # LP connector
network: solana-mainnet-beta           # Network
trading_pair: SOL-USDC                 # Trading pair
pool_address: 'HTvjz...'               # Pool address on DEX

# Price limits (like overlapping grids)
sell_price_max: 88                     # Ceiling - don't sell above
sell_price_min: 86                     # Floor - anchor SELL positions here
buy_price_max: 87                      # Ceiling - anchor BUY positions here
buy_price_min: 85                      # Floor - don't buy below

# Timing
rebalance_seconds: 60                  # Seconds out-of-range before rebalancing
rebalance_threshold_pct: '0.1'         # Price must be this % beyond bounds before timer starts

# Optional
strategy_type: 0                       # Connector-specific (Meteora strategy type)
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `id` | string | auto | Unique controller identifier |
| `total_amount_quote` | decimal | 50 | Total position value in quote currency |
| `side` | int | 1 | Initial side: 0=BOTH, 1=BUY, 2=SELL |
| `position_width_pct` | decimal | 0.5 | Position width as percentage |
| `position_offset_pct` | decimal | 0.01 | Offset from current price to ensure single-sided positions start out-of-range |
| `sell_price_max` | decimal | null | Upper limit for SELL zone |
| `sell_price_min` | decimal | null | Lower limit for SELL zone (anchor point) |
| `buy_price_max` | decimal | null | Upper limit for BUY zone (anchor point) |
| `buy_price_min` | decimal | null | Lower limit for BUY zone |
| `rebalance_seconds` | int | 60 | Seconds out-of-range before rebalancing |
| `rebalance_threshold_pct` | decimal | 0.1 | Price must be this % beyond position bounds before rebalance timer starts |

### Price Limits Visualization

```
Price:    84        85        86        87        88        89
          |---------|---------|---------|---------|---------|
                    ^         ^         ^         ^
               buy_min   sell_min   buy_max   sell_max
                    |         |         |         |
                    +---------+---------+         |
                       BUY ZONE [85-87]           |
                              +---------+---------+
                                SELL ZONE [86-88]
                              +---------+
                              OVERLAP [86-87]
```

## How It Works

### Side and Amount Calculation

Based on `side` and `total_amount_quote`:

| Side | Name | base_amount | quote_amount | Description |
|------|------|-------------|--------------|-------------|
| 0 | BOTH | `(total/2) / price` | `total/2` | Double-sided, 50/50 split |
| 1 | BUY | `0` | `total` | Quote-only, positioned below price |
| 2 | SELL | `total / price` | `0` | Base-only, positioned above price |

### Bounds Calculation

**Side=0 (BOTH)** - Initial only, centered on current price:
```
half_width = position_width_pct / 2
lower = current_price * (1 - half_width)
upper = current_price * (1 + half_width)
```

**Side=1 (BUY)** - Anchored at buy_price_max:
```
upper = min(current_price, buy_price_max)
lower = upper * (1 - position_width_pct)
```

**Side=2 (SELL)** - Anchored at sell_price_min:
```
lower = max(current_price, sell_price_min)
upper = lower * (1 + position_width_pct)
```

### Rebalancing Decision Flow

```
                    +---------------------------------------+
                    |    INITIAL (total_amount_quote=50)    |
                    |    side from config: 0, 1, or 2       |
                    +-------------------+-------------------+
                                        |
                                        v
              +-----------------------------------------------------+
              |                    ACTIVE POSITION                   |
              |    Stores [lower_price, upper_price] in custom_info  |
              +-------------------------+---------------------------+
                                        |
                        +---------------+---------------+
                        |                               |
         current < lower_price              current > upper_price
              (side=2 SELL)                     (side=1 BUY)
                        |                               |
                        v                               v
         +-------------------------+     +-------------------------+
         | lower == sell_price_min?|     | upper == buy_price_max? |
         +------+----------+-------+     +------+----------+-------+
                |          |                    |          |
           YES  |          | NO            YES  |          | NO
                v          v                    v          v
         +----------+ +------------+    +----------+ +------------+
         |   KEEP   | | REBALANCE  |    |   KEEP   | | REBALANCE  |
         | POSITION | | SELL at    |    | POSITION | | BUY at     |
         |          | | sell_min   |    |          | | buy_max    |
         +----------+ +------------+    +----------+ +------------+
```

### Rebalance vs Keep Summary

| Price Exit | At Limit? | Action |
|------------|-----------|--------|
| Above (BUY) | upper < buy_price_max | REBALANCE to buy_max |
| Above (BUY) | upper == buy_price_max | **KEEP** |
| Below (SELL) | lower > sell_price_min | REBALANCE to sell_min |
| Below (SELL) | lower == sell_price_min | **KEEP** |

## Scenarios

### Initial Positions

#### side=0 (BOTH) at price=86.5

```
Amounts: base=0.289 SOL, quote=25 USDC
Bounds:  lower=86.28, upper=86.72

Position:                     [===*===]
                            86.28    86.72
                                  ^
                              price=86.5 (IN_RANGE, centered)
```

#### side=1 (BUY) at price=86.5

```
Amounts: base=0, quote=50 USDC
Bounds:  upper=86.5, lower=86.07

Position:                 [========*]
                        86.07    86.50
                                  ^
                              price=86.5 (IN_RANGE at upper edge)
```

#### side=2 (SELL) at price=86.5

```
Amounts: base=0.578 SOL, quote=0 USDC
Bounds:  lower=86.5, upper=86.93

Position:                 [*========]
                        86.50    86.93
                          ^
                      price=86.5 (IN_RANGE at lower edge)
```

### Scenario A: Price Moves UP (starting from BUY)

**A1: Price 86.5 -> 87.5 (OUT_OF_RANGE above)**

```
Position:                 [========]            *
                        86.07    86.50      price=87.5
```

Decision: upper (86.50) < buy_price_max (87) -> **REBALANCE** to BUY anchored at buy_price_max

**A2: Price 87.5 -> 88.5 (still OUT_OF_RANGE above)**

```
Position:                     [========]                *
                            86.57    87.00          price=88.5
```

Decision: upper (87.00) == buy_price_max (87) -> **KEEP POSITION** - already anchored optimally

**A3: Price 88.5 -> 86.8 (back IN_RANGE)**

```
Position:                     [===*====]
                            86.57    87.00
                                ^
                            price=86.8 (IN_RANGE)
```

Price dropped back into range. Buying base. **This is why we KEEP** - positioned to catch the dip.

### Scenario B: Price Moves DOWN

**B1: Price 86.5 -> 85.5 (OUT_OF_RANGE below)**

```
Position:        *        [========]
             price=85.5 86.07    86.50
```

Decision: lower (86.07) > sell_price_min (86) -> **REBALANCE** to SELL anchored at sell_price_min

**B2: Price 85.5 -> 84.0 (still OUT_OF_RANGE below)**

```
Position:         *                   [========]
              price=84.0            86.00    86.43
```

Decision: lower (86.00) == sell_price_min (86) -> **KEEP POSITION** - already anchored optimally

**B3: Price 84.0 -> 86.2 (back IN_RANGE)**

```
Position:                 [*=======]
                        86.00    86.43
                          ^
                      price=86.2 (IN_RANGE)
```

Price rose back into range. Selling base. **This is why we KEEP** - positioned to catch the pump.

### All Scenarios Summary

| Starting Position | Price Movement | Result |
|-------------------|----------------|--------|
| BUY at current | up, not at limit | REBALANCE to buy_max |
| BUY at buy_max | up | KEEP |
| BUY at current | down | REBALANCE to SELL at sell_min |
| SELL at current | down, not at limit | REBALANCE to sell_min |
| SELL at sell_min | down | KEEP |
| SELL at current | up | REBALANCE to BUY at buy_max |
| BOTH at current | up | REBALANCE to BUY at buy_max |
| BOTH at current | down | REBALANCE to SELL at sell_min |
| Any | oscillate in range | No action, accumulate fees |

## Edge Cases

### Optional Price Limits (None)

If limits are not set, behavior changes:

| Limit | If None | Effect |
|-------|---------|--------|
| buy_price_max | No ceiling | BUY always uses current_price as upper |
| buy_price_min | No floor | Lower bound not clamped |
| sell_price_min | No floor | SELL always uses current_price as lower |
| sell_price_max | No ceiling | Upper bound not clamped |

**No limits = always follow price** (no anchoring, always rebalance).

### Gap Zone (sell_price_min > buy_price_max)

If there's no overlap between zones (e.g., buy_max=86, sell_min=88), positions in the gap [86, 88] work correctly:

- **BUY at price=87**: position [85.57, 86.00] below price, waiting for dips
- **SELL at price=87**: position [88.00, 88.44] above price, waiting for pumps

This is valid - positions don't need to contain current price.

## Retry Behavior and Error Handling

When a transaction fails (e.g., due to chain congestion), the executor automatically retries up to 10 times.

**When max_retries is reached:**
1. Executor stays in current state (`OPENING` or `CLOSING`) - does NOT shut down
2. Sets `max_retries_reached = True` in custom_info
3. Sends notification to user via hummingbot app
4. Stops retrying until user intervenes

**User intervention required:**
- For `OPENING` failures: Position was not created - user can stop the controller
- For `CLOSING` failures: Position exists on-chain - user may need to close manually via DEX UI

## Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| "Invalid bounds" | Calculated lower >= upper | Check price limits configuration |
| Position not created | Price outside valid range for side | Adjust price limits or wait for price |
| Repeated rebalancing | Price oscillating at limit | Increase `rebalance_seconds` |
| Transaction timeout | Chain congestion | Retry logic handles this automatically |
| "LP OPEN/CLOSE FAILED" notification | Max retries reached | Manual intervention required |

### Max Retries Reached - Intervention Required

**For OPENING failures:**
1. Position was NOT created on-chain
2. Stop the controller via hummingbot
3. Check chain status / RPC health
4. Restart when ready

**For CLOSING failures:**
1. Position EXISTS on-chain but couldn't be closed
2. Check the position address on Solscan/Explorer
3. Close manually via DEX UI (e.g., Meteora app)
4. Stop the controller after manual close

## Source

Full documentation: https://github.com/hummingbot/hummingbot/blob/development/controllers/generic/lp_rebalancer/README.md
