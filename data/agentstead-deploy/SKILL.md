---
name: agentstead-deploy
description: Deploy OpenClaw sub-agent APIs to AgentStead cloud hosting with production-ready OpenClaw setup. Use when a user wants to auto-deploy a sub-agent on AgentStead, connect Telegram/Discord, and launch quickly with billing via Stripe (card), crypto (USDC), or ASTD balance.
version: 1.1.0
---

# AgentStead Deploy

Deploy an OpenClaw agent to AgentStead's cloud hosting in minutes.

**API Base URL:** `https://www.agentstead.com/api/v1`

## Quick Deploy Flow

1. Register/login → 2. Create agent → 3. Add channel → 4. Set up billing → 5. Start agent → 6. Verify

## Conversation Guide

Before calling any APIs, gather from the user:

1. **Agent name** — What should the agent be called?
2. **Personality/instructions** — System prompt or personality description
3. **Channel** — Telegram (need bot token from @BotFather) or Discord (need bot token from Discord Developer Portal)
4. **AI plan** — BYOK (bring your own API key, $0) or AgentStead Provided (PAYG, or 1K/3K/5K/10K ASTD/mo)
5. **If BYOK** — Which provider and API key? (Anthropic, OpenAI, Google, OpenRouter, xAI, Groq, Mistral, Bedrock, Venice, and 10+ more)
6. **Hosting plan** — Starter $9/mo, Pro $19/mo, Business $39/mo, Enterprise $79/mo
7. **Payment method** — ASTD Balance, Crypto (USDC), or Card (Stripe)

## Step-by-Step Workflow

### Step 1: Register

```bash
curl -X POST https://www.agentstead.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

Response includes `token` — use as `Authorization: Bearer <token>` for all subsequent requests.

If user already has an account, use login instead:

```bash
curl -X POST https://www.agentstead.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "securepass123"}'
```

### Step 2: Create Agent

```bash
curl -X POST https://www.agentstead.com/api/v1/agents \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "MyAgent",
    "personality": "You are a helpful assistant...",
    "plan": "starter",
    "aiPlan": "byok",
    "byokProvider": "anthropic",
    "byokApiKey": "sk-ant-..."
  }'
```

For AgentStead Provided AI (uses ASTD credits):
```json
{
  "name": "MyAgent",
  "personality": "You are a helpful assistant...",
  "plan": "pro",
  "aiPlan": "ASTD_5000"
}
```

Valid `aiPlan` values: `BYOK`, `PAYG`, `ASTD_1000`, `ASTD_3000`, `ASTD_5000`, `ASTD_10000`

Response includes the agent `id` — save it for subsequent steps.

### Step 3: Add Channel

**Telegram:**
```bash
curl -X POST https://www.agentstead.com/api/v1/agents/<agent_id>/channels \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"type": "telegram", "botToken": "123456:ABC-DEF..."}'
```

**Discord:**
```bash
curl -X POST https://www.agentstead.com/api/v1/agents/<agent_id>/channels \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"type": "discord", "botToken": "MTIz..."}'
```

### Step 4: Set Up Billing

**Crypto (USDC):**
```bash
curl -X POST https://www.agentstead.com/api/v1/billing/crypto/create-invoice \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "<agent_id>", "plan": "starter", "aiPlan": "PAYG"}'
```

Returns a payment address/URL. Guide user to send USDC (Base or Polygon chain).

**Stripe (card):**
```bash
curl -X POST https://www.agentstead.com/api/v1/billing/checkout \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"agentId": "<agent_id>", "plan": "starter", "aiPlan": "PAYG"}'
```

Returns a Stripe checkout URL. Send to user to complete payment.

### Step 5: Start Agent

```bash
curl -X POST https://www.agentstead.com/api/v1/agents/<agent_id>/start \
  -H "Authorization: Bearer <token>"
```

### Step 6: Verify

```bash
curl -X GET https://www.agentstead.com/api/v1/agents/<agent_id> \
  -H "Authorization: Bearer <token>"
```

Check that `status` is `"RUNNING"`. If not, wait a few seconds and retry.

## Pricing Reference

### Hardware Plans (per agent)
| Plan | Price | Specs |
|------|-------|-------|
| Starter | $9/mo | t3.micro · 1 vCPU · 1GB RAM · 5GB storage |
| Pro | $19/mo | t3.small · 2 vCPU · 2GB RAM · 20GB storage |
| Business | $39/mo | t3.medium · 2 vCPU · 4GB RAM · 50GB storage |
| Enterprise | $79/mo | t3.large · 2 vCPU · 8GB RAM · 100GB storage |

### AI Plans
| Plan | Price | Description |
|------|-------|-------------|
| BYOK | $0 | Bring your own API key (20+ providers) |
| PAYG | $0 base | Pay-as-you-go from ASTD balance |
| ASTD_1000 | $10/mo | 1,000 ASTD monthly credits |
| ASTD_3000 | $30/mo | 3,000 ASTD monthly credits |
| ASTD_5000 | $50/mo | 5,000 ASTD monthly credits |
| ASTD_10000 | $100/mo | 10,000 ASTD monthly credits |

AgentStead Provided plans include: Claude 3.5 Haiku, Claude Sonnet 4, Claude Opus 4.6

### Payment Methods
- **ASTD Balance** — top up wallet, auto-deducted on billing cycle
- **Stripe** — credit/debit card subscriptions
- **USDC** — Base or Polygon chain crypto payments
- **Apple IAP** — iOS app only

**Supported BYOK Providers:** Anthropic, OpenAI, Google Gemini, OpenRouter, xAI, Groq, Mistral, AWS Bedrock, Together AI, Hugging Face, Venice AI, Z.AI, Moonshot/Kimi, Cerebras, MiniMax, Xiaomi, Custom Provider, and more.

## Notes

- Telegram bot tokens come from [@BotFather](https://t.me/BotFather)
- Discord bot tokens come from the [Discord Developer Portal](https://discord.com/developers/applications)
- Agents can be stopped with `POST /agents/:id/stop` and restarted anytime
- See `references/api-reference.md` for full API documentation
