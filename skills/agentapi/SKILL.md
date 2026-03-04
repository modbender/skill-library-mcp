---
name: agentapi
description: Browse and search the AgentAPI directory - a curated database of APIs designed for AI agents. Find MCP-compatible APIs for search, AI, communication, databases, payments, and more. Includes free directory access and optional x402 pay-per-use APIs.
author: gizmolab
version: 1.0.7
tags: [api, mcp, agents, directory, search, integrations, x402]
homepage: https://agentapihub.com
source: https://github.com/gizmolab/agentapi
---

# AgentAPI

A curated directory of APIs designed for AI agents. Machine-readable. MCP-compatible. Agent-accessible.

**Website:** https://agentapihub.com  
**Docs:** https://api.agentapihub.com/api/docs

## Free Features

The directory and search functionality is **completely free**:

```bash
# Browse all APIs (FREE)
curl https://agentapihub.com/api/v1/apis

# Search by capability (FREE)
curl "https://agentapihub.com/api/v1/apis?q=send+email&mcp=true"

# Filter by category (FREE)
curl "https://agentapihub.com/api/v1/apis?category=ai"
```

## x402 Pay-Per-Use APIs

Some APIs are available through **x402** — a pay-per-use protocol using USDC on Base chain.

### Available x402 APIs

| API | Endpoint | Approx. Price |
|-----|----------|---------------|
| Gemini Chat | `/api/gemini/chat/completions` | ~$0.001/req |
| Gemini Embeddings | `/api/gemini/embeddings` | ~$0.0005/req |

### How x402 Works

1. Call the API endpoint
2. Receive `402 Payment Required` with price details
3. Send USDC payment on Base chain
4. Retry request with payment proof
5. Receive API response

### ⚠️ Important Safety Notice

**x402 payments require explicit setup and should not be automated without safeguards:**

- **Wallet required:** You must configure a wallet with USDC on Base
- **User approval recommended:** Implement confirmation flows before any payment
- **Verify recipient:** The payment recipient is `0xcCb92A101347406ed140b18C4Ed27276844CD9D7` (gizmolab.eth)
- **Set spending limits:** Configure maximum per-request and daily limits
- **This skill does not auto-execute payments** — it provides documentation only

For implementation details, see: https://api.agentapihub.com/api/docs

## Directory Categories

| Category | APIs | Example |
|----------|------|---------|
| Search | Brave, Serper, Exa, Tavily, Perplexity | Web search with AI summaries |
| AI & ML | OpenAI, Claude, Gemini, Groq, Replicate | LLM inference, image gen |
| Communication | Resend, Twilio, Slack, Discord, Telegram | Email, SMS, messaging |
| Database | Supabase, Pinecone, Qdrant, Neon, Upstash | SQL, vectors, KV store |
| Payments | Stripe, Lemon Squeezy, PayPal | Payment processing |
| Scraping | Firecrawl, Browserbase, Apify | Web scraping, automation |
| Developer | GitHub, Vercel, Linear, Sentry | Code, deploy, issues |
| Productivity | Notion, Google Calendar, Todoist | Tasks, scheduling |

### MCP-Compatible APIs

All 50+ APIs in the directory are MCP-compatible. Filter with `?mcp=true`.

## API Response Format

```json
{
  "id": "resend",
  "name": "Resend",
  "description": "Modern email API for developers",
  "category": "communication",
  "provider": "Resend",
  "docs": "https://resend.com/docs",
  "auth": "api_key",
  "pricing": "freemium",
  "pricingDetails": "3,000 free/mo, then $20/mo",
  "rateLimit": "10 req/sec",
  "mcpCompatible": true,
  "x402Enabled": false,
  "tags": ["email", "transactional", "notifications"]
}
```

## Top APIs by Category

### Search
- **Brave Search** - Privacy-focused, 2k free/mo
- **Exa** - Neural/semantic search for AI
- **Tavily** - Built specifically for AI agents

### AI & ML
- **OpenAI** - GPT-4, DALL-E, Whisper
- **Anthropic Claude** - Best for reasoning/coding
- **Groq** - Fastest inference (500+ tok/sec)

### Communication
- **Resend** - Simple email API, 3k free/mo
- **Twilio** - SMS/voice, industry standard
- **Slack/Discord/Telegram** - Team messaging

### Database
- **Supabase** - Postgres + auth + storage
- **Pinecone/Qdrant** - Vector DBs for RAG
- **Upstash** - Serverless Redis

## Usage Examples

```markdown
# Find an API for sending emails
Search AgentAPI for "email" → Returns Resend, SendGrid, Twilio

# Find vector databases for RAG
Search AgentAPI for "vector embeddings" → Returns Pinecone, Qdrant, Weaviate

# Find fast LLM inference
Search AgentAPI for category "ai" + filter by latency → Returns Groq, Gemini Flash
```

## Contributing

Submit new APIs at https://agentapihub.com (Submit API link in footer).

## Built By

GizmoLab ([@gizmolab_](https://twitter.com/gizmolab_)) — [gizmolab.io](https://gizmolab.io)
