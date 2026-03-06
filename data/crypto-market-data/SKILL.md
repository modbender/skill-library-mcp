---
name: Crypto & Stock Market Data (Node.js)
description: No API KEY needed for free tier. Professional-grade cryptocurrency and stock market data integration for real-time prices, company profiles, and global analytics. Powered by Node.js with zero external dependencies.
---

# Crypto & Stock Market Data Skill (Node.js)

A comprehensive suite of tools for retrieving real-time and historical cryptocurrency and stock market data. This skill interfaces with a dedicated market data server to provide high-performance, authenticated access to global financial statistics. Built entirely on Node.js standard libraries — no `npm install` required.

## Key Capabilities

| Category | Description |
| :--- | :--- |
| **Real-time Prices** | Fetch current valuations, market caps, 24h volumes, and price changes for crypto & stocks. |
| **Market Discovery** | Track trending assets and top-performing coins by market capitalization. |
| **Smart Search** | Quickly find coin IDs or stock tickers by searching names or symbols. |
| **Deep Details** | Access exhaustive asset information, from community links to company profiles. |
| **Precise Charts** | Retrieve OHLC candlestick data and historical price/volume time-series. |
| **Global Metrics** | Monitor total market capitalization and public company treasury holdings. |

## Tool Reference

| Script Name | Primary Function | Command Example |
| :--- | :--- | :--- |
| `get_crypto_price.js` | Multi-coin price fetch | `node scripts/get_crypto_price.js bitcoin` |
| `get_stock_quote.js` | Real-time stock quotes | `node scripts/get_stock_quote.js AAPL MSFT` |
| `get_company_profile.js` | Company overview | `node scripts/get_company_profile.js AAPL` |
| `search_stocks.js` | Find stock tickers | `node scripts/search_stocks.js apple` |
| `get_trending_coins.js` | 24h trending assets | `node scripts/get_trending_coins.js` |
| `get_top_coins.js` | Market leaderboards | `node scripts/get_top_coins.js --per_page=20` |
| `search_coins.js` | Asset discovery | `node scripts/search_coins.js solana` |
| `get_coin_details.js` | Comprehensive metadata | `node scripts/get_coin_details.js ethereum` |
| `get_coin_ohlc_chart.js` | Candlestick data | `node scripts/get_coin_ohlc_chart.js bitcoin` |
| `get_coin_historical_chart.js` | Time-series data | `node scripts/get_coin_historical_chart.js bitcoin` |
| `get_global_market_data.js` | Macro market stats | `node scripts/get_global_market_data.js` |
| `get_public_companies_holdings.js` | Treasury holdings | `node scripts/get_public_companies_holdings.js bitcoin` |
| `get_supported_currencies.js` | Valuation options | `node scripts/get_supported_currencies.js` |

---

## Usage Details

### 1. `get_crypto_price.js`
Fetch real-time pricing and basic market metrics for one or more cryptocurrencies.

**Syntax:**
```bash
node scripts/get_crypto_price.js <coin_id_1> [coin_id_2] ... [--currency=usd]
```

**Parameters:**
- `coin_id`: The unique identifier for the coin (e.g., `bitcoin`, `solana`).
- `--currency`: The target currency for valuation (default: `usd`).

**Example:**
```bash
node scripts/get_crypto_price.js bitcoin ethereum cardano --currency=jpy
```

---

### 2. `get_top_coins.js`
Retrieve a list of the top cryptocurrencies ranked by market capitalization.

**Syntax:**
```bash
node scripts/get_top_coins.js [--currency=usd] [--per_page=10] [--page=1] [--order=market_cap_desc]
```

**Parameters:**
- `--currency`: Valuation currency (default: `usd`).
- `--per_page`: Number of results (1-250, default: `10`).
- `--order`: Sorting logic (e.g., `market_cap_desc`, `volume_desc`).

---

### 3. `get_coin_ohlc_chart.js`
Get Open, High, Low, Close (candlestick) data for technical analysis.

**Syntax:**
```bash
node scripts/get_coin_ohlc_chart.js <coin_id> [--currency=usd] [--days=7]
```

**Allowed `days` values:** `1, 7, 14, 30, 90, 180, 365`.

| Range | Resolution |
| :--- | :--- |
| 1-2 Days | 30 Minute intervals |
| 3-30 Days | 4 Hour intervals |
| 31+ Days | 4 Day intervals |

---

### 4. `get_coin_historical_chart.js`
Retrieve detailed historical time-series data for price, market cap, and volume.

**Syntax:**
```bash
node scripts/get_coin_historical_chart.js <coin_id> [--currency=usd] [--days=30]
```

---

### 5. `get_stock_quote.js`
Fetch real-time stock prices for one or more ticker symbols.

**Syntax:**
```bash
node scripts/get_stock_quote.js <SYMBOL_1> [SYMBOL_2] ...
```

---

### 6. `get_company_profile.js`
Get a comprehensive company profile, including description, industry, and CEO.

**Syntax:**
```bash
node scripts/get_company_profile.js <SYMBOL>
```

---

## Important Guidelines

### Cryptos: Use IDs | Stocks: Use Tickers
- **Cryptocurrencies**: Always use **Coin IDs** (slugs) instead of ticker symbols (e.g., `bitcoin`, `BTC`).
- **Stocks**: Always use **Ticker Symbols** (e.g., `AAPL`, `Apple`).

Use `search_coins.js` if you are unsure of the correct ID.

### Authentication
Authentication is handled **automatically** by the internal `api_client.js`. Here is how it works simply:

- **Endpoint**: `GET https://api.igent.net/api/token`
- **Mechanism**:
    1.  **Automatic Retrieval**: The first time you use a tool, it asks the server for a temporary session token.
    2.  **Local Storage**: This token is stored in a hidden `.token` file locally so it can be reused for subsequent requests.
    3.  **Automatic Headers**: The client automatically includes this token in every request to prove you are authorized.
    4.  **Auto-Refresh**: If a token expires, the client automatically fetches a new one without you needing to do anything.

No manual API keys or configuration are required.

### Rate Limiting
While the system is robust, please avoid burst requests (more than 30 per minute) to maintain service stability for all users.

### Agent Integration
This skill is fully compatible with OpenClaw and other agents using the **AgentSkills** standard. Execute scripts directly from the `scripts/` directory.
