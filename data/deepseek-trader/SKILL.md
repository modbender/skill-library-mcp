---
name: deepseek-trader
description: Hybrid crypto analysis combining technical indicators with DeepSeek
  AI reasoning.
---


# DeepSeek Trader

Cryptocurrency analysis combining technical indicators (RSI, MACD, SMA, Bollinger Bands) with DeepSeek AI interpretation for buy/sell/hold signals.

## Quick Start

```bash
cd {skill_dir}
npm install && npm run build

# Set API key securely (don't pass on command line — visible in `ps`)
export DEEPSEEK_API_KEY=your_key

# Analyze a coin
node dist/cli.js analyze --coin bitcoin

# Analyze multiple coins
node dist/cli.js analyze --coins bitcoin,ethereum,solana

# Trading signals only
node dist/cli.js signals --coin bitcoin
```

## Output Format

```
🔍 BTC Analysis — ¥15,234,567

Technical Indicators:
| Indicator | Value | Signal |
|-----------|-------|--------|
| RSI       | 45.2  | Neutral |
| MACD      | +25   | Bullish |
| SMA 20/50 | Above | Bullish |
| Bollinger | Mid   | Neutral |

AI Signal: HOLD (72% confidence)
Risk: Medium
Action: Wait for RSI < 35 for entry
```

## Architecture

```
CoinGecko → Price Data → Technical Indicators → DeepSeek API → Signal
```

## Security

- **Never pass API keys on command line** — use `export` or `.env` file
- Add `.env` to `.gitignore`
- API key is sent only to DeepSeek API endpoint

## Edge Cases

- **DeepSeek API down**: Fall back to technical-only analysis without AI interpretation
- **CoinGecko rate limit**: Cached data used if available; warn user
- **Conflicting signals**: AI weighs indicators and provides reasoning for its decision

## ⚠️ Disclaimer

**For informational/educational purposes only.** Not financial advice. Always DYOR.

## Configuration

| Variable | Required | Description |
|----------|----------|-------------|
| `DEEPSEEK_API_KEY` | Yes | DeepSeek API key |
| `COINGECKO_API` | No | CoinGecko base URL (default: free tier) |

## Requirements

- Node.js 18+
- DeepSeek API key
- Internet connection
