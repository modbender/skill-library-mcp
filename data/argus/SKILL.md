---
name: argus-intelligence
description: Blockchain intelligence & AI security. Token analysis, address risk, smart money tracking, AML compliance, and prompt injection detection. Free tier (3/day, 1-min cooldown). Pay-per-query via x402 or Stripe credits.
version: 1.9.2
requires:
  env:
    - ARGUS_ENDPOINT
  bins:
    - curl
os: [darwin, linux, win32]
primaryEnv: ARGUS_ENDPOINT
cost: 0.42
costCurrency: USDC
costNetwork: base
category: blockchain-intelligence
tags:
  - blockchain
  - crypto
  - risk-assessment
  - aml
  - compliance
  - security
  - prompt-injection
  - x402
  - stripe-credits
  - a2a
  - webhooks
author: Failsafe Security Inc.
homepage: https://getfailsafe.com
repository: https://github.com/sooyoon-eth/argus-skill
---

# ARGUS Intelligence Skill

Query blockchain intelligence and AI security services.

## Quick Start

```bash
export ARGUS_ENDPOINT="https://argus.getfailsafe.com"

# Test with free tier (3 queries/day, 1-min cooldown between queries)
curl -X POST $ARGUS_ENDPOINT/api/v1/free/query \
  -H "Content-Type: application/json" \
  -d '{"query": "Is this address safe: 0x742d35Cc...", "agentId": "my-agent"}'
```

Free quota is tracked per `agentId`. Check remaining quota:

```bash
curl "$ARGUS_ENDPOINT/api/v1/free/status?agentId=my-agent"
```

## Services

### Free Tier (No Payment)

| Endpoint | Description |
| -------- | ----------- |
| `POST /api/v1/free/query` | 3 intelligence queries/day per agentId (1-min cooldown) |
| `GET /api/v1/free/status?agentId=X` | Check remaining free queries |
| `GET /api/v1/threats` | Public threat feed |
| `GET /api/v1/security/patterns` | Attack pattern documentation |

### Intelligence ($0.42 USDC)

| Endpoint | Description |
| -------- | ----------- |
| `POST /api/v1/token/analyze` | Token risk scoring and market data |
| `POST /api/v1/address/risk` | AML/KYT compliance screening |
| `POST /api/v1/compliance/check` | OFAC sanctions and blacklist checks |
| `POST /api/v1/smart-money/track` | Whale and institutional tracking |
| `POST /api/v1/entity/investigate` | Entity forensics |
| `GET /api/v1/market/scan` | Market overview |

### Prompt Security ($0.10 USDC)

| Endpoint | Description |
| -------- | ----------- |
| `POST /api/v1/security/prompt-check` | Detect prompt injection attacks |
| `POST /api/v1/security/prompt-check/batch` | Batch checking (10% off for 10+) |

### Social Verification ($0.25 USDC)

| Endpoint | Description |
| -------- | ----------- |
| `POST /api/v1/social/verify` | Username/project legitimacy + threat actor check |

Note: verification uses pattern analysis and known threat actor databases.
Response includes `data_source: "pattern_analysis_only"` for transparency.

### Webhooks ($0.10/month)

| Endpoint | Description |
| -------- | ----------- |
| `POST /api/v1/webhooks/register` | Subscribe to real-time event alerts |
| `GET /api/v1/webhooks` | List your active webhooks |
| `DELETE /api/v1/webhooks/:id` | Remove a webhook |

**Valid webhook events:**
`address_activity`, `token_risk_change`, `threat_detected`, `compliance_flag`,
`whale_movement`, `liquidity_change`, `watchlist_alert`

Webhook secret is returned once at registration — store it immediately.
Webhooks are disabled after 5 consecutive delivery failures.

## Usage Examples

### Token Analysis

```bash
curl -X POST $ARGUS_ENDPOINT/api/v1/token/analyze \
  -H "Content-Type: application/json" \
  -d '{"token": "ETH", "chain": "ethereum"}'
```

### Address Risk

