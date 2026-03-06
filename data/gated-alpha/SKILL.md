---
name: gated-alpha
description: Discover, filter, and purchase structured crypto alpha calls from Gated Alpha. Supports push delivery via webhooks (recommended) or direct polling. Pay-per-call via x402 on Base (USDC). Owner payouts fire onchain within seconds of each purchase.
homepage: https://www.gatedalpha.xyz
version: 3.0.0
metadata: {"provider":"Gated Alpha","protocols":["x402","webhook"],"chains":["base","solana"],"currency":"USDC","payTo":"0x93BFdb89EEbbDfE8162bdfBE238f37CCEEd7800C"}
---

# Gated Alpha Skill

Gated Alpha is a pay-per-call alpha marketplace. Crypto signal groups publish calls. Agents pay USDC to unlock the full payload. Group owners receive automatic onchain payouts within seconds of each purchase.

**Live API:** `https://www.gatedalpha.xyz`

---

## Two Ways to Receive Alpha

### Option A — Push (Recommended)
Register a webhook once. New matching alpha is delivered to your endpoint the moment it drops. No polling.

### Option B — Pull
Poll `/alpha/latest` on your own schedule and fetch the ones you want.

---

## Option A: Webhook Subscriptions (Push Model)

### Step 1 — Register your webhook

```http
POST https://www.gatedalpha.xyz/agents/subscribe
Content-Type: application/json

{
  "wallet": "0xYourWalletAddress",
  "webhook_url": "https://your-agent.xyz/hooks/alpha",
  "chains": ["solana", "base"],
  "categories": ["memecoin", "defi"],
  "max_price_usdc": 5
}
```

| Field | Required | Description |
|---|---|---|
| `wallet` | ✅ | Your EVM or Solana wallet address |
| `webhook_url` | ✅ | HTTPS endpoint that receives `POST` when alpha drops |
| `chains` | ❌ | Filter by chain. Empty array = all. Options: `solana`, `base`, `ethereum`, `bsc`, `arbitrum` |
| `categories` | ❌ | Filter by category. Empty = all |
| `max_price_usdc` | ❌ | Skip alpha above this price. `0` = no limit |

**Response:**
```json
{
  "ok": true,
  "subscription": {
    "id": "sub_abc123",
    "wallet": "0xyourwallet",
    "webhook_url": "https://your-agent.xyz/hooks/alpha",
    "chains": ["solana", "base"],
    "categories": [],
    "max_price_usdc": 5,
    "created_at": "2026-02-26T14:00:00.000Z",
    "last_fired_at": null,
    "fire_count": 0
  }
}
```

**Limits:** Max 10 subscriptions per wallet. Dedup window: same alpha won't fire twice to the same subscription within 60 seconds. Webhook must be HTTPS.

---

### Step 2 — Handle incoming webhooks

When a matching alpha drops, your endpoint receives:

```http
POST https://your-agent.xyz/hooks/alpha
Content-Type: application/json

{
  "event": "alpha.new",
  "subscription_id": "sub_abc123",
  "sent_at": "2026-02-26T14:05:00.000Z",
  "alpha": {
    "id": "alpha_01kjXXXX",
    "group_id": "grp_01kjXXXX",
    "group_name": "Liquid Path FNF",
    "group_score": 72,
    "chain": "solana",
    "category": "memecoin",
    "price_usdc": 1,
    "mcap_range": "micro",
    "preview_text": "New Solana micro-cap play...",
    "is_new_group": false,
    "trial_url": null,
    "paid_url": "https://www.gatedalpha.xyz/alpha/alpha_01kjXXXX",
    "posted_at": "2026-02-26T14:04:55.000Z"
  }
}
```

| Field | What it means |
|---|---|
| `group_score` | Trust score 0–100. Higher = stronger verified call track record. **Filter on this first.** |
| `trial_url` | Free preview URL. Present when the group has zero prior purchases — use it to evaluate before buying. `null` if not available. |
| `paid_url` | The full alpha URL. Hit this with an x402 payment header to purchase. |
| `is_new_group` | `true` if the group has never had a purchase. Check `trial_url` first. |
| `preview_text` | Short teaser if the group provided one. May be `null`. |

**Acknowledge fast.** Return `200` immediately, then process async. Delivery is fire-and-forget — if your endpoint is down, the event is not retried.

---

### Step 3 — Decide: trial or buy

```
if trial_url is present AND is_new_group is true:
  → GET trial_url first (free, no payment)
  → Evaluate the preview. If promising, proceed to purchase.

if group_score < 30:
  → Skip. Unproven group.

else:
  → Purchase via x402 (see below)
```

---

### Step 4 — Buy the full alpha (x402)

```js
import { wrapFetchWithPayment } from '@x402/fetch';
import { x402Client } from '@x402/core/client';
import { ExactEvmScheme } from '@x402/evm';
import { createPublicClient, createWalletClient, http } from 'viem';
import { base } from 'viem/chains';
import { privateKeyToAccount } from 'viem/accounts';

const account = privateKeyToAccount('0x<your-private-key>');

const publicClient = createPublicClient({
  chain: base,
  transport: http('https://base-rpc.publicnode.com')
});

const walletClient = createWalletClient({
  account,
  chain: base,
  transport: http('https://base-rpc.publicnode.com')
});

const clientSigner = {
  address: account.address,
  signTypedData: (msg) => walletClient.signTypedData({ account, ...msg }),
  readContract: (args) => publicClient.readContract(args)
};

const coreClient = new x402Client().register('eip155:*', new ExactEvmScheme(clientSigner));
const paidFetch = wrapFetchWithPayment(fetch, coreClient);

// Automatically handles: 402 challenge -> sign ERC-3009 -> retry with payment header
const res = await paidFetch('https://www.gatedalpha.xyz/alpha/alpha_01kjXXXX');
const alpha = await res.json();
```

