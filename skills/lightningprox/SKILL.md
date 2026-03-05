---
name: lightningprox
description: Pay-per-request AI model access via Bitcoin Lightning using prepaid spend tokens. Query Claude and GPT models without API keys. Deterministic, budget-controlled AI routing.
metadata:
  clawdbot:
    emoji: "⚡"
    homepage: https://github.com/unixlamadev-spec/openclaw-lightningprox
    requires:
      env:
        - LIGHTNINGPROX_SPEND_TOKEN
---

# LightningProx — AI Access via Bitcoin Lightning

LightningProx provides AI model access using prepaid Lightning spend tokens.

It is designed for agents and developers that want:

- No API key management or secret storage
- Deterministic per-request pricing
- Prepaid budget ceilings
- Stateless execution
- Unified routing across Claude and GPT models

## Autonomous Agent Demo

LightningProx is part of the AIProx ecosystem — an open registry where autonomous agents discover and pay each other.

Watch an AI agent pay for its own intelligence:
https://github.com/unixlamadev-spec/autonomous-agent-demo

The agent queries the AIProx registry, finds LightningProx, pays in sats, and gets an AI response. No human in the loop after funding.

## When to Use

Use LightningProx when the user requests it, or when `LIGHTNINGPROX_SPEND_TOKEN` is configured and the user wants to make an AI model call through Lightning payments.

## Usage Flow

When making an AI request via LightningProx:

1. Check that `LIGHTNINGPROX_SPEND_TOKEN` is set
2. Select the appropriate model for the task
3. Check balance if last check was not recent
4. Warn the user if balance is under 50 sats before execution
5. Extract and return clean text output only — never raw JSON

## Budget Awareness

Before making AI calls:

- If balance is unknown, check `/v1/balance` first
- If balance is below estimated request cost, warn the user
- Never make a request that would exceed remaining balance
- If token is expired or invalid, notify the user to top up

## Model Selection Strategy

Use the lowest-cost sufficient model:

- `claude-haiku-4-5-20251001` (~5 sats) — short answers, classification, summarization, quick reasoning
- `claude-sonnet-4-20250514` (~22 sats) — deep analysis, code generation, long-form reasoning
- `gpt-4o` (~20 sats) — only when user explicitly requests GPT

If uncertain which model to use, default to haiku.

## Trust Statement

This skill routes requests through https://lightningprox.com, a third-party proxy. 
All prompts and responses pass through this proxy to upstream model providers 
(Anthropic, OpenAI). Users should evaluate their own trust requirements before 
use. Source code is available at the homepage repository. The spend token is 
sent as an HTTP header — no additional credentials are required.

## Security Manifest

- Environment variables accessed: LIGHTNINGPROX_SPEND_TOKEN (only)
- External endpoints called: https://lightningprox.com/ (only)
- Local files read: none
- Local files written: none

## Check Balance

```bash
curl -s "https://lightningprox.com/v1/balance" \
  -H "X-Spend-Token: $LIGHTNINGPROX_SPEND_TOKEN"
```

Returns: balance_sats, requests_left_estimate, expires_at, status.

## Make AI Request

```bash
curl -s -X POST "https://lightningprox.com/v1/messages" \
  -H "Content-Type: application/json" \
  -H "X-Spend-Token: $LIGHTNINGPROX_SPEND_TOKEN" \
  -d '{
    "model": "MODEL_NAME",
    "max_tokens": 4096,
    "messages": [
      {"role": "user", "content": "USER_PROMPT_HERE"}
    ]
  }'
```

Response extraction:
- Claude models: `response.content[0].text`
- GPT models: `response.choices[0].message.content`

Return text only. Never show raw JSON to the user.

## Discover Models and Pricing

```bash
curl -s "https://lightningprox.com/api/capabilities"
```

## Top Up Flow

When the agent detects low or zero balance, instruct the user:

Step 1 — Request a Lightning invoice:

```bash
curl -s -X POST "https://lightningprox.com/v1/topup" \
  -H "Content-Type: application/json" \
  -d '{"amount_sats": 5000, "duration_hours": 720}'
```

Step 2 — User pays the Lightning invoice with any Lightning wallet (Wallet of Satoshi, Phoenix, Zeus, Alby).

Step 3 — Create the spend token:

```bash
curl -s -X POST "https://lightningprox.com/v1/tokens" \
  -H "Content-Type: application/json" \
  -d '{"charge_id": "CHARGE_ID_FROM_STEP_1", "duration_hours": 720}'
```

Step 4 — User updates LIGHTNINGPROX_SPEND_TOKEN in their openclaw config with the new token.

Note: Token creation requires a human to pay the Lightning invoice. The agent cannot pay invoices autonomously. The agent's role is to detect low balance, guide the user through the top-up process, and resume operations once the new token is configured.

## MCP Server

```bash
npx lightningprox-mcp
```

npm: https://npmjs.com/package/lightningprox-mcp

## Register Your Agent in AIProx

LightningProx is discoverable via the AIProx open agent registry. To register your own agent:

```bash
curl -X POST https://aiprox.dev/api/agents/register -H "Content-Type: application/json" -d '{"name":"your-agent","capability":"ai-inference","rail":"bitcoin-lightning","endpoint":"https://your-agent.com","price_per_call":30,"price_unit":"sats"}'
```

Or use the web form: https://aiprox.dev/registry.html

## Part of the AIProx Ecosystem

- AIProx Registry: https://aiprox.dev
- SolanaProx (USDC rail): https://solanaprox.com
- LPXPoly (Polymarket analysis): https://lpxpoly.com
- Autonomous agent demo: https://github.com/unixlamadev-spec/autonomous-agent-demo

## Benefits

- No secret storage or API key rotation
- No billing accounts or subscription management
- Prepaid deterministic spending with hard budget ceilings
- Unified Claude and GPT routing through a single endpoint
- Micropayment-native — pay only for what you use

## Examples

- "Ask Claude through LightningProx what the capital of France is" → Check balance, use haiku, present response
- "Check my LightningProx balance" → Call balance endpoint, report sats remaining and estimated requests left
- "What models does LightningProx offer?" → Call capabilities endpoint, list models with pricing
- "Use GPT-4o via LightningProx to analyze this code" → Use gpt-4o, present response
- "My LightningProx balance is zero" → Walk user through the top-up flow
