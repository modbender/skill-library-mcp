# Market Data Commands

All market data commands are **unauthenticated** (no login required), except where noted.

---

## `grvt market instruments`

List available trading instruments. Uses a filtered endpoint when `--kind`, `--base`, or `--quote` are provided; otherwise returns all instruments.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--kind <kinds>` | No | - | Comma-separated: `PERPETUAL`, `FUTURE`, `CALL`, `PUT` |
| `--base <currencies>` | No | - | Comma-separated base currencies (e.g. `BTC,ETH`) |
| `--quote <currencies>` | No | - | Comma-separated quote currencies (e.g. `USDT`) |
| `--active` | No | `true` | Only return active instruments |
| `--limit <n>` | No | - | Max number of results |

```bash
grvt market instruments
grvt market instruments --kind PERPETUAL
grvt market instruments --kind PERPETUAL,FUTURE --base BTC,ETH
grvt market instruments --base ETH --quote USDT
grvt market instruments --kind CALL,PUT --base BTC --output json
```

---

## `grvt market instrument`

Get detailed metadata for a single instrument (tick size, lot size, decimals, instrument hash, etc.).

| Option | Required | Description |
|--------|----------|-------------|
| `--instrument <name>` | **Yes** | Instrument symbol (e.g. `BTC_USDT_Perp`) |

```bash
grvt market instrument --instrument BTC_USDT_Perp
grvt market instrument --instrument ETH_USDT_Perp --output json --pretty
```

---

## `grvt market currency`

List all supported currencies with their IDs, symbols, and decimal precision. No options required.

```bash
grvt market currency
grvt market currency --output json
```

---

## `grvt market orderbook`

Get the order book (bids and asks) for an instrument.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--instrument <name>` | **Yes** | - | Instrument symbol |
| `--depth <n>` | No | `10` | Book depth: `10`, `50`, `100`, or `500` |

```bash
grvt market orderbook --instrument BTC_USDT_Perp
grvt market orderbook --instrument BTC_USDT_Perp --depth 50
grvt market orderbook --instrument ETH_USDT_Perp --depth 100 --output json
```

---

## `grvt market trades`

Get trade history for an instrument. Supports pagination.

| Option | Required | Description |
|--------|----------|-------------|
| `--instrument <name>` | **Yes** | Instrument symbol |
| `--start-time <time>` | No | Start time (unix s/ms/ns or ISO 8601) |
| `--end-time <time>` | No | End time |
| `--limit <n>` | No | Max trades per page |
| `--cursor <cursor>` | No | Pagination cursor from previous response |
| `--all` | No | Auto-paginate through all pages |

```bash
grvt market trades --instrument BTC_USDT_Perp
grvt market trades --instrument BTC_USDT_Perp --limit 100
grvt market trades --instrument BTC_USDT_Perp --start-time 2025-01-01T00:00:00Z --all --output ndjson
```

---

## `grvt market candles`

Get candlestick (OHLCV) data for an instrument. Supports pagination.

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--instrument <name>` | **Yes** | - | Instrument symbol |
| `--interval <interval>` | **Yes** | - | Candle interval (see below) |
| `--type <type>` | No | `TRADE` | Price type: `TRADE`, `MARK`, `INDEX`, `MID` |
| `--start-time <time>` | No | - | Start time |
| `--end-time <time>` | No | - | End time |
| `--limit <n>` | No | - | Max candles per page |
| `--cursor <cursor>` | No | - | Pagination cursor |
| `--all` | No | - | Auto-paginate all results |

**Valid intervals:** `CI_1_M`, `CI_5_M`, `CI_15_M`, `CI_30_M`, `CI_1_H`, `CI_2_H`, `CI_4_H`, `CI_6_H`, `CI_8_H`, `CI_12_H`, `CI_1_D`, `CI_1_W`

```bash
grvt market candles --instrument BTC_USDT_Perp --interval CI_1_H
grvt market candles --instrument BTC_USDT_Perp --interval CI_1_D --limit 30
grvt market candles --instrument BTC_USDT_Perp --interval CI_5_M \
  --start-time 2025-01-01T00:00:00Z --end-time 2025-01-02T00:00:00Z --all --output ndjson
grvt market candles --instrument ETH_USDT_Perp --interval CI_1_H --type MARK
```

---

## `grvt market funding-rate`

Get funding rate history for an instrument. Supports pagination.

| Option | Required | Description |
|--------|----------|-------------|
| `--instrument <name>` | **Yes** | Instrument symbol |
| `--start-time <time>` | No | Start time |
| `--end-time <time>` | No | End time |
| `--limit <n>` | No | Max entries per page |
| `--cursor <cursor>` | No | Pagination cursor |
| `--all` | No | Auto-paginate all results |

```bash
grvt market funding-rate --instrument BTC_USDT_Perp
grvt market funding-rate --instrument BTC_USDT_Perp --limit 10
grvt market funding-rate --instrument BTC_USDT_Perp --all --output ndjson
```

---

## `grvt market ticker`

Get full ticker data for an instrument. Optionally include greeks (for options) and derived statistics.

| Option | Required | Description |
|--------|----------|-------------|
| `--instrument <name>` | **Yes** | Instrument symbol |
| `--greeks` | No | Include greeks data (for options) |
| `--derived` | No | Include derived statistics |

```bash
grvt market ticker --instrument BTC_USDT_Perp
grvt market ticker --instrument BTC_USDT_Perp --greeks --derived
grvt market ticker --instrument ETH_USDT_Call_20Oct23_2800 --greeks --output json --pretty
```

---

## `grvt market mini-ticker`

Get lightweight price info (last price, 24h change) for an instrument. Faster than full ticker.

| Option | Required | Description |
|--------|----------|-------------|
| `--instrument <name>` | **Yes** | Instrument symbol |

```bash
grvt market mini-ticker --instrument BTC_USDT_Perp
grvt market mini-ticker --instrument ETH_USDT_Perp --output json
```

---

## `grvt market margin-rules`

Get margin rules (initial margin, maintenance margin tiers) for an instrument.

| Option | Required | Description |
|--------|----------|-------------|
| `--instrument <name>` | **Yes** | Instrument symbol |

```bash
grvt market margin-rules --instrument BTC_USDT_Perp
grvt market margin-rules --instrument BTC_USDT_Perp --output json --pretty
```
