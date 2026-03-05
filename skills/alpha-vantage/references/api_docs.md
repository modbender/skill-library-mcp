# Alpha Vantage API Reference (Operational Summary)

Source of truth: https://www.alphavantage.co/documentation/

## Base Request Pattern

- Base URL: `https://www.alphavantage.co/query`
- Common parameters:
  - `function` (required)
  - `apikey` (required)
  - Function-specific parameters (`symbol`, `interval`, `outputsize`, etc.)

Example:

```text
https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=IBM&apikey=YOUR_API_KEY
```

## Auth and Access

- Get API key: https://www.alphavantage.co/support/#api-key
- Premium tiers and throughput: https://www.alphavantage.co/premium/
- Terms for public/commercial usage: https://www.alphavantage.co/terms_of_service/

## Response Guardrails

Handle these response classes in every integration:

1. HTTP error (non-2xx)
2. JSON payload with `Error Message`
3. JSON payload with `Note` (throttle/limit conditions)
4. Empty payload or missing expected keys

## Endpoint Families

## 1) Time Series (Equities/ETFs)

- `TIME_SERIES_INTRADAY`
  - Required: `symbol`, `interval`
  - Useful options: `adjusted`, `extended_hours`, `month`, `outputsize`, `datatype`
- `TIME_SERIES_DAILY`
- `TIME_SERIES_DAILY_ADJUSTED`
- `TIME_SERIES_WEEKLY`
- `TIME_SERIES_WEEKLY_ADJUSTED`
- `TIME_SERIES_MONTHLY`
- `TIME_SERIES_MONTHLY_ADJUSTED`

## 2) Technical Indicators

Examples:

- `SMA`, `EMA`, `RSI`, `MACD`, `ADX`, `BBANDS`, `STOCH`, `ATR`, `OBV`

Typical required parameters:

- `symbol`
- `interval`
- `time_period` (for many indicators)
- `series_type` (`open|high|low|close`) where applicable

## 3) Fundamental Data

- `OVERVIEW`
- `INCOME_STATEMENT`
- `BALANCE_SHEET`
- `CASH_FLOW`
- `EARNINGS`
- `LISTING_STATUS`
- `EARNINGS_CALENDAR`
- `IPO_CALENDAR`

## 4) FX, Crypto, Commodities, Macro

- FX:
  - `FX_INTRADAY`, `FX_DAILY`, `FX_WEEKLY`, `FX_MONTHLY`
  - Often requires `from_symbol`, `to_symbol`
- Crypto:
  - `CRYPTO_INTRADAY`, `DIGITAL_CURRENCY_DAILY`, `DIGITAL_CURRENCY_WEEKLY`, `DIGITAL_CURRENCY_MONTHLY`
- Commodities and macro datasets:
  - See the docs catalog for currently available functions and required params.

## 5) Search and Intelligence

- `SYMBOL_SEARCH`
- `NEWS_SENTIMENT`
- `TOP_GAINERS_LOSERS`

## Parsing Notes

- Numeric values are commonly encoded as strings.
- Keys and section names differ by function; do not assume one fixed schema.
- Preserve metadata section (`Meta Data`, timestamps, timezone) for auditability.

## Suggested Call Strategy for Production

1. Build a typed request object per function family.
2. Validate required params before request dispatch.
3. Execute request with timeout + retry/backoff on `Note`.
4. Normalize raw payload into a stable internal schema.
5. Log request id/function and retry count (never log full API key).
