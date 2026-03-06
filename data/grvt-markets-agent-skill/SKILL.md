---
name: grvt-exchange
description: >-
  Trade on GRVT (Gravity Markets) derivatives exchange via the grvt-cli tool.
  Use when the user wants to trade crypto derivatives, place or cancel orders,
  check positions, view market data (orderbook, candles, tickers, funding rates),
  manage account balances, transfer funds between sub-accounts, withdraw to
  Ethereum, set leverage, query trade or order history, or interact with the
  GRVT API in any way. Covers perpetuals, futures, and options on GRVT.
---

# GRVT Exchange CLI

> **IMPORTANT: Community Project Disclaimer**
>
> `grvt-cli` is a **community hobby project**. It is **NOT** officially supported, endorsed, audited, or maintained by the GRVT team. No security audit or formal code review has been performed.
>
> **The code has not been audited for security vulnerabilities. By using this tool the user acknowledges and accepts the risk of total loss of funds.**
>
> The user is solely responsible for any financial losses, leaked credentials, or unintended trades that may result from using this software.
>
> This tool stores API keys and private keys in plaintext on disk (with `0600` file permissions). Keys should never be shared or used on untrusted machines.
>
> **Before using this CLI on behalf of the user, you MUST inform them of this disclaimer and get their explicit acknowledgment.**

`grvt` is a CLI tool and Node.js library for trading on GRVT (Gravity Markets), a crypto derivatives exchange supporting perpetuals, futures, and options.

Package: `@madeinusmate/grvt-cli` (npm). Binary: `grvt`. Requires Node.js >= 20.

## Safety Recommendations

- Only use testnet until the user fully understands the CLI behavior.
- Review the source code before trusting it with real funds.
- Keep private keys out of shell history (use `grvt setup` which reads from stdin).
- Rotate API keys regularly.
- Never use the CLI with more funds than the user can afford to lose.

## Installation

```bash
pnpm add -g @madeinusmate/grvt-cli
```

Verify: `grvt --version`

## First-Time Setup

The interactive wizard handles everything:

```bash
grvt setup
```

The setup wizard displays a disclaimer requiring explicit acceptance before proceeding. It is interactive and reads sensitive input from stdin (keeping keys out of shell history). It walks through: environment, API key, private key, and default sub-account ID, then authenticates automatically.

**Note:** Because `grvt setup` is interactive and requires user input, agents cannot run it directly. Use the manual setup flow below instead.

Manual setup (recommended for agents):

```bash
grvt config set env testnet
grvt auth login --api-key YOUR_API_KEY --private-key 0xYOUR_PRIVATE_KEY
grvt config set subAccountId YOUR_SUB_ACCOUNT_ID
```

Verify setup:

```bash
grvt auth status
grvt config list
```

## Configuration

Config file: `~/.config/grvt/config.toml` (permissions `0600`).

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `env` | `dev\|staging\|testnet\|prod` | `prod` | GRVT environment |
| `apiKey` | string | - | GRVT API key |
| `privateKey` | string | - | Ethereum private key (0x-prefixed) for EIP-712 signing |
| `subAccountId` | string | - | Default sub-account for trading commands |
| `accountId` | string | - | Main account ID (set automatically on login) |
| `cookie` | string | - | Session cookie (set automatically on login) |
| `outputDefaults.output` | `json\|ndjson\|table\|raw` | `table` | Default output format |
| `outputDefaults.pretty` | boolean | `false` | Pretty-print JSON |
| `outputDefaults.silent` | boolean | `false` | Suppress info logs |
| `http.timeoutMs` | number | `10000` | Request timeout (ms) |
| `http.retries` | number | `3` | Retry count |
| `http.backoffMs` | number | `200` | Initial backoff (ms) |
| `http.maxBackoffMs` | number | `10000` | Max backoff (ms) |

Secret keys (`apiKey`, `privateKey`, `cookie`) are redacted in `config list` / `config get` output.

Use `grvt config set <key> <value>` and `grvt config unset <key>` to modify. Use dot-notation for nested keys (e.g. `outputDefaults.output`).

## Authentication

**Login** requires an API key. A private key is optional but required for write operations (orders, transfers, withdrawals, derisk).

```bash
grvt auth login --api-key KEY --private-key 0xKEY
```

The session cookie is stored in config and sent automatically with authenticated requests.

| Command | Description |
|---------|-------------|
| `grvt auth login` | Authenticate (stores session cookie + account ID) |
| `grvt auth status` | Verify session is valid (calls API) |
| `grvt auth whoami` | Show current auth state (local only, no API call) |
| `grvt auth logout` | Clear all stored credentials |

