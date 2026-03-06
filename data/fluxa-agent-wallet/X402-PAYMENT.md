# x402 Payment (v3 — Intent Mandate) — Reference

## Overview

x402 is an HTTP-native payment protocol. When an agent requests a paid API, the server responds with HTTP 402 and payment requirements. The agent signs a payment via FluxA Wallet and retries with an `X-Payment` header.

**x402 v3** uses **intent mandates**: the user pre-approves a spending plan (budget + time window), then the agent can make autonomous payments within those limits.

This document uses the **CLI** method.

## When to Use This Document

| Scenario | Document |
|----------|----------|
| Pay for a paid API (HTTP 402) | **This document** |
| Pay to a payment link | [PAYMENT-LINK.md](PAYMENT-LINK.md) — see "Paying TO a Payment Link" section |
| Send USDC to a wallet address | [PAYOUT.md](PAYOUT.md) |

## End-to-End Flow

```
1. Create an intent mandate → user signs at authorizationUrl
2. Agent hits paid API → receives HTTP 402
3. Agent calls x402-v3 (CLI) or x402V3Payment (API) with mandateId + 402 payload
4. Agent retries API with X-Payment header → gets data
```

**Important**: The x402-v3 command requires both `--mandate` and `--payload`. You must create a mandate first (Step 1) before executing payments.

## Step 1 — Create Intent Mandate

```bash
node scripts/fluxa-cli.bundle.js mandate-create \
  --desc "Spend up to 0.10 USDC for Polymarket recommendations for 30 days" \
  --amount 100000 \
  --seconds 2592000 \
  --category trading_data
```

**Options:**

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--desc` | Yes | — | Natural language description of the spend plan |
| `--amount` | Yes | — | Budget limit in atomic units |
| `--seconds` | No | `28800` (8h) | Validity duration in seconds |
| `--category` | No | `general` | Category tag |
| `--currency` | No | `USDC` | Currency |

**Output:**

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "mandateId": "mand_xxxxxxxxxxxxx",
    "authorizationUrl": "https://wallet.fluxapay.xyz/onboard/intent?oid=...",
    "expiresAt": "2026-02-04T00:10:00.000Z",
    "agentStatus": "ready"
  }
}
```

**Opening the authorization URL** (see [SKILL.md](SKILL.md) — "Opening Authorization URLs"):

1. Ask the user using `AskUserQuestion`:
   - Question: "I need to open the authorization URL to sign the spending mandate."
   - Options: ["Yes, open the link", "No, show me the URL"]

2. If YES: Run `open "<authorizationUrl>"` to open in their browser

3. Wait for user to confirm they've signed (TTL: 10 minutes), then proceed to Step 2.

## Step 2 — Check Mandate Status

**Important:** Use `--id`, not `--mandate`:

```bash
node scripts/fluxa-cli.bundle.js mandate-status --id mand_xxxxxxxxxxxxx
```

**Output:**

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "mandate": {
      "mandateId": "mand_xxxxxxxxxxxxx",
      "status": "signed",
      "naturalLanguage": "Spend up to 0.10 USDC...",
      "currency": "USDC",
      "limitAmount": "100000",
      "spentAmount": "0",
      "remainingAmount": "100000",
      "validFrom": "2026-02-04T00:00:00.000Z",
      "validUntil": "2026-03-06T00:00:00.000Z"
    }
  }
}
```

Wait until `mandate.status` is `"signed"`.

## Step 3 — Make x402 v3 Payment

Pass the **complete** HTTP 402 response body as `--payload`. The payload **must** contain an `accepts` array.

**Critical:** Do NOT extract individual fields. Pass the entire 402 response JSON:

```bash
# Store the 402 response in a variable first
PAYLOAD_402='{"accepts":[{"scheme":"exact","network":"base","maxAmountRequired":"10000","asset":"0x833589fCD6eDb6E08f4c7C32D4f71b54bdA02913","payTo":"0xFf319473ba1a09272B37c34717f6993b3F385CD3","resource":"https://fluxa-x402-api.gmlgtm.workers.dev/polymarket_recommendations_last_1h","description":"Get Polymarket trading recommendations","extra":{"name":"USD Coin","version":"2"},"maxTimeoutSeconds":60}]}'

