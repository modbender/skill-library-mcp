---
name: agentapi
description: Browse and search the AgentAPI directory - a curated database of APIs designed for AI agents. Find MCP-compatible APIs for search, AI, communication, databases, payments, and more. Includes x402 pay-per-use billing with USDC on Base.
author: gizmolab
version: 1.0.3
tags: [api, mcp, agents, directory, search, integrations, x402, crypto, payments]
---

# AgentAPI

A curated directory of APIs designed for AI agents. Machine-readable. MCP-compatible. Agent-accessible.

**Website:** https://agentapihub.com  
**Billing API:** https://api.agentapihub.com  
**Docs:** https://api.agentapihub.com/api/docs

## x402 Pay-Per-Use Billing

AgentAPI supports **x402** — a payment protocol that lets AI agents pay for API calls with USDC on Base. No API keys required.

### How It Works

1. Agent calls API endpoint (e.g., `/api/gemini/chat/completions`)
2. Server returns `402 Payment Required` with price + wallet address
3. Agent sends USDC payment on Base chain
4. Agent retries with payment proof in header
5. Server verifies payment, proxies request, returns response

### Example Flow

```bash
# 1. Initial request returns 402
curl https://api.agentapihub.com/api/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -d '{"model":"gemini-2.0-flash","messages":[{"role":"user","content":"Hello"}]}'

# Response: 402 Payment Required
# {
#   "price": "0.001",
#   "currency": "USDC",
#   "chain": "base",
#   "recipient": "0xcCb92A101347406ed140b18C4Ed27276844CD9D7",
#   "paymentId": "pay_abc123"
# }

# 2. Agent pays on Base, retries with proof
curl https://api.agentapihub.com/api/gemini/chat/completions \
  -H "Content-Type: application/json" \
  -H "X-Payment-Proof: 0x..." \
  -d '{"model":"gemini-2.0-flash","messages":[{"role":"user","content":"Hello"}]}'
```

### Available x402 APIs

| API | Endpoint | Price |
|-----|----------|-------|
| Gemini Chat | `/api/gemini/chat/completions` | ~$0.001/req |
| Gemini Embeddings | `/api/gemini/embeddings` | ~$0.0005/req |

### Why x402?

- **No API keys** — Agents self-provision access
- **Pay-per-use** — No subscriptions, no minimums
- **Crypto-native** — USDC on Base (fast, cheap txns)
- **Agent-friendly** — Programmatic payments without human bottleneck

## Quick Search

### By Category

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

## API Access

### JSON Endpoint

```bash
# Fetch all APIs
curl https://agentapihub.com/api/v1/apis

# Search by capability
curl "https://agentapihub.com/api/v1/apis?q=send+email&mcp=true"

# Filter by category
curl "https://agentapihub.com/api/v1/apis?category=ai"
```

### Response Format

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
  "examplePrompt": "Send an email notification using Resend",
  "latency": "fast",
  "reliability": 99.9,
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
