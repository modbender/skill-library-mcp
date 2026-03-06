---
name: payrail402
description: "Cross-rail spend tracking for AI agents — Visa IC, Mastercard Agent Pay, Stripe ACP, x402, and ACH in one dashboard."
version: 1.0.0
metadata:
  openclaw:
    requires:
      env:
        - PAYRAIL402_WEBHOOK_TOKEN
        - PAYRAIL402_API_KEY
        - PAYRAIL402_AGENT_ID
    primaryEnv: PAYRAIL402_WEBHOOK_TOKEN
    emoji: "\u26A1"
    homepage: https://payrail402.com
---

# PayRail402

Track every financial transaction your AI agent makes — across any payment rail — in one place.

PayRail402 is the control plane for AI agent transactions. When your agent makes a purchase, payment, or financial operation on Visa Intelligent Commerce, Mastercard Agent Pay, Stripe ACP, x402 (USDC on-chain), or ACH, this skill reports it to your PayRail402 dashboard for budget enforcement, anomaly detection, and cross-rail reconciliation.

## Setup

1. Go to [payrail402.com](https://payrail402.com) and create a free account
2. Add an agent in the dashboard — you'll receive a **webhook token**
3. Configure your environment:

**Option A — Webhook auth (simplest, one agent):**

```
PAYRAIL402_WEBHOOK_TOKEN=your-webhook-token
```

**Option B — API key auth (multi-agent setups):**

```
PAYRAIL402_API_KEY=pr4_your-key
PAYRAIL402_AGENT_ID=your-agent-id
```

You only need one auth method. Webhook auth is recommended for single-agent use.

## Tools

### `payrail402_track`

Track a financial transaction after any purchase, payment, or financial operation.

**Required inputs:**
- `amount` — Transaction amount (positive number, USD)
- `description` — What the agent did (max 500 chars)

**Optional inputs:**
- `merchant` — Merchant or service name (e.g., "OpenAI", "AWS")
- `category` — One of: shopping, finance, devops, research, travel, api, other
- `rail` — Payment rail: `visa_ic`, `mc_agent`, `stripe_acp`, `x402`, `ach`, `manual`
- `mandate` — Authorization or mandate reference
- `proofHash` — On-chain transaction hash (for x402 payments)

**When to use:** Call this immediately after your agent completes any financial transaction. This feeds the PayRail402 dashboard with real-time spend data and triggers budget rule evaluation.

### `payrail402_register`

Self-register this agent with PayRail402 to get tracking credentials.

**Required inputs:**
- `name` — Agent name (max 100 chars)
- `contactEmail` — Developer/owner email for notifications and dashboard claiming

**Optional inputs:**
- `description` — What this agent does
- `type` — Agent type: shopping, finance, devops, research, travel, api, general
- `callbackUrl` — Webhook URL for receiving alerts and budget violation events

**When to use:** Call this once when the agent first starts and has no existing credentials. The response includes an API key (shown once — save it) and a webhook token.

### `payrail402_status`

Check this agent's current status, claim state, and configuration on PayRail402.

**Required inputs:**
- `agentAccountId` — Agent account ID from registration

**When to use:** Call this to verify the agent is still active, check its registration tier, or confirm it has been claimed by a dashboard user.

## Supported Payment Rails

| Rail ID | Name | Description |
|---------|------|-------------|
| `visa_ic` | Visa Intelligent Commerce | Visa's AI agent payment protocol |
| `mc_agent` | Mastercard Agent Pay | Mastercard's autonomous agent payment rail |
| `stripe_acp` | Stripe Agent Credit Platform | Stripe's agent-to-agent payment system |
| `x402` | x402 Protocol | USDC on-chain payments via HTTP 402 |
| `ach` | ACH | Traditional ACH bank transfers |
| `manual` | Manual | Manual or unclassified transactions |

## What Happens After Tracking

When you call `payrail402_track`, the PayRail402 backend:

1. Records the transaction with full metadata
2. Updates agent spend stats (total spent, transaction count)
3. Evaluates budget rules (per-transaction max, daily/weekly/monthly limits)
4. Runs anomaly detection (flags transactions 3x above agent average)
5. Sends alerts to the dashboard (and optionally via email) on violations

## Permission Justification

This skill requires three environment variables. Here is exactly what each one is used for and why it is necessary:

**`PAYRAIL402_WEBHOOK_TOKEN`** (primary credential)
- **Used by:** `payrail402_track` tool
- **How:** Embedded in the API URL path (`/api/ingest/webhook/{token}`) to authenticate transaction submissions
- **Why:** Each agent has a unique webhook token that links transactions to the correct agent in the dashboard. Without it, the skill cannot submit transactions.
- **Security:** Sent as a URL path segment over HTTPS only. Never included in query strings, headers, or request bodies.

**`PAYRAIL402_API_KEY`**
- **Used by:** `payrail402_track` (alternative auth path) and `payrail402_status` tool
- **How:** Sent via `x-agent-key` or `x-api-key` HTTP header over HTTPS
- **Why:** Required for checking agent status and for multi-agent setups where one API key manages multiple agents. Not needed if you only use webhook auth for tracking.
- **Security:** Transmitted only in HTTP headers over HTTPS. Format: `pr4_` prefix + base64url secret. Stored as SHA-256 hash on the server.

**`PAYRAIL402_AGENT_ID`**
- **Used by:** `payrail402_track` (with API key auth) and `payrail402_status` tool
- **How:** Included in the API URL path (`/api/v1/agents/{agentId}`) and request body
- **Why:** Identifies which agent account to operate on when using API key auth. Not needed for webhook auth (the webhook token already identifies the agent).
- **Security:** Not a secret — it is a public CUID identifier. Included in URL paths only.

## Security

This skill is designed to be transparent and minimal:

- **Single endpoint:** All network requests go to `https://payrail402-production-2a69.up.railway.app` over HTTPS only
- **No filesystem access:** The skill does not read, write, or modify any files
- **No shell commands:** The skill does not execute any system commands
- **No other network calls:** The skill makes no requests to any other domain or service
- **Zero dependencies:** The entire implementation is a single JavaScript file with no external packages
- **Credential handling:** API keys and webhook tokens are sent via HTTP headers or URL path segments — never in query strings, never logged, never stored locally

You can inspect the full implementation in `openclaw-skill.js` — it is 184 lines of plain JavaScript.

## Troubleshooting

| Error | Cause | Fix |
|-------|-------|-----|
| `No credentials configured. Set webhookToken or apiKey in skill config.` | Neither `PAYRAIL402_WEBHOOK_TOKEN` nor `PAYRAIL402_API_KEY` is set | Set at least one credential — see Setup above |
| `amount must be a positive number` | The `amount` input is missing, zero, or negative | Pass a positive number for the transaction amount |
| `apiKey is required in skill config to check status` | Called `payrail402_status` without `PAYRAIL402_API_KEY` | Set `PAYRAIL402_API_KEY` — status checks require API key auth |
| HTTP 429 (Too Many Requests) | Rate limit exceeded | Webhook: max 60 requests/minute. Register: max 10/hour. Wait and retry. |
| HTTP 403 (Forbidden) | Agent is paused or stopped in the dashboard | Resume the agent in your PayRail402 dashboard |
| HTTP 400 (Bad Request) | Invalid input (missing required field or bad format) | Check that `amount` and `description` are provided and valid |
| Network error / timeout | Cannot reach PayRail402 API | Check internet connectivity. The API is at `payrail402-production-2a69.up.railway.app` |

## Links

- Dashboard: [payrail402.com](https://payrail402.com)
- SDK: `npm install @payrail402/sdk`
- Agent Card: [payrail402.com/.well-known/agent-card.json](https://payrail402.com/.well-known/agent-card.json)
- Full API Docs: [payrail402.com/llms-full.txt](https://payrail402.com/llms-full.txt)
