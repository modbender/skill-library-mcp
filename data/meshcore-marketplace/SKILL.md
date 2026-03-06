---
name: meshcore-marketplace
description: Discover and call paid AI agents from the MeshCore marketplace. Find specialized agents for weather, data analysis, summarization, and more — with automatic billing.
version: 1.0.0
user-invocable: true
metadata:
  openclaw:
    requires:
      env:
        - MESHCORE_API_TOKEN
      bins:
        - curl
        - jq
    primaryEnv: MESHCORE_API_TOKEN
    emoji: "globe_with_meridians"
    homepage: https://meshcore.ai
---

# MeshCore Marketplace Skill

You have access to the MeshCore AI agent marketplace — a platform where developers publish AI agents and others can discover and pay to use them.

## API Base URL

All API calls go to: `https://api.meshcore.ai`

## Available Actions

### 1. Search for agents

Use semantic search to find agents by what they do:

```bash
curl -s "https://api.meshcore.ai/public/agents/search?query=SEARCH_TERM&limit=5" | jq '.[] | {name, description, pricingType, pricePerCall, id}'
```

Replace `SEARCH_TERM` with what the user is looking for (e.g., "weather", "summarize text", "currency exchange").

### 2. List all agents

Browse all available agents:

```bash
curl -s "https://api.meshcore.ai/public/agents" | jq '.[] | {name, description, pricingType, pricePerCall, id}'
```

### 3. Get agent details

Get full information about a specific agent:

```bash
curl -s "https://api.meshcore.ai/public/AGENT_ID" | jq
```

### 4. Call an agent

Call an agent through the MeshCore gateway:

**For FREE agents (no auth needed):**
```bash
curl -s -X POST "https://api.meshcore.ai/gateway/call/AGENT_ID" \
  -H "Content-Type: application/json" \
  -d 'JSON_PAYLOAD'
```

**For PAID agents (auth required):**
```bash
curl -s -X POST "https://api.meshcore.ai/gateway/call/AGENT_ID" \
  -H "Authorization: Bearer $MESHCORE_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d 'JSON_PAYLOAD'
```

### 5. Check wallet balance

```bash
curl -s "https://api.meshcore.ai/wallet/balance" \
  -H "Authorization: Bearer $MESHCORE_API_TOKEN" | jq
```

## Important Rules

1. **Always show pricing before calling a paid agent.** Tell the user: "This agent costs $X per call. Shall I proceed?"
2. **Wait for user confirmation before calling any paid agent.** Never call a paid agent without explicit approval.
3. **Free agents can be called without asking.** If `pricingType` is `FREE`, just call it.
4. **Show results clearly.** Format the agent's response in a readable way.
5. **If search returns no results**, suggest the user try different terms or browse all agents.

## Example Workflows

**User: "Find me a weather agent"**
1. Search: `curl -s "https://api.meshcore.ai/public/agents/search?query=weather&limit=3"`
2. Show results with name, description, and pricing
3. Ask: "Would you like me to call the Weather Agent?"
4. If yes and it's free: call it directly
5. Show the weather data

**User: "Summarize this text: [long text]"**
1. Search: `curl -s "https://api.meshcore.ai/public/agents/search?query=text+summarizer&limit=3"`
2. Show results: "I found a Text Summarizer agent. It costs $0.01 per call. Want me to use it?"
3. Wait for confirmation
4. Call with auth: `curl -s -X POST ... -H "Authorization: Bearer $MESHCORE_API_TOKEN"`
5. Show the summary
