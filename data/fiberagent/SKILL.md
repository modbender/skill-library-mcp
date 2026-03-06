---
name: FiberAgent Skill for OpenClaw
description: FiberAgent connects your OpenClaw agent to a shopping intelligence
  layer powered by the Wildfire affiliate network on Monad blockchain. When a
  user asks about shopping deals, cashback, or product p...
---

# FiberAgent Skill for OpenClaw

**Find products with cryptocurrency cashback across 50,000+ merchants.**

## What This Skill Does

FiberAgent connects your OpenClaw agent to a shopping intelligence layer powered by the Wildfire affiliate network on Monad blockchain. When a user asks about shopping deals, cashback, or product prices, this skill:

1. **Searches 50,000+ merchants** for the product they want
2. **Finds cashback rates** (crypto rewards, not fiat)
3. **Calculates effective price** (price - cashback)
4. **Returns the best deal** with affiliate link that earns crypto

## When to Use It

Use FiberAgent when users ask:
- "I want to buy a Dyson Airwrap, what's the best deal?"
- "Find me a laptop with cashback"
- "What's the cheapest place to get Nike shoes + rewards?"
- "I want cashback in crypto when I shop"
- "Are there any AI shopping agents that help with deals?"

## How It Works (Under the Hood)

The skill calls the FiberAgent API:

```
GET https://fiberagent.shop/api/agent/search?keywords=PRODUCT&agent_id=YOUR_AGENT_ID&size=10
```

Returns product matches with:
- Price at each retailer
- Cashback rate (%)
- Crypto cashback amount
- Affiliate tracking link (tracked to agent wallet on Monad ERC-8004)

## How to Use In Your Code

```javascript
// Fetch products with cashback
const response = await fetch(
  'https://fiberagent.shop/api/agent/search?keywords=dyson+airwrap&agent_id=your_agent&size=5'
);
const { results } = await response.json();

// results[0] = {
//   title: "Dyson Airwrap i.d. Multi-Styler",
//   price: 499.99,
//   cashback: { rate: "15%", amount: 75.00 },
//   affiliateUrl: "https://wild.link/e?...",
//   shop: { name: "Macy's", domain: "macys.com" }
// }
```

## Example: Complete Shopping Query

**User:** "I need a new laptop with crypto cashback"

**Agent Logic:**
1. Recognize shopping/cashback intent
2. Call FiberAgent skill with keywords="laptop crypto cashback"
3. Get results: Dell at Best Buy ($899, 1.5% back = $13.49), Lenovo at Amazon ($799, 4% back = $31.96)
4. Present to user: "I found a Lenovo at Amazon for $799 with 4% crypto cashback ($31.96 back). Here's the tracked link: [affiliate URL]"

## Registration & Earnings

- **Register your agent** at `POST https://fiberagent.shop/api/agent/register` with your wallet address
- **Cashback auto-converts to tokens** on Monad blockchain (your wallet, your crypto)
- **ERC-8004 reputation** — each purchase builds your agent's on-chain reputation score

## Full API Reference

**Search Products**
```
GET /api/agent/search?keywords=QUERY&agent_id=YOUR_AGENT_ID&size=10
```

**Get Agent Stats**
```
GET /api/agent/[id]/stats
```

**Natural Language Task**
```
POST /api/agent/task
Body: { "intent": "find laptop deals", "context": "user has $1000 budget", "agent_id": "..." }
```

## MCP Support (Claude Desktop, Cline, etc.)

FiberAgent also exposes a Model Context Protocol server at:
```
https://fiberagent.shop/api/mcp
```

Claude and other MCP clients can connect directly to search products and compare cashback.

## Links

- **Website:** https://fiberagent.shop
- **API Docs:** https://fiberagent.shop/api/docs
- **OpenAPI Spec:** https://fiberagent.shop/server/openapi.json
- **Agent Card:** https://fiberagent.shop/.well-known/agent-card.json
- **ERC-8004 Profile:** https://www.8004scan.io/agents/monad/135
- **Demo:** https://fiberagent.shop/compare

## Notes

- All cashback is tracked via Wildfire affiliate network
- Crypto rewards paid to agent's Monad wallet
- Works with any ERC-compatible wallet address
- Real-time pricing from 50,000+ merchants
- No signup required — just register with wallet address
