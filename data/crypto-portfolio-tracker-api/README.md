# crypto-portfolio-tracker-api

Real-time cryptocurrency portfolio tracking API. Track your Bitcoin, Ethereum, Solana and 10,000+ token holdings with live prices, profit/loss calculations, and allocation breakdowns.

## Features

- **Real-time prices** - Live cryptocurrency prices across all major tokens
- **Multi-wallet support** - Track multiple wallets and exchanges in one place
- **P&L calculations** - Automatic profit/loss tracking with cost basis
- **Allocation analysis** - Portfolio breakdown by asset, chain, and sector
- **10,000+ tokens** - Bitcoin, Ethereum, Solana, memecoins, DeFi tokens, and more

## Installation

```bash
npm install crypto-portfolio-tracker-api
```

## Quick Start

```javascript
const { PortfolioTracker } = require('crypto-portfolio-tracker-api');

// Initialize tracker
const tracker = new PortfolioTracker();

// Get current price
const btcPrice = await tracker.getPrice('BTC');
console.log(`Bitcoin: $${btcPrice.price}`);

// Get multiple prices
const prices = await tracker.getPrices(['BTC', 'ETH', 'SOL']);

// Track a portfolio
const portfolio = await tracker.trackPortfolio([
  { symbol: 'BTC', amount: 0.5, costBasis: 30000 },
  { symbol: 'ETH', amount: 10, costBasis: 2000 },
  { symbol: 'SOL', amount: 100, costBasis: 25 }
]);

console.log(`Total Value: $${portfolio.totalValue}`);
console.log(`Total P&L: $${portfolio.totalPnL} (${portfolio.pnlPercent}%)`);
```

## CLI Usage

```bash
# Get single price
npx crypto-portfolio-tracker-api price BTC

# Get multiple prices
npx crypto-portfolio-tracker-api prices BTC,ETH,SOL

# Track portfolio from JSON file
npx crypto-portfolio-tracker-api track portfolio.json
```

## API Reference

### `getPrice(symbol)`
Get real-time price for a single cryptocurrency.

### `getPrices(symbols)`
Get prices for multiple cryptocurrencies in one call.

### `trackPortfolio(holdings)`
Calculate portfolio value, P&L, and allocation from holdings array.

## Data Sources

Powered by [PRISM API](https://prismapi.ai) - unified financial data across crypto, DeFi, and traditional markets.

## License

MIT
