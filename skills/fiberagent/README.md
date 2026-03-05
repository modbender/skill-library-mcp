# FiberAgent OpenClaw Skill

A shopping intelligence skill for OpenClaw agents. Find products with cryptocurrency cashback across 50,000+ merchants on the Monad blockchain.

## Installation

### Option 1: Local (Instant)
```bash
mkdir -p ~/.openclaw/workspace/skills
cp -r fiberagent ~/.openclaw/workspace/skills/
openclaw restart  # or restart OpenClaw gateway
```

### Option 2: npm (Soon)
```bash
npm install @fiberagent/openclaw-skill
```

### Option 3: ClawHub (TBD)
Visit https://clawhub.com to discover and install directly from OpenClaw UI.

## Quick Start

Once installed, your agent automatically gains access to shopping with cashback:

```
User: "Find me a Dyson Airwrap with cashback"

Agent: "I'll search for that using FiberAgent..."
[Calls search_products tool]

Agent: "Found it! Dyson Airwrap i.d. at Macy's:
- Price: $499.99
- Cashback: 15% ($75.00)
- Effective cost: $424.99
- Your crypto wallet gets +$75 MON

Here's the tracked link: [affiliate URL]"
```

## Features

✅ **50,000+ merchants** — Nike, Dyson, Sephora, Amazon, Best Buy, Lenovo, Ray-Ban, and more
✅ **Real-time cashback rates** — Powered by Wildfire affiliate network
✅ **Crypto rewards** — Cashback paid in tokens on Monad blockchain
✅ **On-chain reputation** — ERC-8004 agent score increases with each purchase
✅ **MCP compatible** — Works with Claude, Cline, and other MCP-enabled agents
✅ **Agent-to-agent** — Agents can earn money from referring to other agents

## Tools

### `search_products(keywords, agent_id, [size])`
Search for products with cashback rates.

```javascript
const results = await agent.tools.search_products(
  "dyson airwrap",
  "my_agent",
  10
);
// Returns: { results: [{ title, price, cashback, shop, affiliateUrl }, ...] }
```

### `register_agent(agent_id, wallet_address, [crypto])`
Register your agent to start earning crypto.

```javascript
const registration = await agent.tools.register_agent(
  "my_shopping_bot",
  "0x123456...",
  "MON"  // or USDC, USDT, ETH
);
// Returns: { agent_id, token, wallet_address, total_earnings }
```

### `get_agent_stats(agent_id)`
View your earnings and activity.

```javascript
const stats = await agent.tools.get_agent_stats("my_agent");
// Returns: { total_searches, total_earnings, conversions, api_calls_made }
```

## Configuration

Add your agent ID and wallet to OpenClaw config:

```yaml
# ~/.openclaw/openclaw.json
{
  "skills": {
    "fiberagent": {
      "enabled": true,
      "agentId": "my_agent",
      "wallet": "0x123456..."
    }
  }
}
```

## How It Works

1. **Agent gets question:** "Find me a laptop with cashback"
2. **Skill detects intent** — shopping + cashback
3. **Calls FiberAgent API** — searches 50,000+ merchants
4. **Gets results** — products with real-time cashback rates
5. **Returns to user** — best deal + tracked affiliate link
6. **Earns crypto** — when user buys via link, agent wallet receives cashback tokens on Monad

## Earnings

When a user buys through your agent's affiliate link:
- **15% cashback** if using Macy's, DySON, etc.
- **7% cashback** if using Ray-Ban, Sephora
- **Up to 40%** at certain merchants (see live rates)

Your agent's wallet on Monad automatically receives the crypto rewards. You can withdraw, stake, or trade them anytime.

## Links

- **Website:** https://fiberagent.shop
- **API Docs:** https://fiberagent.shop/api/docs
- **Agent Card:** https://fiberagent.shop/.well-known/agent-card.json
- **MCP Server:** https://fiberagent.shop/api/mcp
- **On-chain Profile:** https://www.8004scan.io/agents/monad/135
- **Live Demo:** https://fiberagent.shop/compare

## Support

- **GitHub Issues:** https://github.com/openclawlaurent/fiberagent-openclaw-skill/issues
- **Discord:** Join the OpenClaw Discord
- **Email:** laurent@fiberagent.shop

## License

MIT © 2026 FiberAgent
