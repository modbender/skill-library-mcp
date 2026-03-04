# Clawd Throttle

Route every LLM request to the cheapest model that can handle it.

Clawd Throttle is an OpenClaw skill (MCP server) and HTTP reverse proxy that classifies prompt complexity in under 1ms and routes to the cheapest capable model across 8 LLM providers and 30+ models.

## Supported Providers

| Provider | Models | Input $/MTok | Output $/MTok |
|----------|--------|-------------|---------------|
| **Anthropic** | Opus 4.6, Opus 4.5, Sonnet 4.5, Haiku 4.5, Haiku 3.5 | $0.25–$5.00 | $1.25–$25.00 |
| **OpenAI** | GPT-5.2, GPT-5.1, GPT-5-mini, GPT-5-nano, GPT-4o, GPT-4o-mini, o3 | $0.10–$5.00 | $0.40–$30.00 |
| **Google** | Gemini 2.5 Pro, 2.5 Flash, 2.0 Flash-Lite | $0.01–$1.25 | $0.02–$10.00 |
| **DeepSeek** | DeepSeek-Chat, DeepSeek-Reasoner | $0.14–$0.55 | $0.28–$2.19 |
| **xAI** | Grok-4, Grok-3, Grok-3-mini, Grok-4.1-fast | $0.30–$3.00 | $0.50–$15.00 |
| **Moonshot** | Kimi K2.5, K2-thinking | $0.35–$0.60 | $1.50–$2.50 |
| **Mistral** | Mistral Large, Small, Codestral | $0.10–$2.00 | $0.30–$6.00 |
| **Ollama** | Local models (any) | $0.00 | $0.00 |

All API keys are **optional**. Configure one or more providers — Clawd Throttle automatically routes to the best available model.

## Quick Start

```bash
# 1. Clone and install
npm install

# 2. Set at least one API key
export ANTHROPIC_API_KEY=sk-...    # or any other provider

# 3. Run setup (optional — prompts for all keys and mode)
npm run setup          # Windows
npm run setup:unix     # macOS/Linux

# 4. Start
npm start              # MCP stdio server
npm start -- --http    # MCP + HTTP proxy
npm start -- --http-only  # HTTP proxy only
```

```json
{
  "clawd-throttle": {
    "command": "npx",
    "args": ["tsx", "src/index.ts"],
    "cwd": "/path/to/clawd-throttle"
  }
}
```

## HTTP Proxy Mode

Clawd Throttle runs as an HTTP reverse proxy that accepts OpenAI and Anthropic API formats. Any client that can point at a custom base URL works without code changes.

### Starting the Proxy

```bash
CLAWD_THROTTLE_HTTP=true npm start           # Enable HTTP proxy
npm start -- --http                           # CLI flag (HTTP + MCP)
npm start -- --http-only                      # HTTP only
CLAWD_THROTTLE_HTTP_PORT=9090 npm start -- --http  # Custom port
```

### Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/v1/messages` | Anthropic Messages API format |
| POST | `/v1/chat/completions` | OpenAI Chat Completions format |
| GET | `/health` | Health check with uptime and mode |
| GET | `/stats` | Routing stats (optional `?days=N`, default 30) |

### Examples

**OpenAI format:**
```bash
curl http://localhost:8484/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {"role": "system", "content": "You are helpful."},
      {"role": "user", "content": "Explain monads"}
    ],
    "max_tokens": 1000
  }'
```

**Streaming:**
```bash
curl --no-buffer http://localhost:8484/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Write a haiku"}],
    "max_tokens": 100,
    "stream": true
  }'
```

**Force a specific model:**
```bash
curl http://localhost:8484/v1/messages \
  -H "Content-Type: application/json" \
  -H "X-Throttle-Force-Model: deepseek" \
  -d '{
    "messages": [{"role": "user", "content": "hello"}],
    "max_tokens": 100
  }'
```

### Response Headers

| Header | Description |
|--------|-------------|
| `X-Throttle-Model` | The model that handled the request |
| `X-Throttle-Tier` | Classified tier: simple, standard, or complex |
| `X-Throttle-Score` | Raw classifier score (0.00–1.00) |
| `X-Throttle-Request-Id` | Unique request ID for log correlation |

