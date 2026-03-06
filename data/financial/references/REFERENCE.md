# YFinance-AI Technical Reference

## Overview

YFinance-AI provides 56+ financial data tools for fetching real-time market data, company fundamentals, analyst ratings, and historical trends from Yahoo Finance.

## Architecture

### Main Class: Tools
The `Tools` class implements the OpenClaw/OpenWebUI skill interface with:
- **Valves**: Configuration parameters
- **56+ async methods**: Individual tools for different data types
- **Rate limiting**: 100 calls per 60 seconds
- **Error handling**: Retry logic with exponential backoff

### Key Dependencies
- `yfinance>=0.2.66` - Yahoo Finance data access
- `pandas>=2.2.0` - Data processing and formatting
- `pydantic>=2.0.0` - Input validation
- `requests>=2.28.0` - HTTP utilities

## Tool Categories

### Real-Time Data (5 tools)
- `get_stock_price` - Current price and metrics
- `get_stock_quote` - Detailed real-time quote
- `get_fast_info` - Quick key metrics
- `get_historical_data` - Historical prices
- `get_isin` - ISIN identifier lookup

### Company Data (2 tools)
- `get_company_info` - Company profile
- `get_company_officers` - Executive team

### Financial Statements (3 tools)
- `get_income_statement` - P&L statements
- `get_balance_sheet` - Asset/liability data
- `get_cash_flow` - Cash flow statements

### Analysis & Ratios (5 tools)
- `get_key_ratios` - P/E, price-to-book, yields
- `get_analyst_recommendations` - Buy/hold/sell
- `get_analyst_estimates` - EPS/revenue forecasts
- `get_growth_estimates` - Growth projections
- `get_earnings_dates` - Earnings schedule

### Dividends & Actions (4 tools)
- `get_dividends` - Dividend history
- `get_stock_splits` - Split history
- `get_corporate_actions` - All corporate actions
- `get_capital_gains` - Capital gains distributions

### Earnings (4 tools)
- `get_earnings_history` - Historical EPS
- `get_earnings_calendar` - Upcoming earnings
- `get_analyst_price_targets` - Price targets
- `get_upgrades_downgrades` - Rating changes

### Ownership (6 tools)
- `get_institutional_holders` - Large institutions
- `get_major_holders` - Top shareholders
- `get_mutualfund_holders` - Fund ownership
- `get_insider_transactions` - Insider trades
- `get_insider_purchases` - Insider buys
- `get_insider_roster_holders` - Insider roster

### Options (2 tools)
- `get_options_chain` - Options data by expiry
- `get_options_expirations` - Available expiries

### News & Filings (2 tools)
- `get_stock_news` - Recent news articles
- `get_sec_filings` - 10-K, 10-Q, 8-K filings

### Market Data (3 tools)
- `get_market_indices` - Index prices/performance
- `compare_stocks` - Multi-stock comparison
- `get_sector_performance` - Sector metrics

### Crypto/Forex/Commodities (3 tools)
- `get_crypto_price` - Cryptocurrency prices
- `get_forex_rate` - Exchange rates
- `get_commodity_price` - Commodity prices

### Funds & ETFs (3 tools)
- `get_fund_overview` - Fund/ETF data
- `get_fund_holdings` - Fund positions
- `get_fund_sector_weights` - Sector allocation

### Advanced (4 tools)
- `get_peer_comparison` - Peer analysis
- `get_company_overview` - Full company summary
- `get_complete_analysis` - Comprehensive analysis
- `get_financial_summary` - Financial summary

### Bulk Operations (2 tools)
- `download_multiple_tickers` - Batch downloads
- `get_trending_tickers` - Popular tickers

### Utilities (3 tools)
- `search_ticker` - Ticker search
- `validate_ticker` - Validation
- `get_api_status` - API health check

### Testing (1 tool)
- `run_self_test` - Validation test suite

## Network Behavior

### Outbound Connections
- ONLY to Yahoo Finance API (via yfinance library)
- Rate limited: 100 calls per 60 seconds
- Automatic retry with exponential backoff
- Connection pooling and session management

### No Inbound Connections
- No listeners or servers
- No webhooks or callbacks
- No external API callbacks

## Security

### Input Validation
- All ticker symbols validated against format rules
- Period/interval parameters checked against valid lists
- Number parameters bounded

### No File System Access
- Does not read local files
- Does not write output to disk
- Does not execute arbitrary commands

### No Code Execution
- Uses only standard library + PyPI packages
- No subprocess calls
- No dynamic code evaluation

## Configuration (Valves)

Default parameters in `Tools.Valves`:
- `default_period: "1y"` - Historical data period
- `default_interval: "1d"` - Data granularity
- `enable_caching: False` - Response caching
- `max_news_items: 10` - Max news results
- `max_comparison_tickers: 10` - Max tickers in comparison
- `include_technical_indicators: False` - Technical analysis

## Error Handling

### Graceful Degradation
- Missing data fields return null/empty
- API errors trigger retry logic
- Timeout errors with clear messages
- Fallback values for unavailable data

### Common Issues
- **Rate limit**: Automatic backoff, then error message
- **Invalid ticker**: Validation error before API call
- **Timeout**: Retry up to 3 times with exponential backoff
- **No data**: Returns empty or null fields

## Testing

Built-in `run_self_test()` validates:
- All 56+ functions can be called
- No exceptions on standard inputs
- Output formatting is correct
- API connectivity works

Run via: `run_self_test()`

## Performance

- Average response time: 200-500ms per call
- Rate limit: 100 calls/60 seconds
- Memory usage: ~50MB baseline
- No persistent state between calls
