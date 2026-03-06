# PRISM OS SDK — What's Actually Here

> Grounded in the real PRISM API v4.0.0 (218 endpoints)
> Every method below maps 1:1 to a live endpoint at api.prismapi.ai

---

## The Real Coverage Map

```
┌──────────────────────────────────────────────────────────────────┐
│                    PRISM OS — 218 Real Endpoints                 │
├─────────────────┬────────────────────┬──────────────────────────-┤
│  STOCKS (20)    │  CRYPTO (10)       │  MACRO (14)               │
│  DEFI (8)       │  ONCHAIN (7)       │  TECHNICALS (5)           │
│  SIGNALS (5)    │  RISK (3)          │  SOCIAL (5)               │
│  HISTORICAL (6) │  PREDICTIONS (15)  │  SPORTS/ODDS (13)         │
│  MARKET (7)     │  VALUATION (3)     │  NEWS (3)                 │
│  CALENDAR (3)   │  ETFs (3)          │  INDEXES (6)              │
│  FOREX (3)      │  COMMODITIES (3)   │  DEX (7)                  │
│  RESOLUTION (4) │  ANALYSIS (7)      │  ORDERBOOK (4)            │
│  UNIVERSE (6)   │  BATCH (6)         │  AGENT (4)                │
│  CONVERT (1)    │  SECTORS (1)       │  BENCHMARKS (1)           │
└─────────────────┴────────────────────┴──────────────────────────-┘
```

---

## Module Reference (All Real)

### `prism.stocks` — 20 endpoints
*Equity analysts, portfolio managers, retail traders*

```typescript
// Quotes & Price
prism.stocks.getQuote('AAPL')
prism.stocks.getBatchQuotes(['AAPL', 'MSFT', 'NVDA'])
prism.stocks.getSparkline('AAPL', 30)
prism.stocks.getBatchSparklines(['AAPL', 'MSFT'])

// Fundamentals & Financials
prism.stocks.getProfile('AAPL')
prism.stocks.getFundamentals('AAPL')
prism.stocks.getFinancials('AAPL', 'income', 'annual')     // income | balance | cash-flow
prism.stocks.getValuationRatios('AAPL')                    // P/E, EV/EBITDA, P/B, P/S
prism.stocks.getDCF('AAPL', { growthRate: 0.08 })

// Earnings & Events
prism.stocks.getEarnings('AAPL', 8)
prism.stocks.getAnalystRatings('AAPL')
prism.stocks.getFilings('AAPL', '10-K')

// Corporate Activity
prism.stocks.getDividends('AAPL')
prism.stocks.getSplits('AAPL')
prism.stocks.getInsiders('AAPL')
prism.stocks.getInstitutional('AAPL')
prism.stocks.getPeers('AAPL')

// Market Movers
prism.stocks.getGainers()
prism.stocks.getLosers()
prism.stocks.getMostActive()
prism.stocks.getMultiDayMovers(3)

// News
prism.news.getStocks('AAPL')
prism.news.getStocksBatch(['AAPL', 'MSFT', 'NVDA'])
```

---

### `prism.etfs` — 3 endpoints
*ETF investors, asset allocators*

```typescript
prism.etfs.getPopular()                        // SPY, QQQ, VTI, etc.
prism.etfs.getHoldings('QQQ')                  // Top holdings
prism.etfs.getSectorWeights('SPY')             // Sector breakdown
```

---

### `prism.indexes` — 6 endpoints
*Benchmark tracking, index analysis*

```typescript
prism.stocks.getIndexes()                      // All major indexes
prism.stocks.getSP500()                        // All 500 constituents
prism.stocks.getNASDAQ100()                    // All 100 constituents
prism.stocks.getDOW30()                        // 30 DJIA stocks
prism.stocks.getCryptoIndex()                  // Crypto market index
prism.stocks.getDeFiIndex()                    // DeFi index
prism.stocks.getSectors()                      // Sector performance
```

