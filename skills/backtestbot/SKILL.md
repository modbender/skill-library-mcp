---
name: backtestbot
description: Backtest trading strategies against historical market data with
  detailed performance analytics.
---


# BacktestBot

Backtest trading strategies against historical market data with detailed performance analytics.

## What it does

BacktestBot enables you to define, test, and evaluate trading strategies using historical data, including:

- **Strategy definition** — describe strategies in natural language or structured rules (entry/exit signals, position sizing, stop losses)
- **Historical simulation** — run strategies against years of tick or daily data across equities, options, futures, and crypto
- **Performance metrics** — Sharpe ratio, max drawdown, win rate, profit factor, CAGR, and trade-level breakdown
- **Risk analysis** — value-at-risk, correlation to benchmarks, worst-case drawdown periods, and tail risk metrics
- **Comparison** — test multiple strategy variants side-by-side and rank by risk-adjusted returns

## Usage

Ask your agent to backtest strategies and analyze results:

- "Backtest a mean reversion strategy on SPY using RSI below 30 as entry over the last 5 years"
- "Compare buy-and-hold vs momentum rotation across the S&P 500 sectors since 2020"
- "What is the max drawdown if I use a 2% trailing stop on AAPL swing trades?"
- "Optimize the lookback period for my moving average crossover strategy on QQQ"

## Configuration

Set the following environment variables:

- `BACKTESTBOT_API_KEY` — API key for BacktestBot. Used to authenticate requests for historical OHLCV data, strategy simulations, and performance metrics.
- `BACKTESTBOT_DATA_DIR` — (optional) local directory for cached historical data. Defaults to `~/.backtestbot/data`.
