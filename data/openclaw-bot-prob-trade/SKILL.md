---
name: probtrade-bot
version: 1.0.0
description: "Autonomous trading bot for Polymarket via prob.trade. Run strategies, manage risk, scan markets. Requires the probtrade skill for API access."
homepage: https://github.com/vlprosvirkin/openclaw-bot-prob-trade
user-invocable: true
metadata: {"openclaw":{"requires":{"bins":["python3"],"skills":["probtrade"]},"emoji":"🤖","install":[{"id":"python3","kind":"brew","formula":"python@3","bins":["python3"],"label":"Install Python 3","os":["darwin","linux"]}]}}
---

# probtrade-bot — Autonomous Polymarket Trading Bot

Autonomous trading bot that uses the [probtrade](https://clawhub.ai/probtrade/prob-trade-polymarket-analytics) skill to trade on Polymarket via [prob.trade](https://app.prob.trade). Includes built-in risk management, pluggable strategies, and dry-run mode.

**Requires:** The `probtrade` skill must be installed and configured with API keys.

## Setup

1. Install and configure the `probtrade` skill first (API key required)
2. Edit `{baseDir}/config.yaml` to set your strategy and risk limits
3. By default, `dry_run: true` — the bot will only log, not trade

## Commands

### Run Bot
Start the autonomous trading loop. Scans markets and places orders every cycle.
```bash
python3 {baseDir}/scripts/bot.py run
```

Override strategy:
```bash
python3 {baseDir}/scripts/bot.py run --strategy pair_arb
```

### Scan Markets
Run a single scan to see what the strategy would do, without placing orders.
```bash
python3 {baseDir}/scripts/bot.py scan
```

### Bot Status
Check balance, positions, open orders, and risk state.
```bash
python3 {baseDir}/scripts/bot.py status
```

### List Strategies
See all available strategies.
```bash
python3 {baseDir}/scripts/bot.py strategies
```

## Built-in Strategies

- **momentum** — Contrarian momentum / mean reversion. Buys markets where YES price dropped significantly in 24h, betting on reversion.
- **pair_arb** — Async pair cost arbitrage. Finds markets where YES + NO price < $0.95, buys the cheaper side for guaranteed profit on resolution.

## Creating Your Own Strategy

1. Create a file in `{baseDir}/lib/strategies/` (e.g. `my_strategy.py`)
2. Implement a class that extends `Strategy`:

```python
from lib.strategy_base import Strategy, Signal, get_yes_price, get_price_change

class MyStrategy(Strategy):
    name = "my_strategy"

    def initialize(self, config):
        self.threshold = config.get("my_param", 0.15)

    def scan(self, markets, positions, balance):
        signals = []
        for m in markets:
            if should_buy(m):
                signals.append(Signal(
                    market=m["condition_id"],
                    side="BUY", outcome="Yes",
                    order_type="LIMIT", amount=5,
                    price=get_yes_price(m),
                    confidence=0.8,
                    reason="My reason"
                ))
        return signals
```

3. Set `strategy: my_strategy` in `config.yaml`
4. Test: `python3 {baseDir}/scripts/bot.py scan --strategy my_strategy`

## Risk Management

The bot enforces risk limits defined in `config.yaml`:
- **max_position_size**: Maximum USDC per single order
- **max_daily_spend**: Total USDC allowed per day
- **max_open_positions**: Maximum concurrent positions
- **max_drawdown_pct**: Circuit breaker — halts all trading if portfolio drops by this %
- **max_consecutive_losses**: Circuit breaker trigger after N losses in a row

## Environment Variables

Override config values via env vars:
- `DRY_RUN=true` — force dry run mode
- `STRATEGY=pair_arb` — override strategy
- `LOOP_INTERVAL=60` — override scan interval
- `PROBTRADE_SKILL_PATH=/path/to/probtrade/lib` — custom path to probtrade skill lib

## Output

All commands output structured data (JSON or formatted text) for easy parsing by AI agents.
