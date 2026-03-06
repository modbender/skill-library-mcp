---
name: vynn-backtester
description: Run trading strategy backtests with natural language — powered by Vynn
version: 1.0.0
homepage: https://the-vynn.com
metadata:
  clawdbot:
    emoji: "📈"
    requires:
      env: ["VYNN_API_KEY"]
    primaryEnv: "VYNN_API_KEY"
    files: ["plugin.py", "config.example.toml"]
tags: [backtest, trading, quant, finance, strategy, stocks, portfolio, alpha]
---

# Vynn Backtester

Backtest any trading strategy with natural language. Get Sharpe ratio, returns, drawdown, and full equity curves in seconds.

## What it does

- **Natural language strategies**: Describe your strategy in plain English and Vynn translates it into a runnable backtest
- **Structured strategies**: Power users can pass precise entry/exit rules as JSON
- **Full metrics**: Sharpe ratio, total return, max drawdown, win rate, trade count, and equity curve
- **Multi-ticker**: Backtest across any combination of stocks, ETFs, or indices
- **Strategy comparison**: Compare multiple strategies head-to-head, ranked by Sharpe ratio
- **No infrastructure**: No local data downloads, no dependencies beyond Python stdlib

## Setup

1. Get a free API key at [the-vynn.com](https://the-vynn.com) (10 backtests/month, no credit card)
2. Set `VYNN_API_KEY` in your environment or skill config
3. Run `/backtest "your strategy here"` from any OpenClaw agent

### Quick start

```bash
# Sign up (instant, returns your API key)
curl -X POST https://the-vynn.com/v1/signup -H "Content-Type: application/json" -d '{"email": "you@example.com"}'

# Set the key
export VYNN_API_KEY="vynn_free_..."
```

## Usage examples

### Simple natural language backtest

```
/backtest "RSI mean reversion on AAPL, 2 year lookback"
```

### Momentum strategy

```
/backtest "MACD crossover on SPY with 20/50 EMA filter"
```

### Multi-ticker portfolio

```
/backtest --tickers AAPL,MSFT,GOOGL --strategy "momentum top 3"
```

### Structured entry/exit rules

```
/backtest '{"entries": [{"indicator": "RSI", "op": "<", "value": 30}], "exits": [{"indicator": "RSI", "op": ">", "value": 70}]}' --tickers AAPL
```

### Compare strategies

```python
from plugin import VynnBacktesterPlugin

vynn = VynnBacktesterPlugin()
results = vynn.compare(
    strategies=[
        "RSI mean reversion",
        "MACD crossover",
        "Bollinger band breakout",
    ],
    tickers=["SPY"],
)
for r in results:
    print(f"{r.strategy}: Sharpe={r.sharpe_ratio}, Return={r.total_return_pct}%")
```

## Environment Variables

| Variable | Required | Description | Default |
|---|---|---|---|
| `VYNN_API_KEY` | Yes | Your API key from the-vynn.com | -- |
| `VYNN_BASE_URL` | No | Override API base URL (for self-hosted instances) | `https://the-vynn.com/v1` |

## External Endpoints

| Endpoint | Purpose | Data Sent |
|---|---|---|
| `https://the-vynn.com/v1/backtest` | Execute a strategy backtest | Strategy text, ticker list, lookback period |
| `https://the-vynn.com/v1/signup` | Free API key registration | Email address |

## Security & Privacy

- All requests authenticated via `X-API-Key` header
- Strategy descriptions and ticker lists are sent to the Vynn API for backtest execution
- No trading data, portfolio holdings, or personal information is stored beyond the backtest run
- Backtest results are ephemeral and not persisted on Vynn servers
- No credentials are stored by the skill -- only your API key in environment variables
- Source code is fully open: [github.com/beee003/astrai-openclaw](https://github.com/beee003/astrai-openclaw)

## Model Invocation

This skill does not invoke any LLM models. It sends strategy descriptions to the Vynn backtest engine, which is a quantitative execution engine (not an AI model). No prompts or completions are generated.

## Pricing

- **Free**: 10 backtests/month, all features, no credit card required
- **Pro** ($29/mo): Unlimited backtests, priority execution, extended lookback periods
