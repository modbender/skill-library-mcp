---
name: crypto-trader
description: |
  Automated cryptocurrency trading skill for OpenClaw. Supports 8 trading strategies
  (Grid Trading, DCA, Trend Following, Scalping, Arbitrage, Swing Trading, Copy Trading,
  Portfolio Rebalancing), multi-exchange connectivity (Binance, Bybit, Kraken, Coinbase),
  AI-driven sentiment analysis, comprehensive risk management, backtesting, paper trading,
  and real-time monitoring with Telegram/Discord/Email alerts.
  Use when the user asks about crypto trading, portfolio management, market analysis,
  starting/stopping strategies, checking balances, or running backtests.
metadata:
  openclaw:
    requires:
      bins: ["python3"]
      env: ["BINANCE_API_KEY", "BINANCE_API_SECRET"]
    primaryEnv: "BINANCE_API_KEY"
---

# Crypto Trader Skill

Automated cryptocurrency trading with 8 strategies, multi-exchange support, AI sentiment analysis, and comprehensive risk management.

**Important**: By default all operations run against **testnet** (paper trading). Set `CRYPTO_DEMO=false` only when you are absolutely certain the user wants to trade with real money.

## Prerequisites

Install dependencies once from the skill directory:

```bash
pip install -r {baseDir}/requirements.txt
```

Required environment variables (set in `.env` or via OpenClaw settings):

- `BINANCE_API_KEY` and `BINANCE_API_SECRET` (required for Binance)
- `CRYPTO_DEMO=true` (default: paper trading mode)

Optional:
- `BYBIT_API_KEY`, `BYBIT_API_SECRET` (for Bybit)
- `KRAKEN_API_KEY`, `KRAKEN_API_SECRET` (for Kraken)
- `COINBASE_API_KEY`, `COINBASE_API_SECRET` (for Coinbase)
- `TELEGRAM_BOT_TOKEN`, `TELEGRAM_CHAT_ID` (for Telegram alerts)
- `DISCORD_WEBHOOK_URL` (for Discord alerts)
- `CRYPTOPANIC_API_KEY` (for sentiment analysis)

## Available Modes

### 1. status -- Portfolio and strategy overview

```bash
python3 {baseDir}/scripts/main.py --mode status
```

Returns JSON with:
- Portfolio value per exchange
- Active strategies and their state
- Risk status (daily P&L, drawdown, kill switch)
- Environment (paper/live)

Use when the user asks: "How is my portfolio?", "What's running?", "Give me an overview."

### 2. balance -- Check exchange balances

```bash
python3 {baseDir}/scripts/main.py --mode balance
python3 {baseDir}/scripts/main.py --mode balance --exchange binance
```

Returns balances for the specified exchange (or all exchanges). Shows total, free, and used amounts per asset.

Use when the user asks: "How much BTC do I have?", "What's my balance?", "Show my funds."

### 3. start_strategy -- Start a trading strategy

```bash
python3 {baseDir}/scripts/main.py --mode start_strategy --strategy grid --params '{"symbol":"BTC/USDT","price_range":[90000,110000],"num_grids":10,"order_amount_usdt":10}'
python3 {baseDir}/scripts/main.py --mode start_strategy --strategy dca --params '{"symbol":"ETH/USDT","interval":"daily","amount_per_buy_usdt":5}'
python3 {baseDir}/scripts/main.py --mode start_strategy --strategy trend --params '{"symbol":"BTC/USDT","timeframe":"4h"}'
```

Supported strategies:

| Strategy | Name | Description |
|----------|------|-------------|
| Grid Trading | `grid_trading` | Buy/sell at evenly spaced price levels within a range |
| DCA | `dca` | Buy fixed amounts at regular intervals |
| Trend Following | `trend_following` | EMA crossover + RSI signals |
| Scalping | `scalping` | Fast small trades on spread/momentum |
| Arbitrage | `arbitrage` | Cross-exchange price difference exploitation |
| Swing Trading | `swing_trading` | Bollinger Bands + MACD, hold 2-14 days |
| Copy Trading | `copy_trading` | Replicate trades from tracked wallets/traders |
| Rebalancing | `rebalancing` | Maintain target portfolio allocation |

Each strategy uses defaults from `config/strategies.yaml` which can be overridden via `--params`.

**CRITICAL**: Always confirm with the user before starting a strategy. Show the parameters clearly and ask for approval.

Use when the user asks: "Start grid trading on BTC", "I want to DCA into ETH", "Follow the trend on SOL."

### 4. stop_strategy -- Stop a running strategy

```bash
python3 {baseDir}/scripts/main.py --mode stop_strategy --strategy-id <id>
```

Stops a specific strategy instance. The strategy ID is returned when starting and shown in the list.

### 5. list_strategies -- List all strategies

```bash
python3 {baseDir}/scripts/main.py --mode list_strategies
```

Returns all available and running strategies with their status, parameters, and performance stats.

### 6. backtest -- Test a strategy on historical data