---

### `prism.macro` — 14 endpoints
*Macro traders, economists, fixed income investors*

```typescript
// US Economic Indicators (FRED-backed)
prism.macro.getFedRate()                       // Federal funds rate + history
prism.macro.getInflation()                     // CPI, PCE, core measures
prism.macro.getGDP()                           // GDP growth + components
prism.macro.getUnemployment()                  // Unemployment rate + claims
prism.macro.getTreasuryYields()                // Full yield curve (2yr–30yr)
prism.macro.getM2Supply()                      // M2 money supply
prism.macro.getHousing()                       // Housing starts, permits, prices
prism.macro.getConsumer()                      // Consumer confidence, spending
prism.macro.getIndustrial()                    // Industrial production
prism.macro.getJoblessClaims()                 // Initial + continuing claims
prism.macro.getMarketIndicators()              // VIX, credit spreads, dollar index

// Summary & Custom FRED Series
prism.macro.getSummary()                       // All macro in one call
prism.macro.getAvailableSeries()               // All FRED series available
prism.macro.getFREDSeries('FEDFUNDS', 24)      // Any FRED series by ID
```

---

### `prism.forex` — 3 endpoints
*FX traders, multinationals, international investors*

```typescript
prism.forex.getAll()                           // All major FX pairs (live)
prism.forex.getTradeableForms('EUR')           // ETFs, futures that track EUR
prism.forex.getTechnicals('EURUSD', 'daily')   // RSI, MACD, trend for FX pair
```

> Note: Spot rates + technicals only. No forwards, options, or vol surface.

---

### `prism.commodities` — 3 endpoints
*Commodity traders, energy companies, agricultural businesses*

```typescript
prism.commodities.getAll()                     // Gold, silver, oil, gas, etc.
prism.commodities.getTradeableForms('GOLD')    // GLD, IAU, GOLD ETFs + futures
prism.commodities.getTechnicals('GCUSD', '4h') // Technical analysis for gold
```

> Note: Spot prices + technicals only. No futures chains, storage data, or rig counts.

---

### `prism.historical` — 6 endpoints
*Works across ALL asset classes: stocks, crypto, forex, commodities*

```typescript
prism.historical.getPrices('AAPL', { days: 365, interval: 'daily' })
prism.historical.getVolume('BTC', { days: 90 })
prism.historical.getMetrics('ETH', { days: 30 })          // P/E, market cap over time
prism.historical.getReturns('SPY', ['1d', '1w', '1m', '3m', '1y'])
prism.historical.getVolatility('NVDA', 30)                // 30-day realized vol
prism.historical.compare(['BTC', 'ETH', 'SOL', 'SPY'], 90, 'price')
```

---

### `prism.technicals` — 5 endpoints
*Cross-asset: stocks, crypto, forex, commodities all work*

```typescript
prism.technicals.getFull('AAPL', 'daily')
prism.technicals.getIndicators('NVDA', 'rsi,macd,bb', 'daily', 14)
prism.technicals.getSupportResistance('BTC', 'weekly')
prism.technicals.getTrend('ETH', '4h')
prism.technicals.getBatch(['AAPL', 'MSFT', 'BTC', 'EURUSD'])
```

---

### `prism.signals` — 5 endpoints
*Signal generators for any asset: stocks, crypto, forex, commodities*

```typescript
prism.signals.getMomentum({ symbols: ['AAPL', 'NVDA', 'BTC'] })
prism.signals.getVolumeSpike({ symbols: ['TSLA', 'GME'], spikeThreshold: 3 })
prism.signals.getBreakout({ symbols: ['AAPL', 'ETH'], lookback: 20 })
prism.signals.getDivergence({ symbols: ['SPY', 'QQQ'] })
prism.signals.getSummary({ symbols: ['AAPL', 'BTC', 'EURUSD'] })
```

---

### `prism.risk` — 3 endpoints
*Portfolio managers, risk officers — cross-asset*

