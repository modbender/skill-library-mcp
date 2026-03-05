# OpenClaw Trading Bot for Polymarket

Autonomous trading bot for [Polymarket](https://polymarket.com) prediction markets. OpenClaw skill with pluggable strategies, built-in risk management, and dry-run mode.

Powered by [**prob.trade**](https://app.prob.trade) — no private keys, no blockchain complexity. Get an API key and start trading in minutes.

## How It Works

```
Your Strategy (Python class)
        ↓
   Engine + Risk Manager
        ↓
   prob.trade API (HMAC-signed)
        ↓
   Polymarket CLOB (order book)
```

You write a strategy as a simple Python class. The engine runs it on a schedule, checks risk limits, and executes orders through [prob.trade](https://app.prob.trade). All blockchain operations (wallet management, transaction signing, gas) are handled by prob.trade — your bot only makes HTTP calls.

## Quick Start

### 1. Get your prob.trade API key

1. Create an account at [**app.prob.trade**](https://app.prob.trade)
2. Deposit USDC to your trading wallet
3. Go to **Settings → API Keys** → generate a new key
4. Save your `api_key` and `api_secret`

### 2. Install the probtrade skill

```bash
npx clawhub@latest install probtrade
```

Configure `~/.openclaw/skills/probtrade/config.yaml`:
```yaml
api_key: "ptk_live_..."
api_secret: "pts_..."
```

Or use environment variables:
```bash
export PROBTRADE_API_KEY="ptk_live_..."
export PROBTRADE_API_SECRET="pts_..."
```

### 3. Clone and configure

```bash
git clone https://github.com/vlprosvirkin/openclaw-bot-prob-trade.git
cd openclaw-bot-prob-trade
```

Edit `config.yaml`:
```yaml
strategy: momentum       # choose a strategy
dry_run: true            # start safe — logs only, no real orders
loop_interval_sec: 300   # scan every 5 minutes
```

### 4. Run

```bash
# See available strategies
python3 scripts/bot.py strategies

# Preview signals (no orders placed)
python3 scripts/bot.py scan

# Start autonomous trading
python3 scripts/bot.py run

# Check balance and positions
python3 scripts/bot.py status
```

## Built-in Strategies

11 strategies — 8 work out of the box, 3 need external API keys. See [docs/strategies.md](docs/strategies.md) for details.

| Strategy | Type | Description |
|----------|------|-------------|
| `momentum` | Mean Reversion | Buys markets where YES price dropped >10% in 24h |
| `trend_breakout` | Trend Following | Rides rising markets with high volume confirmation |
| `pair_arb` | Arbitrage | Buys when YES + NO < $0.95 — guaranteed profit at resolution |
| `value_investor` | Value Investing | Finds undervalued markets, Kelly criterion sizing |
| `whale_tracking` | Copy Trading | Follows high-winrate wallets from leaderboard |
| `expiration_timing` | Volatility | Trades 24-72h before market resolution |
| `market_making` | Market Making | Two-sided quotes, dynamic spread on volatility |
| `ensemble` | Meta-Strategy | Runs multiple strategies, Byzantine consensus voting |
| `logic_arb` | LLM Arbitrage | Claude/GPT-4 finds correlated market mispricings * |
| `weather_arb` | Data Arbitrage | NOAA forecasts vs market prices * |
| `sentiment` | NLP Divergence | FinBERT social sentiment vs market price * |

\* Requires external API key — see [docs/strategies.md](docs/strategies.md)

## Create Your Own Strategy

Create a file in `lib/strategies/` — the bot discovers it automatically.

```python
# lib/strategies/my_strategy.py
from lib.strategy_base import Strategy, Signal, get_yes_price, get_price_change

class MyStrategy(Strategy):
    name = "my_strategy"  # use this name in config.yaml

    def initialize(self, config):
        """Called once at startup."""
        self.threshold = config.get("my_param", 0.15)

    def scan(self, markets, positions, balance):
        """Called every cycle. Return list of trading signals."""
        signals = []
        for m in markets:
            price = get_yes_price(m)
            drop = get_price_change(m)
            if drop and drop < -self.threshold and price:
                signals.append(Signal(
                    market=m["condition_id"],
                    side="BUY",
                    outcome="Yes",
                    order_type="LIMIT",
                    amount=5,
                    price=price,
                    confidence=0.8,
                    reason=f"Dropped {drop:.0%}, buying dip"
                ))
        return signals
```

Set `strategy: my_strategy` in `config.yaml` and run.

### Helper functions

```python
from lib.strategy_base import (
    get_yes_price,     # → 0.45
    get_no_price,      # → 0.55
    get_price_change,  # → -0.12 (24h absolute change)
    get_liquidity,     # → 8000.0
    get_volume_24h,    # → 12500.0
)
```

### Signal fields

| Field | Type | Description |
|-------|------|-------------|
| `market` | str | Polymarket condition_id |
| `side` | str | `"BUY"` or `"SELL"` |
| `outcome` | str | `"Yes"` or `"No"` |
| `order_type` | str | `"MARKET"` or `"LIMIT"` |
| `amount` | float | USDC to spend |
| `price` | float | Price for LIMIT orders (0.01–0.99) |
| `confidence` | float | 0.0–1.0, strategy's confidence |
| `reason` | str | Human-readable explanation |

## Risk Management

Every signal passes through the risk manager before execution:

```yaml
risk:
  max_position_size: 50      # max $50 per order
  max_daily_spend: 50        # max $50/day total
  max_open_positions: 5      # max 5 positions at once
  max_total_exposure: 0.5    # max 50% of balance in positions
  max_drawdown_pct: 0.30     # STOP ALL if portfolio drops 30%
  max_consecutive_losses: 3  # STOP ALL after 3 losses in a row
  min_balance: 10            # STOP ALL if balance < $10
```

**Circuit Breaker**: `max_drawdown_pct` or `max_consecutive_losses` halts all trading until restart.

## Deploy

See [docs/deployment.md](docs/deployment.md) for the full deployment guide (local, VPS, Docker).

### Local
```bash
python3 scripts/bot.py run
```

### Systemd (VPS)
```bash
sudo cp deploy/openclaw-bot.service /etc/systemd/system/
sudo systemctl enable --now openclaw-bot
```

### Docker
```bash
docker build -f deploy/Dockerfile -t openclaw-bot ../../
docker run -d --name openclaw-bot \
  -e PROBTRADE_API_KEY=ptk_live_... \
  -e PROBTRADE_API_SECRET=pts_... \
  openclaw-bot
```

## Project Structure

```
├── SKILL.md                    # OpenClaw skill definition
├── config.yaml                 # Bot configuration
├── scripts/
│   └── bot.py                  # CLI entry point
├── lib/
│   ├── strategy_base.py        # Strategy interface + helpers
│   ├── risk_manager.py         # Risk checks + circuit breaker
│   ├── engine.py               # Main trading loop
│   └── strategies/             # 11 built-in strategies
│       ├── momentum.py         # #1 Mean reversion
│       ├── trend_breakout.py   # #2 Trend following
│       ├── pair_arb.py         # #3 Pair arbitrage
│       ├── logic_arb.py        # #4 LLM correlation arb
│       ├── market_making.py    # #5 Two-sided spread
│       ├── ensemble.py         # #6 Multi-strategy consensus
│       ├── weather_arb.py      # #7 Weather forecast arb
│       ├── value_investor.py   # #8 Value + Kelly criterion
│       ├── whale_tracking.py   # #9 Smart money tracking
│       ├── sentiment.py        # #10 NLP sentiment divergence
│       └── expiration_timing.py # #11 Near-expiry volatility
├── docs/
│   ├── deployment.md           # Full deployment guide
│   ├── strategies.md           # All 11 strategies reference
│   └── references.md           # 44 research sources
└── deploy/
    ├── Dockerfile
    └── openclaw-bot.service
```

## Requirements

- Python 3.8+
- [prob.trade](https://app.prob.trade) account with API key
- [probtrade](https://clawhub.ai/vlprosvirkin/prob-trade-polymarket-analytics) OpenClaw skill

## Contributing

1. Fork this repo
2. Create your strategy in `lib/strategies/`
3. Test: `python3 scripts/bot.py scan --strategy your_strategy`
4. Submit a PR — share your strategy with the community

## Documentation

- [docs/strategies.md](docs/strategies.md) — all 11 strategies with parameters and config examples
- [docs/deployment.md](docs/deployment.md) — local, VPS, Docker deployment guide
- [docs/references.md](docs/references.md) — curated library of 44 research sources

## Disclaimer

This software is for educational and research purposes. Trading on prediction markets involves financial risk. Past performance does not guarantee future results. Always start with `dry_run: true` and only trade with funds you can afford to lose.

## License

[MIT](LICENSE)
