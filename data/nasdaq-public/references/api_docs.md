# Nasdaq API References

## Primary sources (official Nasdaq docs)

- Data organization and API families:
  - https://docs.data.nasdaq.com/docs/data-organization
  - Confirms available API families: Streaming API, REST API for real-time/delayed data, and REST API for tables.

- Real-time/delayed REST API rate limits:
  - https://docs.data.nasdaq.com/docs/rate-limits-for-real-timedelayed-rest-api
  - States a limit of 100 requests/second across real-time/delayed endpoints and per-endpoint symbol caps.

- Nasdaq Data Link API overview page:
  - https://www.nasdaq.com/solutions/data/nasdaq-data-link/api
  - High-level product-facing summary of available endpoint categories.

## Public screener endpoint used by this skill

- Endpoint:
  - `https://api.nasdaq.com/api/screener/stocks`

- Typical query parameters:
  - `tableonly` (`true`/`false`)
  - `limit` (page size)
  - `offset` (page start)
  - `exchange` (`NASDAQ`, `NYSE`, `AMEX`)
  - `download` (`true`/`false`)

- Expected response shape:
  - Top-level JSON with `data.rows` for records and header metadata.

## Important caveat

The screener endpoint above is publicly reachable and used by Nasdaq web experiences, but it is not documented in the same formal style as the Nasdaq Data Link docs above. Treat screener parameters and response schema as operational/public behavior that may change.

## Practical request guidance

- Send a realistic `User-Agent` and `Accept` header to reduce request blocking.
- Use pagination (`limit` + `offset`) and merge results client-side.
- Build defensive parsing for nullable fields and occasional schema drift.
