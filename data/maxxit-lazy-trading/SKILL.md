---
emoji: 📈
name: maxxit-lazy-trading
version: 1.2.6
author: Maxxit
description: Execute perpetual trades on Ostium and Aster via Maxxit's Lazy Trading API. Includes programmatic endpoints for opening/closing positions, managing risk, fetching market data, copy-trading other OpenClaw agents, and a trustless Alpha Marketplace for buying/selling ZK-verified trading signals (Arbitrum Sepolia).
homepage: https://maxxit.ai
repository: https://github.com/Maxxit-ai/maxxit-latest
disableModelInvocation: true
requires:
  env:
    - MAXXIT_API_KEY
    - MAXXIT_API_URL
metadata:
  openclaw:
    requiredEnv:
      - MAXXIT_API_KEY
      - MAXXIT_API_URL
    bins:
      - curl
    primaryCredential: MAXXIT_API_KEY
---

# Maxxit Lazy Trading

Execute perpetual futures trades on Ostium and Aster DEX through Maxxit's Lazy Trading API. This skill enables automated trading through programmatic endpoints for opening/closing positions and managing risk.

## When to Use This Skill

- User wants to execute trades on Ostium
- User wants to execute trades on Aster DEX
- User asks about their lazy trading account details
- User wants to check their USDC/ETH balance
- User wants to view their open positions or portfolio
- User wants to see their closed position history or PnL
- User wants to discover available trading symbols
- User wants to get market data or LunarCrush metrics for analysis
- User wants a whole market snapshot for the trading purpose
- User wants to compare altcoin rankings (AltRank) across different tokens
- User wants to identify high-sentiment trading opportunities
- User wants to know social volume trends for crypto assets
- User wants to open a new trading position (long/short)
- User wants to close an existing position
- User wants to set or modify take profit levels
- User wants to set or modify stop loss levels
- User wants to fetch current token/market prices
- User mentions "lazy trade", "perps", "perpetuals", or "futures trading"
- User wants to automate their trading workflow
- User wants to copy-trade or mirror another trader's positions
- User wants to discover other OpenClaw agents to learn from
- User wants to see what trades top-performing traders are making
- User wants to find high-impact-factor traders to replicate
- User wants to sell their trading signals as alpha
- User wants to browse or buy trustless alpha from ZK-verified traders
- User wants to generate a ZK proof of their trading performance or flag a position as alpha
- User mentions "alpha marketplace", "sell alpha", "buy alpha", or "ZK proof"

---

## ⚠️ DEX Routing Rules (Mandatory)

1. **Always ask venue first if unclear**: "Do you want to trade on Ostium or Aster?"
2. **Always state the active venue explicitly** in your response (e.g., "Using Ostium..." or "Using Aster...").
3. **Do not mix venue suggestions**:
   - If user is trading on **Ostium**, only suggest Ostium endpoints/actions.
   - If user is trading on **Aster**, only suggest Aster endpoints/actions.
4. **Do not ask network clarification**:
   - **Ostium is mainnet-only** in this setup.
   - **Aster is testnet-only** in this setup.
   - Therefore do **not** ask "mainnet or testnet?" for either venue.
5. If user switches venue mid-conversation, confirm the switch and then continue with only that venue's flow.

---

## ⚠️ CRITICAL: API Parameter Rules (Read Before Calling ANY Endpoint)

> **NEVER assume, guess, or hallucinate values for API request parameters.** Every required parameter must come from either a prior API response or explicit user input. If you don't have a required value, you MUST fetch it from the appropriate dependency endpoint first.

### Parameter Dependency Graph

The following shows where each required parameter comes from. **Always resolve dependencies before calling an endpoint.**

| Parameter | Source | Endpoint to Fetch From |
|-----------|--------|------------------------|
| `userAddress` / `address` | `/club-details` response → `user_wallet` | `GET /club-details` |
| `agentAddress` | `/club-details` response → `ostium_agent_address` | `GET /club-details` |
| `tradeIndex` | `/open-position` response → `actualTradeIndex` **OR** `/positions` response → `tradeIndex` | `POST /open-position` or `POST /positions` |
| `pairIndex` | `/positions` response → `pairIndex` **OR** `/symbols` response → symbol `id` | `POST /positions` or `GET /symbols` |
| `entryPrice` | `/open-position` response → `entryPrice` **OR** `/positions` response → `entryPrice` | `POST /open-position` or `POST /positions` |
| `market` / `symbol` | User specifies token **OR** `/symbols` response → `symbol` (e.g. `ETH/USD`) | User input or `GET /symbols` |
| `side` | User specifies `"long"` or `"short"` | User input (required) |
| `collateral` | User specifies the USDC amount | User input (required) |
| `leverage` | User specifies the multiplier | User input (required) |
| `takeProfitPercent` | User specifies (e.g., 0.30 = 30%) | User input (required) |
| `stopLossPercent` | User specifies (e.g., 0.10 = 10%) | User input (required) |
| `address` (for copy-trader-trades) | `/copy-traders` response → `creatorWallet` or `walletAddress` | `GET /copy-traders` |
| `commitment` (Alpha) | `/alpha/agents` response → `commitment` | `GET /alpha/agents` |
| `listingId` (Alpha) | `/alpha/listings` response → `listingId` | `GET /alpha/listings` |
| `alpha`, `contentHash` (Alpha) | `/alpha/purchase` Phase 2 response → `alpha`, `contentHash` | `GET /alpha/purchase` + `X-Payment` header |
| `txHash` (Alpha) | `/alpha/pay` response → `txHash` | `POST /alpha/pay` |

### Mandatory Workflow Rules

1. **Always call `/club-details` first** to get `user_wallet` (used as `userAddress`/`address`) and `ostium_agent_address` (used as `agentAddress`). Cache these for the session — they don't change.
2. **Never hardcode or guess wallet addresses.** They are unique per user and must come from `/club-details`.
3. **For opening a position:** Fetch market data first (via `/lunarcrush` or `/market-data`), present it to the user, get explicit confirmation plus trade parameters (collateral, leverage, side, TP, SL), then execute.
   - **Market format rule (Ostium):** `/symbols` returns pairs like `ETH/USD`, but `/open-position` expects `market` as base token only (e.g. `ETH`). Convert by taking the base token before `/`.
4. **For setting TP/SL after opening:** Use the `actualTradeIndex` from the `/open-position` response. If you don't have it (e.g., position was opened earlier), call `/positions` to get `tradeIndex`, `pairIndex`, and `entryPrice`.
5. **For closing a position:** You need the `tradeIndex` — always call `/positions` first to look up the correct one for the user's specified market/position.
6. **Ask the user for trade parameters** — never assume collateral amount, leverage, TP%, or SL%. Present defaults but let the user confirm or override.
7. **Validate the market exists** by calling `/symbols` before trading if you're unsure whether a token is available on Ostium.
8. **For Alpha consumer flow:** Follow the exact order: `/alpha/agents` → `/alpha/listings` → `/alpha/purchase` (402) → `/alpha/pay` → `/alpha/purchase` (with `X-Payment`) → `/alpha/verify` → `/club-details` → `/alpha/execute`. Never skip steps. For `/alpha/verify`, pass the `content` object **exactly** as received from purchase — do not modify keys or values.

### Pre-Flight Checklist (Run Mentally Before Every API Call)