**EIP-712 signing** is used for: order creation, transfers, withdrawals, and derisk operations. The private key never leaves the local machine.

## Environments

| Environment | Market Data | Trading | Edge (Auth) |
|------------|------------|---------|-------------|
| `dev` | `market-data.dev.gravitymarkets.io` | `trades.dev.gravitymarkets.io` | `edge.dev.gravitymarkets.io` |
| `staging` | `market-data.staging.gravitymarkets.io` | `trades.staging.gravitymarkets.io` | `edge.staging.gravitymarkets.io` |
| `testnet` | `market-data.testnet.grvt.io` | `trades.testnet.grvt.io` | `edge.testnet.grvt.io` |
| `prod` | `market-data.grvt.io` | `trades.grvt.io` | `edge.grvt.io` |

Switch with: `grvt config set env testnet`

## Global Options

Available on every command:

| Option | Description | Default |
|--------|-------------|---------|
| `--output <format>` | `json`, `ndjson`, `table`, `raw` | `table` (TTY) / `json` (piped) |
| `--pretty` | Pretty-print JSON | `false` |
| `--silent` | Suppress info logs | `false` |
| `--no-color` | Disable colors | - |
| `--yes` | Skip confirmation prompts | - |
| `--retries <n>` | Retry count | `3` |
| `--timeout-ms <n>` | Request timeout (ms) | `10000` |

Write commands (`order create`, `order cancel`, `transfer create`, `withdraw create`, `derisk`) also support:

| Option | Description |
|--------|-------------|
| `--dry-run` | Validate and show the signed payload without sending |
| `--json <path>` | Read full request body from file (`@file.json`) or stdin (`-`) |

## Command Overview

```
grvt
  setup                         Interactive setup wizard
  config                        Manage local configuration
    path / get / set / unset / list / export / import
  auth                          Authentication and session
    login / status / whoami / logout
  market                        Market data (mostly unauthenticated)
    instruments / instrument / currency / orderbook / trades
    candles / funding-rate / ticker / mini-ticker / margin-rules
  account                       Account info (requires auth)
    funding / summary / aggregated / history
  trade                         Trading (requires auth; writes need private key)
    order create / order get / order open / order cancel / order cancel-all / order history
    fills / positions / funding-payments
    leverage get / leverage set
    cancel-on-disconnect / derisk
  funds                         Fund management (requires auth; writes need private key)
    deposit history
    transfer create / transfer history
    withdraw create / withdraw history
```

For full flag details on each command, read the corresponding reference file:
- `references/commands-config.md` — config and auth commands
- `references/commands-market.md` — market data commands
- `references/commands-trade.md` — trading commands
- `references/commands-account.md` — account commands
- `references/commands-funds.md` — fund management commands
- `references/errors.md` — error codes and troubleshooting

## Instrument Naming

GRVT uses structured instrument symbols:

| Type | Pattern | Example |
|------|---------|---------|
| Perpetual | `{BASE}_{QUOTE}_Perp` | `BTC_USDT_Perp` |
| Future | `{BASE}_{QUOTE}_Fut_{DATE}` | `BTC_USDT_Fut_20Oct23` |
| Call | `{BASE}_{QUOTE}_Call_{DATE}_{STRIKE}` | `ETH_USDT_Call_20Oct23_2800` |
| Put | `{BASE}_{QUOTE}_Put_{DATE}_{STRIKE}` | `ETH_USDT_Put_20Oct23_2800` |

Always discover available instruments before trading:

```bash
grvt market instruments
grvt market instruments --kind PERPETUAL --base BTC
grvt market instrument --instrument BTC_USDT_Perp
```

## Output Format Guide

| Format | When to use |
|--------|-------------|
| `table` | Interactive display in terminal (default in TTY) |
| `json` | Parsing output programmatically, piping to `jq` |
| `ndjson` | Streaming large datasets with `--all` pagination |
| `raw` | Debugging raw API responses |

The CLI auto-detects: `table` when stdout is a TTY, `json` when piped. Override with `--output <format>`.

When using `--all` with `ndjson`, records stream to stdout as they arrive (one JSON object per line), enabling efficient processing of large result sets without buffering everything in memory.

## Key Workflows

### Market Analysis

