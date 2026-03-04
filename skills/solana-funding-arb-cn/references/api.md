# API Reference

## REST Endpoints

### GET /api/rates

Returns all funding rates from all DEXes.

```json
{
  "driftRates": [...],
  "flashRates": [...],
  "gmRates": [...],
  "opportunities": [...],
  "comparison": [...],
  "stats": {
    "driftCount": 64,
    "flashCount": 19,
    "gmCount": 37,
    "commonCount": 15,
    "arbCount": 5
  },
  "lastUpdate": "2024-01-15T10:30:00Z"
}
```

### Rate Object

```typescript
interface FundingRate {
  exchange: 'Drift' | 'Flash' | 'GMTrade' | 'Zeta';
  symbol: string;           // e.g., "SOL", "BTC"
  price: number;            // Current mark price
  fundingRate: number;      // Hourly rate (decimal)
  fundingRateApy: number;   // Annualized percentage
  openInterest: number;     // USD value
  volume24h: number;        // 24h volume USD
  lastUpdated: number;      // Unix timestamp ms
}
```

### Opportunity Object

```typescript
interface ArbitrageOpportunity {
  symbol: string;
  longExchange: string;     // DEX to go long on
  shortExchange: string;    // DEX to go short on
  longRate: FundingRate;
  shortRate: FundingRate;
  spreadApy: number;        // Combined spread
  netApy: number;           // Estimated net after fees
}
```

## Programmatic Usage

```typescript
import { MultiDexAggregator } from './core/multi-dex-aggregator';

const aggregator = new MultiDexAggregator();

// Get all rates
const allRates = await aggregator.getAllRates();

// Get specific DEX
const driftRates = await aggregator.getDriftRates();
const flashRates = await aggregator.getFlashTradeRates();
const gmRates = await aggregator.getGMTradeRates();

// Find arbitrage opportunities
const opportunities = await aggregator.findCrossExchangeArbitrage(5); // top 5
```

## Data Sources

### Drift Protocol
- Endpoint: `https://mainnet-beta.api.drift.trade/contracts`
- Update frequency: Real-time
- No API key required

### Flash Trade & GMTrade
- Source: CoinGecko Derivatives API
- Endpoint: `https://api.coingecko.com/api/v3/derivatives`
- Update frequency: ~1 minute
- No API key required (rate limited)

### Zeta Markets
- Source: On-chain via SDK
- Requires: Solana RPC connection
- Update frequency: Real-time

## Webhooks (Future)

Coming soon: Configure webhooks to receive alerts when arbitrage opportunities exceed thresholds.

```json
{
  "webhook_url": "https://your-server.com/webhook",
  "min_spread_apy": 100,
  "symbols": ["SOL", "BTC", "ETH"]
}
```
