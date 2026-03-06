# realtime-crypto-price-api

Real-time cryptocurrency price data for Bitcoin, Ethereum, Solana, and 10,000+ tokens. Simple REST API for trading bots, dashboards, price alerts, and DeFi applications.

## Features

- **Real-time prices** - Live price data with sub-second updates
- **10,000+ tokens** - Bitcoin, Ethereum, Solana, memecoins, DeFi tokens
- **Batch queries** - Get multiple prices in one API call
- **Historical data** - OHLCV candles for charting
- **Trending coins** - Top gainers and losers
- **Search** - Find tokens by name or symbol
- **Free tier** - No API key required for basic usage

## Installation

```bash
npm install realtime-crypto-price-api
```

## Quick Start

```javascript
const { CryptoPrice } = require('realtime-crypto-price-api');

const client = new CryptoPrice();

// Get Bitcoin price
const btc = await client.getPrice('BTC');
console.log(`Bitcoin: $${btc.price}`);
// Output: Bitcoin: $69420.00

// Get multiple prices at once
const prices = await client.getPrices(['BTC', 'ETH', 'SOL']);
console.log(prices);

// Get top 10 coins by market cap
const top10 = await client.getTopCoins(10);

// Get trending gainers
const gainers = await client.getTrending('gainers');

// Get historical data for charting
const history = await client.getHistory('ETH', '1d', 30);
```

## CLI Usage

```bash
# Get single price
npx realtime-crypto-price-api BTC
# Output: BTC: $69,420.00
#         24h: +2.34%

# Get multiple prices
npx realtime-crypto-price-api batch BTC,ETH,SOL

# Top coins
npx realtime-crypto-price-api top 20

# Trending
npx realtime-crypto-price-api trending gainers

# Search
npx realtime-crypto-price-api search pepe
```

## API Reference

### `getPrice(symbol, currency?)`
Get real-time price for a single cryptocurrency.

**Returns:**
```javascript
{
  symbol: 'BTC',
  price: 69420.00,
  change24h: 1234.56,
  changePercent24h: 2.34,
  volume24h: 28000000000,
  marketCap: 1360000000000,
  timestamp: 1707912345678
}
```

### `getPrices(symbols, currency?)`
Get prices for multiple cryptocurrencies in one call.

### `getTopCoins(limit?, currency?)`
Get top cryptocurrencies ranked by market cap.

### `getTrending(direction?, limit?)`
Get trending cryptocurrencies. Direction: 'gainers' or 'losers'.

### `getHistory(symbol, interval?, limit?)`
Get historical OHLCV data. Intervals: '1h', '4h', '1d', '1w'.

### `search(query)`
Search for cryptocurrencies by name or symbol.

## Environment Variables

| Variable | Description |
|----------|-------------|
| `PRISM_API_KEY` | API key for higher rate limits |
| `PRISM_API_URL` | Custom API endpoint (optional) |

## Rate Limits

- **Free tier**: 100 requests/minute
- **Pro tier**: 1000 requests/minute
- Get your API key at [prismapi.ai](https://prismapi.ai)

## Data Sources

Aggregated from 50+ exchanges including Binance, Coinbase, Kraken, and major DEXs. Prices are volume-weighted for accuracy.

## License

MIT
