# AgentSecrets — OpenClaw Integration

> Zero-knowledge credential proxy for OpenClaw agents

Your OpenClaw agent can make authenticated API calls to any service — Stripe, OpenAI, GitHub, Google Maps, etc. — without ever seeing your API key values.

## Setup

### From ClawHub
```bash
openclaw skill install agentsecrets
```

### Manual
```bash
# Copy this directory to your OpenClaw skills folder
cp -r integrations/openclaw ~/.openclaw/skills/agentsecrets
```

## Prerequisites

```bash
pip install agentsecrets
agentsecrets init
agentsecrets secrets set STRIPE_KEY=sk_test_your_key
```

## Usage

Once installed, just ask your OpenClaw agent:

> "Check my Stripe balance"

The agent will:
1. Run `agentsecrets secrets list` to find available keys
2. Run `agentsecrets call --url https://api.stripe.com/v1/balance --bearer STRIPE_KEY`
3. Return the response — without ever seeing `sk_test_...`

## Why This Matters

OpenClaw stores credentials in plaintext (`~/.openclaw/.env`, config JSON files). After CVE-2026-25253 and the ClawHub supply chain attacks, **30,000+ installations were compromised** and API keys were stolen.

AgentSecrets fixes this architecturally:
- Keys in OS keychain, not plaintext files
- Agent sees key **names**, never **values**
- Full audit trail of every key usage
- Nothing to steal from agent memory or chat logs

## Publishing to ClawHub

```bash
clawhub publish integrations/openclaw
```

## Links

- [AgentSecrets GitHub](https://github.com/The-17/agentsecrets)
- [Security Docs](https://github.com/The-17/agentsecrets/blob/main/docs/PROXY.md)
- [The Seventeen](https://github.com/The-17)