```bash
python3 {baseDir}/scripts/main.py --mode backtest --strategy grid_trading --params '{"symbol":"BTC/USDT","price_range":[40000,50000],"num_grids":10}' --start 2025-01-01 --end 2025-12-31
python3 {baseDir}/scripts/main.py --mode backtest --strategy dca --params '{"symbol":"BTC/USDT","interval":"daily","amount_per_buy_usdt":10}' --start 2025-06-01 --end 2025-12-31
python3 {baseDir}/scripts/main.py --mode backtest --strategy trend_following --params '{"symbol":"BTC/USDT","timeframe":"4h"}' --start 2025-01-01 --end 2025-12-31
```

Returns performance metrics:
- Total return % vs buy-and-hold
- Win rate, trade count
- Max drawdown, Sharpe ratio
- Fee impact
- Individual order history

Results are saved to `data/backtests/`.

Use when the user asks: "Would grid trading have worked?", "Backtest DCA on ETH", "Test this strategy."

### 7. history -- Trade history

```bash
python3 {baseDir}/scripts/main.py --mode history --days 7
python3 {baseDir}/scripts/main.py --mode history --days 30
```

Returns completed orders from all exchanges for the last N days.

### 8. sentiment -- Market sentiment analysis

```bash
python3 {baseDir}/scripts/main.py --mode sentiment --symbol BTC
python3 {baseDir}/scripts/main.py --mode sentiment --symbol ETH
```

Analyzes sentiment from:
- Crypto news RSS feeds (CoinTelegraph, CoinDesk)
- CryptoPanic (requires API key)
- Reddit (r/cryptocurrency, r/bitcoin)
- Twitter (requires bearer token)

Returns aggregate score (-1.0 to 1.0) with labels: very_bearish, bearish, neutral, bullish, very_bullish.

Use when the user asks: "What's the market sentiment?", "Is BTC bullish right now?", "Any news about ETH?"

### 9. monitor -- Real-time monitoring daemon

```bash
python3 {baseDir}/scripts/main.py --mode monitor --action start
python3 {baseDir}/scripts/main.py --mode monitor --action status
python3 {baseDir}/scripts/main.py --mode monitor --action stop
```

The monitoring daemon runs in the background and:
- Checks open orders every 10 seconds
- Updates portfolio snapshot every 60 seconds
- Checks risk limits every 60 seconds
- Evaluates strategy signals every 5 minutes
- Runs sentiment analysis every 30 minutes
- Sends alerts via Telegram/Discord/Email

### 10. emergency_stop -- Kill switch

```bash
python3 {baseDir}/scripts/main.py --mode emergency_stop
```

Immediately:
1. Cancels ALL open orders on ALL exchanges
2. Stops ALL running strategies
3. Activates the kill switch (blocks all future trades)

The kill switch must be manually deactivated before trading can resume.

Use when the user says: "Stop everything!", "Emergency!", "Kill all trades."

## Configuration Files

### config/exchanges.yaml
Exchange connectivity settings, sandbox mode, rate limits.

### config/strategies.yaml
Default parameters for each strategy. Users can override via `--params`.

### config/risk_limits.yaml
Risk management rules:
- `max_position_size_pct`: Max portfolio % per position (default: 25%)
- `max_daily_loss_eur`: Emergency stop on daily loss (default: 50 EUR)
- `max_drawdown_pct`: Stop at drawdown from ATH (default: 15%)
- `max_order_size_eur`: Max per order (default: 100 EUR)
- `max_open_orders`: Max concurrent orders (default: 50)
- Stop-loss (fixed 5%, trailing 3%)
- Take-profit (10%, partial at 5%)

### config/notifications.yaml
Alert routing rules per event type and channel.

## Safety Rules

1. **NEVER** execute trades without explicit user confirmation in live mode.
2. Default mode is **paper trading** (`CRYPTO_DEMO=true`). Remind the user which mode is active.
3. API keys must have **TRADE** permissions only. **NEVER** withdrawal permissions.
4. Risk limits are enforced automatically. If a limit is hit, explain to the user what happened.
5. Emergency stop is always available and overrides everything.
6. Always show estimated cost and risk before confirming a trade.
7. If `CRYPTO_DEMO=false`, warn the user clearly that this uses **real money**.
8. Log all actions. The user can review history at any time.
9. When starting a strategy, show the full parameter set and ask for confirmation.
10. Never bypass risk limits, even if the user asks. Explain why the limit exists.

## Output Format

All modes return structured JSON to stdout. Parse it and present a human-readable summary to the user. Highlight important numbers (P&L, prices, risk metrics). Use clear formatting with tables where appropriate.

## Running Tests

```bash
cd {baseDir}
pip install pytest
python -m pytest tests/ -v
```

## Troubleshooting

### "Exchange not initialized"
Check that the API key and secret are set in environment variables for the target exchange.

### "Authentication failed"
Verify your API keys are correct and not expired. For testnet, make sure you're using testnet keys.

### "Rate limit reached"
The skill automatically retries with backoff. If persistent, reduce strategy evaluation frequency.

### "Kill switch is active"
The emergency stop was triggered. Review what happened, then deactivate:
The kill switch state is stored in `~/.openclaw/.crypto-trader-risk-state.json`. Set `"killed": false` to reset, or use a future CLI command to deactivate.