```
✅ Do I have the user's wallet address? → If not, call /club-details
✅ Do I have the agent address? → If not, call /club-details
✅ Does this endpoint need a tradeIndex? → If not in hand, call /positions
✅ Does this endpoint need entryPrice/pairIndex? → If not in hand, call /positions
✅ Did I ask the user for all trade parameters? → collateral, leverage, side, TP%, SL%
✅ Is the market/symbol valid? → If unsure, call /symbols to verify
✅ (Alpha) Do I have commitment? → If not, call /alpha/agents
✅ (Alpha) Do I have listingId? → If not, call /alpha/listings
✅ (Alpha) For /verify: Am I passing content exactly as received? → No modifications
✅ (Alpha) For /execute: Do I have agentAddress + userAddress? → Call /club-details
```

---

## Authentication

All requests require an API key with prefix `lt_`. Pass it via:
- Header: `X-API-KEY: lt_your_api_key`
- Or: `Authorization: Bearer lt_your_api_key`

## API Endpoints

## Ostium Programmatic Endpoints (`/api/lazy-trading/programmatic/*`)

> All endpoints under `/api/lazy-trading/programmatic/*` are for **Ostium** unless explicitly prefixed with `/aster/`.

### Get Account Details

Retrieve lazy trading account information including agent status, Telegram connection, and trading preferences.

```bash
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/club-details" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

**Response:**
```json
{
  "success": true,
  "user_wallet": "0x...",
  "agent": {
    "id": "agent-uuid",
    "name": "Lazy Trader - Username",
    "venue": "ostium",
    "status": "active"
  },
  "telegram_user": {
    "id": 123,
    "telegram_user_id": "123456789",
    "telegram_username": "trader"
  },
  "deployment": {
    "id": "deployment-uuid",
    "status": "active",
    "enabled_venues": ["ostium"]
  },
  "trading_preferences": {
    "risk_tolerance": "medium",
    "trade_frequency": "moderate"
  },
  "ostium_agent_address": "0x...",
  "aster_configured": "true",
}
```

### Get Available Symbols

Retrieve all available trading symbols from the Ostium exchange. Use this to discover which symbols you can trade and get LunarCrush data for.

```bash
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/symbols" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

**Response:**
```json
{
  "success": true,
  "symbols": [
    {
      "id": 0,
      "symbol": "BTC/USD",
      "group": "crypto",
      "maxLeverage": 150
    },
    {
      "id": 1,
      "symbol": "ETH/USD",
      "group": "crypto",
      "maxLeverage": 100
    }
  ],
  "groupedSymbols": {
    "crypto": [
      { "id": 0, "symbol": "BTC/USD", "group": "crypto", "maxLeverage": 150 },
      { "id": 1, "symbol": "ETH/USD", "group": "crypto", "maxLeverage": 100 }
    ],
    "forex": [...]
  },
  "count": 45
}
```

### Get LunarCrush Market Data

Retrieve cached LunarCrush market metrics for a specific symbol. This data includes social sentiment, price changes, volatility, and market rankings.

> **⚠️ Dependency**: You must call the `/symbols` endpoint first to get the exact symbol string (e.g., `"BTC/USD"`). The symbol parameter requires an exact match.

```bash
# First, get available symbols
SYMBOL=$(curl -s -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/symbols" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" | jq -r '.symbols[0].symbol')

# Then, get LunarCrush data for that symbol
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/lunarcrush?symbol=${SYMBOL}" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

**Response:**
```json
{
  "success": true,
  "symbol": "BTC/USD",
  "lunarcrush": {
    "galaxy_score": 72.5,
    "alt_rank": 1,
    "social_volume_24h": 15234,
    "sentiment": 68.3,
    "percent_change_24h": 2.45,
    "volatility": 0.032,
    "price": "95000.12345678",
    "volume_24h": "45000000000.00000000",
    "market_cap": "1850000000000.00000000",
    "market_cap_rank": 1,
    "social_dominance": 45.2,
    "market_dominance": 52.1,
    "interactions_24h": 890000,
    "galaxy_score_previous": 70.1,
    "alt_rank_previous": 1
  },
  "updated_at": "2026-02-14T08:30:00.000Z"
}
```

**LunarCrush Field Descriptions:**

| Field | Type | Description |
|-------|------|-------------|
| `galaxy_score` | Float | Overall coin quality score (0-100) combining social, market, and developer activity |
| `alt_rank` | Int | Rank among all cryptocurrencies (lower is better, 1 = best) |
| `social_volume_24h` | Float | Social media mentions in last 24 hours |
| `sentiment` | Float | Market sentiment score (0-100, 50 is neutral, >50 is bullish) |
| `percent_change_24h` | Float | Price change percentage in last 24 hours |
| `volatility` | Float | Price volatility score (0-1, <0.02 stable, 0.02-0.05 normal, >0.05 risky) |
| `price` | String | Current price in USD (decimal string for precision) |
| `volume_24h` | String | Trading volume in last 24 hours (decimal string) |
| `market_cap` | String | Market capitalization (decimal string) |
| `market_cap_rank` | Int | Rank by market cap (lower is better) |
| `social_dominance` | Float | Social volume relative to total market |
| `market_dominance` | Float | Market cap relative to total market |
| `interactions_24h` | Float | Social media interactions in last 24 hours |
| `galaxy_score_previous` | Float | Previous galaxy score (for trend analysis) |
| `alt_rank_previous` | Int | Previous alt rank (for trend analysis) |

**Data Freshness:**
- LunarCrush data is cached and updated periodically by a background worker
- Check the `updated_at` field to see when the data was last refreshed
- Data is typically refreshed every few hours

### Get Account Balance

Retrieve USDC and ETH balance for the user's Ostium wallet address.

> **⚠️ Dependency**: The `address` field is the user's Ostium wallet address (`user_wallet`). You MUST fetch it from `/club-details` first — do NOT hardcode or assume any address.

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/balance" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{"address": "0x..."}"
```

**Response:**
```json
{
  "success": true,
  "address": "0x...",
  "usdcBalance": "1000.50",
  "ethBalance": "0.045"
}
```

### Get Portfolio Positions

Get all open positions for the user's Ostium trading account. **This endpoint is critical** — it returns `tradeIndex`, `pairIndex`, and `entryPrice` which are required for closing positions and setting TP/SL.

> **⚠️ Dependency**: The `address` field must come from `/club-details` → `user_wallet`. NEVER guess it.
>
> **🔑 This endpoint provides values needed by**: `/close-position` (needs `tradeIndex`), `/set-take-profit` (needs `tradeIndex`, `pairIndex`, `entryPrice`), `/set-stop-loss` (needs `tradeIndex`, `pairIndex`, `entryPrice`).

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/positions" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d "{"address": "0x..."}"
```

**Request Body:**
```json
{
  "address": "0x..."  // REQUIRED — from /club-details → user_wallet. NEVER guess this.
}
```

**Response:**
```json
{
  "success": true,
  "positions": [
    {
      "market": "BTC",
      "marketFull": "BTC/USD",
      "side": "long",
      "collateral": 100.0,
      "entryPrice": 95000.0,
      "leverage": 10.0,
      "tradeId": "12345",
      "tradeIndex": 2,
      "pairIndex": "0",
      "notionalUsd": 1000.0,
      "totalFees": 2.50,
      "stopLossPrice": 85500.0,
      "takeProfitPrice": 0.0
    }
  ],
  "totalPositions": 1
}
```

> **Key fields to extract from each position:**
> - `tradeIndex` — needed for `/close-position`, `/set-take-profit`, `/set-stop-loss`
> - `pairIndex` — needed for `/set-take-profit`, `/set-stop-loss`
> - `entryPrice` — needed for `/set-take-profit`, `/set-stop-loss`
> - `side` — needed for `/set-take-profit`, `/set-stop-loss`
```

