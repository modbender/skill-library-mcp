# PayRail402 — AI Agent Spend Control Plane

Track every financial transaction your AI agent makes across Visa IC, Mastercard Agent Pay, Stripe ACP, x402 blockchain, and ACH — in one dashboard.

## What It Does

This skill gives your OpenClaw agent three tools:

| Tool | Purpose |
|------|---------|
| `payrail402_track` | Report a financial transaction for monitoring, budget enforcement, and anomaly detection |
| `payrail402_register` | Self-register the agent and receive API credentials |
| `payrail402_status` | Check the agent's current status and configuration |

After each tracked transaction, PayRail402 evaluates budget rules, runs anomaly detection, and sends alerts to your dashboard.

## How It Works

```
Your Agent                    PayRail402
    |                             |
    |-- payrail402_track -------->|  Record transaction
    |                             |  Update agent stats
    |                             |  Evaluate budget rules
    |                             |  Run anomaly detection
    |                             |
    |                             +--> Dashboard (real-time)
    |                             +--> Email alerts (if configured)
    |                             |
    |<--- { success, txId } ------|
```

The skill communicates with the PayRail402 API over HTTPS. No data is stored locally.

## Setup

1. Create a free account at [payrail402.com](https://payrail402.com)
2. Add an agent in the dashboard
3. Copy the webhook token from the agent detail page
4. Set the environment variable:

```
PAYRAIL402_WEBHOOK_TOKEN=your-webhook-token
```

For multi-agent setups, use API key auth instead:

```
PAYRAIL402_API_KEY=pr4_your-key
PAYRAIL402_AGENT_ID=your-agent-id
```

## Supported Payment Rails

| Rail ID | Name |
|---------|------|
| `visa_ic` | Visa Intelligent Commerce |
| `mc_agent` | Mastercard Agent Pay |
| `stripe_acp` | Stripe Agent Credit Platform |
| `x402` | x402 Protocol (USDC on-chain via HTTP 402) |
| `ach` | ACH bank transfers |
| `manual` | Manual or unclassified |

## Security

- All requests go to a single endpoint over HTTPS only
- No filesystem access, no shell commands, no third-party network calls
- Zero external dependencies — one self-contained JavaScript file
- Credentials are sent via HTTP headers or URL path segments, never in query strings
- API keys are stored as SHA-256 hashes on the server
- Full source code is in `openclaw-skill.js` (184 lines) — read it yourself

## Troubleshooting

**"No credentials configured"**
Set `PAYRAIL402_WEBHOOK_TOKEN` or `PAYRAIL402_API_KEY` in your environment.

**"amount must be a positive number"**
The `amount` input to `payrail402_track` must be greater than zero.

**"apiKey is required in skill config to check status"**
The `payrail402_status` tool requires `PAYRAIL402_API_KEY` — webhook auth alone is not sufficient for status checks.

**HTTP 429 (rate limited)**
Webhook ingest allows 60 requests/minute. Agent registration allows 10/hour. Wait and retry.

**HTTP 403 (forbidden)**
The agent may be paused or stopped in the dashboard. Resume it at payrail402.com.

## Links

- Homepage: [payrail402.com](https://payrail402.com)
- Full API Documentation: [payrail402.com/llms-full.txt](https://payrail402.com/llms-full.txt)
- Agent Discovery Card: [payrail402.com/.well-known/agent-card.json](https://payrail402.com/.well-known/agent-card.json)
- npm SDK: `npm install @payrail402/sdk`
