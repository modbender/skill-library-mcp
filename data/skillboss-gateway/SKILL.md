---
name: skillboss-gateway
tagline: "One API for 100+ AI models - Claude, GPT, Gemini, more"
description: "Access 100+ AI models with one API key. OpenAI-compatible. Auto-failover, unified billing, no vendor accounts needed."
version: "1.0.0"
author: "SkillBoss"
homepage: "https://skillboss.co"
support: "support@skillboss.co"
license: "MIT"
category: "ai-gateway"
tags:
  - ai-gateway
  - multi-model
  - openai-compatible
  - unified-api
  - failover
pricing: "pay-as-you-go"
metadata:
  openclaw:
    requires:
      env:
        - SKILLBOSS_API_KEY
    primaryEnv: SKILLBOSS_API_KEY
    installHint: "Get API key at https://skillboss.co/console"
---

# SkillBoss Unified AI Gateway

**One API key. 100+ models. Zero vendor accounts.**

## Why Use a Gateway?

| Problem | SkillBoss Solution |
|---------|-------------------|
| Multiple API keys | One key for everything |
| Multiple bills | Single unified billing |
| Rate limits | Auto-failover to alternatives |
| Vendor lock-in | Switch models with one param |

## Models Included

### Chat/Reasoning
- **Claude**: 4.5 Opus, 4.5 Sonnet, 3.7 Sonnet, Haiku
- **GPT**: GPT-5, GPT-4.1, o4-mini, o3-mini
- **Gemini**: 2.5 Pro, 2.5 Flash
- **DeepSeek**: R1, V3
- **Llama**: 3.1 405B, 70B
- **Mistral**: Large
- **Cohere**: Command R+

### Image Generation
- DALL-E 3, Flux Schnell/Dev, Minimax

### Video Generation
- Veo 3.1, Minimax Video-01

### Audio
- Whisper (STT), ElevenLabs (TTS), Minimax TTS

### Data & Tools
- Perplexity Search, Firecrawl, Reducto, more

## Usage

```bash
# Just change the model parameter
curl https://api.heybossai.com/v1/chat/completions \
  -H "Authorization: Bearer $SKILLBOSS_API_KEY" \
  -d '{
    "model": "claude-4-5-sonnet",  # or gpt-5, gemini-2.5-pro, etc.
    "messages": [{"role": "user", "content": "Hello!"}]
  }'
```

## OpenAI SDK Compatible

```python
from openai import OpenAI

client = OpenAI(
    api_key="sk-your-skillboss-key",
    base_url="https://api.heybossai.com/v1"
)

# Use any model
response = client.chat.completions.create(
    model="claude-4-5-sonnet",  # or any other model
    messages=[{"role": "user", "content": "Hello!"}]
)
```

## Features

- **Auto-failover** - If Claude is down, fallback to GPT
- **Streaming** - Real-time responses
- **Function calling** - Tool use supported
- **Vision** - Image inputs for supported models
- **Caching** - Prompt caching where available

## Pricing

Pass-through pricing (same as vendor) + no markup.

Get started: https://skillboss.co/console