### Get Position History

Get raw trading history for an address (includes open, close, cancelled orders, etc.).

**Note:** The user's Ostium wallet address can be fetched from the `/api/lazy-trading/programmatic/club-details` endpoint (see Get Account Balance section above).

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/history" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"address": "0x...", "count": 50}'
```

**Request Body:**
```json
{
  "address": "0x...",  // User's Ostium wallet address (required)
  "count": 50           // Number of recent orders to retrieve (default: 50)
}
```

**Response:**
```json
{
  "success": true,
  "history": [
    {
      "market": "ETH",
      "side": "long",
      "collateral": 50.0,
      "leverage": 5,
      "price": 3200.0,
      "pnlUsdc": 15.50,
      "profitPercent": 31.0,
      "totalProfitPercent": 31.0,
      "rolloverFee": 0.05,
      "fundingFee": 0.10,
      "executedAt": "2025-02-10T15:30:00Z",
      "tradeId": "trade_123"
    }
  ],
  "count": 25
}
```

### Open Position

Open a new perpetual futures position on Ostium.

> **⚠️ Dependencies — ALL must be resolved BEFORE calling this endpoint:**
> 1. `agentAddress` → from `/club-details` → `ostium_agent_address` (NEVER guess)
> 2. `userAddress` → from `/club-details` → `user_wallet` (NEVER guess)
> 3. `market` → validate via `/symbols` endpoint if unsure the token exists
>    - If `/symbols` returns `ETH/USD`, pass `market: "ETH"` to `/open-position` (not `ETH/USD`)
> 4. `side`, `collateral`, `leverage` → **ASK the user explicitly**, do not assume
>
> **📊 Recommended Pre-Trade Flow:**
> 1. Call `/lunarcrush?symbol=TOKEN/USD` or `/market-data` to get market conditions
> 2. Present the market data to the user (price, sentiment, volatility)
> 3. Ask the user: "Do you want to proceed? Specify: collateral (USDC), leverage, long/short"
> 4. Only after user confirms → call `/open-position`
>
> **🔐 Verification Note:** Every trade is analyzed by EigenAI for alignment with market conditions. Users can verify the cryptographic signatures and reasoning for all their trades at [maxxit.ai/openclaw](https://www.maxxit.ai/openclaw).
>
> **🔑 SAVE the response** — `actualTradeIndex` and `entryPrice` are needed for setting TP/SL later.

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/open-position" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "agentAddress": "0x...",
    "userAddress": "0x...",
    "market": "BTC",
    "side": "long",
    "collateral": 100,
    "leverage": 10
  }'
```

**Request Body:**
```json
{
  "agentAddress": "0x...",      // REQUIRED — from /club-details → ostium_agent_address. NEVER guess.
  "userAddress": "0x...",       // REQUIRED — from /club-details → user_wallet. NEVER guess.
  "market": "BTC",              // REQUIRED — Base token only for Ostium (e.g. "ETH", not "ETH/USD"). Validate via /symbols if unsure.
  "side": "long",               // REQUIRED — "long" or "short". ASK the user.
  "collateral": 100,            // REQUIRED — Collateral in USDC. ASK the user.
  "leverage": 10,               // Optional (default: 10). ASK the user.
  "deploymentId": "uuid...",    // Optional — associated deployment ID
  "signalId": "uuid...",        // Optional — associated signal ID
  "isTestnet": false            // Optional (default: false)
}
```

**Response (IMPORTANT — save these values):**
```json
{
  "success": true,
  "orderId": "order_123",
  "tradeId": "trade_abc",
  "transactionHash": "0x...",
  "txHash": "0x...",
  "status": "OPEN",
  "message": "Position opened successfully",
  "actualTradeIndex": 2,       // ← SAVE THIS — needed for /set-take-profit and /set-stop-loss
  "entryPrice": 95000.0,        // ← SAVE THIS — needed for /set-take-profit and /set-stop-loss
  "reasoning": "Market sentiment is bullish...", // EigenAI trade alignment analysis
  "llmSignature": "0x..."       // Cryptographic signature for auditability
}
```

### Close Position

Close an existing perpetual futures position on Ostium.

> **⚠️ Dependencies — resolve BEFORE calling this endpoint:**
> 1. `agentAddress` → from `/club-details` → `ostium_agent_address`
> 2. `userAddress` → from `/club-details` → `user_wallet`
> 3. `tradeIndex` → call `/positions` first to find the position you want to close, then use its `tradeIndex`
>
> **NEVER guess the `tradeIndex` or `tradeId`.** Always fetch from `/positions` endpoint.

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/close-position" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "agentAddress": "0x...",
    "userAddress": "0x...",
    "market": "BTC",
    "tradeId": "12345"
  }'
```

**Request Body:**
```json
{
  "agentAddress": "0x...",      // REQUIRED — from /club-details → ostium_agent_address. NEVER guess.
  "userAddress": "0x...",       // REQUIRED — from /club-details → user_wallet. NEVER guess.
  "market": "BTC",              // REQUIRED — Token symbol
  "tradeId": "12345",           // Optional — from /positions → tradeId
  "actualTradeIndex": 2,         // Highly recommended — from /positions → tradeIndex. NEVER guess.
  "isTestnet": false            // Optional (default: false)
}
```

**Response:**
```json
{
  "success": true,
  "result": {
    "txHash": "0x...",
    "market": "BTC",
    "closePnl": 25.50
  },
  "closePnl": 25.50,
  "message": "Position closed successfully",
  "alreadyClosed": false
}
```

### Set Take Profit

Set or update take-profit level for an existing position on Ostium.

> **⚠️ Dependencies — you need ALL of these before calling:**
> 1. `agentAddress` → from `/club-details` → `ostium_agent_address`
> 2. `userAddress` → from `/club-details` → `user_wallet`
> 3. `tradeIndex` → from `/open-position` response → `actualTradeIndex`, **OR** from `/positions` → `tradeIndex`
> 4. `entryPrice` → from `/open-position` response → `entryPrice`, **OR** from `/positions` → `entryPrice`
> 5. `pairIndex` → from `/positions` → `pairIndex`, **OR** from `/symbols` → symbol `id`
> 6. `takeProfitPercent` → **ASK the user** (default: 0.30 = 30%)
> 7. `side` → from `/positions` → `side` ("long" or "short")
>
> **If you just opened a position:** Use `actualTradeIndex` and `entryPrice` from the `/open-position` response.
> **If the position was opened earlier:** Call `/positions` to fetch `tradeIndex`, `entryPrice`, `pairIndex`, and `side`.

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/set-take-profit" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "agentAddress": "0x...",
    "userAddress": "0x...",
    "market": "BTC",
    "tradeIndex": 2,
    "takeProfitPercent": 0.30,
    "entryPrice": 90000,
    "pairIndex": 0
  }'
```

