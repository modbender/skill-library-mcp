---
name: checkout
description: Complete online shopping purchases on any online store using the Credpay Checkout API with x402 payments. Trigger when a user wants to buy, order, or checkout a product.
---

# Credpay Checkout Skill

**API Base URL:** `https://checkout-agent.credpay.xyz`

Trigger this skill whenever the user wants to purchase, order, or checkout a product from any online store.

## What you need from the user

Collect these before starting (ask if missing):

| Field | Example |
|---|---|
| Product URL | `https://example.com/products/tee` |
| Quantity | `1` |
| Size / Color (if applicable) | `"Size": "M", "Color": "Black"` |
| Email | `customer@example.com` |
| Goods total (USD) | `"49.99"` — item price as a USD string, no currency symbol |
| Shipping address | firstName, lastName, line1, city, state, postalCode, country, phone |

## Step 1 — Get a quote (no payment needed)

```http
POST https://checkout-agent.credpay.xyz/v1/quote
Content-Type: application/json

{
  "items": [
    {
      "url": "<product URL>",
      "quantity": 1,
      "options": { "Size": "M", "Color": "Black" }
    }
  ],
  "email": "<email>",
  "shippingAddress": {
    "firstName": "Jane",
    "lastName": "Doe",
    "line1": "123 Main St",
    "city": "Austin",
    "state": "TX",
    "postalCode": "78701",
    "country": "United States",
    "countryCode": "US",
    "phone": "+15125551234"
  },
  "goodsTotal": "<item price in USD as string, e.g. \"49.99\">"
}
```

→ Save `maxAmount` from the response. This is the USDC amount you will pay via x402.

## Step 2 — Submit checkout (x402 payment required)

```http
POST https://checkout-agent.credpay.xyz/v1/checkout
Content-Type: application/json
X-PAYMENT: <x402 payment payload for maxAmount on Base chainId 8453>

<same body as Step 1>
```

→ On `202`: save `requestId` and go to Step 3.
→ On `402`: re-read the payment requirements from the response and retry with a correct `X-PAYMENT` header.

## Step 3 — Poll for completion

```http
GET https://checkout-agent.credpay.xyz/v1/checkout/{requestId}
```

Poll every 5 seconds. Stop when status is `completed` or `failed`. Timeout after 10 minutes.

| Status | Action |
|---|---|
| `processing` | Keep polling |
| `authorization_required` | See Step 4 |
| `completed` | Done — return result to user |
| `failed` | Report `errorCode` + `errorMessage` to user |

## Step 4 — Handle extra payment (if needed)

If status is `authorization_required`, the order total exceeded the quoted amount:

```http
POST https://checkout-agent.credpay.xyz/v1/checkout/{requestId}/authorize
X-PAYMENT: <x402 payment for extraOwed amount>
```

Then resume polling from Step 3.

## Rules

- Works with any online store — just pass the product page URL.
- Never create a second checkout for the same intent while a `requestId` is active.
- Retry transient network errors with exponential backoff. Never blind-retry `failed` status.
- Default `chainId` is `8453` (Base).

## Success response

```json
{
  "requestId": "req_abc123",
  "status": "completed",
  "success": true,
  "orderNumber": "1234"
}
```

## Failure response

```json
{
  "requestId": "req_abc123",
  "status": "failed",
  "success": false,
  "errorCode": "payment_failed",
  "errorMessage": "Card declined"
}
```