### Client Configuration

Point any OpenAI-compatible client at the proxy:

```python
# Python (openai SDK)
import openai
client = openai.OpenAI(base_url="http://localhost:8484/v1", api_key="unused")
response = client.chat.completions.create(
    model="auto",
    messages=[{"role": "user", "content": "hello"}],
)
```

```typescript
// TypeScript (Anthropic SDK)
import Anthropic from '@anthropic-ai/sdk';
const client = new Anthropic({
  baseURL: 'http://localhost:8484',
  apiKey: 'unused',
});
```

## Routing Modes

Routing uses **preference lists** — ordered arrays of models per (mode, tier). The router picks the first model whose provider has a configured API key.

| Mode | Simple | Standard | Complex |
|------|--------|----------|---------|
| **eco** | Ollama, Flash-Lite, GPT-5-nano | Flash, GPT-4o-mini, DeepSeek | DeepSeek-R1, Kimi, Sonnet |
| **standard** | Flash, GPT-4o-mini, DeepSeek | Kimi, Sonnet, GPT-5.1 | Opus 4.5, GPT-5.2, Grok-4 |
| **performance** | Haiku, GPT-5-mini, Kimi | Sonnet, GPT-5.1, Grok-3 | Opus 4.6, GPT-5.2, o3 |

## How It Works

1. Prompt arrives via `route_request` MCP tool or HTTP proxy endpoint
2. Classifier scores it on 8 dimensions in <1ms
3. Composite score maps to a tier: simple (<=0.30), standard, or complex (>=0.65)
4. Preference list lookup: first model whose provider is configured wins
5. Fallback: if no preferred model available, use cheapest available model
6. Request proxied to the selected provider's API
7. Decision logged to JSONL for cost tracking

## MCP Tools

| Tool | Description |
|------|-------------|
| `route_request` | Send prompt to cheapest capable model, get response + routing metadata |
| `classify_prompt` | Analyze complexity without API call (diagnostic) |
| `get_routing_stats` | Cost savings, model distribution, tier breakdown |
| `set_mode` | Change routing mode at runtime |
| `get_config` | View config with all 8 providers (keys redacted) |
| `get_recent_routing_log` | Inspect recent routing decisions |

## Overrides

- **Heartbeats/summaries**: "ping", "summarize this" -> always cheapest
- **Force model**: `/opus`, `/deepseek`, `/grok`, `/kimi`, `/mistral`, `/local`, `/gpt-5`, `/o3`, etc.
- **HTTP header**: `X-Throttle-Force-Model: deepseek`
- **Sub-agents**: Pass `parentRequestId` to step down one tier automatically

## Configuration

Config file: `~/.config/clawd-throttle/config.json`

### Environment Variables

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Anthropic API key |
| `GOOGLE_AI_API_KEY` | Google AI API key |
| `OPENAI_API_KEY` | OpenAI API key |
| `DEEPSEEK_API_KEY` | DeepSeek API key |
| `XAI_API_KEY` | xAI/Grok API key |
| `MOONSHOT_API_KEY` | Moonshot/Kimi API key |
| `MISTRAL_API_KEY` | Mistral API key |
| `OLLAMA_BASE_URL` | Ollama base URL (default: http://localhost:11434/v1) |
| `CLAWD_THROTTLE_MODE` | eco, standard, or performance |
| `CLAWD_THROTTLE_LOG_LEVEL` | debug, info, warn, error |
| `CLAWD_THROTTLE_HTTP` | Set to `true` to enable HTTP proxy |
| `CLAWD_THROTTLE_HTTP_PORT` | HTTP proxy port (default: 8484) |

## Requirements

- Node.js 18+
- At least one LLM provider API key (or Ollama running locally)

## Privacy

- Prompt content is never stored — only SHA-256 hashes in logs
- All data stays local in `~/.config/clawd-throttle/`
- API keys stored in your local config file or environment variables

## Development

```bash
npm run dev          # Watch mode
npm test             # Run tests
npm run stats        # View routing stats
```
