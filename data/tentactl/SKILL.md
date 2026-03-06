---
name: kraken
description: "Interact with the Kraken cryptocurrency exchange — spot + futures, REST + WebSocket. Use when: (1) checking crypto prices or market data, (2) viewing account balances, positions, or trade history, (3) placing or cancelling orders (spot or futures), (4) streaming live market data via WebSocket, (5) building DCA strategies, price alerts, or portfolio monitoring, (6) any mention of Kraken, crypto trading, or portfolio management. Requires the tentactl binary. Kraken API keys needed only for authenticated endpoints."
metadata:
  {
    "openclaw":
      {
        "emoji": "🐙",
        "requires":
          {
            "bins": ["tentactl"],
            "env": ["KRAKEN_API_KEY", "KRAKEN_API_SECRET"],
          },
        "install":
          [
            {
              "id": "cargo",
              "kind": "cargo",
              "package": "tentactl",
              "bins": ["tentactl"],
              "label": "Install tentactl via cargo (source: https://github.com/askbeka/tentactl)",
            },
          ],
        "credentials":
          {
            "KRAKEN_API_KEY": "Kraken API key — generate at https://www.kraken.com/u/security/api",
            "KRAKEN_API_SECRET": "Kraken API secret (private key from the same page)",
          },
        "privacy":
          {
            "files_written": ["~/.tentactl.env"],
            "network": ["api.kraken.com", "futures.kraken.com", "ws.kraken.com", "futures.kraken.com/ws/v1"],
            "notes": "API keys are stored in ~/.tentactl.env (chmod 600). Market data endpoints require no authentication. Account and trading endpoints require KRAKEN_API_KEY and KRAKEN_API_SECRET.",
          },
      },
  }
---

# Kraken Exchange

MCP server for the [Kraken](https://www.kraken.com) cryptocurrency exchange — **114 tools** covering spot, futures, REST, and WebSocket APIs. Source: [github.com/askbeka/tentactl](https://github.com/askbeka/tentactl) (MIT license).

## How It Works

`tentactl` is a Rust binary that speaks MCP (Model Context Protocol) over stdio. It provides:

- **Spot REST** (57 tools): Market data, account info, trading, funding, earn, subaccounts, exports
- **Futures REST** (21 tools): Instruments, positions, orders, transfers, funding rates
- **Spot WebSocket v2** (19 tools): Live market data streams, real-time order management
- **Futures WebSocket** (17 tools): Live futures feeds, real-time futures trading

## Setup

### 1. Install the binary

```bash
cargo install tentactl
```

Or download from [GitHub Releases](https://github.com/askbeka/tentactl/releases) (Linux, macOS, Windows).

### 2. Configure API keys (optional)

Market data tools work **without any keys**. For account and trading tools:

```bash
echo "KRAKEN_API_KEY=your-key" > ~/.tentactl.env
echo "KRAKEN_API_SECRET=your-secret" >> ~/.tentactl.env
chmod 600 ~/.tentactl.env
```

Or use the 1Password setup script: `scripts/setup-keys.sh`

**Key permissions:** Create keys at https://www.kraken.com/u/security/api
- Read-only: enable **Query Funds** and **Query Open Orders & Trades**
- Trading: also enable **Create & Modify Orders**

## Usage

```bash
# Market data (no auth)
scripts/kraken.sh get_ticker '{"pair":"XBTUSD"}'
scripts/kraken.sh get_orderbook '{"pair":"ETHUSD","count":5}'
scripts/kraken.sh futures_tickers '{}'

# Live WebSocket streams
scripts/kraken.sh ws_subscribe_ticker '{"symbols":["BTC/USD"]}'
scripts/kraken.sh ws_subscribe_book '{"symbols":["ETH/USD"],"depth":10}'
scripts/kraken.sh wf_subscribe_ticker '{"product_ids":["PI_XBTUSD"]}'
scripts/kraken.sh ws_status '{}'

# Account (needs API keys)
scripts/kraken.sh get_balance '{}'
scripts/kraken.sh futures_open_positions '{}'

# Trading (needs API keys) ⚠️ REAL MONEY
scripts/kraken.sh place_order '{"pair":"XBTUSD","direction":"buy","order_type":"limit","volume":"0.001","price":"50000","validate":true}'
scripts/kraken.sh ws_add_order '{"symbol":"BTC/USD","side":"buy","order_type":"limit","limit_price":"50000","order_qty":"0.001","validate":true}'
```

## Tools Reference

See `references/tools.md` for full parameter docs on all 114 tools.

## Safety Rules

- **ALWAYS** use `validate: true` first when placing orders
- **ALWAYS** confirm with the user before placing real orders
- **NEVER** place orders without explicit user approval
- Market orders execute IMMEDIATELY — prefer limit orders
- Display validation result and ask for confirmation before removing `validate`
- Trading tools are marked with ⚠️ REAL MONEY in their descriptions

## Trading Pairs

- **Spot REST:** Kraken format — `XBTUSD`, `ETHUSD`, `SOLUSD`
- **Spot WebSocket:** Standard format — `BTC/USD`, `ETH/USD`, `SOL/USD`
- **Futures:** Product IDs — `PI_XBTUSD`, `PI_ETHUSD`, `PF_SOLUSD`

## Automation Patterns

### DCA (Dollar Cost Average)
```
openclaw cron add --schedule "0 9 * * 1" --task "Buy $50 of BTC on Kraken using the kraken skill. Use validate first, then execute."
```

### Price Alerts
Subscribe to WebSocket ticker, check thresholds in heartbeat/cron, notify via WhatsApp/Telegram.

### Portfolio Monitoring
Cron job that checks balances + positions + current prices, calculates P&L, alerts on significant changes.

### Funding Rate Arbitrage
Subscribe to futures tickers, monitor funding rates, alert when rates diverge significantly.
