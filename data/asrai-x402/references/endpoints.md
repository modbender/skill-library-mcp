# Asrai x402 Endpoints

## Base URL
`https://x402.asrai.me`

## Payment
x402 automatic — $0.005 USDC per endpoint on Base mainnet ($0.01 for `/ai`)

## Endpoint Catalog

### Market Pulse
- `GET /api/trending/` — trending coins
- `GET /api/gainers-losers/` — top gainers and losers
- `GET /api/rsi/` — RSI extremes (overbought/oversold)
- `GET /api/top-bottom/` — top/bottom signals
- `GET /api/ath/` — coins near all-time high
- `GET /api/channel-summary/` — latest narratives from monitored channels

### Sentiment
- `GET /api/cbbi/` — Bitcoin cycle index
- `GET /api/cmc-sentiment/` — CMC market sentiment
- `GET /api/cmcai/` — CMC AI insights
- `GET /api/cmcai/<symbol>` — CMC AI for specific coin

### Technical Signals (single coin)
- `GET /api/signal/<symbol>usdt/1D|4H|1W` — buy/sell signal
- `GET /api/alsat/<symbol>usdt/1D|4H|1W` — ALSAT indicator
- `GET /api/superalsat/<symbol>usdt` — SuperALSAT
- `GET /api/alphatrend/<symbol>usdt/1D|4H|1W` — AlphaTrend
- `GET /api/psar/<symbol>usdt/1D|4H|1W` — Parabolic SAR
- `GET /api/macd-dema/<symbol>usdt/1D|4H|1W` — MACD + DEMA
- `GET /api/td/<symbol>usdt/1D|4H|1W` — Tom DeMark sequential
- `GET /api/ichimoku/<symbol>usdt/1D|4H|1W` — Ichimoku cloud
- `GET /api/ew/<symbol>usdt/1D|4H|1W` — Elliott Wave
- `GET /api/smartmoney/<symbol>usdt/1D|4H|1W` — SMC (order blocks, FVG, BOS)
- `GET /api/support-resistance/<symbol>usdt/1D|4H|1W` — support/resistance levels
- `GET /api/forecasting/<symbol>usdt` — AI price forecast

### Screeners
- `GET /api/ichimoku-trend/`
- `GET /api/sar-coins/`
- `GET /api/macd-coins/`
- `GET /api/emacross/`
- `GET /api/techrating/`
- `GET /api/vwap/`
- `GET /api/volume/`
- `GET /api/highvolumelowcap/`
- `GET /api/bounce-dip/`
- `GET /api/galaxyscore/`
- `GET /api/socialdominance/`
- `GET /api/late-unlocked-coins/`
- `GET /api/rsi/` — RSI heatmap
- `GET /api/ao/` — Awesome Oscillator screener

### Coin Info
- `GET /api/coinstats/<symbol>` — market cap, volume, supply
- `GET /api/info/<symbol>` — project info
- `GET /api/price/<symbol>` — current price
- `GET /api/tags/<symbol>` — coin tags/categories

### Cashflow
- `GET /api/cashflow/market` — market-wide capital flow
- `GET /api/cashflow/coin/<symbol>` — flow for one coin
- `GET /api/cashflow/group/<symbols_csv>` — flow for group of coins

### Chain / DEX
- `GET /api/dexscreener/<contract_address>` — DEX data by contract
- `GET /api/dexscreener/<chain>/<contract_address>` — DEX data by chain + contract
- `GET /api/chain/<chain>/<max_mcap>` — low-cap tokens on a chain

### Portfolio
- `GET /api/portfolio/` — full portfolio
- `GET /api/portfolio/<symbol>` — portfolio for specific coin

### AI
- `POST /ai` body: `{"message": "<question>"}` — AI analyst ($0.01)

## Macro signals
- `GET /api/signal/btc.d/1D` — BTC dominance
- `GET /api/signal/others.d/1D` — altcoin dominance
- `GET /api/signal/spx/1D` — S&P 500
- `GET /api/signal/ndq/1D` — Nasdaq
