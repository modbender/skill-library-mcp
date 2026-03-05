# Portfolio Tracker — Claude Code Skill

A local-first investment portfolio tracker that runs as a Claude Code skill. All data stays on your machine — no backend, no cloud, no account needed.

## Features

- Track stocks (US, HK, A-shares), crypto, and cash across multiple portfolios
- Sync from **Binance**, **Interactive Brokers**, and **EVM blockchain wallets**
- Real-time prices from Binance, CoinGecko, and Yahoo Finance
- Multi-currency support (USD, CNY, HKD)
- AI investment advice powered by Claude (no API key needed)

## Installation

```bash
npx @anthropic-ai/claude-code skills add <github-url>
```

## Quick Start

```
/setup              # Configure API keys and wallets
/portfolio          # View your portfolio
/portfolio add BTC  # Add an asset
/prices             # Refresh all prices
/sync-binance       # Sync from Binance
/sync-ibkr          # Sync from Interactive Brokers
/sync-wallet        # Sync from blockchain wallet
/advise             # Get AI investment advice
```

## Commands

| Command | Description |
|---------|-------------|
| `/portfolio` | View current portfolio, add/remove/edit assets, manage portfolios |
| `/prices` | Refresh all asset prices and FX rates |
| `/setup` | Configure exchange API keys, wallet addresses, risk profile |
| `/sync-binance` | Sync balances from Binance (spot, funding, earn, futures) |
| `/sync-ibkr` | Sync positions from Interactive Brokers via Flex Query |
| `/sync-wallet` | Sync EVM wallet balances (ETH, BSC, Polygon, Arbitrum, Optimism) |
| `/advise` | Get personalized investment advice from Claude |

## Data Storage

All data is stored locally:

- `~/.portfolio-tracker/data.json` — Portfolios, assets, prices, settings
- `~/.portfolio-tracker/config.json` — API keys, wallet addresses, user profile

## Supported Asset Types

| Type | Examples | Price Source |
|------|----------|-------------|
| CRYPTO | BTC, ETH, SOL | Binance → CoinGecko |
| USSTOCK | AAPL, SPY, QQQ | Yahoo Finance |
| HKSTOCK | 0700.HK, 9988.HK | Yahoo Finance |
| ASHARE | 600519.SS, 000001.SZ | Yahoo Finance |
| CASH | USD, CNY, HKD | Fixed at 1 |

## Exchange Setup

### Binance
1. Create API keys at [Binance API Management](https://www.binance.com/en/my/settings/api-management)
2. Enable **read-only** permissions (no trading needed)
3. Run `/setup` and select Binance

### Interactive Brokers
1. Log into IBKR Account Management
2. Go to Reports → Flex Queries → Create a new query
3. Include sections: Open Positions, Cash Report, Trades
4. Note your Token and Query ID
5. Run `/setup` and select IBKR

### Blockchain Wallets
1. Have your EVM wallet address ready (0x...)
2. Run `/setup` and select blockchain wallet
3. Choose which chains to monitor

## Security

- API keys are stored locally in `~/.portfolio-tracker/config.json`
- Only **read-only** API access is needed for exchanges
- No data is sent to any server — all processing happens locally
- Recommend setting `chmod 600 ~/.portfolio-tracker/config.json`

## Development

```bash
cd skill/scripts
npm install
npm test          # Run all tests
npx vitest        # Watch mode
```

## License

MIT