**Request Body:**
```json
{
  "agentAddress": "0x...",        // REQUIRED — from /club-details. NEVER guess.
  "userAddress": "0x...",         // REQUIRED — from /club-details. NEVER guess.
  "market": "BTC",                // REQUIRED — Token symbol
  "tradeIndex": 2,                // REQUIRED — from /open-position or /positions. NEVER guess.
  "takeProfitPercent": 0.30,       // Optional (default: 0.30 = 30%). ASK the user.
  "entryPrice": 90000,             // REQUIRED — from /open-position or /positions. NEVER guess.
  "pairIndex": 0,                  // REQUIRED — from /positions or /symbols. NEVER guess.
  "side": "long",                  // Optional (default: "long") — from /positions.
  "isTestnet": false              // Optional (default: false)
}
```

**Response:**
```json
{
  "success": true,
  "message": "Take profit set successfully",
  "tpPrice": 117000.0
}
```

### Set Stop Loss

Set or update stop-loss level for an existing position on Ostium.

> **⚠️ Dependencies — identical to Set Take Profit. You need ALL of these before calling:**
> 1. `agentAddress` → from `/club-details` → `ostium_agent_address`
> 2. `userAddress` → from `/club-details` → `user_wallet`
> 3. `tradeIndex` → from `/open-position` response → `actualTradeIndex`, **OR** from `/positions` → `tradeIndex`
> 4. `entryPrice` → from `/open-position` response → `entryPrice`, **OR** from `/positions` → `entryPrice`
> 5. `pairIndex` → from `/positions` → `pairIndex`, **OR** from `/symbols` → symbol `id`
> 6. `stopLossPercent` → **ASK the user** (default: 0.10 = 10%)
> 7. `side` → from `/positions` → `side` ("long" or "short")
>
> **If you just opened a position:** Use `actualTradeIndex` and `entryPrice` from the `/open-position` response.
> **If the position was opened earlier:** Call `/positions` to fetch `tradeIndex`, `entryPrice`, `pairIndex`, and `side`.

```bash
# Same dependency resolution as Set Take Profit (see above for full example)
# Step 1: Get addresses from /club-details
# Step 2: Get position details from /positions
# Step 3: Set stop loss with user-specified stopLossPercent

curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/set-stop-loss" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "agentAddress": "0x...",
    "userAddress": "0x...",
    "market": "BTC",
    "tradeIndex": 2,
    "stopLossPercent": 0.10,
    "entryPrice": 90000,
    "pairIndex": 0,
    "side": "long"
  }'
```

**Request Body:**
```json
{
  "agentAddress": "0x...",        // REQUIRED — from /club-details. NEVER guess.
  "userAddress": "0x...",         // REQUIRED — from /club-details. NEVER guess.
  "market": "BTC",                // REQUIRED — Token symbol
  "tradeIndex": 2,                // REQUIRED — from /open-position or /positions. NEVER guess.
  "stopLossPercent": 0.10,         // Optional (default: 0.10 = 10%). ASK the user.
  "entryPrice": 90000,             // REQUIRED — from /open-position or /positions. NEVER guess.
  "pairIndex": 0,                  // REQUIRED — from /positions or /symbols. NEVER guess.
  "side": "long",                  // Optional (default: "long") — from /positions.
  "isTestnet": false              // Optional (default: false)
}
```

**Response:**
```json
{
  "success": true,
  "message": "Stop loss set successfully",
  "slPrice": 81000.0,
  "liquidationPrice": 85500.0,
  "adjusted": false
}
```

### Get All Market Data

Retrieve the complete market snapshot from Ostium, including all symbols and their full LunarCrush metrics. This is highly recommended for AI agents that want to perform market-wide scanning or analysis in a single request.

```bash
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/market-data" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

**Response:**
```json
{
  "success": true,
  "data": [
    {
      "id": 0,
      "symbol": "BTC/USD",
      "group": "crypto",
      "maxLeverage": 150,
      "metrics": {
        "galaxy_score": 72.5,
        "alt_rank": 1,
        "social_volume_24h": 15234,
        "sentiment": 68.3,
        "percent_change_24h": 2.45,
        "volatility": 0.032,
        "price": "95000.12345678",
        "volume_24h": "45000000000.00000000",
        "market_cap": "1850000000000.00000000",
        "market_cap_rank": 1,
        "social_dominance": 45.2,
        "market_dominance": 52.1,
        "interactions_24h": 890000,
        "galaxy_score_previous": 70.1,
        "alt_rank_previous": 1
      },
      "updated_at": "2026-02-14T08:30:00.000Z"
    },
    ...
  ],
  "count": 45
}
```

### Get Token Price

Fetch the current market price for a token from Ostium price feed.

```bash
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/price?token=BTC&isTestnet=false" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

**Query Parameters:**
| Parameter | Type | Required | Description |
|-----------|-------|----------|-------------|
| `token` | string | Yes | Token symbol to fetch price for (e.g., BTC, ETH, SOL) |
| `isTestnet` | boolean | No | Use testnet price feed (default: false) |

**Response:**
```json
{
  "success": true,
  "token": "BTC",
  "price": 95000.0,
  "isMarketOpen": true,
  "isDayTradingClosed": false
}
```

### Discover Traders to Copy (Copy Trading — Step 1)

Discover other OpenClaw Traders and top-performing traders to potentially copy-trade. This is the **first step** in the copy-trading workflow — the returned wallet addresses are used as the `address` parameter in the `/copy-trader-trades` endpoint.

> **⚠️ Dependency Chain**: This endpoint provides the wallet addresses needed by `/copy-trader-trades`. You MUST call this endpoint FIRST to get trader addresses — do NOT guess or hardcode addresses.
>
> **🚫 Self-copy guard**: Never use your own `user_wallet` from `/club-details` as a copy-trader address.

```bash
# Get all traders (OpenClaw + Leaderboard)
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/copy-traders" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"

# Get only OpenClaw Traders (prioritized)
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/copy-traders?source=openclaw" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"

# Get only Leaderboard traders with filters
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/copy-traders?source=leaderboard&minImpactFactor=50&minTrades=100" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `source` | string | `all` | `openclaw` (OpenClaw agents only), `leaderboard` (top traders only), `all` (both) |
| `limit` | int | 20 | Max results per tier (max 100) |
| `minTrades` | int | — | Min trade count filter (leaderboard only) |
| `minImpactFactor` | float | — | Min impact factor filter (leaderboard only) |

**Response:**
```json
{
  "success": true,
  "openclawTraders": [
    {
      "agentId": "3dbc322f-...",
      "agentName": "OpenClaw Trader - 140226114735",
      "creatorWallet": "0x4e7f1e29d9e1f81c3e9249e3444843c2006f3325",
      "venue": "OSTIUM",
      "status": "PRIVATE",
      "isCopyTradeClub": false,
      "performance": {
        "apr30d": 0,
        "apr90d": 0,
        "aprSinceInception": 0,
        "sharpe30d": 0
      },
      "deployment": {
        "id": "dep-uuid",
        "status": "ACTIVE",
        "safeWallet": "0x...",
        "isTestnet": false
      }
    }
  ],
  "topTraders": [
    {
      "walletAddress": "0xabc...",
      "totalVolume": "1500000.000000",
      "totalClosedVolume": "1200000.000000",
      "totalPnl": "85000.000000",
      "totalProfitTrades": 120,
      "totalLossTrades": 30,
      "totalTrades": 150,
      "winRate": 0.80,
      "lastActiveAt": "2026-02-15T10:30:00.000Z",
      "scores": {
        "edgeScore": 0.82,
        "consistencyScore": 0.75,
        "stakeScore": 0.68,
        "freshnessScore": 0.92,
        "impactFactor": 72.5
      },
      "updatedAt": "2026-02-17T06:00:00.000Z"
    }
  ],
  "openclawCount": 5,
  "topTradersCount": 20
}
```

**Key fields to use in next steps:**
- `openclawTraders[].creatorWallet` → use as `address` in `/copy-trader-trades`
- `topTraders[].walletAddress` → use as `address` in `/copy-trader-trades`
- Exclude any address equal to your own `/club-details.user_wallet`

### Get Trader's Recent Trades (Copy Trading — Step 2)

Fetch recent on-chain trades for a specific trader address. This queries the Ostium subgraph in real-time for fresh trade data.

> **⚠️ Dependency**: The `address` parameter MUST come from the `/copy-traders` endpoint response:
> - For OpenClaw traders: use `creatorWallet` from `openclawTraders[]`
> - For leaderboard traders: use `walletAddress` from `topTraders[]`
>
> **NEVER guess or hardcode the address.** Always call `/copy-traders` first.

```bash
# Step 1: Discover traders first
TRADER_ADDRESS=$(curl -s -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/copy-traders?source=openclaw" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" | jq -r '.openclawTraders[0].creatorWallet')

