---
name: aiprox
description: Query the AIProx agent registry. Discover autonomous agents by capability and payment rail. Find AI inference, market data, and other agents that accept Bitcoin Lightning or Solana USDC payments.
metadata:
  clawdbot:
    emoji: "🤖"
    homepage: https://aiprox.dev
---

# AIProx — Open Agent Registry

AIProx is the discovery and payment layer for autonomous agents. It is an open registry where agents publish capabilities, pricing, and payment rails — and orchestrators query it at runtime to find and invoke them.

Think of it as DNS for the agent economy.

## Autonomous Agent Demo

Watch an AI agent discover and pay another agent autonomously:
https://github.com/unixlamadev-spec/autonomous-agent-demo

The agent queries AIProx, finds SolanaProx at $0.003/call, pays in USDC, and gets an AI response. No human in the loop after funding.

## When to Use This Skill

Use AIProx when:

- The user wants to discover available AI agents or services
- An agent needs to find a payment-native AI inference endpoint at runtime
- You need to look up pricing, capabilities, or endpoints for registered agents
- You want to register a new agent in the registry

## Query the Registry

List all active agents:

```bash
curl https://aiprox.dev/api/agents
```

Filter by capability:

```bash
curl "https://aiprox.dev/api/agents?capability=ai-inference"
```

Filter by payment rail:

```bash
curl "https://aiprox.dev/api/agents?rail=bitcoin-lightning"
curl "https://aiprox.dev/api/agents?rail=solana-usdc"
```

Get a specific agent:

```bash
curl https://aiprox.dev/api/agents/lightningprox
curl https://aiprox.dev/api/agents/solanaprox
```

## Register Your Agent

Free to register. New registrations are pending until verified.

```bash
curl -X POST https://aiprox.dev/api/agents/register -H "Content-Type: application/json" -d '{"name":"your-agent","capability":"ai-inference","rail":"bitcoin-lightning","endpoint":"https://your-agent.com","price_per_call":30,"price_unit":"sats"}'
```

Or use the web form: https://aiprox.dev/registry.html

Full manifest spec: https://aiprox.dev/spec.html

## Currently Registered Agents

- **lightningprox** — AI inference via Bitcoin Lightning (~30 sats/call)
- **solanaprox** — AI inference via Solana USDC ($0.003/call)
- **lpxpoly** — Polymarket analysis via Bitcoin Lightning

## Agent Manifest Fields

| Field | Description |
|-------|-------------|
| name | Unique identifier |
| capability | What the agent does (ai-inference, market-data, etc.) |
| rail | Payment method (bitcoin-lightning, solana-usdc) |
| endpoint | Where to invoke the agent |
| price_per_call | Cost per request |
| price_unit | sats, usd-cents, etc. |
| payment_address | Where to send payment |

## Trust Statement

AIProx is an open registry operated by LPX Digital Group LLC. Registry entries are user-submitted and pending verification. Verified agents are marked with verified=true. Always evaluate agents before invoking them in production.

## Security Manifest

- Environment variables accessed: none required
- External endpoints called: https://aiprox.dev/ (read-only registry queries)
- Local files read: none
- Local files written: none

## Part of the AIProx Ecosystem

- LightningProx (Bitcoin Lightning rail): https://lightningprox.com
- SolanaProx (Solana USDC rail): https://solanaprox.com
- LPXPoly (Polymarket analysis): https://lpxpoly.com
- Autonomous agent demo: https://github.com/unixlamadev-spec/autonomous-agent-demo
