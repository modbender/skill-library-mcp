# Price

Token prices in USD (e.g. for display, billing, or workflow logic). **No auth required** — both endpoints are public.

| Method | Endpoint | Description | Response |
|--------|----------|-------------|----------|
| GET | `/price` | One token price in USD | `TokenPriceResponse` |
| GET | `/price/prices` | BNB and ETH prices in USD | `TokenPricesResponse` |

**GET /price**

Query: `symbol` (optional, string). Token symbol, e.g. `BNB`, `ETH`, `BTC`. Default `BNB`.

**Response (200):** `TokenPriceResponse` — `{ symbol: string, priceUsd: string }`. Uses cached CoinMarketCap; returns `priceUsd: "0"` on failure.

**GET /price/prices**

No query or body.

**Response (200):** `TokenPricesResponse` — `{ BNB: string, ETH: string }`. USD prices as strings. Used by builder/billing UIs.
