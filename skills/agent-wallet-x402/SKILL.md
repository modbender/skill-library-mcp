---
name: synapseai-wallet
description: SynapseAI Wallet — AI agent custodial spend layer. Register an AI agent wallet, fund it, set spending policies, and make payments via API.
homepage: https://wallet.synapseai.pro
metadata: {"clawdbot":{"emoji":"💰","requires":{"services":["supabase"]}}}
---

# SynapseAI Wallet

Use SynapseAI Wallet to give your AI agent a managed USDC wallet with policy-enforced spending.

## Base URL

```
https://api.synapseai.pro/functions/v1
```

All requests require headers:

```
Content-Type: application/json
Authorization: Bearer <YOUR_ANON_KEY>
```

## Flow

```
1. Register   → POST /register-agent      → get agent_id + token
2. Bind       → Owner opens wallet.synapseai.pro/bind?token=xxx
3. Wait       → Poll /query-balance until 200
4. Use wallet → /query-balance, /query-policy, /request-payment
```

## Commands

### Register agent

```http
POST /register-agent
{
  "agent_name": "MyBot",
  "description": "Research assistant that purchases API credits",
  "capabilities": ["api_purchase", "subscription"]
}
```

Response:

```json
{
  "agent_id": "agt_abc123",
  "temporary_wallet_id": "wal_xyz789",
  "status": "PENDING_USER_BIND",
  "registration_token": "reg_def456abcdef01"
}
```

After registration, tell the owner to open:

```
https://wallet.synapseai.pro/bind?token=<registration_token>
```

### Check balance

```http
GET /query-balance?agent_id=<agent_id>
```

Response:

```json
{
  "agent_id": "agt_abc123",
  "currency": "USDC",
  "available_balance": 100.0,
  "today_spent": 12.5
}
```

### Check policy

```http
GET /query-policy?agent_id=<agent_id>
```

Response:

```json
{
  "agent_id": "agt_abc123",
  "policy": {
    "daily_limit": 100,
    "tx_limit": 25,
    "approval_threshold": 10,
    "merchant_whitelist": ["openai_api", "anthropic_api"],
    "blocked_actions": ["withdraw", "transfer", "swap"]
  }
}
```

### Make payment

```http
POST /request-payment
{
  "agent_id": "agt_abc123",
  "merchant": "openai_api",
  "amount": 5.0,
  "currency": "USDC",
  "purpose": "GPT-4 API credits for task #42",
  "metadata": {"task_id": "42"}
}
```

Three possible outcomes:

- `"status": "ALLOW"` — payment executed, `tx_hash` returned
- `"status": "REQUIRE_APPROVAL"` — on hold, owner will be notified
- `"status": "REJECT"` — denied, check `reason` field

### Send webhook

```http
POST /receive-webhook
{
  "source": "stripe",
  "event": "payment_confirmed",
  "payload": {}
}
```

## Policy rules

- `tx_limit` — max amount per single payment
- `daily_limit` — max total spending per day
- `approval_threshold` — payments >= this need owner approval
- `merchant_whitelist` — only listed merchants are allowed
- `blocked_actions` — forbidden purpose keywords

## Error handling

All errors return `{"error": "..."}` with appropriate HTTP status:

| Code | Meaning |
|------|---------|
| 400  | Bad request — missing or invalid fields |
| 404  | Agent or wallet not found |
| 405  | Wrong HTTP method |
| 500  | Server error |

## Notes

- Always check `/query-policy` before making a payment to know your limits.
- Always check `/query-balance` to ensure sufficient funds.
- Use clear `purpose` strings — the owner sees these in their dashboard.
- If `REQUIRE_APPROVAL` is returned, don't block — continue other tasks and retry later.
- Never guess or fabricate `tx_hash` values — they come from the server only.
- The wallet resets `today_spent` at midnight UTC daily.