# Step 2: Fetch their recent trades
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/copy-trader-trades?address=${TRADER_ADDRESS}" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"

# With custom lookback and limit
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/copy-trader-trades?address=${TRADER_ADDRESS}&hours=48&limit=50" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

**Query Parameters:**
| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `address` | string | *required* | Trader wallet address (from `/copy-traders`) |
| `limit` | int | 20 | Max trades to return (max 50) |
| `hours` | int | 24 | Lookback window in hours (max 168 / 7 days) |

**Response:**
```json
{
  "success": true,
  "traderAddress": "0x4e7f1e29d9e1f81c3e9249e3444843c2006f3325",
  "trades": [
    {
      "tradeId": "0x123...",
      "side": "LONG",
      "tokenSymbol": "BTC",
      "pair": "BTC/USD",
      "collateral": 500.00,
      "leverage": 10.0,
      "entryPrice": 95000.50,
      "takeProfitPrice": 100000.00,
      "stopLossPrice": 90000.00,
      "timestamp": "2026-02-17T14:30:00.000Z"
    }
  ],
  "count": 5,
  "lookbackHours": 24
}
```

**Trade Field Descriptions:**
| Field | Description |
|-------|-------------|
| `side` | `"LONG"` or `"SHORT"` — the trade direction |
| `tokenSymbol` | Token being traded (e.g., `BTC`, `ETH`) |
| `pair` | Full pair label (e.g., `BTC/USD`) |
| `collateral` | USDC amount used as collateral |
| `leverage` | Leverage multiplier (e.g., 10.0 = 10x) |
| `entryPrice` | Price at which the trade was opened |
| `takeProfitPrice` | Take profit price (null if not set) |
| `stopLossPrice` | Stop loss price (null if not set) |
| `timestamp` | When the trade was opened |

> **Next step**: After reviewing the trades, use `/open-position` to open a similar position. You'll need your own `agentAddress` and `userAddress` from `/club-details`.

## Signal Format Examples

The lazy trading system processes natural language trading signals. Here are examples:

### Opening Positions
- `"Long ETH with 5x leverage, entry at 3200"`
- `"Short BTC 10x, TP 60000, SL 68000"`
- `"Buy 100 USDC worth of ETH perpetual"`

### With Risk Management
- `"Long SOL 3x leverage, entry 150, take profit 180, stop loss 140"`
- `"Short AVAX 5x, risk 2% of portfolio"`

### Closing Positions
- `"Close ETH long position"`
- `"Take profit on BTC short"`

---

## Complete Workflow Examples

These are the mandatory step-by-step workflows for common trading operations. **Follow these exactly.**

### Workflow 1: Opening a New Position (Full Flow)

```
Step 1: GET /club-details
   → Extract: user_wallet (→ userAddress), ostium_agent_address (→ agentAddress)
   → Cache these for the session

Step 2: GET /symbols
   → Verify the user's requested token is available on Ostium
   → Extract exact symbol string and maxLeverage
   → Convert pair format to market token for /open-position:
     "ETH/USD" -> "ETH"

Step 3: GET /lunarcrush?symbol=TOKEN/USD  (or GET /market-data for all)
   → Get market data: price, sentiment, volatility, galaxy_score
   → Present this data to the user:
     "BTC is currently at $95,000 with sentiment 68.3 (bullish) and volatility 0.032 (normal).
      Galaxy Score: 72.5/100. Do you want to proceed?"

Step 4: ASK the user for trade parameters
   → "Please confirm: collateral (USDC), leverage, long or short?"
   → "Would you like to set TP and SL? If so, what percentages?"
   → Wait for explicit user confirmation before proceeding

Step 5: POST /open-position
   → Use agentAddress and userAddress from Step 1
   → Use market, side, collateral, leverage from Step 4
   → IMPORTANT: Pass market as base token only (e.g. ETH), not pair format (ETH/USD)
   → SAVE the response: actualTradeIndex and entryPrice

Step 6 (if user wants TP/SL): POST /set-take-profit and/or POST /set-stop-loss
   → Use tradeIndex = actualTradeIndex from Step 5
   → Use entryPrice from Step 5
   → For pairIndex, use the symbol id from Step 2 or call /positions
   → Use takeProfitPercent/stopLossPercent from Step 4

Step 7: ASK — "Would you like to list this trade as alpha on the marketplace?"
   → If user says NO → Done.
   → If user says YES → Continue to Step 8.
   → Also ask: "What price in USDC would you like to charge?" (e.g. 5 USDC)

Step 8: POST /alpha/generate-proof
   → Body: { "tradeId": "{tradeId from Step 5}", "autoProcess": false }
   → tradeId comes from the /open-position response
   → autoProcess: false queues the proof for the worker (~3-5 min)
   → SAVE: proofId from the response

Step 9: Wait for proof verification
   → If autoProcess was true and response has status: "VERIFIED" → go to Step 10
   → If autoProcess was false or status is still PENDING/PROVING:
     Poll GET /alpha/proof-status?proofId={proofId} every 10 seconds
     → Wait until status === "VERIFIED"
     → If status === "FAILED" → inform the user and stop

Step 10: POST /alpha/flag
   → Body: {
       "proofId": "{proofId from Step 8}",
       "priceUsdc": {price from Step 7},
       "token": "{market from Step 5, e.g. ETH}",
       "side": "{side from Step 5, e.g. long}",
       "leverage": {leverage from Step 5}
     }
   → Show user the response: listingId, tradeId, proofMetrics
   → "Your trade is now listed as alpha! Listing ID: {listingId}"
```

### Workflow 2: Closing an Existing Position

```
Step 1: GET /club-details
   → Extract: user_wallet, ostium_agent_address

Step 2: POST /positions (address = user_wallet from Step 1)
   → List all open positions
   → Present them to the user if multiple: "You have 3 open positions: BTC long, ETH short, SOL long. Which one do you want to close?"
   → Extract the tradeIndex for the position to close

Step 3: POST /close-position
   → Use agentAddress and userAddress from Step 1
   → Use market and actualTradeIndex from Step 2
   → Show the user the closePnl from the response
```

### Workflow 3: Setting TP/SL on an Existing Position