```bash
grvt market instruments --kind PERPETUAL
grvt market orderbook --instrument BTC_USDT_Perp --depth 50
grvt market ticker --instrument BTC_USDT_Perp --greeks --derived
grvt market candles --instrument BTC_USDT_Perp --interval CI_1_H --limit 24
grvt market funding-rate --instrument BTC_USDT_Perp --limit 10
grvt market margin-rules --instrument BTC_USDT_Perp
```

### Place and Manage Orders

```bash
# Limit buy
grvt trade order create --instrument BTC_USDT_Perp --side buy --type limit --qty 0.01 --price 68000

# Market sell
grvt trade order create --instrument BTC_USDT_Perp --side sell --type market --qty 0.01

# With options
grvt trade order create --instrument BTC_USDT_Perp --side buy --type limit \
  --qty 0.01 --price 68000 --post-only --time-in-force IOC --expiration-seconds 60

# Monitor
grvt trade order open
grvt trade order get --order-id 0x123...

# Cancel
grvt trade order cancel --order-id 0x123...
grvt trade order cancel-all
grvt trade order cancel-all --instrument BTC_USDT_Perp
```

### Portfolio Check

```bash
grvt trade positions
grvt account summary
grvt account aggregated
grvt account funding
grvt account history --start-time 2025-01-01T00:00:00Z --limit 24
```

### Fund Management

```bash
# Transfer between sub-accounts
grvt funds transfer create \
  --from-sub-account-id FROM_ID --to-sub-account-id TO_ID \
  --currency USDT --amount 100

# Withdraw to Ethereum address
grvt funds withdraw create \
  --to-address 0xYOUR_ETH_ADDRESS --currency USDT --amount 50

# View history
grvt funds deposit history --all
grvt funds transfer history --start-time 2025-01-01T00:00:00Z
grvt funds withdraw history --limit 10
```

### Leverage and Risk

```bash
grvt trade leverage get
grvt trade leverage set --instrument BTC_USDT_Perp --leverage 10
grvt trade cancel-on-disconnect --countdown 5000
grvt trade derisk --ratio 0.5
```

## Shell Patterns

Pipe JSON output to `jq`:

```bash
grvt market instruments --output json | jq '.[].instrument'
grvt trade order open --output json | jq '.[] | {instrument, side: .legs[0].is_buying_asset, size: .legs[0].size}'
```

Stream paginated results:

```bash
grvt trade fills --all --output ndjson | jq '.instrument'
grvt trade order history --all --output ndjson > all_orders.jsonl
```

Read order payload from a file:

```bash
grvt trade order create --json @order.json
echo '{"order": {...}}' | grvt trade order create --json -
```

Skip confirmations for scripting:

```bash
grvt trade order cancel-all --yes --silent
grvt funds transfer create ... --yes --silent
```

Dry-run to preview:

```bash
grvt trade order create --instrument BTC_USDT_Perp --side buy --type limit --qty 0.01 --price 68000 --dry-run
```

## Timestamp Formats

All `--start-time` and `--end-time` flags accept:

| Format | Example |
|--------|---------|
| Unix seconds | `1704067200` |
| Unix milliseconds | `1704067200000` |
| Unix nanoseconds | `1704067200000000000` |
| ISO 8601 | `2025-01-01T00:00:00Z` |

## Error Handling

| Exit Code | Meaning |
|-----------|---------|
| `0` | Success |
| `2` | Usage / validation error (bad flags, missing required options) |
| `3` | Authentication / permission error (expired session, invalid key) |
| `4` | Partial failure (batch operations like cancel-all) |
| `5` | API / network error (server errors, timeouts, rate limits) |

Common recovery patterns:
- Exit 3: Run `grvt auth login` to refresh session
- Exit 5 with 429: Reduce request frequency; CLI retries automatically with exponential backoff
- Exit 2: Check `grvt <command> --help` for required options

For detailed error scenarios and troubleshooting, read `references/errors.md`.

## Library Usage

`@madeinusmate/grvt-cli` can also be imported as a Node.js library:

```typescript
import { createHttpClient, login, createOrder, getOpenOrders, getPositions } from "@madeinusmate/grvt-cli";
```

See `src/index.ts` in the package source for all exported functions.

## Candle Intervals

Valid values for `--interval` on `grvt market candles`:

`CI_1_M`, `CI_5_M`, `CI_15_M`, `CI_30_M`, `CI_1_H`, `CI_2_H`, `CI_4_H`, `CI_6_H`, `CI_8_H`, `CI_12_H`, `CI_1_D`, `CI_1_W`

## Instrument Kind Filters

Valid values for `--kind` filters (comma-separated):

`PERPETUAL`, `FUTURE`, `CALL`, `PUT`
