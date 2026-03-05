---
name: polyox-nba
description: >
  Query the PolyOx API for NBA data, Polymarket predictions, and
  AI matchup analysis. The analysis endpoint uses the x402 payment
  protocol (USDC on Base Sepolia).
metadata:
  author: polyox
  version: "0.2"
---

# PolyOx NBA API

Base URL: `https://api-hoobs.polyox.io`

All responses are JSON. Paginated endpoints return `{ data, page, pageSize, total }`.

---

## Step 0 — Check your wallet

Before calling any paid endpoint you need an EVM wallet with USDC on
**Base Sepolia**.

**Already have a wallet?** Make sure the `EVM_PRIVATE_KEY` environment
variable is set and skip to [Quick start](#quick-start).

**Don't have a wallet?** Set one up with
[Coinbase Agentic Wallet](https://docs.cdp.coinbase.com/agentic-wallet/welcome)
— a CLI wallet built for AI agents. No private key management required.

### Set up Coinbase Agentic Wallet

Prerequisites: **Node.js 24+** and an email address.

```bash
# Install the agentic-wallet skills (one-time)
npx skills add coinbase/agentic-wallet-skills
```

#### Authenticate

```bash
# 1. Start login — sends a 6-digit code to your email
npx awal@latest auth login agent@example.com

# 2. Verify with the code you received
npx awal@latest auth verify <flowId> <otp>

# 3. Confirm authentication
npx awal@latest status
```

#### Check address & balance

```bash
npx awal@latest address
npx awal@latest balance
```

#### Fund your wallet

Get testnet USDC from the Base Sepolia faucet, or ask another agent /
user to send USDC to your wallet address.

> **Full Agentic Wallet docs:**
> <https://docs.cdp.coinbase.com/agentic-wallet/quickstart>

---

## Quick start

```bash
# Today's games
curl "https://api-hoobs.polyox.io/nba/games?date=2026-02-08"

# Matchup context (injuries, recent form, Polymarket odds)
curl "https://api-hoobs.polyox.io/nba/games/context?date=2026-02-08&home=MIN&away=LAC"

# Latest injury report
curl "https://api-hoobs.polyox.io/nba/injury-reports/latest"
```

---

## Free endpoints

### NBA

| Method | Path | Description |
|--------|------|-------------|
| GET | `/nba/teams` | List all teams |
| GET | `/nba/teams/{id}` | Get one team |
| GET | `/nba/games` | List games (filter: `date`, `from`, `to`, `status`, `season`, `teamId`) |
| GET | `/nba/games/{id}` | Get one game |
| GET | `/nba/games/{id}/markets` | Polymarket markets for a game |
| GET | `/nba/games/context` | Full matchup context — requires `date`, `home`, `away` |
| GET | `/nba/players` | List players (filter: `search`, `isActive`, `teamId`) |
| GET | `/nba/players/{id}` | Get one player |
| GET | `/nba/team-stats` | Team game stats (filter: `gameId`, `teamId`) |
| GET | `/nba/player-stats` | Player game stats (filter: `gameId`, `playerId`, `teamId`) |
| GET | `/nba/injury-reports` | List injury reports |
| GET | `/nba/injury-reports/latest` | Latest entries (filter: `team`, `status`, `date`) |

### Polymarket

| Method | Path | Description |
|--------|------|-------------|
| GET | `/polymarket/events` | List events (filter: `date`, `search`) |
| GET | `/polymarket/markets` | List markets (filter: `eventId`, `search`) |
| GET | `/polymarket/price` | Live CLOB prices (`tokenId` or `marketIds`) |
| GET | `/polymarket/orderbook` | Live CLOB orderbook (`tokenId` or `marketIds`) |

All list endpoints support `page` and `pageSize` query params.

---

## Paid endpoint — x402 protocol

### `POST /nba/analysis`

AI-powered matchup analysis. Payment via **x402** — the HTTP-native payment standard.

- **Network:** Base Sepolia (chain ID `84532`)
- **Token:** USDC at `0x036CbD53842c5426634e7929541eC2318f3dCF7e`
- **Protocol docs:** https://docs.x402.org

#### Request body

```json
{
  "date": "2026-02-08",
  "home": "MIN",
  "away": "LAC"
}
```

All three fields required. `date` is `YYYY-MM-DD`, `home`/`away` are team abbreviations.

---

### How x402 works (step by step)

#### Step 1 — Send the request

Make a normal HTTP request. The server will respond with **HTTP 402**.

```bash
curl -s -D - -X POST \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-02-08","home":"MIN","away":"LAC"}' \
  "https://api-hoobs.polyox.io/nba/analysis"
```

#### Step 2 — Parse the 402 response

The 402 response includes a `PAYMENT-REQUIRED` header. Decode it from base64 to get the payment requirements:

```bash
# Extract and decode the payment requirements
PAYMENT_REQUIRED=$(curl -s -D - -X POST \
  -H "Content-Type: application/json" \
  -d '{"date":"2026-02-08","home":"MIN","away":"LAC"}' \
  "https://api-hoobs.polyox.io/nba/analysis" \
  | grep -i "payment-required" | cut -d' ' -f2 | tr -d '\r')

echo "$PAYMENT_REQUIRED" | base64 -d | jq .
```

The decoded JSON contains:

```json
{
  "maxAmountRequired": "...",
  "resource": "...",
  "payTo": "0x...",
  "asset": "0x036CbD53842c5426634e7929541eC2318f3dCF7e",
  "network": "eip155:84532",
  "expiresAt": "...",
  "nonce": "...",
  "paymentId": "...",
  "accepts": [{ "scheme": "exact", "network": "eip155:84532" }]
}
```

#### Step 3 — Sign and construct the payment

Using the payment requirements, create an **EIP-712 typed-data signature**
that authorises the USDC transfer. This is an off-chain signature — no gas spent.

The signature must be sent as a base64-encoded JSON payload in the
`PAYMENT-SIGNATURE` header when retrying the request.

**Important:** The EIP-712 signing step requires a crypto library. Pure `curl`
cannot sign. Use one of the approaches below.

#### Step 4 — Retry with payment

```bash
curl -X POST \
  -H "Content-Type: application/json" \
  -H "PAYMENT-SIGNATURE: <base64_encoded_signed_payload>" \
  -d '{"date":"2026-02-08","home":"MIN","away":"LAC"}' \
  "https://api-hoobs.polyox.io/nba/analysis"
```

The server verifies the signature, settles the payment on-chain, and returns
the analysis. A `PAYMENT-RESPONSE` header is included with settlement proof.

---

### Agent integration options

Choose the approach that matches your setup:

#### Option A — Coinbase Agentic Wallet (recommended)

The simplest path. If you set up your wallet via `awal` in Step 0, you can
pay for x402 endpoints in a single command — no code, no private key handling.

```bash
# Pay and call the analysis endpoint
npx awal@latest x402 pay \
  "https://api-hoobs.polyox.io/nba/analysis" \
  -X POST \
  -d '{"date":"2026-02-08","home":"MIN","away":"LAC"}'
```

The `awal x402 pay` command handles the full 402 → sign → retry flow
automatically. Options:

| Flag | Description |
|------|-------------|
| `-X, --method <method>` | HTTP method (default: GET) |
| `-d, --data <json>` | JSON request body |
| `-q, --query <params>` | Query parameters |
| `--max-amount <amount>` | Max USDC to spend (in micro-units) |
| `--json` | Output raw JSON |

> **Agentic Wallet skills reference:**
> <https://docs.cdp.coinbase.com/agentic-wallet/skills/overview>

#### Option B — Node.js / TypeScript

If you already have an EVM private key and prefer programmatic control:

```bash
npm install @x402/fetch @x402/core @x402/evm viem
```

```typescript
import { wrapFetchWithPayment } from "@x402/fetch";
import { x402Client } from "@x402/core/client";
import { registerExactEvmScheme } from "@x402/evm/exact/client";
import { privateKeyToAccount } from "viem/accounts";

const signer = privateKeyToAccount(process.env.EVM_PRIVATE_KEY as `0x${string}`);
const client = new x402Client();
registerExactEvmScheme(client, { signer });

const fetchWithPayment = wrapFetchWithPayment(fetch, client);

const res = await fetchWithPayment(
  "https://api-hoobs.polyox.io/nba/analysis",
  {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ date: "2026-02-08", home: "MIN", away: "LAC" }),
  },
);

console.log(await res.json());
```

> **Note for AI agents:** Option A is the fastest way to get started — no
> private key required. Option B gives full programmatic control if you
> already manage your own wallet.

---

## Reference

**Team abbreviations:** ATL, BOS, BKN, CHA, CHI, CLE, DAL, DEN, DET, GSW, HOU, IND, LAC, LAL, MEM, MIA, MIL, MIN, NOP, NYK, OKC, ORL, PHI, PHX, POR, SAC, SAS, TOR, UTA, WAS

**Date format:** `YYYY-MM-DD`

**Pagination:** `page` (1-indexed), `pageSize` (default 50)