```
Step 1: GET /club-details
   → Extract: user_wallet, ostium_agent_address

Step 2: POST /positions (address = user_wallet from Step 1)
   → Find the target position
   → Extract: tradeIndex, entryPrice, pairIndex, side

Step 3: ASK the user
   → "Position: BTC long at $95,000. Current TP: none, SL: $85,500."
   → "What TP% and SL% would you like to set?"

Step 4: POST /set-take-profit and/or POST /set-stop-loss
   → Use ALL values from Steps 1-3 — NEVER guess any of them
```

### Workflow 4: Checking Portfolio & Market Overview

```
Step 1: GET /club-details
   → Extract: user_wallet

Step 2: POST /balance (address = user_wallet)
   → Show the user their USDC and ETH balances

Step 3: POST /positions (address = user_wallet)
   → Show all open positions with PnL details

Step 4 (optional): GET /market-data
   → Show market conditions for tokens they hold
```

### Workflow 5: Copy-Trading Another OpenClaw Agent (Full Flow)

```
Step 1: GET /copy-traders?source=openclaw
   → Discover other OpenClaw Trader agents
   → Extract: creatorWallet from the trader you want to copy
   → Exclude your own wallet (`/club-details.user_wallet`) if it appears
   → IMPORTANT: This is a REQUIRED first step — you cannot call
     /copy-trader-trades without an address from this endpoint

Step 2: GET /copy-trader-trades?address={creatorWallet}
   → Fetch recent trades for that trader from the Ostium subgraph
   → Review: side (LONG/SHORT), tokenSymbol, leverage, collateral, entry price
   → Decide: "Should I copy this trade?"
   → DEPENDENCY: The address param comes from Step 1 (creatorWallet or walletAddress)

Step 3: GET /club-details
   → Get YOUR OWN userAddress (user_wallet) and agentAddress (ostium_agent_address)
   → These are needed to execute your own trade

Step 4: POST /open-position
   → Mirror the trade from Step 2 using your own addresses from Step 3:
     - market = tokenSymbol from the copied trade
     - side = side from the copied trade (LONG/SHORT → long/short)
     - collateral = decide based on your own risk tolerance
     - leverage = match the copied trader's leverage or adjust
   → SAVE: actualTradeIndex and entryPrice from response

Step 5 (optional): POST /set-take-profit and/or POST /set-stop-loss
   → Use actualTradeIndex and entryPrice from Step 4
   → Match the copied trader's TP/SL ratios or set your own
```

**Dependency Chain Summary:**
```
/copy-traders → provides address → /copy-trader-trades → provides trade details
/club-details → provides your addresses → /open-position → copies the trade
```

---

## Aster DEX (BNB Chain) Endpoints

> Aster DEX is a perpetual futures exchange on BNB Chain. Use Aster endpoints when the user wants to trade on BNB Chain. The Aster API uses **API Key + Secret** authentication (stored server-side) — you do NOT need `agentAddress`. You only need `userAddress` from `/club-details`.

### Venue Selection

| Venue | Chain | Symbol Format | Auth Required | When to Use |
|-------|-------|--------------|---------------|-------------|
| **Ostium** | Arbitrum (mainnet only) | `BTC`, `ETH` | `agentAddress` + `userAddress` | Default for most trades |
| **Aster** | BNB Chain (testnet only) | `BTCUSDT`, `ETHUSDT` | `userAddress` only | When user specifies BNB Chain or Aster |

> **Network behavior rule:** Do not ask users to choose mainnet/testnet for these venues. Ostium is fixed to mainnet and Aster is fixed to testnet in this environment.

**How to check if Aster is configured:** In the `/club-details` response, `aster_configured: true` means the user has set up Aster API keys. If `false`, direct them to set up Aster at maxxit.ai/openclaw.

### Aster Symbols

Aster uses Binance-style symbol format: `BTCUSDT`, `ETHUSDT`, etc. The API auto-appends `USDT` if you pass just `BTC`.

```bash
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/symbols" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

**Response:**
```json
{
  "success": true,
  "symbols": [
    {
      "symbol": "BTCUSDT",
      "baseAsset": "BTC",
      "quoteAsset": "USDT",
      "pricePrecision": 2,
      "quantityPrecision": 3,
      "contractType": "PERPETUAL",
      "status": "TRADING"
    }
  ],
  "count": 50
}
```

### Aster Price

```bash
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/price?token=BTC" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

**Response:**
```json
{
  "success": true,
  "token": "BTC",
  "symbol": "BTCUSDT",
  "price": 95000.50
}
```

### Aster Market Data

```bash
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/market-data?symbol=BTC" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```

### Aster Balance

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/balance" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x..."
  }'
```

**Request Body:**
```json
{
  "userAddress": "0x..."    // REQUIRED — from /club-details → user_wallet. NEVER guess.
}
```

**Response:**
```json
{
  "success": true,
  "balance": 1000.50,
  "availableBalance": 800.25,
  "unrealizedProfit": 50.10
}
```

### Aster Positions

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/positions" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x..."
  }'
```

**Response:**
```json
{
  "success": true,
  "positions": [
    {
      "symbol": "BTCUSDT",
      "positionAmt": 0.01,
      "entryPrice": 95000.0,
      "markPrice": 96000.0,
      "unrealizedProfit": 10.0,
      "liquidationPrice": 80000.0,
      "leverage": 10,
      "side": "long"
    }
  ],
  "count": 1
}
```

### Aster History (All Orders)

Fetch full order history for a symbol (includes active, canceled, and filled orders) from Aster.

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/history" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x...",
    "symbol": "BTC",
    "limit": 100
  }'
```

**Request Body:**
```json
{
  "userAddress": "0x...",        // REQUIRED — from /club-details → user_wallet
  "symbol": "BTC",               // REQUIRED — token or full symbol (BTC or BTCUSDT)
  "limit": 100,                  // Optional — default depends on exchange (max 1000)
  "orderId": 12345,              // Optional — fetch from this orderId onward
  "startTime": 1709251200000,    // Optional — ms timestamp
  "endTime": 1709856000000       // Optional — ms timestamp
}
```

> `POST /api/lazy-trading/programmatic/aster/history` now proxies to Aster `/fapi/v3/allOrders`.
> Use this endpoint when users ask for "all old trades/orders", "order history", or "past orders" on Aster.

### Aster Open Position

> **📋 LLM Pre-Call Checklist — Ask the user these questions before calling this endpoint:**
> 1. **Symbol**: "Which token do you want to trade?" (e.g. BTC, ETH, SOL)
> 2. **Side**: "Long or short?"
> 3. **Quantity**: "How much [TOKEN] do you want to trade?" — get the answer in base asset units (e.g. `0.01 BTC`, `0.5 ETH`).
> 4. **Leverage**: "What leverage? (e.g. 10x)"
> 5. **Order type**: "Market order or limit order?" (default: MARKET). If LIMIT, also ask for the limit price.
>
> **Aster requires `quantity` (base asset) for open-position. Do not use collateral.**
> **NEVER call this endpoint without a confirmed `quantity` in base asset units.**

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/open-position" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x...",
    "symbol": "BTC",
    "side": "long",
    "quantity": 0.01,
    "leverage": 10
  }'
```

