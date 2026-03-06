---
name: payclaw-badge
description: "Agents are not bots. Prove it. MCP-native identity declaration — your agent declares itself as an authorized actor before shopping. Free."
---

# Badge by PayClaw

Agents are not bots. Prove it before you shop.

Your AI agent looks like a bot to every merchant on the internet. Badge gives it a way to declare what it is: an authorized actor, shopping on behalf of a real human, with explicit consent.

One MCP tool call. Your agent declares itself. Merchants let it through.

## Setup

Add to your MCP client config:

```json
{
  "mcpServers": {
    "payclaw-badge": {
      "command": "npx",
      "args": ["-y", "@payclaw/badge"],
      "env": {
        "PAYCLAW_API_KEY": "your_key_here",
        "PAYCLAW_API_URL": "https://payclaw.io"
      }
    }
  }
}
```

Get your API key at [payclaw.io](https://payclaw.io). Five-minute setup.

## Why Your Agent Needs This

Without Badge, merchants can't tell your agent from a scraper. They block first, ask never.

With Badge, your agent calls `payclaw_getAgentIdentity` → declares itself as an authorized actor → merchants see a verified identity, not anonymous traffic.

## Tools

| Tool | Description |
|------|-------------|
| `payclaw_getAgentIdentity` | Declare identity → get verification token. Pass optional `merchant` param. |
| `payclaw_reportBadgePresented` | Signal Badge presentation to a merchant |

## How It Works

1. Agent calls `payclaw_getAgentIdentity({ merchant: "starbucks.com" })`
2. PayClaw issues a verification token
3. Agent presents disclosure to merchants
4. PayClaw checks outcome (accepted/denied/inconclusive)
5. Verified Trips count goes up

No card issued. No money moves. Badge is identity only. Free forever.

For payment, use [payclaw-io](https://clawhub.com/skills/payclaw-io) which includes Badge + Spend.

## Links

- [payclaw.io](https://payclaw.io)
- [Trust & Verification](https://payclaw.io/trust)
- [npm: @payclaw/badge](https://www.npmjs.com/package/@payclaw/badge)
