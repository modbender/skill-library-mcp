---
name: Crypto Trader & Analyst
description: A skill for OpenClaw to research crypto market trends (technical & sentiment) and trade ETH on Binance.
---

# Crypto Trader & Analyst Skill

This skill allows OpenClaw to analyze the crypto market using technical indicators and news sentiment, record its findings, and execute trades on Binance.

## Dependencies

Ensure the following Python packages are installed:
```bash
pip install ccxt pandas pandas-ta requests TextBlob
```
*Note: `TextBlob` is suggested for basic sentiment analysis if needed, though simple keyword matching might suffice.*

## Environment Variables

You must set the following environment variables for trading:
- `BINANCE_API_KEY`: Your Binance API Key.
- `BINANCE_API_SECRET`: Your Binance API Secret.

**WARNING**: Never share these keys or commit them to version control.

## Workflow

### 1. Market Analysis

**Technical Analysis**
Run the market data script to get current indicators for a symbol (default ETH/USDT).
```bash
python skills/crypto_trader/scripts/market_data.py --symbol ETH/USDT
```
*Output: JSON containing RSI, MACD, close price, etc.*

**Sentiment Analysis**
Run the sentiment script to fetch latest news headers and forum buzz.
```bash
python skills/crypto_trader/scripts/sentiment_data.py
```
*Output: Text/JSON summary of positive/negative news.*

### 2. Decision Making & Logging

**Analyze & Record**
Based on the outputs from step 1, form a hypothesis. Is the market Bullish, Bearish, or Neutral?
Before trading, you **MUST** save your analysis.
```bash
python skills/crypto_trader/scripts/logger.py "Your detailed analysis here. E.g., RSI is 30 (oversold) and news is positive. Planning to BUY."
```

### 3. Execution

**Trade**
If the analysis supports a trade, execute it.
```bash
# Buy 0.01 ETH at Market Price
python skills/crypto_trader/scripts/trade.py --symbol ETH/USDT --side buy --amount 0.01 --type market

# Dry Run (Test without real money)
python skills/crypto_trader/scripts/trade.py --symbol ETH/USDT --side buy --amount 0.01 --dry-run
```
*The trade script will automatically append the transaction to `skills/crypto_trader/logs/trade_history.csv`.*

## Files structure
- `scripts/market_data.py`: Fetches OHLCV and calculates indicators.
- `scripts/sentiment_data.py`: Fetches news/forum data.
- `scripts/logger.py`: Appends analysis to `logs/analysis_journal.md`.
- `scripts/trade.py`: Executes trades and logs to `logs/trade_history.csv`.
- `logs/`: Directory storing your analysis history and trade logs.