```typescript
prism.risk.getMetrics('NVDA', { assetType: 'stock', period: 90 })
prism.risk.getVaR('BTC', { confidence: 0.95, positionSize: 100000 })
prism.risk.analyzePortfolio([
  { symbol: 'AAPL', weight: 0.3, assetType: 'stock' },
  { symbol: 'BTC',  weight: 0.3, assetType: 'crypto' },
  { symbol: 'GLD',  weight: 0.2, assetType: 'etf' },
  { symbol: 'SPY',  weight: 0.2, assetType: 'etf' },
])
```

---

### `prism.market` — 7 endpoints
*Macro + sentiment overview*

```typescript
prism.market.getOverview()                     // Global market snapshot
prism.market.getFearGreed()                    // Fear & greed index
prism.market.getCorrelations(['BTC','ETH','SPY','GLD'], 30)
prism.market.getCryptoGainers()
prism.market.getCryptoLosers()
```

---

### `prism.valuation` — 3 endpoints
*Equity analysts, crypto investors*

```typescript
prism.stocks.getValuationRatios('AAPL')        // P/E, EV/EBITDA, etc.
prism.stocks.getDCF('AAPL', { growthRate: 0.1, discountRate: 0.1 })
prism.crypto.getNVT('BTC')                     // Network Value to Transactions
```

---

### `prism.calendar` — 3 endpoints
*Event-driven traders, analysts*

```typescript
prism.calendar.getEarnings('2025-01-01', '2025-01-31')
prism.calendar.getEarningsThisWeek()
prism.calendar.getEconomic('2025-01-01', '2025-01-31')
```

---

### `prism.crypto` — 10 endpoints
*Crypto traders, DeFi users*

```typescript
prism.crypto.getPrice('BTC')                   // Consensus price (multi-exchange)
prism.crypto.getPrices(['BTC', 'ETH', 'SOL'])  // Batch consensus prices
prism.crypto.getGlobal()                       // Total market cap, dominance, etc.
prism.crypto.getTrending()                     // Trending by search volume
prism.crypto.getTrendingAll()                  // All sources (CG + DEX + Solana)
prism.crypto.getTrendingEVM('base')            // EVM chain trending
prism.crypto.getTrendingPools('24h')           // Trending DEX pools
prism.crypto.getSolanaBonding()                // Pump.fun bonding phase
prism.crypto.getSolanaGraduated()              // Graduated to DEX
prism.crypto.getSourcesStatus()                // Health of price sources
```

---

### `prism.defi` — 8 endpoints
*DeFi users, yield farmers, protocol analysts*

```typescript
prism.defi.getTotalTVL()
prism.defi.getChainTVLs()
prism.defi.getProtocolTVL('uniswap')
prism.defi.getProtocols({ category: 'DEX', chain: 'ethereum' })
prism.defi.checkProtocol('UNI')                // Is this token a known protocol?
prism.defi.getYields({ chain: 'ethereum', minApy: 5, stablecoin: true })
prism.defi.getStablecoins()
prism.defi.getBridges()
```

---

### `prism.dex` — 7 endpoints
*Perp traders, funding rate arb, DEX data*

```typescript
prism.defi.getDEXInfo()
prism.defi.getAllPairs()
prism.defi.getDEXPairs('hyperliquid')
prism.defi.getFundingRate('hyperliquid', 'BTC')
prism.defi.getOpenInterest('hyperliquid', 'ETH')
prism.defi.getFundingRatesAll('BTC')           // Across all DEXes
prism.defi.getOpenInterestAll('ETH')           // Across all DEXes
```

---

### `prism.onchain` — 7 endpoints
*Blockchain analysts, whale watchers*