**Note:** `@x402/core`, `@x402/evm`, `@x402/fetch`, and `viem` must be installed. Run from a directory where these packages exist in `node_modules`.

**Returning buyer:** If the same wallet purchases the same alpha_id again, content is served free. No double charge.

---

### Full alpha payload (200 response after payment)

```json
{
  "id": "alpha_01kj457g0nzqdhacwd8jn25ykq",
  "group": {
    "group_id": "grp_...",
    "display_name": "Group Name",
    "group_score": 72,
    "price_usdc": 1
  },
  "token": {
    "name": "TokenName",
    "symbol": "TKN",
    "chain": "base",
    "contract_address": "0x...",
    "pair_address": "0x..."
  },
  "market": {
    "mcap_at_call": 50200,
    "liquidity_usd": 55893,
    "age_hours": 24.7
  },
  "alpha": {
    "thesis": "Raw call text from the group",
    "catalyst": "source_telegram_message",
    "category": "memecoin",
    "confidence": 0.85,
    "risk_level": "low",
    "target_mcap": 15000000
  }
}
```

---

## Option B: Pull (Polling)

### Browse free previews

```http
GET https://www.gatedalpha.xyz/alpha/latest?limit=20&chain=solana
```

Key preview fields:
- `id` — use to fetch the full paid payload
- `group_score` — quality signal (0–100), filter on this first
- `chain` — `base`, `solana`, `ethereum`, `bsc`, `arbitrum`
- `category` — `memecoin`, `defi`, etc.
- `risk_level` — `"low"`, `"medium"`, `"high"`, or `null`
- `confidence` — float 0–1 or `null`
- `mcap_range` — `"<100K"`, `"100K-1M"`, etc.
- `price_usdc` — cost to unlock

### Filter by default

```
min_group_score = 40   (skip unproven groups)
chains = ["base"]      (or your target chains)
limit = 20
skip if confidence AND risk_level are both null (unscored call)
```

### Decision logic

```
if group_score < 40           → skip
if risk_level == "high"
  AND confidence < 0.7        → skip
if mcap_at_call > 5_000_000   → skip (likely too late)
else                          → candidate for purchase
```

### Buy via x402 (same as push flow above)

Hit `GET /alpha/{id}` — it returns `402` with the payment challenge. Use `@x402/fetch` to handle automatically. See Step 4 above.

---

## Manage Subscriptions

### List your subscriptions
```http
GET https://www.gatedalpha.xyz/agents/{wallet}/subscriptions
```

### Delete a subscription
```http
DELETE https://www.gatedalpha.xyz/agents/unsubscribe
Content-Type: application/json

{
  "wallet": "0xYourWallet",
  "subscription_id": "sub_abc123"
}
```

---

## Free Trial Endpoints

If a group has zero purchases, a free trial is available:

```http
GET https://www.gatedalpha.xyz/alpha/{id}/trial
```

Returns a redacted preview — no payment required. Use this to evaluate new groups before committing.

When `trial_url` is present in a webhook payload or a `402` response, always check it first.

---

## Minimal Webhook Handler (Node.js)

```js
import express from 'express';
import { wrapFetchWithPayment } from '@x402/fetch';

const app = express();
app.use(express.json());

app.post('/hooks/alpha', async (req, res) => {
  const { alpha } = req.body;
  res.sendStatus(200); // Acknowledge immediately

  if (alpha.group_score < 30) return; // Skip low-trust groups

  // Free trial if available (new group, no track record yet)
  if (alpha.trial_url) {
    const trial = await fetch(`https://www.gatedalpha.xyz${alpha.trial_url}`);
    const preview = await trial.json();
    // Evaluate preview — if not interesting, return early
    if (!isWorthBuying(preview)) return;
  }

  // Buy the full alpha
  const res2 = await paidFetch(alpha.paid_url); // paidFetch from Step 4
  const content = await res2.json();
  // Your trading logic here
});

app.listen(3000);
```

---

## Payment Details

- **Network:** Base mainnet (`eip155:8453`, chainId 8453)
- **Token:** USDC on Base — `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913`
- **Amount:** per-call price (usually 1 USDC = 1,000,000 micro-USDC)
- **payTo:** `0x93BFdb89EEbbDfE8162bdfBE238f37CCEEd7800C`
- **Platform fee:** 15% retained
- **Owner cut:** 85% — paid onchain automatically within seconds of purchase

---

## Group Owner Onboarding

To list your group, provide:
1. Telegram group name + chat ID (negative integer, e.g. `-100123456789`)
2. Price per alpha in USDC
3. Your Base wallet address (for automatic payouts)

Contact @ZekiAgent or DM @gatedalpha_bot on Telegram.

---

## Key Constants

| Constant | Value |
|---|---|
| Live URL | `https://www.gatedalpha.xyz` |
| Platform wallet | `0x93BFdb89EEbbDfE8162bdfBE238f37CCEEd7800C` |
| USDC on Base | `0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913` |
| Network | Base mainnet (chainId 8453) |
| Platform fee | 15% |
| Owner cut | 85% |
