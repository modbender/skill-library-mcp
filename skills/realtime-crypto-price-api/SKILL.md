---
name: realtime-crypto-price-api
description: Real-time cryptocurrency price data API for Bitcoin, Ethereum, Solana and 10,000+ tokens. Get live prices, historical data, trending coins, and batch queries for trading bots and dashboards.
---

# Real-time Crypto Price API

Get real-time cryptocurrency prices for 10,000+ tokens.

## Installation

```bash
npm install realtime-crypto-price-api
```

## Usage

```javascript
const { CryptoPrice } = require('realtime-crypto-price-api');

const client = new CryptoPrice();

// Get Bitcoin price
const btc = await client.getPrice('BTC');
console.log(`Bitcoin: $${btc.price}`);

// Get multiple prices
const prices = await client.getPrices(['BTC', 'ETH', 'SOL']);

// Top coins by market cap
const top10 = await client.getTopCoins(10);

// Trending gainers/losers
const gainers = await client.getTrending('gainers');

// Historical OHLCV data
const history = await client.getHistory('ETH', '1d', 30);

// Search tokens
const results = await client.search('pepe');
```

## CLI

```bash
# Single price
npx realtime-crypto-price-api BTC

# Multiple prices
npx realtime-crypto-price-api batch BTC,ETH,SOL

# Top coins
npx realtime-crypto-price-api top 20

# Trending
npx realtime-crypto-price-api trending gainers
```

## API Methods

- `getPrice(symbol)` - Single token price with 24h change
- `getPrices(symbols)` - Batch price query
- `getTopCoins(limit)` - Top by market cap
- `getTrending(direction)` - Gainers or losers
- `getHistory(symbol, interval)` - OHLCV candles
- `search(query)` - Find tokens

## Data Source

Powered by [PRISM API](https://prismapi.ai) - aggregated from 50+ exchanges.
