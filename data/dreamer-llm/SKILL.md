---
name: dreamer-llm
description: Send requests to the dr.eamer.dev LLM API for chat completions, vision analysis, image generation, text-to-speech, and video generation across 12 model providers. Use when you need to call an external LLM endpoint or want to compare responses across providers.
---

# Dreamer LLM

Access 12 LLM providers through a single unified API at `https://api.dr.eamer.dev`.

## Authentication

Set your API key in an environment variable or pass it per-request:

```bash
export DREAMER_API_KEY=your_key_here
```

Get a key: email luke@lukesteuber.com or visit https://dr.eamer.dev

## Endpoints

### Chat Completion
```
POST https://api.dr.eamer.dev/v1/llm/chat
Headers: X-API-Key: $DREAMER_API_KEY
Body:
{
  "model": "claude-sonnet-4-5-20250929",
  "messages": [{"role": "user", "content": "Hello"}],
  "provider": "anthropic"
}
```

### Available Providers
`anthropic`, `openai`, `xai`, `mistral`, `cohere`, `gemini`, `perplexity`, `groq`, `huggingface`, `ollama`

### List Models
```
GET https://api.dr.eamer.dev/v1/llm/models
```

### Vision (image analysis)
```
POST https://api.dr.eamer.dev/v1/llm/vision
Body: { "model": "claude-sonnet-4-5-20250929", "image_url": "...", "prompt": "Describe this image" }
```

### Image Generation
```
POST https://api.dr.eamer.dev/v1/llm/image
Body: { "prompt": "A sunset over the ocean", "provider": "openai" }
```

### Text-to-Speech
```
POST https://api.dr.eamer.dev/v1/llm/tts
Body: { "text": "Hello world", "voice": "alloy" }
```

## When to Use
- Comparing responses across multiple LLM providers
- Accessing providers you don't have direct API keys for
- Building applications that need multi-provider LLM access

## Don't Use When
- You already have direct API keys for the provider you need
- You need streaming responses (use direct provider APIs instead)
