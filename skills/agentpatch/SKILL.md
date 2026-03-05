---
name: agentpatch
description: Discover and use 25+ tools from the AgentPatch marketplace — image generation, web search, email, Google Trends, Maps, and more. Use when you need external tools or APIs at runtime via MCP.
version: 1.0.0
metadata:
  openclaw:
    primaryEnv: AGENTPATCH_API_KEY
    emoji: "wrench"
    homepage: https://agentpatch.ai
    os: [darwin, linux, win32]
---

# AgentPatch

AgentPatch is an open marketplace of tools that AI agents can discover and invoke at runtime via MCP. It provides discoverability, micropayments, and async job support.

## Setup

Before using AgentPatch tools, ensure the MCP server is configured.

### 1. Get an API Key

Have the user sign up at https://agentpatch.ai and get their API key from the [Dashboard](https://agentpatch.ai/dashboard). New accounts receive free credits.

### 2. Configure MCP Server

Add AgentPatch to `~/.openclaw/openclaw.json`:

```json
{
  "mcp": {
    "servers": {
      "agentpatch": {
        "transport": "streamable-http",
        "url": "https://agentpatch.ai/mcp",
        "headers": {
          "Authorization": "Bearer YOUR_API_KEY"
        }
      }
    }
  }
}
```

Replace `YOUR_API_KEY` with the actual key from the dashboard.

### 3. Verify

Restart OpenClaw. You should now have these tools available:

| Tool | Purpose |
|------|---------|
| `search_tools` | Find tools by keyword or browse all |
| `get_tool_details` | Get a tool's input/output schema and pricing |
| `invoke_tool` | Call a tool with input data |
| `get_job_status` | Poll for async job results |

## Finding Tools

Search for what you need:

```
search_tools({ query: "image generation" })
search_tools({ query: "email" })
search_tools({})  // browse all available tools
```

Each result includes `owner_username`, `slug`, `price_credits_per_call`, and `input_schema`.

## Invoking a Tool

Use `owner_username` and `slug` from search results:

```
invoke_tool({
  username: "agentpatch",
  slug: "google-search",
  input: { query: "best restaurants in NYC" }
})
```

Tools return results synchronously when fast, or a `job_id` for polling when slow.

## Async Jobs

If `invoke_tool` returns `status: "pending"`, poll with:

```
get_job_status({ job_id: "job_abc123" })
```

Poll every few seconds until status is `"completed"` or `"failed"`.

## Available Tools

Categories include:

- **Search:** Google Search, Bing Search, Google News, Google Image Search, Reddit Search
- **Maps & Location:** Google Maps
- **Trends & Data:** Google Trends, Stock Quotes, Currency Rates, Weather
- **Image Generation:** Recraft, Flux 2 Pro, Flux Schnell
- **Email:** Send email, check inbox, claim email address
- **Web Scraping:** Scrape web pages, take screenshots, PDF to text
- **Social & Profiles:** LinkedIn profiles, Twitter profiles/posts
- **Other:** YouTube transcripts, Amazon search, eBay products, Craigslist search

New tools are added regularly. Use `search_tools` to discover what's current.

## Credits

- 1 credit = $0.0001 USD (10,000 credits = $1)
- Price per tool call varies (shown in search results)
- Failed calls (5xx, timeout) are refunded automatically
- Top up at https://agentpatch.ai/dashboard
