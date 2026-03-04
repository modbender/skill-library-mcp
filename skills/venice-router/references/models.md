# Venice.ai Model Reference

## Text Models — Full Pricing (per 1M tokens, USD)

### Tier: CHEAP ($0.05–$0.15 input)

| Model | ID | Input | Output | Context | Privacy |
|-------|-----|-------|--------|---------|---------|
| Venice Small | `qwen3-4b` | $0.05 | $0.15 | 32K | Private |
| GPT OSS 120B | `openai-gpt-oss-120b` | $0.07 | $0.30 | 128K | Private |
| GLM 4.7 Flash | `zai-org-glm-4.7-flash` | $0.13 | $0.50 | 128K | Private |
| Llama 3.2 3B | `llama-3.2-3b` | $0.15 | $0.60 | 128K | Private |

### Tier: BUDGET ($0.14–$0.25 input)

| Model | ID | Input | Output | Context | Privacy |
|-------|-----|-------|--------|---------|---------|
| GLM 4.7 Flash Heretic | `olafangensan-glm-4.7-flash-heretic` | $0.14 | $0.80 | 128K | Private |
| Qwen 3 235B | `qwen3-235b-a22b-instruct-2507` | $0.15 | $0.75 | 128K | Private |
| Venice Uncensored | `venice-uncensored` | $0.20 | $0.90 | 32K | Private |
| Qwen3 VL 235B | `qwen3-vl-235b-a22b` | $0.25 | $1.50 | 256K | Private |

### Tier: MID ($0.25–$0.70 input)

| Model | ID | Input | Output | Context | Privacy | Thinking |
|-------|-----|-------|--------|---------|---------|----------|
| Grok Code Fast | `grok-code-fast-1` | $0.25 | $1.87 | 256K | Anonymized | |
| DeepSeek V3.2 | `deepseek-v3.2` | $0.40 | $1.00 | 160K | Private | |
| MiniMax M2.1 | `minimax-m21` | $0.40 | $1.60 | 198K | Private | |
| MiniMax M2.5 | `minimax-m25` | $0.40 | $1.60 | 198K | Private | |
| Qwen 3 Next 80B | `qwen3-next-80b` | $0.35 | $1.90 | 256K | Private | |
| Qwen3 235B Thinking 🧠 | `qwen3-235b-a22b-thinking-2507` | $0.45 | $3.50 | 128K | Private | ✅ |
| Venice Medium | `mistral-31-24b` | $0.50 | $2.00 | 128K | Private | |
| Llama 3.3 70B | `llama-3.3-70b` | $0.70 | $2.80 | 128K | Private | |

### Tier: HIGH ($0.50–$1.10 input)

| Model | ID | Input | Output | Context | Privacy | Thinking |
|-------|-----|-------|--------|---------|---------|----------|
| Grok 4.1 Fast | `grok-41-fast` | $0.50 | $1.25 | 256K | Anonymized | |
| GLM 4.7 | `zai-org-glm-4.7` | $0.55 | $2.65 | 198K | Private | |
| Gemini 3 Flash | `gemini-3-flash-preview` | $0.70 | $3.75 | 256K | Anonymized | |
| Kimi K2 Thinking 🧠 | `kimi-k2-thinking` | $0.75 | $3.20 | 256K | Private | ✅ |
| Kimi K2.5 🧠 | `kimi-k2-5` | $0.75 | $3.75 | 256K | Private | ✅ |
| Qwen 3 Coder 480B | `qwen3-coder-480b-a35b-instruct` | $0.75 | $3.00 | 256K | Private | |
| GLM 5 | `zai-org-glm-5` | $1.00 | $3.20 | 198K | Private | |
| Hermes 3 405B 🔧 | `hermes-3-llama-3.1-405b` | $1.10 | $3.00 | 128K | Private | |

### Tier: PREMIUM ($2.19–$6.00 input)

| Model | ID | Input | Output | Context | Privacy |
|-------|-----|-------|--------|---------|---------|
| GPT-5.2 | `openai-gpt-52` | $2.19 | $17.50 | 256K | Anonymized |
| GPT-5.2 Codex 💻 | `openai-gpt-52-codex` | $2.19 | $17.50 | 256K | Anonymized |
| Gemini 3 Pro | `gemini-3-pro-preview` | $2.50 | $15.00 | 198K | Anonymized |
| Gemini 3.1 Pro | `gemini-3-1-pro-preview` | $2.50 | $15.00 | 1M | Anonymized |
| Claude Sonnet 4.6 | `claude-sonnet-4-6` | $3.75 | $18.75 | 1M | Anonymized |
| Claude Sonnet 4.5 | `claude-sonnet-45` | $3.75 | $18.75 | 198K | Anonymized |
| Claude Opus 4.5 | `claude-opus-45` | $6.00 | $30.00 | 198K | Anonymized |
| Claude Opus 4.6 | `claude-opus-4-6` | $6.00 | $30.00 | 1M | Anonymized |

### Beta / Additional Models

| Model | ID | Input | Output | Context | Privacy | Notes |
|-------|-----|-------|--------|---------|---------|-------|
| Qwen 3 235B Thinking | `qwen3-235b-a22b-thinking-2507` | $0.45 | $3.50 | 128K | Private | In MID tier |
| GPT-5.2 Codex | `openai-gpt-52-codex` | $2.19 | $17.50 | 256K | Anonymized | Code specialist |
| Gemini 3.1 Pro | `gemini-3-1-pro-preview` | $2.50 | $15.00 | 1M | Anonymized | 1M context |
| Kimi K2.5 | `kimi-k2-5` | $0.75 | $3.75 | 256K | Private | In HIGH tier |
| Hermes 3 405B | `hermes-3-llama-3.1-405b` | $1.10 | $3.00 | 128K | Private | Tool-use specialist |

## Cost Comparison

A typical 1000-token prompt + 2000-token response costs:

| Tier | Approx Cost | Example |
|------|-------------|---------|
| Cheap | $0.0004 | "What is 2+2?" |
| Budget | $0.0017 | "Summarize this article" |
| Mid | $0.0024 | "Write a Python function for X" |
| High | $0.0072 | "Debug this async code and explain the race condition" |
| Premium | $0.037 | "Design a distributed event-driven architecture for..." |

**Savings**: Using the router vs always-premium saves ~99% on simple queries.

## API Endpoint

```
POST https://api.venice.ai/api/v1/chat/completions
Authorization: Bearer <VENICE_API_KEY>
Content-Type: application/json
```

OpenAI-compatible. Works with any OpenAI SDK by changing the base URL.

## Privacy

- **Private**: Venice hosts the model directly, no data leaves Venice infrastructure
- **Anonymized**: Request is proxied to external provider (OpenAI, Anthropic, Google, xAI) with user identity stripped

## Additional Features

| Feature | Parameter | Cost |
|---------|-----------|------|
| Web Search | `enable_web_search: true` | $10/1K calls |
| Web Scraping | `enable_web_scraping: true` | $10/1K calls |
| Prompt Caching | `prompt_cache_key` | Varies by model |
