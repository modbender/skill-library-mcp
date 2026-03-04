# Badge by PayClaw

**Agents are not bots. Prove it.**

Your AI agent looks like a bot to every merchant on the internet. Badge gives it a way to declare what it is: an authorized actor, shopping on behalf of a real human, with explicit consent.

One MCP tool call. Your agent declares itself. Merchants let it through.

## Quick Start

Add to your MCP client config:

```json
{
  "mcpServers": {
    "payclaw-badge": {
      "command": "npx",
      "args": ["-y", "@payclaw/badge"],
      "env": {
        "PAYCLAW_API_KEY": "pk_your_key_here",
        "PAYCLAW_API_URL": "https://payclaw.io"
      }
    }
  }
}
```

Get your API key at [payclaw.io](https://payclaw.io). Five-minute setup.

## Why Your Agent Needs This

Your agent is smart. It can browse, compare prices, build carts, find deals. But to every merchant on the internet, it looks identical to a scraper.

Merchants don't ask "is this agent helpful?" They ask "is this a bot?" And they block first, ask never.

**Without Badge:** Your agent hits a merchant → bot detection fires → blocked. Task fails. Your user is disappointed. The merchant lost a sale and doesn't know it.

**With Badge:** Your agent calls `payclaw_getAgentIdentity` → receives a verification token → presents it to the merchant. The merchant sees: authorized actor, verified human behind it, declared intent. Your agent gets through. Task succeeds.

Your agent will recognize when it needs this. When it encounters a merchant that may challenge automated traffic, it tells you: "I need PayClaw Badge installed to complete this safely." You click Allow. Done.

## What Badge Declares

Every time your agent calls `payclaw_getAgentIdentity`, it receives a verification token that declares:

- **Agent type:** Authorized actor (not a bot, not a scraper)
- **Principal:** Verified human behind this session
- **Scope:** What the agent intends to do (`[BROWSE]` in V1)
- **Contact:** `agent_identity@payclaw.io` for merchant verification

The agent presents this disclosure to merchants. Merchants see a verified identity, not anonymous traffic.

## How It Works

```
1. Your agent calls payclaw_getAgentIdentity before shopping
2. PayClaw issues an HMAC-SHA256 verification token
3. Agent presents the disclosure to merchants
4. PayClaw checks back: "Were you accepted or denied?"
5. Outcome recorded — your Verified Trips count goes up
```

No card is issued. No money moves. Badge is the identity layer — the skeleton key that lets authorized agents through while bot defenses stay intact.

## Tools

| Tool | Description |
|------|-------------|
| `payclaw_getAgentIdentity` | Declare identity, get verification token |
| `payclaw_reportBadgePresented` | Signal that you presented your Badge to a merchant |

## Need Payment Too?

Badge is the base layer. For virtual Visa cards, use [@payclaw/mcp-server](https://www.npmjs.com/package/@payclaw/mcp-server) — which includes Badge automatically.

```bash
clawhub install payclaw-io
```

## KYA — Know Your Agent

PayClaw is KYA infrastructure. Every declaration creates a verified record of agentic commerce behavior — building the trust signal that merchants need to tell authorized agents from anonymous bots.

- [Trust & Verification](https://payclaw.io/trust) — The full trust architecture
- [Dashboard](https://payclaw.io/dashboard/badge) — Your agent's Verified Trips

## Links

- **Website:** [payclaw.io](https://payclaw.io)
- **npm:** [@payclaw/badge](https://www.npmjs.com/package/@payclaw/badge)
- **ClawHub:** [payclaw-badge](https://clawhub.com/skills/payclaw-badge)
- **Trust:** [payclaw.io/trust](https://payclaw.io/trust)
- **Contact:** agent_identity@payclaw.io

---

*Agents are not bots. PayClaw proves it.*
