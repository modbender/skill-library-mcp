# Payment Link — CLI Reference

## Overview

Payment Links allow the agent to create shareable payment URLs to **receive** USDC. Useful for invoicing, selling content, collecting tips, or any scenario where the agent needs to get paid.

## End-to-End Flow

```
1. Agent creates a payment link via CLI
2. Agent shares the returned URL with payers
3. Payers open the URL and pay (or agent pays programmatically via x402)
4. Agent checks payments received via CLI
```

## Command Reference

### Create Payment Link

```bash
node scripts/fluxa-cli.bundle.js paymentlink-create \
  --amount "5000000" \
  --desc "AI Research Report" \
  --max-uses 100 \
  --expires "2026-02-11T00:00:00.000Z"
```

**Options:**

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--amount` | Yes | — | Amount in atomic units |
| `--desc` | No | — | Description |
| `--resource` | No | — | Resource content delivered after payment |
| `--expires` | No | — | Expiry date (ISO 8601) |
| `--max-uses` | No | — | Maximum number of payments |
| `--network` | No | `base` | Network |

**Output:**

```json
{
  "success": true,
  "data": {
    "paymentLink": {
      "linkId": "lnk_a1b2c3d4e5",
      "amount": "5000000",
      "currency": "USDC",
      "network": "base",
      "description": "AI Research Report",
      "status": "active",
      "expiresAt": "2026-02-11T00:00:00.000Z",
      "maxUses": 100,
      "useCount": 0,
      "url": "https://wallet.fluxapay.xyz/pay/lnk_a1b2c3d4e5",
      "createdAt": "2026-02-04T12:00:00.000Z"
    }
  }
}
```

Share the `url` value with payers.

### List Payment Links

```bash
node scripts/fluxa-cli.bundle.js paymentlink-list --limit 20
```

**Options:**

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--limit` | No | — | Max number of results |

### Get Payment Link Details

```bash
node scripts/fluxa-cli.bundle.js paymentlink-get --id lnk_a1b2c3d4e5
```

### Update Payment Link

```bash
# Disable a link
node scripts/fluxa-cli.bundle.js paymentlink-update --id lnk_a1b2c3d4e5 --status disabled

# Update description
node scripts/fluxa-cli.bundle.js paymentlink-update --id lnk_a1b2c3d4e5 --desc "SOLD OUT"

# Remove expiry limit
node scripts/fluxa-cli.bundle.js paymentlink-update --id lnk_a1b2c3d4e5 --expires null

# Remove max uses limit
node scripts/fluxa-cli.bundle.js paymentlink-update --id lnk_a1b2c3d4e5 --max-uses null
```

**Options (all optional except `--id`):**

| Option | Required | Description |
|--------|----------|-------------|
| `--id` | Yes | Payment link ID |
| `--desc` | No | New description |
| `--resource` | No | New resource content |
| `--status` | No | `active` or `disabled` |
| `--expires` | No | New expiry (ISO 8601), `null` to clear |
| `--max-uses` | No | New max uses, `null` to clear |

### Delete Payment Link

```bash
node scripts/fluxa-cli.bundle.js paymentlink-delete --id lnk_a1b2c3d4e5
```

### View Payments Received

```bash
node scripts/fluxa-cli.bundle.js paymentlink-payments --id lnk_a1b2c3d4e5 --limit 10
```

**Options:**

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--id` | Yes | — | Payment link ID |
| `--limit` | No | — | Max number of results |

**Output:**

```json
{
  "success": true,
  "data": {
    "payments": [
      {
        "id": 1,
        "payerAddress": "0xBuyerAddr...",
        "amount": "5000000",
        "currency": "USDC",
        "settlementStatus": "settled",
        "settlementTxHash": "0xabcdef...",
        "createdAt": "2026-02-05T10:30:00.000Z"
      }
    ]
  }
}
```

## Paying TO a Payment Link

To pay a payment link programmatically (agent-to-agent payments), use the x402 flow documented in [X402-PAYMENT.md](X402-PAYMENT.md).

**Quick reference:**
```
1. curl -s <payment_link_url>                    → Get 402 payload
2. mandate-create --desc "..." --amount <amount> → Create mandate
3. User signs at authorizationUrl                → Mandate becomes "signed"
4. x402-v3 --mandate <id> --payload "$PAYLOAD"   → Get xPaymentB64
5. curl -H "X-Payment: <token>" <url>            → Submit payment
```

Payment link URL format: `https://walletapi.fluxapay.xyz/paymentlink/<link_id>`

## Scripted Example

```bash
#!/bin/bash
CLI="node scripts/fluxa-cli.bundle.js"

# Create a payment link
RESULT=$($CLI paymentlink-create --amount "1000000" --desc "Test payment link")

LINK_ID=$(echo "$RESULT" | jq -r '.data.paymentLink.linkId')
URL=$(echo "$RESULT" | jq -r '.data.paymentLink.url')

echo "Created payment link: $URL"

# Check for payments
$CLI paymentlink-payments --id "$LINK_ID" | jq
```

## Use Cases

| Scenario | Configuration |
|----------|--------------|
| One-time invoice | `--max-uses 1` |
| Limited-time sale | `--expires "<date>"` |
| Tip jar / donation | No limits |
| Digital goods | `--resource "Download link: ..."` |
| Batch collection | High `--max-uses`, track via `paymentlink-payments` |
| Agent-to-agent payment | Use x402 flow above |
