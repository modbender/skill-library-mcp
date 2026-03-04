---
name: prefy
description: Connect to Prefy AI platform — Conductor API (19 models, OpenAI-compatible), server management, web search, image generation, phone calls (AutoCall). Use when agent needs multi-model AI routing, dedicated server provisioning, web intelligence, or restaurant/hotel phone calls. Base URL https://prefy.com.
---

# Prefy — AI Platform Skill

## Quick Start

```bash
# Chat completion (OpenAI-compatible, streaming)
curl https://prefy.com/api/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $PREFY_API_KEY" \
  -d '{"model":"conductor:fast","messages":[{"role":"user","content":"Hello"}],"stream":true}'
```

## Authentication

All endpoints require `Authorization: Bearer <key>` header.
- **Conductor API**: Use Prefy API key (starts with `pc_`)
- **Server/Agent APIs**: Use Supabase JWT token

## Conductor AI — Smart Model Router

POST `https://prefy.com/api/v1/chat/completions`

OpenAI-compatible. Drop-in replacement. Supports streaming.

### Models

| Model | Best For | Speed |
|-------|----------|-------|
| `conductor` | Auto-route to best model | Auto |
| `conductor:fast` | Speed priority | ⚡ |
| `conductor:quality` | Quality priority | Medium |
| `conductor:creative` | Creative tasks | Medium |
| `conductor:private` | Privacy priority | Varies |
| `gemini-flash` | Quick tasks | ⚡ |
| `gemini-pro` | General purpose | Fast |
| `gpt-4o` | Best all-round | Fast |
| `gpt-4o-mini` | Budget tasks | ⚡ |
| `claude-sonnet` | Analysis, writing | Fast |
| `deepseek-v3` | Code, math | Fast |
| `deepseek-r1` | Chain-of-thought | Medium |
| `llama-70b` | Complex reasoning | Medium |
| `groq-llama` | Speed-critical | ⚡ |
| `qwen-7b` | Multilingual | Fast |

### Strategies

Append strategy to `conductor` model name:
- `:fast` — Gemini Flash / Groq (cheapest, fastest)
- `:quality` — GPT-4o / Claude (best quality)
- `:creative` — High temperature, diverse outputs
- `:private` — Routes through privacy-first providers

## Web Search

POST `https://prefy.com/api/v1/search`

```json
{"query": "latest AI news", "max_results": 5}
```

Returns Tavily search results with snippets.

## Image Generation

POST `https://prefy.com/api/v1/images/generate`

```json
{"prompt": "a sunset over mountains", "model": "flux-schnell"}
```

Returns base64 image. Uses Together AI FLUX Schnell (free tier).

## Server Management

Provision and manage dedicated VPS servers.

- `POST /api/v1/servers/checkout` — Create Stripe checkout for server plan
- `POST /api/v1/servers/command` — Send command to server agent
- `GET /api/v1/servers/hetzner` — List user's servers

### Server Plans
| Plan | Price | Specs |
|------|-------|-------|
| starter | $9.99/mo | 2 vCPU, 2GB RAM, 40GB SSD |
| plus | $14.99/mo | 4 vCPU, 8GB RAM, 80GB SSD |
| pro | $29.99/mo | 8 vCPU, 16GB RAM, 160GB SSD |

### Agent Commands
Send via POST `/api/v1/servers/command`:
```json
{"serverId": "...", "command": "stats"}
```
Available: `stats`, `ollama list/pull/run/rm`, `cron list/add/remove`, `bot connect/stop/status`, `shell <cmd>`

## Agent API

POST `https://prefy.com/api/v1/agent`

Intelligent agent with memory, web search, intent detection.

```json
{"message": "Find flights from Dubai to London next week", "userId": "..."}
```

Auto-detects intent: chat, search, flights, hotels, call.

## AutoCall (Phone Calls)

POST `https://prefy.com/api/v1/autocall`

AI phone calls to restaurants/hotels (Vapi + ElevenLabs).

```json
{
  "phone": "+971...",
  "venue_name": "Restaurant Name",
  "task": "Book table for 2, Friday 8pm",
  "language": "en"
}
```

## Events & Activities

GET `https://prefy.com/api/v1/events?city=Dubai`

Returns upcoming events and activities for a city.

## Rate Limits

| Tier | Requests/day |
|------|-------------|
| Free | 10 |
| Starter ($4.99/mo) | 100 |
| Pro ($14.99/mo) | 500 |
| BYOK | Unlimited |

## Docs

Full documentation: https://prefy.com/docs
