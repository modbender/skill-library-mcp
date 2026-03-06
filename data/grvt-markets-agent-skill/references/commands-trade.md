# Trading Commands

All trading commands require authentication (`grvt auth login`). Commands that create or modify state (order create, order cancel, cancel-all, derisk) also require a private key for EIP-712 signing.

The `--sub-account-id` option is available on most commands and falls back to the value in config (`grvt config set subAccountId <id>`).

---

## `grvt trade order create`

Create a new order. Requires a private key for EIP-712 signing.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--instrument <name>` | **Yes** | - | Instrument symbol (e.g. `BTC_USDT_Perp`) |
| `--side <side>` | **Yes** | - | `buy` or `sell` |
| `--type <type>` | **Yes** | - | `market` or `limit` |
| `--qty <amount>` | **Yes** | - | Order quantity |
| `--price <price>` | **Yes** (limit orders) | - | Limit price |
| `--sub-account-id <id>` | No | config value | Sub-account ID |
| `--time-in-force <tif>` | No | `GTT` | `GTT` (Good Till Time), `IOC` (Immediate or Cancel), `AON` (All or None), `FOK` (Fill or Kill) |
| `--reduce-only` | No | `false` | Reduce-only order |
| `--post-only` | No | `false` | Post-only order |
| `--client-order-id <id>` | No | auto-generated | Custom numeric order ID |
| `--expiration-seconds <n>` | No | `3600` | Order expiration in seconds from now |
| `--json <path>` | No | - | Read full request body from file (`@file.json`) or stdin (`-`) |
| `--dry-run` | No | - | Show signed payload without sending |

```bash
# Simple limit buy
grvt trade order create --instrument BTC_USDT_Perp --side buy --type limit --qty 0.01 --price 68000

# Market sell
grvt trade order create --instrument BTC_USDT_Perp --side sell --type market --qty 0.01

# Post-only limit with IOC and short expiration
grvt trade order create --instrument BTC_USDT_Perp --side buy --type limit \
  --qty 0.5 --price 67500 --post-only --time-in-force IOC --expiration-seconds 60

# Reduce-only (close position only)
grvt trade order create --instrument BTC_USDT_Perp --side sell --type market --qty 0.01 --reduce-only

# Dry-run to preview the signed payload
grvt trade order create --instrument BTC_USDT_Perp --side buy --type limit \
  --qty 0.01 --price 68000 --dry-run

# From JSON file
grvt trade order create --json @order.json

# From stdin
echo '{"order": {...}}' | grvt trade order create --json -
```

**Time-in-force values** (case-insensitive, short or full form accepted):

| Short | Full | Description |
|-------|------|-------------|
| `GTT` | `GOOD_TILL_TIME` | Stays open until expiration |
| `IOC` | `IMMEDIATE_OR_CANCEL` | Fill immediately or cancel unfilled portion |
| `AON` | `ALL_OR_NONE` | Fill entirely or not at all |
| `FOK` | `FILL_OR_KILL` | Fill entirely immediately or cancel |

---

## `grvt trade order get`

Get details of a specific order by ID.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--order-id <id>` | One of these required | GRVT-assigned order ID |
| `--client-order-id <id>` | One of these required | Client-specified order ID |

```bash
grvt trade order get --order-id 0x123abc...
grvt trade order get --client-order-id 9876543210
grvt trade order get --order-id 0x123abc... --output json --pretty
```

---

## `grvt trade order open`

List all currently open orders.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--kind <kinds>` | No | Comma-separated filter: `PERPETUAL`, `FUTURE`, `CALL`, `PUT` |
| `--base <currencies>` | No | Base currency filter (comma-separated) |
| `--quote <currencies>` | No | Quote currency filter (comma-separated) |

```bash
grvt trade order open
grvt trade order open --kind PERPETUAL
grvt trade order open --base BTC --output json
```

---

## `grvt trade order cancel`

Cancel a single order. Requires either `--order-id` or `--client-order-id`.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--order-id <id>` | One of these required | Order ID to cancel |
| `--client-order-id <id>` | One of these required | Client order ID to cancel |
| `--dry-run` | No | Show payload without sending |

```bash
grvt trade order cancel --order-id 0x123abc...
grvt trade order cancel --client-order-id 9876543210
grvt trade order cancel --order-id 0x123abc... --dry-run
```

---

## `grvt trade order cancel-all`

