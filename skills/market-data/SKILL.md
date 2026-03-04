# Market Data Skill

This skill provides access to financial market data.

## Tools

### `get_stock_price`

Fetches OHLCV (Open, High, Low, Close, Volume) data for a specific ticker.

**Parameters:**

- `ticker` (string): The stock symbol (e.g., "AAPL", "BTC-USD").
- `timeframe` (string): The data interval. Supported: '1d', '1wk', '1mo'. Default: '1d'.
- `period1` (string, optional): Start date in YYYY-MM-DD format. Defaults to 30 days ago.
- `period2` (string, optional): End date in YYYY-MM-DD format. Defaults to today.

**Usage:**

Use this tool when the user asks for stock prices, historical data, chart data, or recent performance of a specific asset.

**Examples:**

- "Get daily data for Apple." -> `get_stock_price({ ticker: 'AAPL', timeframe: '1d' })`
- "Show me Bitcoin's weekly chart for the last year." -> `get_stock_price({ ticker: 'BTC-USD', timeframe: '1wk', period1: '2023-01-01' })`

### `get_crypto_price`

Fetches current price and 24h volatility data for a crypto token.

**Parameters:**

- `token` (string): The token name or ID (e.g., "bitcoin", "solana", "ethereum").
- `currency` (string, optional): Target currency. Default: "usd".

**Usage:**

Use this for checking crypto prices, volatility, and 24h changes.

**Examples:**

- "Price of Solana?" -> `get_crypto_price({ token: 'solana' })`
- "How is Bitcoin doing?" -> `get_crypto_price({ token: 'bitcoin' })`

### `fetch_economic_calendar`

Fetches upcoming high-impact economic events (e.g., CPI, FOMC, GDP).

**Parameters:**

- `importance` (string, optional): Impact level filter. 'High', 'Medium', 'Low', 'All'. Default: 'High'.
- `currencies` (string, optional): Comma-separated currency codes (e.g., 'USD,EUR'). Default: All.

**Usage:**

Use this to check for market-moving news or schedule risk.

**Examples:**

- "Any high impact news this week?" -> `fetch_economic_calendar({ importance: 'High' })`
- "Check USD and EUR calendar." -> `fetch_economic_calendar({ currencies: 'USD,EUR' })`

### `get_news_headlines`

Fetches the latest 50 news headlines for a specific asset or topic.

**Parameters:**

- `query` (string): The search topic (e.g., "Apple Stock", "Bitcoin Regulation", "Nvidia Earnings").

**Usage:**

Use this for sentiment analysis and staying updated on market narratives.

**Examples:**

- "Any news on Tesla?" -> `get_news_headlines({ query: 'Tesla Stock' })`
- "Latest crypto regulation updates?" -> `get_news_headlines({ query: 'Crypto Regulation' })`
