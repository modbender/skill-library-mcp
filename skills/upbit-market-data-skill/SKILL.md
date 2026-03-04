# Upbit Market Data Skill

A CLI-based OpenClaw skill that fetches quotation/market data from the Upbit Open API.

This skill is designed to be executed via **OpenClaw `exec`** (run-once). It supports:
- Trading pair (market) list
- Candles (second/minute/day/week/month/year)
- Recent trades
- Tickers (by trading pairs / by quote currency)
- Orderbooks
- Watchlist tickers (from config)

All responses are JSON:
- Success → stdout: `{ "ok": true, "result": ... }`
- Error   → stderr: `{ "ok": false, "error": { ... } }` and exit code `1`

---

## Requirements

- Node.js **18+** (uses built-in `fetch`)
- NPM

---

## Installation

```bash
npm install
```

---

## Configuration (JSON)

Create `config/config.json`.

Example:

```json
{
  "upbit": {
    "baseUrl": "https://api.upbit.com",
    "accessKey": "",
    "secretKey": ""
  },
  "watchlist": ["KRW-BTC", "KRW-ETH", "KRW-SOL"]
}
```

### Config path override

Default path:
- `config/config.json`

Override at runtime:

```bash
node skill.js tickers --markets=KRW-BTC --config=./config/config.json
```

---

## CLI Grammar

General format:

```bash
node skill.js <command> [subcommand] [--option=value]
```

Rules:
1. `<command>` is required.
2. `[subcommand]` is optional and **MUST NOT** start with `--`.
3. Options must be provided as `--key=value` or `--key value`.
4. Outputs are always JSON.

---

## STRICT MODE (Recommended for OpenClaw)

OpenClaw/LLM agents may reorder arguments when generating CLI calls. To prevent confusion, enable **strict mode**.

### Enable strict mode

Add `--strict=true` to the command:

```bash
node skill.js tickers --markets=KRW-BTC,KRW-ETH --strict=true
```

### Strict mode rules (hard requirements)

When `--strict=true`:

1. Candle type **MUST** appear immediately after `candles`:
   - ✅ `node skill.js candles minutes --market=KRW-ETH --unit=5 --strict=true`
   - ❌ `node skill.js candles --market=KRW-ETH minutes --unit=5 --strict=true`
2. Candle type **MUST NOT** be passed as an option (do not use `--type=` in strict mode).
3. For non-candles commands, `subcommand` must be omitted.
4. Any unexpected positional arguments (extra words not starting with `--`) will cause an error.

Why strict mode helps:
- It forces a single canonical command shape, making it far harder for OpenClaw/LLM to generate ambiguous or reordered invocations.

---

## Commands

### 1) List trading pairs (markets)

```bash
node skill.js pairs --details=true --strict=true
```

---

### 2) Candles (CRITICAL STRUCTURE)

Candles require a **candle type immediately after `candles`**.

#### Canonical structure

```bash
node skill.js candles <type> --market=<MARKET> [options]
```

Where `<type>` MUST be one of:
- `seconds`
- `minutes`
- `days`
- `weeks`
- `months`
- `years`

⚠️ `<type>` is NOT passed as `--unit`.  
⚠️ `<type>` must appear immediately after `candles`.

#### Minutes candles (5-minute example)

```bash
node skill.js candles minutes --market=KRW-ETH --unit=5 --count=100 --strict=true
```

Allowed minute units:
`1, 3, 5, 10, 15, 30, 60, 240`

#### Other candles

```bash
node skill.js candles seconds --market=KRW-BTC --count=200 --strict=true
node skill.js candles days    --market=KRW-BTC --count=50  --strict=true
node skill.js candles weeks   --market=KRW-BTC --count=30  --strict=true
node skill.js candles months  --market=KRW-BTC --count=12  --strict=true
node skill.js candles years   --market=KRW-BTC --count=5   --strict=true
```

#### Incorrect examples (DO NOT USE)

```bash
# ❌ type passed as option
node skill.js candles --unit=minutes --market=KRW-ETH

# ❌ type after options
node skill.js candles --market=KRW-ETH minutes --unit=5
```

---

### 3) Recent trades

```bash
node skill.js trades --market=KRW-BTC --count=50 --strict=true
```

---

### 4) Tickers by trading pairs

```bash
node skill.js tickers --markets=KRW-BTC,KRW-ETH,KRW-SOL --strict=true
```

---

### 5) Tickers by quote currency

```bash
node skill.js quote-tickers --quote=KRW,BTC --strict=true
```

---

### 6) Orderbooks

```bash
node skill.js orderbook --markets=KRW-BTC --level=100000 --count=15 --strict=true
```

---

### 7) Watchlist tickers (from config)

```bash
node skill.js watchlist --strict=true
```

---

## Error handling & rate limits

Upbit may respond with:
- 429: Too Many Requests
- 418: Request blocked
- 400: Bad request

The skill passes Upbit error payloads (when present) under `error.upbit`.

Reference:
https://docs.upbit.com/kr/reference/rest-api-guide