Cancel all open orders. Prompts for confirmation unless `--yes` is passed.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--instrument <name>` | No | Only cancel orders for this instrument |
| `--dry-run` | No | Show payload without sending |

```bash
grvt trade order cancel-all
grvt trade order cancel-all --instrument BTC_USDT_Perp
grvt trade order cancel-all --yes --silent
```

---

## `grvt trade order history`

Get historical orders. Supports pagination.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--kind <kinds>` | No | Comma-separated kind filter |
| `--base <currencies>` | No | Base currency filter |
| `--quote <currencies>` | No | Quote currency filter |
| `--start-time <time>` | No | Start time |
| `--end-time <time>` | No | End time |
| `--limit <n>` | No | Max results per page |
| `--cursor <cursor>` | No | Pagination cursor |
| `--all` | No | Auto-paginate all results |

```bash
grvt trade order history
grvt trade order history --kind PERPETUAL --start-time 2025-01-01T00:00:00Z
grvt trade order history --all --output ndjson > order_history.jsonl
```

---

## `grvt trade fills`

Get fill (trade execution) history. Supports pagination.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--kind <kinds>` | No | Comma-separated kind filter |
| `--base <currencies>` | No | Base currency filter |
| `--quote <currencies>` | No | Quote currency filter |
| `--start-time <time>` | No | Start time |
| `--end-time <time>` | No | End time |
| `--limit <n>` | No | Max results per page |
| `--cursor <cursor>` | No | Pagination cursor |
| `--all` | No | Auto-paginate all results |

```bash
grvt trade fills
grvt trade fills --kind PERPETUAL --base BTC
grvt trade fills --start-time 2025-01-01T00:00:00Z --all --output ndjson
grvt trade fills --output json | jq '.[].price'
```

---

## `grvt trade positions`

Get current open positions.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--kind <kinds>` | No | Comma-separated kind filter |
| `--base <currencies>` | No | Base currency filter |
| `--quote <currencies>` | No | Quote currency filter |

```bash
grvt trade positions
grvt trade positions --kind PERPETUAL
grvt trade positions --base BTC --output json --pretty
```

---

## `grvt trade funding-payments`

Get funding payment history for perpetual positions. Supports pagination.

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--kind <kinds>` | No | Comma-separated kind filter |
| `--base <currencies>` | No | Base currency filter |
| `--quote <currencies>` | No | Quote currency filter |
| `--start-time <time>` | No | Start time |
| `--end-time <time>` | No | End time |
| `--limit <n>` | No | Max results per page |
| `--cursor <cursor>` | No | Pagination cursor |
| `--all` | No | Auto-paginate all results |

```bash
grvt trade funding-payments
grvt trade funding-payments --base BTC --start-time 2025-01-01T00:00:00Z --all
```

---

## `grvt trade leverage get`

Get initial leverage settings for all instruments (or filter to one).

| Option | Required | Description |
|--------|----------|-------------|
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--instrument <name>` | No | Filter to a single instrument (client-side filter) |

```bash
grvt trade leverage get
grvt trade leverage get --instrument BTC_USDT_Perp
grvt trade leverage get --output json --pretty
```

---

## `grvt trade leverage set`

Set initial leverage for a specific instrument.

| Option | Required | Description |
|--------|----------|-------------|
| `--instrument <name>` | **Yes** | Instrument symbol |
| `--leverage <value>` | **Yes** | Leverage value (e.g. `10`, `20`) |
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |

```bash
grvt trade leverage set --instrument BTC_USDT_Perp --leverage 10
grvt trade leverage set --instrument ETH_USDT_Perp --leverage 5
```

---

## `grvt trade cancel-on-disconnect`

Set, refresh, or disable the cancel-on-disconnect countdown. When enabled, all open orders are canceled if the session disconnects for longer than the countdown.

| Option | Required | Description |
|--------|----------|-------------|
| `--countdown <ms>` | **Yes** | Countdown in milliseconds: `1000`-`300000`, or `0` to disable |
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |

```bash
# Enable with 5-second countdown
grvt trade cancel-on-disconnect --countdown 5000

# Refresh the countdown timer
grvt trade cancel-on-disconnect --countdown 5000

# Disable
grvt trade cancel-on-disconnect --countdown 0
```

---

## `grvt trade derisk`

Set the derisk-to-maintenance-margin ratio. Requires a private key for EIP-712 signing.

| Option | Required | Description |
|--------|----------|-------------|
| `--ratio <value>` | **Yes** | Derisk MM ratio as a decimal (e.g. `0.5`) |
| `--sub-account-id <id>` | No | Sub-account ID (falls back to config) |
| `--dry-run` | No | Show signed payload without sending |

```bash
grvt trade derisk --ratio 0.5
grvt trade derisk --ratio 0.8 --dry-run
```
