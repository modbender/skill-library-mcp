---
name: agentfin
description: Issue virtual Visa/MC cards funded by USDT. Check balance, get card credentials, fetch OTP codes — all via REST API.
version: 1.0.0
homepage: https://agentfin.tech
metadata: {"openclaw":{"requires":{"env":["AGENTFIN_API_KEY"]},"primaryEnv":"AGENTFIN_API_KEY","emoji":"💳"}}
---

# AgentFin — Virtual Cards for Agents

You have access to the AgentFin API. Use it to check your balance, get virtual card credentials for online purchases, and fetch OTP codes for 3DS verification.

## Authentication

All requests require a Bearer token. Use the `AGENTFIN_API_KEY` environment variable.

```
Authorization: Bearer $AGENTFIN_API_KEY
```

Base URL: `https://agentfin.tech/api`

## Endpoints

### Check Balance & Card Status

```bash
curl -H "Authorization: Bearer $AGENTFIN_API_KEY" \
  https://agentfin.tech/api/me
```

Response includes `balance` (USD string), `card` object with `maskedPan` and `status`, and `depositAddress` for USDT top-ups.

### Get Card Credentials (for online purchases)

```bash
curl -H "Authorization: Bearer $AGENTFIN_API_KEY" \
  https://agentfin.tech/api/cards/{cardId}/sensitive
```

Returns `pan`, `cvv`, `expiryMonth`, `expiryYear`, `cardHolderName`, `billingAddress`. Rate limited to 10 requests/minute.

**Important:** Use the `cardId` from the `/api/me` response (`card.cardId` field).

### Fetch Latest OTP Code (for 3DS verification)

```bash
curl -H "Authorization: Bearer $AGENTFIN_API_KEY" \
  https://agentfin.tech/api/inbox/latest-otp
```

Returns the most recent email with extracted OTP codes. The `extractedCodes` field is an array of strings. Use the first element as the verification code.

If a purchase triggers 3DS, wait 10-30 seconds for the OTP email to arrive, then call this endpoint.

### Top Up Card Balance

```bash
curl -X POST -H "Authorization: Bearer $AGENTFIN_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"amount": 50, "currency": "USD"}' \
  https://agentfin.tech/api/cards/{cardId}/topup
```

Moves funds from your account balance to the card. The card is prepaid — you cannot spend more than the loaded amount.

### View Transaction History

```bash
curl -H "Authorization: Bearer $AGENTFIN_API_KEY" \
  https://agentfin.tech/api/me/transactions
```

Returns all deposits, card charges, top-ups, and refunds.

## Typical Purchase Flow

1. Check balance with `GET /api/me` — ensure sufficient funds
2. Get card credentials with `GET /api/cards/{cardId}/sensitive`
3. Use PAN, CVV, expiry to fill in payment form on merchant site
4. If 3DS is triggered, wait ~15 seconds then `GET /api/inbox/latest-otp`
5. Submit the OTP code from `extractedCodes[0]`
6. Purchase complete

## Important Notes

- The card is **prepaid**. You cannot spend more than the loaded balance.
- Card credentials are rate-limited (10/min). Cache them for the duration of a purchase session.
- OTP codes arrive via email to a dedicated inbox. There may be a 10-30 second delay.
- Fund the account by sending USDT (TRC20) to the deposit address from `GET /api/me`.