**Request Body:**
```json
{
  "userAddress": "0x...",     // REQUIRED — from /club-details → user_wallet. NEVER guess.
  "symbol": "BTC",           // REQUIRED — Token name or full symbol (BTCUSDT). ASK the user.
  "side": "long",            // REQUIRED — "long" or "short". ASK the user.
  "quantity": 0.01,          // REQUIRED — Position size in BASE asset (e.g. 0.01 BTC). ASK the user.
  "leverage": 10,            // Optional — Leverage multiplier. ASK the user.
  "type": "MARKET",          // Optional — "MARKET" (default) or "LIMIT". ASK the user.
  "price": 95000             // Required only for LIMIT orders. ASK the user if type is LIMIT.
}
```

> ⚠️ **IMPORTANT:** `quantity` must always be specified in the **base asset** (e.g. `0.01` for 0.01 BTC).  
> If the user provides a USDT/collateral amount, ask them to provide the exact token quantity instead.  
> Do not convert collateral to quantity in this workflow.

**Response (IMPORTANT — save these values):**
```json
{
  "success": true,
  "orderId": 12345678,
  "symbol": "BTCUSDT",
  "side": "BUY",
  "status": "FILLED",
  "avgPrice": "95000.50",
  "executedQty": "0.010",
  "message": "Position opened: long BTCUSDT"
}
```

### Aster Close Position

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/close-position" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x...",
    "symbol": "BTC"
  }'
```

**Request Body:**
```json
{
  "userAddress": "0x...",    // REQUIRED
  "symbol": "BTC",          // REQUIRED
  "quantity": 0.005         // Optional — omit to close full position
}
```

### Aster Set Take Profit

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/set-take-profit" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x...",
    "symbol": "BTC",
    "takeProfitPercent": 0.30,
    "entryPrice": 95000,
    "side": "long"
  }'
```

**Request Body (two options):**
```json
{
  "userAddress": "0x...",
  "symbol": "BTC",
  "stopPrice": 123500          // Option A: exact trigger price
}
```
```json
{
  "userAddress": "0x...",
  "symbol": "BTC",
  "takeProfitPercent": 0.30,   // Option B: percentage (0.30 = 30%)
  "entryPrice": 95000,
  "side": "long"
}
```

### Aster Set Stop Loss

Same pattern as take profit:

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/set-stop-loss" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x...",
    "symbol": "BTC",
    "stopLossPercent": 0.10,
    "entryPrice": 95000,
    "side": "long"
  }'
```

### Aster Change Leverage

```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/aster/change-leverage" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "userAddress": "0x...",
    "symbol": "BTC",
    "leverage": 20
  }'
```

### Aster Parameter Dependency Graph

| Parameter | Source | How to Get |
|-----------|--------|-----------|
| `userAddress` | `/club-details` → `user_wallet` | `GET /club-details` |
| `aster_configured` | `/club-details` → `aster_configured` | `GET /club-details` (must be `true`) |
| `symbol` | User specifies token | User input (auto-resolved: `BTC` → `BTCUSDT`) |
| `side` | User specifies `"long"` or `"short"` | User input (required) |
| `quantity` | User specifies in base asset units (e.g. `0.01 BTC`) | User input (required). If user provides USDT/collateral amount, ask for quantity instead. Do not calculate in the workflow. |
| `leverage` | User specifies | User input |
| `entryPrice` | `/aster/positions` → `entryPrice` | From position data |
| `stopPrice` | User specifies or calculated from percent | User input or calculated |

### Aster Workflow: Open Position on BNB Chain

```
Step 1: GET /club-details
   → Extract: user_wallet
   → Check: aster_configured == true (if false, tell user to set up Aster at maxxit.ai/openclaw)

Step 2: GET /aster/symbols
   → Verify the token is available on Aster

Step 3: GET /aster/price?token=BTC
   → Get current price, present to user

Step 4: ASK the user for ALL trade parameters
   → "Which token?" (e.g. BTC, ETH, SOL)
   → "Long or short?"
   → "How much [TOKEN] do you want to buy/sell?" — collect answer in BASE asset units (e.g. 0.01 BTC)
       • If user gives a USDT/collateral amount, ask them to provide token quantity instead.
   → "Leverage? (e.g. 10x)"
   → "Market or limit order?" — if LIMIT, also ask for the limit price

Step 5: POST /aster/open-position
   → Use userAddress from Step 1
   → Use symbol, side, quantity (base asset), leverage from Step 4
   → SAVE orderId and avgPrice from response

Step 6 (if user wants TP/SL): POST /aster/set-take-profit and/or POST /aster/set-stop-loss
   → Use entryPrice = avgPrice from Step 5
   → Use side from Step 4
   → Ask user for takeProfitPercent / stopLossPercent (or exact stopPrice)
```

### Aster Workflow: Close Position

```
Step 1: GET /club-details → Extract user_wallet

Step 2: POST /aster/positions (userAddress = user_wallet)
   → Show positions to user, let them pick which to close

Step 3: POST /aster/close-position
   → Pass userAddress and symbol
   → Omit quantity to close full position
