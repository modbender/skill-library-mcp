---
name: ibkr
aliases:
  - openclaw
  - openclaw-ibkr
description: Comprehensive Interactive Brokers (IBKR) TWS/Gateway skill using ib_insync. Includes Python and bash CLIs for account, market data, historical data, contract lookup, scanners, and order lifecycle management.
---

# IBKR Skill

## Overview

This skill integrates with Interactive Brokers Trader Workstation (TWS) and IB Gateway through `ib_insync`, exposing operational IBKR workflows through:

- A unified Python CLI: `scripts/ibkr_cli.py`
- A bash CLI wrapper: `scripts/ibkr.sh`
- Compatibility alias: `scripts/openclaw.sh`
- Backward-compatible script entrypoints:
  - `scripts/get_account_info.py`
  - `scripts/get_historical_data.py`
  - `scripts/place_order.py`

## Prerequisites

- Interactive Brokers account with API permissions.
- TWS or IB Gateway running with API enabled.
- Python 3.9+ recommended.
- `ib_insync` installed:

```bash
pip install ib_insync
```

## Connection Configuration

All CLIs support connection overrides using flags or env vars.

Environment variables:

- `IBKR_HOST` (default `127.0.0.1`)
- `IBKR_PORT` (default `7497`)
- `IBKR_CLIENT_ID` (default `1`)
- `IBKR_ACCOUNT` (optional)

Examples:

```bash
IBKR_PORT=4002 IBKR_CLIENT_ID=14 ./scripts/ibkr.sh account-summary
python3 scripts/ibkr_cli.py positions --host 127.0.0.1 --port 7496 --account DU123456
```

## Bash CLI

`./scripts/ibkr.sh <command> [args]`

Supported commands:

- `account` (account summary + positions)
- `account-summary`
- `positions`
- `portfolio`
- `pnl`
- `quote`
- `historical`
- `place-order`
- `cancel-order`
- `open-orders`
- `executions`
- `contract-details`
- `scanner`

`./scripts/openclaw.sh` is an alias to the same CLI surface.

## Python CLI

`python3 scripts/ibkr_cli.py <command> [args]`

### Account Services

```bash
python3 scripts/ibkr_cli.py account-summary --json
python3 scripts/ibkr_cli.py positions --account DU123456
python3 scripts/ibkr_cli.py portfolio --json
python3 scripts/ibkr_cli.py pnl --account DU123456 --wait 2
```

### Market Data Services

```bash
python3 scripts/ibkr_cli.py quote --symbol AAPL --sec-type STK --market-data-type 3
python3 scripts/ibkr_cli.py historical --symbol EURUSD --sec-type CASH --duration "30 D" --bar-size "1 hour"
```

Notes:

- Historical requests support full IB-format values via flags, including spaced tokens like `"30 D"`.
- For `CASH`, default `whatToShow` is `MIDPOINT` unless explicitly overridden.

### Contract Discovery

```bash
python3 scripts/ibkr_cli.py contract-details --symbol ES --sec-type FUT --expiry 202606
```

### Trading and Order Lifecycle

```bash
python3 scripts/ibkr_cli.py place-order --symbol AAPL --sec-type STK --action BUY --quantity 10 --order-type MKT
python3 scripts/ibkr_cli.py place-order --symbol AAPL --sec-type STK --action SELL --quantity 10 --order-type LMT --limit-price 250 --tif GTC
python3 scripts/ibkr_cli.py open-orders
python3 scripts/ibkr_cli.py cancel-order --order-id 12345
python3 scripts/ibkr_cli.py executions --json
```

Supported order types in the CLI:

- `MKT`
- `LMT`
- `STP`
- `STP LMT`

`place-order` waits for status updates and surfaces API errors collected during placement.

### Scanner Service

```bash
python3 scripts/ibkr_cli.py scanner --instrument STK --location-code STK.US.MAJOR --scan-code TOP_PERC_GAIN --rows 25
```

## Compatibility Scripts

Legacy scripts remain supported and now delegate to the unified CLI:

- `get_account_info.py`
- `get_historical_data.py` (legacy positional mode still works)
- `place_order.py` (legacy positional mode still works)

## Error Handling

The CLI returns non-zero exit codes for:

- Import/dependency failures
- Connection failures
- Contract qualification failures
- Invalid arguments
- Missing open order for cancellation

## References

See `references/api_reference.md` for IBKR and ib_insync documentation links.
