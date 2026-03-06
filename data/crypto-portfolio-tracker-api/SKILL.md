---
name: crypto-portfolio-tracker-api
description: Track cryptocurrency portfolios with real-time prices, P&L calculations, and allocation analysis. Query Bitcoin, Ethereum, Solana and 10,000+ token holdings.
---

# Crypto Portfolio Tracker API

Track cryptocurrency portfolios with real-time prices and P&L calculations.

## Installation

```bash
npm install crypto-portfolio-tracker-api
```

## Usage

```javascript
const { PortfolioTracker } = require('crypto-portfolio-tracker-api');

const tracker = new PortfolioTracker();

// Get current price
const btc = await tracker.getPrice('BTC');

// Get multiple prices
const prices = await tracker.getPrices(['BTC', 'ETH', 'SOL']);

// Track portfolio with P&L
const portfolio = await tracker.trackPortfolio([
  { symbol: 'BTC', amount: 0.5, costBasis: 30000 },
  { symbol: 'ETH', amount: 10, costBasis: 2000 }
]);

console.log(`Total: $${portfolio.totalValue}`);
console.log(`P&L: $${portfolio.totalPnL}`);
```

## CLI

```bash
# Get price
npx crypto-portfolio-tracker-api price BTC

# Track portfolio from file
npx crypto-portfolio-tracker-api track portfolio.json
```

## API Methods

- `getPrice(symbol)` - Get single token price
- `getPrices(symbols)` - Get multiple prices
- `trackPortfolio(holdings)` - Calculate portfolio value and P&L

## Data Source

Powered by [PRISM API](https://prismapi.ai)
