# API Endpoints Reference

## Finnhub (US Stocks)
- Quote: `GET https://finnhub.io/api/v1/quote?symbol={sym}&token={key}`
- Company News: `GET https://finnhub.io/api/v1/company-news?symbol={sym}&from={date}&to={date}&token={key}`
- Company Profile: `GET https://finnhub.io/api/v1/stock/profile2?symbol={sym}&token={key}`
- Rate limit: 60 calls/minute

## Binance (Crypto)
- 24hr Ticker: `GET https://api.binance.com/api/v3/ticker/24hr?symbol={pair}`
- Price: `GET https://api.binance.com/api/v3/ticker/price?symbol={pair}`
- Klines: `GET https://api.binance.com/api/v3/klines?symbol={pair}&interval={int}&limit={n}`
- Rate limit: 1200 requests/minute

## CoinGecko (Crypto TRY)
- Simple Price: `GET https://api.coingecko.com/api/v3/simple/price?ids={id}&vs_currencies=try,usd`
- Rate limit: 10-30 calls/minute (free tier)

## ExchangeRate-API (Forex)
- Pair: `GET https://v6.exchangerate-api.com/v6/{key}/pair/{base}/{target}`
- Latest: `GET https://v6.exchangerate-api.com/v6/{key}/latest/{base}`
- Free alt: `GET https://open.er-api.com/v6/latest/{base}`

## yfinance (Fallback)
- Python library, no direct HTTP endpoints
- BIST stocks use `.IS` suffix (e.g., THYAO.IS)

## FRED (Macro)
- Series: `GET https://api.stlouisfed.org/fred/series/observations?series_id={id}&api_key={key}&file_type=json`
- Rate limit: 120 requests/minute

## Alpha Vantage (Sentiment)
- News Sentiment: `GET https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={sym}&apikey={key}`
- Rate limit: 5 calls/minute

## FMP (Earnings)
- Earnings Calendar: `GET https://financialmodelingprep.com/api/v3/earning_calendar?apikey={key}`
- Rate limit: 250 calls/day
