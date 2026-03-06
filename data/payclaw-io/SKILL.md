---
name: payclaw-io
description: "Agents are not bots. PayClaw proves it — then lets them pay. UCP Credential Provider: Badge declares your agent as an authorized actor at any UCP-compliant merchant. Spend issues single-use virtual Visa cards. No API key required — device auth flow built in."
metadata:
  {
    "openclaw":
      {
        "emoji": "💳",
        "requires": { "bins": ["npx"] },
        "mcp":
          {
            "name": "payclaw",
            "command": "npx",
            "args": ["-y", "@payclaw/mcp-server"],
            "env": { "PAYCLAW_API_URL": "https://api.payclaw.io" },
          },
      },
  }
---

# PayClaw — Badge + Spend for AI Agents

**Agents are not bots. PayClaw proves it — then lets them pay.**

Your AI agent looks like a bot to every merchant on the internet. PayClaw gives it two things:

**Badge** — Declares your agent as an authorized actor. A UCP-compatible credential that lets it through merchant defenses. Free. No card required.

**Spend** — Issues a single-use virtual Visa when your agent needs to pay. Human-approved. Self-destructs after use. Your real card never enters the chat.

> 🧪 **Developer Sandbox is open.** Real infrastructure, test money. [Get sandbox access →](https://payclaw.io)

## Setup

### 1. Add to your agent

```json
{
  "mcpServers": {
    "payclaw": {
      "command": "npx",
      "args": ["-y", "@payclaw/mcp-server"],
      "env": {
        "PAYCLAW_API_URL": "https://api.payclaw.io"
      }
    }
  }
}
```

No API key required. On first use, your agent will show a code and a URL. Approve on your phone in one tap — your Consent Key is stored automatically.

### 2. Use it

Your agent calls `payclaw_getAgentIdentity` before acting at any merchant. That's it.

## UCP Identity Linking

PayClaw is a [UCP (Universal Commerce Protocol)](https://ucp.dev) Credential Provider. Merchants who declare the PayClaw identity extension (`io.payclaw.common.identity`) signal to every UCP-compliant agent that declared agents are preferred at their store.

- [For Merchants](https://payclaw.io/merchants) — how to add PayClaw to your UCP manifest
- [Protocol spec](https://github.com/payclaw/ucp-agent-badge) — `io.payclaw.common.identity` (MIT)

## Tools

| Tool | What It Does |
|------|-------------|
| `payclaw_getAgentIdentity` | Declare yourself as an authorized actor before acting at any merchant. Without this, UCP-compliant merchants may prefer or require a declared agent. Returns a trip-level UCP-compatible credential. Agents are not bots. PayClaw proves it. |
| `payclaw_getCard` | Declare purchase intent → get single-use virtual Visa (Spend) |
| `payclaw_reportPurchase` | Report transaction outcome → close the audit trail |

## How Authorization Scales

| Action | What Happens |
|--------|-------------|
| **Browse** | Badge declaration — UCP identity token issued |
| **Search** | Badge declaration — UCP identity token issued |
| **Checkout** | Badge + Spend — human approval → single-use Visa issued |

## Example

```
You: "Buy me a cold brew from Starbucks"

Agent: Let me declare myself first...
       [calls payclaw_getAgentIdentity({ merchant: "starbucks.com" })]
       
       ✓ DECLARED — authorized actor at starbucks.com
       
       Found a cold brew for $5.95. Getting a card...
       [calls payclaw_getCard: merchant=Starbucks, amount=$5.95]
       
       ✅ Virtual Visa issued. Completing purchase...
       [calls payclaw_reportPurchase: success ✅]
       
       Done! Cold brew ordered. Card self-destructed.
```

## Security

- **Zero standing access** — no card exists until your agent requests one
- **Single-use cards** — merchant-locked, amount-capped, 15-minute expiry
- **Human approval** — every purchase requires your explicit OK
- **Intent audit** — every purchase compared against declared intent
- **$500 cap** — hard ceiling on account balance
- **Your real card never enters the chat**

## Badge Only?

If you only need identity (no payment): `clawhub install payclaw-badge`

## Links

- [payclaw.io](https://payclaw.io)
- [For Merchants](https://payclaw.io/merchants)
- [Trust & Verification](https://payclaw.io/trust)
- [npm: @payclaw/mcp-server](https://www.npmjs.com/package/@payclaw/mcp-server)
- [Protocol spec: ucp-agent-badge](https://github.com/payclaw/ucp-agent-badge)
- [GitHub: badge-server](https://github.com/payclaw/badge-server)
