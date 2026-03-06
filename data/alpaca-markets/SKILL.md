---
name: alpaca
description: This skill provides integration with the Alpaca Markets API for trading stocks, options, and cryptocurrencies. Use it when you need to interact with Alpaca's brokerage services programmatically, such as placing orders, fetching account data, managing positions, or retrieving market data for automated trading or portfolio management.
homepage: https://clawhub.ai/oscraters/alpaca-markets
metadata:
  openclaw:
    requires:
      env:
        - ALPACA_API_KEY
        - ALPACA_API_SECRET
      optionalEnv:
        - ALPACA_BASE_URL
      primaryEnv:
        - ALPACA_API_KEY
        - ALPACA_API_SECRET
      sourceRepository: https://github.com/oscraters/alpaca-markets-skill.git
      distributionPlatform: clawhub
      distributionUrl: https://clawhub.ai/oscraters/alpaca-markets
---

# Alpaca

## Overview

This skill enables programmatic access to Alpaca Markets for automated trading, portfolio management, and market data retrieval via their REST API. It supports both live and paper trading accounts for stocks, options, and crypto.

## Quick Start

### Authentication
To use the Alpaca API, you need an API key and secret. Obtain these from your Alpaca account dashboard.
- Paper trading: `https://paper-api.alpaca.markets`
- Live trading: `https://api.alpaca.markets`

Set environment variables:

- `ALPACA_API_KEY`
- `ALPACA_API_SECRET`
- `ALPACA_BASE_URL` (optional; defaults to paper trading URL)

### Security / Credential Use

- Use paper trading credentials by default.
- Do not use live trading credentials until you have audited the code path you plan to run.
- Keep `ALPACA_BASE_URL` unset unless you intentionally need a non-default environment.
- Consider running the helper scripts in an isolated container or VM during evaluation.

### Example Usage
- Place a stock or crypto order: `POST /v2/orders`
- Fetch account balance: `GET /v2/account`
- Get positions (stocks/options/crypto): `GET /v2/positions`
- List orders: `GET /v2/orders`

## API Operations

### Trading API
- **Get Account**: `GET /v2/account`
- **Place Order**: `POST /v2/orders` (stocks, options, crypto)
- **List Orders**: `GET /v2/orders`
- **Get Order**: `GET /v2/orders/{order_id}`
- **Replace Order**: `PATCH /v2/orders/{order_id}`
- **Cancel Order**: `DELETE /v2/orders/{order_id}`
- **Cancel All Orders**: `DELETE /v2/orders`
- **Get Positions**: `GET /v2/positions`
- **Close Position**: `DELETE /v2/positions/{symbol}`
- **Close All Positions**: `DELETE /v2/positions`
- **Get Assets**: `GET /v2/assets`

### Market Data
- Use Alpaca Market Data API endpoints for crypto quotes and bars (see `references/api_reference.md`).

## Included Files
- `scripts/alpaca_api.py`: command-line helper for calling Alpaca endpoints with robust error handling and exit codes.
- `scripts/example.py`: sample script showing account and order calls.
- `agents/openai.yaml`: Clawhub/OpenClaw interface manifest for display name and default prompt metadata.
- `references/api_reference.md`: concise endpoint reference and payload examples.
