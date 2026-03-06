---
name: portfolio-tracker
description: An investment portfolio tracker that runs entirely locally. All data stays in ~/.portfolio-tracker/.
---

# Portfolio Tracker Skill

An investment portfolio tracker that runs entirely locally. All data stays in `~/.portfolio-tracker/`.

## Architecture

- **Data**: `~/.portfolio-tracker/data.json` (portfolios, assets, prices)
- **Config**: `~/.portfolio-tracker/config.json` (API keys, wallet addresses, user profile)
- **Scripts**: TypeScript CLI tools in `<skill-path>/scripts/`, run via `npx tsx`

## First-Time Setup

Before running any script, ensure dependencies are installed:

```bash
npm install --prefix <skill-path>/scripts
```

Replace `<skill-path>` with the actual installed path of this skill.

## How Scripts Work

Each script is a standalone CLI tool. Run them with:

```bash
npx tsx <skill-path>/scripts/<script>.ts <command> [args]
```

Scripts read from stdin when needed and output JSON to stdout.

### data-store.ts
- `load` — Read portfolio data (creates default if missing)
- `save` — Write portfolio data (JSON from stdin)
- `load-config` — Read config
- `save-config` — Write config (JSON from stdin)

### fetch-prices.ts
- `crypto <symbol>` — Get crypto price (Binance → CoinGecko)
- `stock <symbol>` — Get stock price (Yahoo Finance)
- `fx` — Get USD/CNY/HKD exchange rates
- `historical <symbol>` — Get 3yr monthly historical data
- `search <query>` — Search for assets by name/symbol
- `refresh` — Batch refresh prices (assets JSON from stdin)

### binance-sync.ts
- `sync <apiKey> <apiSecret>` — Fetch all Binance balances (6 account types)
- `validate <apiKey> <apiSecret>` — Validate API credentials

### ibkr-sync.ts
- `sync <token> <queryId>` — Fetch IBKR positions via Flex Query
- `validate <token> <queryId>` — Validate IBKR credentials

### blockchain-sync.ts
- `sync <address> [chain]` — Fetch wallet balances (single chain or all 5 EVM chains)
- `validate <address>` — Validate EVM address

## Data Types

### Asset
```json
{
  "id": "unique-id",
  "type": "CRYPTO | USSTOCK | HKSTOCK | ASHARE | CASH",
  "symbol": "BTC",
  "name": "Bitcoin",
  "quantity": 1.5,
  "avgPrice": 40000,
  "currentPrice": 50000,
  "currency": "USD | CNY | HKD",
  "transactions": [],
  "source": { "type": "manual | binance | wallet | ibkr" }
}
```

### Portfolio
```json
{
  "id": "unique-id",
  "name": "Main",
  "assets": [...]
}
```

## Workflow Patterns

### Viewing Portfolio
1. Load data via `data-store.ts load`
2. Find current portfolio by `currentPortfolioId`
3. Calculate total value using `quantity * currentPrice` per asset
4. Convert to display currency using `exchangeRates`
5. Present as a formatted table

### Adding Assets
1. Load data
2. Search for the asset using `fetch-prices.ts search <query>`
3. Get current price via `fetch-prices.ts crypto/stock <symbol>`
4. Add asset to current portfolio with a generated unique ID
5. Save data

### Refreshing Prices
1. Load data
2. Pipe current portfolio assets to `fetch-prices.ts refresh` via stdin
3. Also run `fetch-prices.ts fx` for exchange rates
4. Update each asset's `currentPrice` and the `exchangeRates`
5. Set `lastPriceRefresh` to current ISO timestamp
6. Save data

### Syncing from Exchange/Wallet
1. Load config to get credentials
2. Run the appropriate sync script
3. Merge results: update existing assets (match by symbol+source), add new ones
4. Save data

## Commands

Available user commands:
- `/portfolio` — View and manage portfolios
- `/prices` — Refresh all prices
- `/setup` — Configure API keys and wallets
- `/sync-binance` — Sync from Binance
- `/sync-ibkr` — Sync from Interactive Brokers
- `/sync-wallet` — Sync from blockchain wallet
- `/advise` — Get AI investment advice