```

---

## Alpha Marketplace (Arbitrum Sepolia)

Trustless ZK-verified trading signals. **Producers** generate proofs and flag positions as alpha; **consumers** discover agents by commitment, purchase alpha via x402, verify content, and execute.

**Base path:** `${MAXXIT_API_URL}/api/lazy-trading/programmatic/alpha/*`  
**Auth:** `X-API-KEY` header (same as other endpoints).  
**Payment:** On-chain USDC on Arbitrum Sepolia (testnet) or Arbitrum One (mainnet).

**Prerequisites for consuming alpha:**
- User must have completed Lazy Trading setup (agent deployed) — `/club-details` must return `ostium_agent_address`. The `/pay` endpoint uses this agent to send USDC; without it, `/pay` returns 400.
- Agent wallet must hold enough USDC for the listing price. If insufficient, `/pay` returns 402 with `required` and `available` amounts — inform the user to fund the agent address.

### Alpha Endpoints Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/alpha/agents` | GET | Discover agents with verified metrics (commitment, winRate, totalPnl). Query: `minWinRate`, `minTrades`, `limit`. |
| `/alpha/listings` | GET | Browse active alpha listings (metadata + price, no trade content). Query: `commitment`, `maxPrice`, `limit`. |
| `/alpha/purchase/:listingId` | GET | **Phase 1** (no `X-Payment` header): returns 402 + payment details. **Phase 2** (with `X-Payment: txHash`): verifies on-chain, returns alpha. |
| `/alpha/pay/:listingId` | POST | **Payment helper**: sends USDC from your agent on-chain. Returns `txHash`. Call between Phase 1 and Phase 2. |
| `/alpha/verify` | POST | Body: `{ listingId, content }`. Verify purchased content hash matches commitment. |
| `/alpha/execute` | POST | Body: `{ alphaContent, agentAddress, userAddress, collateral, leverageOverride? }`. Execute alpha trade on Ostium. |
| `/alpha/generate-proof` | POST | (Producer) Generate ZK proof of trading performance. Body: `{ tradeId?: string, autoProcess?: boolean }`. Pass `tradeId` to feature a specific trade; omit for most recent open trade. `autoProcess: false` processesed by the worker (~3-5 min). |
| `/alpha/proof-status` | GET | (Producer) Check proof processing status. Query: `proofId`. |
| `/alpha/my-proof` | GET | (Producer) Latest proof status and metrics. |
| `/alpha/flag` | POST | (Producer) Body: `{ proofId, priceUsdc, token, side, leverage? }`. List verified trade as alpha using the proof ID from generate-proof. |

### How x402 Purchase Works (3 API Calls)

> **⚠️ CRITICAL**: To purchase alpha content you MUST call these 3 endpoints in this exact order. Do NOT skip steps. The `/pay` endpoint handles all wallet operations server-side — you do NOT need a private key.

```
Step A:  GET  /alpha/purchase/{listingId}              → 402 + paymentDetails
Step B:  POST /alpha/pay/{listingId}                   → { txHash }
Step C:  GET  /alpha/purchase/{listingId}              → 200 + alpha content
         + Header: X-Payment: {txHash from Step B}
```

**Step A — Get payment details:**
```bash
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/alpha/purchase/{listingId}" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```
Response: `402` with `paymentDetails.price`, `paymentDetails.payTo`, `paymentDetails.network`.  
If response is `200`: you already own this listing — alpha is returned directly, skip to Step 4.

**Step B — Send USDC (server handles everything):**
```bash
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/alpha/pay/{listingId}" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}"
```
Response: `200` with `txHash`, `from`, `to`, `amount`.  
If `alreadyPaid: true`: use the returned `txHash` directly.  
If `402`: insufficient USDC balance — response has `required` and `available` amounts.

**Step C — Retrieve alpha content:**
```bash
curl -L -X GET "${MAXXIT_API_URL}/api/lazy-trading/programmatic/alpha/purchase/{listingId}" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "X-Payment: {txHash from Step B}"
```
Response: `200` with `alpha` object (token, side, leverage, venue, entryPrice), `contentHash`, `payment` receipt.

**SAVE from Step C:** `alpha`, `contentHash`, `listingId` — needed for `/verify` and `/execute`.

**Pass `content` exactly as received:** For `/alpha/verify`, the `content` field must be the exact `alpha` object from Step C. Do not modify keys, values, or key order — the hash is computed using sorted keys and any change will cause verification to fail.

### Alpha Dependency Chain

```
/alpha/agents          → commitment
/alpha/listings        → listingId  (needs commitment)
/alpha/purchase        → 402 paymentDetails  (needs listingId)
/alpha/pay             → txHash  (needs listingId)
/alpha/purchase        → alpha content  (needs listingId + txHash in X-Payment header)
/alpha/verify          → verified  (needs listingId + alpha content)
/club-details          → agentAddress, userAddress
/alpha/execute         → trade result  (needs alpha + addresses + collateral)
```

### Workflow: Consuming Alpha (Complete Flow)

```
Step 1: GET /alpha/agents
   → Pick an agent by commitment, winRate, totalPnl
   → SAVE: commitment

Step 2: GET /alpha/listings?commitment={commitment}
   → Browse listings, pick one
   → SAVE: listingId

Step 3a: GET /alpha/purchase/{listingId}
   → If 200: already purchased, skip to Step 4
   → If 402: need to pay → go to Step 3b

Step 3b: POST /alpha/pay/{listingId}
   → Server sends USDC from your agent to the producer
   → If 402: insufficient USDC balance → fund your agent wallet and retry
   → If alreadyPaid: use the returned txHash
   → SAVE: txHash

Step 3c: GET /alpha/purchase/{listingId}
   → Header: X-Payment: {txHash from Step 3b}
   → SAVE: alpha, contentHash, listingId

Step 4: POST /alpha/verify
   → Body: { "listingId": "...", "content": { ...alpha from Step 3c } }
   → Check: verified === true

Step 5: GET /club-details
   → Extract: user_wallet → userAddress
   → Extract: ostium_agent_address → agentAddress

Step 6: POST /alpha/execute
   → Body: { "alphaContent": { ...alpha }, "agentAddress": "...",
             "userAddress": "...", "collateral": 100 }
   → alphaContent must include at least token and side (from alpha)
   → agentAddress = ostium_agent_address, userAddress = user_wallet (both from /club-details)
   → collateral: ask user or use default (e.g. 100 USDC)
   → Check: success === true
```

### Workflow: Producing Alpha

> **⚠️ This is the standalone producer workflow.** If the user just opened a position via Workflow 1, Steps 7-10 already handle alpha listing — you don't need to repeat this. Use this workflow only when the user wants to list an existing open position.

```
Step 1: POST /positions (address = user_wallet from /club-details)
   → List open positions
   → Let user pick which trade to feature
   → SAVE: tradeId, market (token), side, leverage from the chosen position

Step 2: POST /alpha/generate-proof
   → Body: { "tradeId": "{tradeId from Step 1}", "autoProcess": true }
   → SAVE: proofId from response
   → If status is already VERIFIED → go to Step 4

Step 3: Poll GET /alpha/proof-status?proofId={proofId}
   → Wait until status === "VERIFIED"
   → Poll every 10 seconds (max ~5 min)
   → If FAILED → inform user and stop

Step 4: ASK user for price
   → "What USDC price would you like to charge for this alpha?"

Step 5: POST /alpha/flag
   → Body: {
       "proofId": "{proofId from Step 2}",
       "priceUsdc": {price from Step 4},
       "token": "{market from Step 1}",
       "side": "{side from Step 1}",
       "leverage": {leverage from Step 1}
     }
   → Show user: listingId, proofMetrics (tradeCount, winRate, totalPnl)
   → "Your trade is listed as alpha! Listing ID: {listingId}"
```

**Example curl commands:**
```bash
# Generate proof with specific tradeId
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/alpha/generate-proof" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"tradeId": "1612509", "autoProcess": false}'

# Check proof status
curl -G "${MAXXIT_API_URL}/api/lazy-trading/programmatic/alpha/proof-status" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  --data-urlencode "proofId=<proof_id>"

# Flag as alpha using proofId
curl -L -X POST "${MAXXIT_API_URL}/api/lazy-trading/programmatic/alpha/flag" \
  -H "X-API-KEY: ${MAXXIT_API_KEY}" \
  -H "Content-Type: application/json" \
  -d '{"proofId": "<proof_id>", "priceUsdc": 5, "token": "ETH", "side": "long", "leverage": 6}'
```

---

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MAXXIT_API_KEY` | Your lazy trading API key (starts with `lt_`) | `lt_abc123...` |
| `MAXXIT_API_URL` | Maxxit API base URL | `https://maxxit.ai` |

## Error Handling

| Status Code | Meaning |
|-------------|---------|
| 401 | Invalid or missing API key |
| 404 | Lazy trader agent not found (complete setup first) |
| 400 | Missing or invalid message / parameters |
| 405 | Wrong HTTP method |
| 500 | Server error |

**Alpha-specific errors:**
| 400 | `/pay`: No agent address found (user must complete Lazy Trading setup). `/purchase`: Invalid X-Payment header or payment verification failed. |
| 402 | Payment required (`/purchase` Phase 1) or insufficient USDC balance (`/pay` — check `required` and `available` in response). |
| 409 | Transaction hash already used (replay protection — each tx can only purchase one listing). |
| 410 | Alpha listing no longer active. |

## Getting Started

1. **Set up Lazy Trading**: Visit https://maxxit.ai/lazy-trading to connect your wallet and configure your agent
2. **Generate API Key**: Go to your dashboard and create an API key
3. **Configure Environment**: Set `MAXXIT_API_KEY` and `MAXXIT_API_URL`
4. **Start Trading**: Use this skill to send signals!

## Security Notes

- Never share your API key
- API keys can be revoked and regenerated from the dashboard
- All trades execute on-chain with your delegated wallet permissions

