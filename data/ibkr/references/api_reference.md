# Interactive Brokers API Reference

This reference consolidates current primary docs for IBKR automation with TWS/Gateway and `ib_insync`.

## Primary Documentation

- IBKR Campus API Hub (current landing):
  - https://ibkrcampus.com/campus/ibkr-api-page/
- TWS API docs on IBKR Campus:
  - https://ibkrcampus.com/campus/ibkr-api-page/twsapi-doc/
- Legacy TWS API reference (still useful for method pages/examples):
  - https://interactivebrokers.github.io/tws-api/
- ib_insync documentation:
  - https://ib-insync.readthedocs.io/

## Core IBKR API Concepts

### Connection

- Local host is usually `127.0.0.1`.
- Common ports:
  - `7497` (TWS paper default)
  - `7496` (TWS live default)
  - `4002` (Gateway paper default)
  - `4001` (Gateway live default)
- `clientId` must be unique per active client session.

### Contracts

IBKR requires precise contract definitions. Use qualification before requests/orders.

- Stocks: `Stock(symbol, exchange, currency)`
- FX: `Forex('EURUSD')`
- Futures: `Future(symbol, expiry, exchange, currency)`
- Options: `Option(symbol, expiry, strike, right, exchange, multiplier, currency)`

Related docs:

- Contract model: https://interactivebrokers.github.io/tws-api/basic_contracts.html
- Contract details requests: https://interactivebrokers.github.io/tws-api/contract_details.html

### Market Data and Historical Bars

- Market data types: `1` live, `2` frozen, `3` delayed, `4` delayed-frozen.
- Historical bars require valid combinations of `durationStr`, `barSizeSetting`, and `whatToShow`.
- For FX (`CASH`), `MIDPOINT` is commonly used.

Related docs:

- Market data type: https://interactivebrokers.github.io/tws-api/market_data_type.html
- Historical bars: https://interactivebrokers.github.io/tws-api/historical_bars.html

### Orders

Common order families in this skill:

- Market (`MKT`)
- Limit (`LMT`)
- Stop (`STP`)
- Stop Limit (`STP LMT`)

Related docs:

- Order submission: https://interactivebrokers.github.io/tws-api/order_submission.html
- Available order types: https://interactivebrokers.github.io/tws-api/available_orders.html

### Account and Portfolio

Related docs:

- Account summary and updates: https://interactivebrokers.github.io/tws-api/account_updates.html
- PnL: https://interactivebrokers.github.io/tws-api/pnl.html
- Positions: https://interactivebrokers.github.io/tws-api/positions.html

### Scanner

Related docs:

- Market scanners: https://interactivebrokers.github.io/tws-api/market_scanners.html

## Reliability / Safety Notes

- Always test against paper trading first.
- Use explicit `--account`, `--client-id`, and `--port` when running multiple automation processes.
- Qualify contracts before data requests and order submission.
- Wait for terminal order statuses and inspect reported error codes/messages.
