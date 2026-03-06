# Credit Card Payments

Pay a merchant with a credit card (no 402 involved).

## Request

```
POST https://api.crowpay.ai/authorize/card
X-API-Key: crow_sk_...
Content-Type: application/json

{
  "amountCents": 1000,
  "merchant": "OpenAI",
  "reason": "GPT-4 API credits"
}
```

- `amountCents` is in cents: 1000 = $10.00
- `currency` is optional, defaults to `"usd"`

## Responses

- **200 — Approved**: Use the returned `sptToken` to pay the merchant via Stripe. Token expires in 1 hour.
- **202 — Pending**: Poll `/authorize/status?id=<approvalId>` same as x402 flow.
- **403 — Denied**: Spending rules blocked this payment.
