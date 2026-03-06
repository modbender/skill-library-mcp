---
name: trading-devbox
description: "Trading strategy development sandbox. User describes trading intent in natural language, agent writes a Python backtest strategy and returns results."
user-invocable: true
---

# Trading DevBox

Help users develop and backtest trading strategies from natural language descriptions.

## When to Use

- User describes a trading idea or intent (e.g. "SOL 跌 10% 买入，涨 30% 止盈")
- User asks to write, backtest, or optimize a trading strategy
- User mentions keywords: 策略, 回测, backtest, strategy, trading

## Workflow

1. Parse the user's trading intent into structured parameters:
   - Asset (e.g. SOL, BTC, ETH)
   - Entry condition (e.g. price drops 10%)
   - Exit condition (e.g. take profit at 30%, stop loss at 5%)
   - Timeframe (e.g. 1h, 4h, 1d)

2. Confirm the parsed parameters with the user before proceeding.

3. Generate a Python backtest strategy using backtrader:

```bash
mkdir -p /tmp/trading-devbox && cat > /tmp/trading-devbox/strategy.py << 'PYEOF'
import backtrader as bt
import sys
import json

class UserStrategy(bt.Strategy):
    params = dict(
        entry_drop_pct=10,
        take_profit_pct=30,
        stop_loss_pct=5,
    )

    def __init__(self):
        self.order = None
        self.buy_price = None

    def next(self):
        if self.order:
            return
        if not self.position:
            # entry: price dropped by entry_drop_pct from recent high
            high = max(self.data.close.get(size=20) or [self.data.close[0]])
            drop = (high - self.data.close[0]) / high * 100
            if drop >= self.p.entry_drop_pct:
                self.order = self.buy()
                self.buy_price = self.data.close[0]
        else:
            pnl = (self.data.close[0] - self.buy_price) / self.buy_price * 100
            if pnl >= self.p.take_profit_pct or pnl <= -self.p.stop_loss_pct:
                self.order = self.sell()

if __name__ == '__main__':
    print(json.dumps({"status": "ok", "message": "Strategy generated"}))
PYEOF
python3 /tmp/trading-devbox/strategy.py
```

4. Report the result to the user in a clear format.

## Response Format

Always respond in the user's language. Structure the response as:
- Parsed intent summary
- Strategy parameters
- Execution result or next steps