```typescript
prism.onchain.getTopHolders('0xdAC17F9...', 'eth')
prism.onchain.getHolderDistribution('0xdAC17F9...', 'eth')
prism.onchain.getSupply('ETH')
prism.onchain.getActiveAddresses('BTC')
prism.onchain.getTransactionCount('ETH')
prism.onchain.getWhaleMovements({ address: '0x...', minValueUsd: 500000 })
prism.onchain.getExchangeFlows('BTC', '0x...', 'eth', '24h')
```

---

### `prism.predictions` — 15 endpoints
*Prediction market traders, event analysts*

```typescript
prism.predictions.getMarkets({ category: 'crypto', sort: 'volume' })
prism.predictions.searchMarkets('bitcoin ETF')
prism.predictions.getTrending()
prism.predictions.getMarket('market_id')
prism.predictions.getOdds('market_id')
prism.predictions.getOrderbook('market_id')
prism.predictions.getPrice('market_id')
prism.predictions.getHistory('market_id')
prism.predictions.getCandlesticks('market_id', { interval: '1h' })
prism.predictions.getLinkedMarkets('market_id')
prism.predictions.getTradeHistory('market_id')
prism.predictions.getArbitrage({ minProfit: 2 })
prism.predictions.getCategories()
prism.predictions.getEvents({ category: 'politics' })
prism.predictions.resolveQuery('Who will win the 2026 midterms?')
```

---

### `prism.sports` + `prism.odds` — 13 endpoints
*Sports bettors, arbitrage hunters*

```typescript
prism.sports.list()
prism.sports.getEvents('basketball_nba', { daysAhead: 7 })
prism.sports.getEvent('event_id')
prism.sports.getEventOdds('event_id', 'h2h')
prism.sports.search('Lakers vs Celtics')
prism.sports.resolve('Who plays tonight in the NBA?')
prism.sports.getSportsbooks()
prism.odds.findArbitrage({ minProfitPct: 1.5 })
prism.odds.getEventArbitrage('event_id')
prism.odds.getBest({ sport: 'basketball_nba' })
prism.odds.compare('event_id', 'h2h')
prism.odds.getHistory('market_id', { interval: '1h', days: 7 })
prism.odds.getPlatforms()
```

---

### `prism.social` — 5 endpoints
*Sentiment traders, social analysts*

```typescript
prism.social.getSentiment('BTC')
prism.social.getMentions('ETH')
prism.social.getTrendingScore('DOGE')
prism.social.getTrending()
prism.social.getGitHubActivity('ETH')           // Commits, contributors, stars
```

---

### `prism.resolve` — 4 endpoints
*The canonical ID layer — any identifier → PRISM asset*

```typescript
prism.resolve.symbol('BTC', { expand: 'venues' })
prism.resolve.batch(['ETH', 'ethereum', '0xC02aaa...'])
prism.resolve.family('bitcoin')
prism.resolve.venues('USDC', { chain: 'ethereum' })
```

---

### `prism.analysis` — 7 endpoints
*Token intelligence: is this legit?*

```typescript
prism.analysis.analyze('PEPE')                 // Full: fork + bridge + copycat + rebrand
prism.analysis.batch(['wstETH', 'MATIC', 'BCH'])
prism.analysis.checkBridge('USDC', { chain: 'arbitrum' })
prism.analysis.checkCopycat('SHIB')
prism.analysis.checkFork('BCH')
prism.analysis.checkRebrand('MATIC')
prism.analysis.getDerivation('wstETH')         // stETH → wstETH derivation chain
```

---

### `prism.news` — 3 endpoints

```typescript
prism.news.getCrypto(30)
prism.news.getStocks('AAPL')
prism.news.getStocksBatch(['AAPL', 'MSFT', 'NVDA'], 3)
```

---

### Other Real Endpoints

