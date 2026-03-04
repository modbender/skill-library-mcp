# Strategy Selection Guide

## Perp Market Maker
**Best for**: Earning the bid-ask spread on liquid perpetual futures.

**How it works**: Places buy orders below the current price and sell orders above it. When both sides fill, you profit from the spread. Uses inventory skew to stay market-neutral.

**Recommended markets**: High-volume perps like ETH, BTC, HYPE, SOL, ICP.

**Typical settings for beginners**:
- `base_order_size`: 15-25 USD
- `base_spread_bps`: 15-30
- `max_position_usd`: 50-100
- `leverage`: 3x
- `max_quote_count`: 2

**Risk**: Inventory accumulation during trends. Mitigated by skew settings.

---

## Spot Market Maker
**Best for**: HIP-1 spot tokens that have a perp oracle for pricing.

**How it works**: Uses the perpetual futures price as an oracle to determine fair value for the spot token. Places bid/ask quotes around this oracle price.

**Recommended markets**: XMR1/USDC, PURR/USDC, or any HIP-1 token with an active perp.

**Typical settings for beginners**:
- `base_order_size`: 0.1-0.5 units
- `base_spread_bps`: 30-50 (spot is less liquid, need wider spreads)
- `max_position_size`: 1-5 units

**Risk**: Spot-perp divergence. The `max_spot_perp_deviation_pct` safety parameter protects against this.

---

## Grid Trader
**Best for**: Range-bound assets, airdrop farming, or when you have a directional view.

**How it works**: Places orders at fixed price levels (grid lines) above and below the current price. When price crosses a level, the filled order creates a profit opportunity. Supports long, short, or neutral bias.

**Recommended markets**: Assets you expect to oscillate in a range. HIP-3 builder markets for farming.

**Bias settings**:
- `"neutral"`: Equal buys and sells. Pure oscillation profit.
- `"long"`: More buy levels than sell. Accumulates on dips, sells on rallies. Good if bullish.
- `"short"`: More sell levels than buy. Reduces on rallies. Good if bearish.

**Typical settings for beginners**:
- `spacing_pct`: 0.5-1.0%
- `num_levels_each_side`: 4-6
- `order_size_usd`: 15-25
- `max_position_usd`: 100-200

**Risk**: Price moving out of grid range. Unrealized losses if price trends away from grid.
