---
name: phemex-trade
description: Trade on Phemex (USDT-M futures, Coin-M futures, Spot) — place orders, manage positions, check balances, and query market data. Use when the user wants to (1) check crypto prices or market data on Phemex, (2) place, amend, or cancel orders, (3) view account balances or positions, (4) set leverage or switch position modes, (5) transfer funds between spot and futures wallets, or (6) any task involving the Phemex exchange.
homepage: https://github.com/betta2moon/phemex-trade-mcp
metadata:
  {
    "openclaw":
      {
        "emoji": "📈",
        "requires": { "bins": ["phemex-cli"], "env": ["PHEMEX_API_KEY", "PHEMEX_API_SECRET"] },
        "primaryEnv": "PHEMEX_API_KEY",
        "install":
          [
            {
              "id": "phemex-trade-mcp",
              "kind": "node",
              "package": "phemex-trade-mcp",
              "bins": ["phemex-cli"],
              "label": "Install Phemex CLI (node)",
            },
          ],
      },
  }
---

# Phemex Trading

Trade on Phemex via the phemex-cli tool. Supports USDT-M futures, Coin-M futures, and Spot markets.

## Before you start

Ensure you have the latest version installed:

```bash
npm install -g phemex-trade-mcp@latest
```

## How to call tools

```bash
phemex-cli <tool_name> --param1 value1 --param2 value2
```

Or with JSON args:

```bash
phemex-cli <tool_name> '{"param1":"value1","param2":"value2"}'
```

Output is always JSON. Environment variables `PHEMEX_API_KEY`, `PHEMEX_API_SECRET`, and `PHEMEX_API_URL` are read automatically.

## Contract types

Every tool accepts an optional `--contractType` flag:

- `linear` (default) — USDT-M perpetual futures. Symbols end in USDT (e.g. BTCUSDT).
- `inverse` — Coin-M perpetual futures. Symbols end in USD (e.g. BTCUSD).
- `spot` — Spot trading. Symbols end in USDT (e.g. BTCUSDT). The server auto-prefixes `s` for the API.

## Tools

### Market data (no auth needed)

- `get_ticker` — 24hr price ticker. Example: `phemex-cli get_ticker --symbol BTCUSDT`
- `get_orderbook` — Order book (30 levels). Example: `phemex-cli get_orderbook --symbol BTCUSDT`
- `get_klines` — Candlestick data. Example: `phemex-cli get_klines --symbol BTCUSDT --resolution 3600 --limit 100`
- `get_recent_trades` — Recent trades. Example: `phemex-cli get_recent_trades --symbol BTCUSDT`
- `get_funding_rate` — Funding rate history. Example: `phemex-cli get_funding_rate --symbol .BTCFR8H --limit 20`

### Account (read-only, auth required)

- `get_account` — Balance and margin info. Example: `phemex-cli get_account --currency USDT`
- `get_spot_wallet` — Spot wallet balances. Example: `phemex-cli get_spot_wallet`
- `get_positions` — Current positions with PnL. Example: `phemex-cli get_positions --currency USDT`
- `get_open_orders` — Open orders. Example: `phemex-cli get_open_orders --symbol BTCUSDT`
- `get_order_history` — Closed/filled orders. Example: `phemex-cli get_order_history --symbol BTCUSDT --limit 50`
- `get_trades` — Trade execution history. Example: `phemex-cli get_trades --symbol BTCUSDT --limit 50`

### Trading (auth required)

- `place_order` — Place an order (Market, Limit, Stop, StopLimit). Key params: `--symbol`, `--side` (Buy/Sell), `--orderQty`, `--ordType`, `--price` (Limit/StopLimit), `--stopPx` (Stop/StopLimit), `--timeInForce` (GoodTillCancel/PostOnly/ImmediateOrCancel/FillOrKill), `--reduceOnly`, `--posSide` (Long/Short/Merged), `--stopLoss`, `--takeProfit`, `--qtyType` (spot only). **orderQty units differ by contract type:**
  - `linear` (USDT-M): orderQty = base currency amount (e.g. `0.01` = 0.01 BTC). To buy 10 USDT worth, calculate qty = 10 / current price.
  - `inverse` (Coin-M): orderQty = number of contracts as integer (e.g. `10` = 10 contracts). Each contract has a fixed USD value (e.g. 1 USD/contract for BTCUSD).
  - `spot`: depends on `--qtyType`. `ByBase` (default) = base currency (e.g. `0.01` = 0.01 BTC). `ByQuote` = quote currency (e.g. `50` = 50 USDT worth of BTC).
  - Example: `phemex-cli place_order --symbol BTCUSDT --side Buy --orderQty 0.01 --ordType Market`
- `amend_order` — Modify an open order. Example: `phemex-cli amend_order --symbol BTCUSDT --orderID xxx --price 95000`
- `cancel_order` — Cancel one order. Example: `phemex-cli cancel_order --symbol BTCUSDT --orderID xxx`
- `cancel_all_orders` — Cancel all orders for a symbol. Example: `phemex-cli cancel_all_orders --symbol BTCUSDT`
- `set_leverage` — Set leverage. Example: `phemex-cli set_leverage --symbol BTCUSDT --leverage 10`
- `switch_pos_mode` — Switch OneWay/Hedged. Example: `phemex-cli switch_pos_mode --symbol BTCUSDT --targetPosMode OneWay`

### Transfers (auth required)

- `transfer_funds` — Move funds between spot and futures. Example: `phemex-cli transfer_funds --currency USDT --amount 100 --direction spot_to_futures`
- `get_transfer_history` — Transfer history. Example: `phemex-cli get_transfer_history --currency USDT --limit 20`

## Safety rules

1. **Always confirm before placing orders.** Before calling `place_order`, show the user exactly what the order will do: symbol, side, quantity, type, price. Ask for confirmation.
2. **Always confirm before cancelling all orders.** Before calling `cancel_all_orders`, list the open orders first and confirm with the user.
3. **Explain leverage changes.** Before calling `set_leverage`, explain the implications (higher leverage = higher liquidation risk).
4. **Show context before trading.** Before suggesting a trade, show current positions and account balance so the user can make an informed decision.
5. **Never auto-trade.** Do not place orders without explicit user instruction.

## Common workflows

### Check a price

```bash
phemex-cli get_ticker --symbol BTCUSDT
```

### Place a market buy (USDT-M futures)

```bash
phemex-cli place_order --symbol BTCUSDT --side Buy --orderQty 0.01 --ordType Market
```

### Place a limit sell (Coin-M futures)

```bash
phemex-cli place_order --symbol BTCUSD --side Sell --orderQty 10 --ordType Limit --price 100000 --contractType inverse
```

### Buy spot

```bash
phemex-cli place_order --symbol BTCUSDT --side Buy --orderQty 10 --ordType Market --contractType spot --qtyType ByQuote
```

### Check positions

```bash
phemex-cli get_positions --currency USDT
```

## Setup

1. Create a Phemex account at https://phemex.com
2. Create an API key (Account → API Management)
3. Set environment variables `PHEMEX_API_KEY` and `PHEMEX_API_SECRET`
4. Optionally set `PHEMEX_API_URL` (defaults to testnet `https://testnet-api.phemex.com` for safety; set to `https://api.phemex.com` for real trading)
5. Optionally set `PHEMEX_MAX_ORDER_VALUE` to limit maximum order size (USD)
