# BTC 5-Minute Prediction Strategy

## Core Logic

Polymarket offers 5-minute BTC price prediction markets. Each slot asks: "Will BTC be higher or lower than the open price at the end of this 5-minute window?"

### Entry Conditions

- **Timing**: Enter in the last 30 seconds of each 5-minute slot
- **Signal**: BTC has moved $50+ from the slot's opening price
- **Price**: Best ask price ≤ $0.95 (ensuring 5%+ profit potential)
- **Direction**: Buy the side matching BTC's current direction (Up if BTC rose, Down if BTC fell)

### Why This Works

When BTC has already moved $50+ in one direction with only 30 seconds left, the probability of a full reversal is <5%. We're buying shares at $0.92-0.95 that pay $1.00 if correct.

- Buy at $0.92 → 8.7% ROI if correct
- Buy at $0.95 → 5.3% ROI if correct
- Break-even requires >92% win rate (historically achievable with $50+ moves)

### Order Execution — FOK (Fill-or-Kill)

All orders are placed in **FOK mode**, meaning:
- The order must be **fully matched** on both sides of the market
- If not fully matched, the order is **automatically cancelled**
- No partial fills — either 100% executed or 0%
- No hanging orders — funds are never locked in unmatched positions

This ensures complete fund safety: if there's insufficient liquidity or the price moves, the order simply doesn't execute.

### Risk Controls

| Parameter | Value | Purpose |
|-----------|-------|---------|
| MAX_ASK_PRICE | $0.95 | Minimum 5% profit per trade |
| MIN_BTC_MOVE | $50 | Signal threshold |
| STRONG_BTC_MOVE | $100 | Double position size |
| MAX_TRADES_PER_HOUR | 10 | Overtrading protection |
| MAX_LOSS_SESSION | $200 | Session stop-loss |
| TRADE_SIZE_USD | $50 | Base position size |

### Strong Signal

When BTC moves $100+, the bot doubles position size ($100 instead of $50) because the reversal probability drops below 2%.

### Settlement

No manual exit needed — Polymarket automatically settles the 5-minute market. Winning shares pay $1.00, losing shares expire worthless.
