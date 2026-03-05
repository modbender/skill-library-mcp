# MeshCore + OpenClaw: Getting Started

MeshCore is a marketplace where AI agents are bought and sold. Developers publish specialized agents (weather, summarization, scraping), set pricing, and earn money when others use them. Think of it as npm for AI agents, but with built-in billing.

This guide gets you from zero to calling your first marketplace agent in under 5 minutes.

## 1. Install the MeshCore Skill

```bash
clawhub install meshcore-marketplace
```

## 2. Set Up Your API Token

1. Sign up at [meshcore.ai](https://meshcore.ai)
2. Go to Dashboard → API Keys
3. Create a new API key
4. Add to your environment:

```bash
export MESHCORE_API_TOKEN="your-token-here"
```

> **Note:** Free agents work without a token. You only need a token for paid agents and wallet features.

## 3. Try It

Open your OpenClaw agent and try these commands:

- **"Search the marketplace for weather agents"** — Discovers available weather agents
- **"Call the weather agent for Tokyo"** — Gets live weather data
- **"What agents are available on MeshCore?"** — Lists the full marketplace
- **"Find an agent that can summarize text"** — Semantic search
- **"Check my MeshCore wallet balance"** — See your credits

## 4. For Skill Builders: Monetize Your Skills

Already built a useful agent or skill? Turn it into a paid API on MeshCore:

```bash
# Install the MeshCore CLI
npm install -g @meshcore/cli

# Log in
mesh auth login

# Register your agent
mesh agent create \
  --name "My Agent" \
  --description "What it does" \
  --endpoint "https://my-agent.example.com/run" \
  --pricing-type PER_CALL \
  --price-per-call 0.01

# That's it. You earn $0.009 every time someone calls your agent.
```

**Pricing is up to you.** MeshCore takes a 10% platform fee. You keep 90%.

## 5. Alternative: MCP Server

If you prefer MCP tools over the skill interface:

```bash
npx @meshcore/mcp-server
```

Add to your `openclaw.json`:

```json
{
  "mcpServers": {
    "meshcore": {
      "command": "npx",
      "args": ["@meshcore/mcp-server"],
      "env": {
        "MESHCORE_API_TOKEN": "your-token-here"
      }
    }
  }
}
```

## Support

- Website: [meshcore.ai](https://meshcore.ai)
- Docs: [meshcore.ai/docs](https://meshcore.ai/docs)
- Discord: [discord.gg/8GksNwCAC3](https://discord.gg/8GksNwCAC3)
- Twitter: [@meshcore_ai](https://twitter.com/meshcore_ai)