node scripts/fluxa-cli.bundle.js x402-v3 \
  --mandate mand_xxxxxxxxxxxxx \
  --payload "$PAYLOAD_402"
```

**Options:**

| Option | Required | Description |
|--------|----------|-------------|
| `--mandate` | Yes | Mandate ID from Step 1 |
| `--payload` | Yes | The **complete** HTTP 402 response body (must include `accepts` array) |

**Wrong:**
```bash
# This will fail with "Invalid payload: missing accepts array"
--payload '{"maxAmountRequired":"10000","payTo":"0x..."}'
```

**Correct:**
```bash
# Pass the full 402 response with accepts array
--payload '{"accepts":[{...}]}'
```

**Output:**

```json
{
  "success": true,
  "data": {
    "status": "ok",
    "xPaymentB64": "eyJ4NDAyVmVyc2lvbi...",
    "xPayment": { "x402Version": 1, "scheme": "exact", "network": "base", "payload": { "..." } },
    "paymentRecordId": 123,
    "expiresAt": 1700000060
  }
}
```

## Step 4 — Retry with X-Payment Header

Use `xPaymentB64` as the `X-Payment` header:

```bash
curl -H "X-Payment: eyJ4NDAyVmVyc2lvbi..." \
  https://fluxa-x402-api.gmlgtm.workers.dev/polymarket_recommendations_last_1h
```

## Mandate Ownership Caveat

Mandates are tied to the agent that created them. A mandate created via CLI belongs to the CLI's configured agent, while a mandate created via API belongs to the API-authenticated agent (identified by JWT).

If using both methods, ensure you're using the same agent identity.

## Scripted Example (CLI)

```bash
#!/bin/bash
CLI="node scripts/fluxa-cli.bundle.js"
API_URL="https://fluxa-x402-api.gmlgtm.workers.dev/polymarket_recommendations_last_1h"
MANDATE_ID="mand_xxxxxxxxxxxxx"

# Hit the API
RESPONSE=$(curl -s -w "\n%{http_code}" "$API_URL")
HTTP_CODE=$(echo "$RESPONSE" | tail -n1)

if [ "$HTTP_CODE" = "402" ]; then
  PAYLOAD=$(echo "$RESPONSE" | head -n -1)

  # Sign payment
  RESULT=$($CLI x402-v3 --mandate "$MANDATE_ID" --payload "$PAYLOAD")
  XPAYMENT=$(echo "$RESULT" | jq -r '.data.xPaymentB64')

  # Retry with payment header
  curl -H "X-Payment: $XPAYMENT" "$API_URL"
fi
```

## Error Handling

| Error in output | Meaning | Action |
|----------------|---------|--------|
| `Missing required parameters: --desc, --amount` | mandate-create called without required flags | Add both `--desc "..."` and `--amount <number>` |
| `Missing required parameter: --id` | mandate-status called with wrong flag | Use `--id`, not `--mandate` |
| `Missing required parameters: --mandate, --payload` | x402-v3 called without prerequisites | Create a mandate first using `mandate-create` |
| `Invalid payload: missing accepts array` | Payload is incomplete or malformed | Pass the **complete** 402 response JSON including `accepts` array |
| `mandate_not_signed` | User hasn't signed yet | Ask user to open `authorizationUrl` |
| `mandate_expired` | Time window passed | Create a new mandate |
| `mandate_budget_exceeded` | Budget exhausted | Create a new mandate with higher limit |
| `mandate_insufficient_budget` | Payment amount exceeds remaining budget | Create a new mandate with higher limit |
| `mandate_not_found` | Mandate ID doesn't exist or belongs to different agent | Verify mandate ID and agent identity |
| `agent_not_registered` | No Agent ID | Run `init` first |

## Network Format Note

The 402 response may use different network formats:
- `eip155:8453` — Chain ID format (EIP-155)
- `base` — Human-readable network name

Both refer to Base network. The CLI and API accept either format.