```typescript
// Conversion
prism.convert('BTC', 'USD', 0.5)               // Any crypto or fiat

// Order book (crypto)
prism.orderbook.get('BTC', { levels: 20 })
prism.orderbook.getDepth('ETH', 50)
prism.orderbook.getSpread('BTC')
prism.orderbook.getImbalance('ETH')

// Trades
prism.trades.getRecent('BTC', 100)
prism.trades.getLarge('AAPL', { minValue: 100000 })

// Wallets
prism.onchain.getWalletBalances('0x...', { chain: 'eth', excludeSpam: true })
prism.onchain.getWalletNative('0x...', 'eth')

// Pools (DEX liquidity pools)
prism.defi.getPoolOHLCV('0xpool...', 'eth', '1h', 100)
prism.defi.getPoolPairs('0xtoken...', 'eth')

// Analytics (Solana / contract-level)
prism.onchain.getBondingStatus('pumpfun_address')
prism.onchain.getHolderStats('0xtoken...', 'eth')
prism.onchain.getOnchainPrice('0xtoken...', 'base')

// Gas
prism.defi.getGasAll()
prism.defi.getGas('ethereum')

// Chains
prism.resolve.getChains()

// Contracts
prism.resolve.getContract('ethereum', '0xdAC17...')

// Benchmarks
prism.historical.compareVsBenchmark('AAPL', 'SPY', 90)

// Universe browsing
prism.universe.getCrypto({ orderBy: 'market_cap', limit: 100 })
prism.universe.getStocks({ exchange: 'NASDAQ' })
prism.universe.getETFs()
prism.universe.getIndexes()
prism.universe.search('apple', { type: 'stock' })
prism.universe.getStats()

// Agent tools (for AI agents calling PRISM)
prism.agent.getContext()                       // Market summary for LLM context
prism.agent.getEndpoints()                     // Categorized endpoint list
prism.agent.getSchemas()                       // OpenAPI schemas for agents
prism.agent.resolve(['BTC', 'AAPL', 'gold'])   // Batch resolve for agents
```

---

## What PRISM Does NOT Have (Yet)

Being honest about coverage gaps:

| Vertical | Status |
|----------|--------|
| Real estate | ❌ No endpoints |
| Bond pricing (CUSIP/OAS/DV01) | ❌ Only treasury yields |
| FX derivatives (forwards, options, vol) | ❌ Spot quotes only |
| Commodity futures chains | ❌ Spot prices only |
| Options chains (equity/index) | ❌ Not available |
| Private market / VC data | ❌ Not available |
| ESG scores | ❌ Not available |
| Insurance / actuarial | ❌ Not available |
| Personal finance calculators | ❌ Not available |

---

## Cross-Asset Power: What Makes This Different

The same tools work across ALL asset classes:

```typescript
// Technicals work on EVERYTHING
prism.technicals.getFull('AAPL')      // Stock
prism.technicals.getFull('BTC')       // Crypto
prism.technicals.getFull('EURUSD')    // Forex pair
prism.technicals.getFull('GCUSD')     // Gold

// Signals work on EVERYTHING
prism.signals.getMomentum({ symbols: ['AAPL', 'BTC', 'EURUSD', 'GCUSD'] })

// Risk works on EVERYTHING
prism.risk.getMetrics('SPY')          // ETF
prism.risk.getMetrics('ETH')          // Crypto
prism.risk.analyzePortfolio([...])    // Mixed portfolio

// Historical works on EVERYTHING
prism.historical.compare(['SPY', 'BTC', 'GLD', 'EURUSD'], 365)
```

## Agent × Module Matrix

| Agent Type | Primary Modules |
|-----------|----------------|
| Equity analyst | stocks, calendar, news, signals, technicals |
| Macro trader | macro, market, historical, forex, commodities |
| Crypto trader | crypto, defi, dex, onchain, social, predictions |
| DeFi yield farmer | defi, onchain, wallets |
| Quant/systematic | signals, technicals, risk, historical |
| Prediction market trader | predictions, sports, odds |
| Multi-asset PM | stocks, etfs, crypto, macro, risk, historical |
| NFT/token analyst | analysis, onchain, social, resolve |
| News trader | news, calendar, social, signals |
