---
name: funding-rate-scanner
version: 1.0.1
description: Scan crypto funding rates and find arbitrage opportunities. No API key needed.
---

# Funding Rate Scanner

Scan all crypto perpetual futures funding rates and find high-yield arbitrage opportunities.

## Features

- Scan 500+ coins on Binance Futures
- Find extreme negative funding rates (earn by going long)
- Calculate annualized returns at different leverage levels
- Track rate changes over time

## Usage

```bash
# Scan top opportunities
node scripts/scan.js

# Monitor specific coins
node scripts/monitor.js DUSK DASH AXS

# Get detailed analysis
node scripts/analyze.js DUSK
```

## Output Example

```
=== Funding Rate Opportunities ===

Rank  Coin    Rate      Annual(5x)  Volume
1     DUSK    -0.38%    2071%       $30M
2     AXS     -0.12%    655%        $46M
3     DASH    -0.12%    649%        $50M

Next settlement: 03:00 UTC (2h away)
```

## Strategy

Negative funding rate = shorts pay longs every 8 hours.

1. Open long position on high negative rate coin
2. Collect funding every 8 hours (3x daily)
3. Set stop-loss to limit downside
4. Profit from both rate + potential price appreciation

## Risk Warning

- High leverage = high risk
- Rates can change
- Always use stop-loss
- Only risk what you can afford to lose
