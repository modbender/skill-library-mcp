# Listing Copy Template

Use these snippets when publishing to the OpenClaw skills market.

## Title

Stock Backtest Analyst

## One-Line Pitch

Backtest stock strategies from OHLCV data and instantly report return, win rate, drawdown, Sharpe, and trade logs.

## Full Description

Stock Backtest Analyst is a practical research skill for validating stock trading strategies on historical data. It supports trend-following (SMA crossover), mean-reversion (RSI), and breakout logic with realistic execution assumptions.

What it does:
- Runs long-only backtests with signal-at-t, execution-at-t+1 open.
- Includes transaction costs and slippage in every run.
- Outputs machine-readable JSON and trade-by-trade CSV.
- Reports essential metrics: total return, CAGR, max drawdown, Sharpe ratio, win rate, and profit factor.

Who should use it:
- Quant researchers validating ideas before coding full systems.
- Discretionary traders testing entry/exit rules.
- Builders who need standardized strategy reports for clients or teams.

## Suggested Tags

- quant
- backtest
- stocks
- strategy
- trading
- research

## Default Prompt (for listing UI)

Use $stock-strategy-backtester to run a stock strategy backtest from OHLCV CSV data and compare return, drawdown, and win rate across parameter sets.
