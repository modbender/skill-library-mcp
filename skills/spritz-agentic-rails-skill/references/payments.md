# Payments

Off-ramp crypto to fiat bank accounts.

<!-- TODO: Replace placeholder endpoints/shapes with actual Spritz API once finalized -->

## How Off-Ramp Payments Work

1. **Create payment** — Specify USD amount, bank account, chain, and token
2. **Receive deposit details** — Spritz returns a deposit address and crypto amount
3. **Send crypto** — Agent sends the exact crypto amount to the deposit address
4. **Spritz converts** — Spritz receives the crypto and initiates ACH transfer
5. **Fiat arrives** — Bank account receives USD (typically 1-3 business days)

## Create Payment

```bash
POST /v1/payments
```

### Request

```json
{
  "bank_account_id": "<bank_account_id>",
  "amount_usd": "100.00",
  "network": "base",
  "token": "USDC"
}
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `bank_account_id` | string | Yes | Destination bank account ID |
| `amount_usd` | string | Yes | USD amount to deliver |
| `network` | string | Yes | Blockchain network for payment |
| `token` | string | Yes | Token to pay with |

### Response

```json
{
  "id": "pay_abc123",
  "status": "awaiting_deposit",
  "amount_usd": "100.00",
  "deposit": {
    "address": "0x...",
    "amount": "100.050000",
    "token": "USDC",
    "network": "base"
  },
  "bank_account_id": "ba_xyz789",
  "created_at": "2026-02-24T10:30:00Z",
  "expires_at": "2026-02-24T11:30:00Z"
}
```

**After creating the payment, the agent must send exactly `deposit.amount` of `deposit.token` to `deposit.address` on the specified network.**

The deposit address is time-limited. Send the crypto before `expires_at`.

## Get Payment

```bash
GET /v1/payments/{payment_id}
```

### Payment Statuses

| Status | Description |
|--------|-------------|
| `awaiting_deposit` | Waiting for crypto deposit |
| `deposit_received` | Crypto received, processing |
| `converting` | Converting crypto to fiat |
| `sending` | ACH transfer initiated |
| `completed` | Fiat delivered to bank account |
| `expired` | Deposit window expired |
| `failed` | Payment failed (see `error` field) |

## List Payments

```bash
GET /v1/payments
```

Query parameters:
- `status` — Filter by status
- `limit` — Max results (default 25)
- `offset` — Pagination offset

## Supported Networks and Tokens

<!-- TODO: Confirm actual supported networks and tokens -->

| Network | Tokens | Notes |
|---------|--------|-------|
| `ethereum` | USDC, USDT, DAI | Higher gas fees |
| `base` | USDC | Recommended — low fees |
| `polygon` | USDC, USDT | Low fees |
| `arbitrum` | USDC | Low fees |
| `optimism` | USDC | Low fees |
| `avalanche` | USDC | Low fees |
| `bsc` | USDC, BUSD | Low fees |

**Recommendation:** Use USDC on Base for lowest fees and fastest settlement.

## Payment Flow Example

### Complete off-ramp: $250 USDC on Base

```bash
# Step 1: Create the payment
curl -X POST "https://api.spritz.finance/v1/payments" \
  -H "Authorization: Bearer $SPRITZ_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "bank_account_id": "ba_xyz789",
    "amount_usd": "250.00",
    "network": "base",
    "token": "USDC"
  }'

# Response includes deposit address and amount
# → deposit.address = "0xABC..."
# → deposit.amount = "250.125000"

# Step 2: Send USDC from agent wallet to deposit address
# (Use the agent's wallet skill to execute this transaction)

# Step 3: Check status
curl -X GET "https://api.spritz.finance/v1/payments/pay_abc123" \
  -H "Authorization: Bearer $SPRITZ_API_KEY"
```

## Error Handling

Common errors:

| Error | Description |
|-------|-------------|
| `INVALID_BANK_ACCOUNT` | Bank account ID not found or invalid |
| `AMOUNT_TOO_LOW` | Below minimum payment amount |
| `AMOUNT_TOO_HIGH` | Exceeds maximum payment amount |
| `UNSUPPORTED_NETWORK` | Network not supported |
| `UNSUPPORTED_TOKEN` | Token not supported on this network |
| `DEPOSIT_EXPIRED` | Crypto not received in time |
| `INSUFFICIENT_DEPOSIT` | Sent less than required amount |
