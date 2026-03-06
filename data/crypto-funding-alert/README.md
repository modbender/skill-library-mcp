# Crypto Funding Rate Alert

Real-time cryptocurrency funding rate scanner for Binance futures markets.

## Quick Start

```bash
node scan.js
```

## What It Does

Scans 40+ cryptocurrencies for negative funding rates (where longs get paid by shorts) and identifies profitable opportunities based on:
- Funding rate magnitude
- 24h price trend
- Trading volume
- Risk management filters

## Installation

```bash
cd ~/.openclaw/workspace/skills
clawhub install crypto-funding-alert
```

## Usage

See [SKILL.md](./SKILL.md) for full documentation.

## Safety First

- Max 3x leverage
- 10% stop-loss minimum
- Only liquid markets ($10M+ volume)
- Position sizing limits
- Trend-aware filtering

## License

MIT