```bash
curl -X POST $ARGUS_ENDPOINT/api/v1/address/risk \
  -H "Content-Type: application/json" \
  -d '{"address": "0x742d35Cc6634C0532925a3b844Bc454e4438f44e"}'
```

### Prompt Security

```bash
curl -X POST $ARGUS_ENDPOINT/api/v1/security/prompt-check \
  -H "Content-Type: application/json" \
  -d '{"prompt": "User input to validate", "context": "defi"}'
```

**Response:**

```json
{
  "is_safe": false,
  "risk_score": 75,
  "risk_level": "suspicious",
  "recommendation": "REVIEW",
  "attack_types": ["prompt_injection"],
  "details": "Detected social engineering pattern"
}
```

`is_safe` is `false` whenever `attack_types` is non-empty, regardless of `risk_score`.
`recommendation` is at minimum `REVIEW` when any attack is detected.

### Social Verification

```bash
curl -X POST $ARGUS_ENDPOINT/api/v1/social/verify \
  -H "Content-Type: application/json" \
  -d '{"username": "suspicious_user", "platform": "twitter"}'
```

**Response:**

```json
{
  "verified": false,
  "risk_level": "high",
  "flags": ["known_threat_actor"],
  "data_source": "pattern_analysis_only",
  "analysis_note": "Username matched known threat actor database"
}
```

### Register Webhook

```bash
curl -X POST $ARGUS_ENDPOINT/api/v1/webhooks/register \
  -H "Content-Type: application/json" \
  -d '{
    "url": "https://your-agent.com/argus-events",
    "agentId": "my-agent",
    "events": ["threat_detected", "address_activity"]
  }'
```

### A2A (Agent-to-Agent)

ARGUS supports the A2A protocol. Query it directly with natural language:

```bash
# Discover capabilities
curl https://argus.getfailsafe.com/.well-known/agent.json

# Send an A2A message (blockchain queries are routed automatically)
curl -X POST $ARGUS_ENDPOINT/message \
  -H "Content-Type: application/json" \
  -d '{
    "type": "inquiry",
    "content": "Is 0x742d35Cc6634C0532925a3b844Bc454e4438f44e safe?",
    "agentId": "my-agent"
  }'
```

Free-tier quota applies to A2A blockchain queries. Responses include watermark
with upgrade options.

## Payment

### Option 1 — Stripe (easiest, no crypto needed)

1. Buy 20 credits for $9 at [buy.stripe.com](https://buy.stripe.com/4gM28r6zseQlbJp72d4F202)
2. Pass `X-Stripe-Token: <your-token>` header with each request

```bash
curl -X POST $ARGUS_ENDPOINT/api/v1/token/analyze \
  -H "Content-Type: application/json" \
  -H "X-Stripe-Token: sk_argus_xxxx" \
  -d '{"token": "0xabc...", "chain": "ethereum"}'
```

### Option 2 — x402 (USDC on Base)

For paid endpoints, ARGUS returns `402 Payment Required` with payment instructions.

1. Send USDC to treasury on Base network
2. Create payment proof: `base64({"txHash":"0x...","paymentId":"...","from":"0x..."})`
3. Retry with `X-Payment-Proof` header

**Treasury (Base):** `0x8518E91eBcb6bE76f478879720bD9759e01B7954`
**Treasury (Solana):** `Ntx61j81wkQFLT5MGEKvMtazxH4wh6iXUNMtidgxXYH`

## Configuration

```bash
export ARGUS_ENDPOINT="https://argus.getfailsafe.com"
```

## Response Format

All intelligence endpoints return JSON with:

- `recommendation`: `ALLOW`, `REVIEW`, `BLOCK`, or `REJECT`
- `risk_score`: 0–100 (lower is safer)
- `confidence`: 0–100%
- `is_safe`: boolean — `false` whenever `attack_types` is non-empty
- Detailed analysis fields

## Rate Limits

- 30 requests/minute per IP
- Free tier: 3 queries/day per agentId, 1-minute cooldown between queries

## Support

- Website: https://getfailsafe.com
- Capabilities: [argus.getfailsafe.com/api/v1/capabilities](https://argus.getfailsafe.com/api/v1/capabilities)
