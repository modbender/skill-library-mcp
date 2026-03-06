---
name: alura-backend-api
description: "Integrate with Alura Trading backend API. Use when calling Alura
  testnet API, trading sessions, user auth, indicators, or leaderboard. Base
  URL: https://testnet-api.alura.fun"
---


# Alura Backend API

Use this skill when integrating with or calling the Alura Trading backend API. The testnet API base URL is **https://testnet-api.alura.fun**.

## Base URL

```
https://testnet-api.alura.fun
```

- Swagger docs: `https://testnet-api.alura.fun/api/docs`
- All authenticated endpoints require `Authorization: Bearer <JWT>`

## Authentication (EVM Wallet)

### 1. Get challenge

```
POST /auth/evm/challenge
Content-Type: application/json

{ "address": "0x..." }
```

Returns `{ address, nonce, message }`.

### 2. Sign & verify

User signs `message` with MetaMask (personal_sign). Then:

```
POST /auth/evm/verify
Content-Type: application/json

{ "address": "0x...", "signature": "0x...", "referralCode": "OPTIONAL" }
```

Returns `{ ok: true, accessToken, tokenType: "Bearer", expiresIn: 86400, ... }`. Use `accessToken` for subsequent requests.

## Trading Sessions

Base path: `/trading-sessions`. All require Bearer token.

### Quick trade – create session

```
POST /trading-sessions
Authorization: Bearer <token>
Content-Type: application/json

{
  "budget": 100,
  "profitTarget": 40,
  "lossThreshold": 5,
  "maxPositions": 3,
  "assetIndex": 0
}
```

**Required**: `budget` (min 10), `profitTarget` (max 500), `assetIndex` (Hyperliquid perp index: 0=BTC, 1=ETH, 2=SOL, etc.).

### Advance trade – create session

```
POST /trading-sessions/advance
Authorization: Bearer <token>
Content-Type: application/json

{
  "amount": 100,
  "executionStrategy": "Conservative" | "Aggressive" | "Degen",
  "strategyDuration": "1D" | "3D" | "7D" | "30D" | "90D" | "365D",
  "assetIndex": 0,
  "maxWalletBudget": false
}
```

### Other trading endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | /trading-sessions/active | List active sessions |
| GET | /trading-sessions/current-trade | Current trade with positions |
| GET | /trading-sessions/:sessionId/logs | Session logs |
| GET | /trading-sessions/trades/:tradeId/logs | Trade logs (paginated) |
| POST | /trading-sessions/positions/:positionId/close | Close a position |
| POST | /trading-sessions/positions/:positionId/close-signature | Get signed close tx for frontend |
| POST | /trading-sessions/trades/:tradeId/close | Close trade (all positions) |
| POST | /trading-sessions/trigger-cron | Manually trigger cron (testing) |

## User

Base path: `/user`. All require Bearer token.

| Method | Path | Description |
|--------|------|-------------|
| GET | /user/profile | Current user profile |
| POST | /user/fills/sync | Sync fills from Hyperliquid |
| POST | /user/withdraw | Withdraw funds |
| POST | /user/close-position | Close position by assetIndex |
| POST | /user/close-all-positions | Close all positions |
| POST | /user/send-usdc | Send USDC |
| GET | /auth/evm/trading-key | Get trading agent key (auth) |
| POST | /user/claim-reward | Claim rewards |

## Indicators & Market Data

Base path: `/api/indicators`. Most are public.

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/indicators/health | Service health |
| GET | /api/indicators/candles/latest | Latest candles |
| GET | /api/indicators/candles/history/:symbol | Historical candles |
| GET | /api/indicators/candles/:symbol/:interval | Candles by symbol/interval |
| GET | /api/indicators/candles/aggregated/symbols | Available symbols |
| GET | /api/indicators/signals/:symbol/:interval | Signals for symbol |
| GET | /api/indicators/signals/all/:interval | All symbols signals |

## Leaderboard

Base path: `/api/leaderboard`.

| Method | Path | Description |
|--------|------|-------------|
| GET | /api/leaderboard/stats | Leaderboard stats |
| GET | /api/leaderboard/rankings | Rankings |
| GET | /api/leaderboard/user/:userId | User ranking |
| GET | /api/leaderboard/analytics | Analytics |
| GET | /api/leaderboard/health | Health |

## Referrals

Base path: `/referrals`.

| Method | Path | Description |
|--------|------|-------------|
| GET | /referrals/:userId | User referral info |
| GET | /referrals/:userId/stats | Referral stats |
| POST | /referrals/:userId/code | Create referral code |
| POST | /referrals/check | Check referral code |

## USDC Verification

Base path: `/usdc-verification`.

| Method | Path | Description |
|--------|------|-------------|
| POST | /usdc-verification/verify | Verify USDC deposit |
| GET | /usdc-verification/my-transactions | My transactions |
| GET | /usdc-verification/total-deposited | Total deposited |

## Health

| Method | Path | Description |
|--------|------|-------------|
| GET | /health | Basic health |
| GET | /health/kafka | Kafka health |

## Asset Indices (Hyperliquid Perps)

Common perp asset indices:

| Symbol | Index |
|--------|-------|
| BTC | 0 |
| ETH | 1 |
| SOL | 2 |
| XRP | 3 |
| DOGE | 4 |
| AVAX | 5 |

## Error Handling

- 401: Missing/invalid Bearer token. Re-auth via `/auth/evm/challenge` and `/auth/evm/verify`.
- 400: Validation error. Check `message` in response body.
- 429: Rate limit. Retry with backoff.
- Common messages: `Duplicate asset index: you already have an active trading session for this asset`, `Builder fee approval failed: HTTP request failed: status 429`.
