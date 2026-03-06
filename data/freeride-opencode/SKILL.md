---
name: freeride-opencode
description: Configure and optimize OpenCode Zen free models with smart fallbacks for subtasks, heartbeat, and cron jobs. Use when setting up cost-effective AI model routing with automatic failover between free models.
version: 1.2.0
---

# Freeride OpenCode

Configure OpenCode Zen free models with intelligent fallbacks to optimize costs while maintaining reliability.

> **⚠️ Important:** To use this skill, you need **two API keys**:
> 1. **OpenCode Zen API key** - For OpenCode free models (MiniMax M2.1, Kimi K2.5, GLM 4.7, GPT 5 Nano)
> 2. **OpenRouter API key** - For OpenRouter free models (Trinity Large and other OpenRouter providers)
>
> Configure both keys in your OpenCode/Zen settings before applying these configurations.

## Quick Start

Apply optimal free model configuration with provider diversification:

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "openrouter/arcee-ai/trinity-large-preview:free",
          "opencode/kimi-k2.5-free"
        ]
      },
      "heartbeat": {
        "model": "opencode/glm-4.7-free"
      },
      "subagents": {
        "model": "opencode/kimi-k2.5-free"
      }
    }
  }
}
```

## 🔑 API Keys Required

This skill uses models from **two different providers**, so you need both API keys configured:

### 1. OpenCode Zen API Key
**Required for:**
- `opencode/minimax-m2.1-free`
- `opencode/kimi-k2.5-free`
- `opencode/glm-4.7-free`
- `opencode/gpt-5-nano`

**Where to get:** Sign up at [OpenCode Zen](https://opencode.ai) and generate an API key.

### 2. OpenRouter API Key
**Required for:**
- `openrouter/arcee-ai/trinity-large-preview:free`
- Any other OpenRouter free models you add

**Where to get:** Sign up at [OpenRouter.ai](https://openrouter.ai) and generate an API key.

### Configuration

Add both keys to your OpenCode configuration:

```json
{
  "providers": {
    "opencode": {
      "api_key": "YOUR_OPENCODE_ZEN_API_KEY"
    },
    "openrouter": {
      "api_key": "YOUR_OPENROUTER_API_KEY"
    }
  }
}
```

### Fallback Behavior by Provider

- If **OpenCode models** fail → tries next OpenCode fallback or OpenRouter model
- If **OpenRouter models** fail → tries next OpenRouter or OpenCode fallback
- Configure both providers for maximum reliability

## Model Selection Guide

See [models.md](models.md) for detailed model comparisons, capabilities, and provider information.

| Task Type | Recommended Model | Rationale |
|-----------|------------------|-----------|
| **Primary/General** | MiniMax M2.1 Free | Best free model capability |
| **Fallback 1** | Trinity Large Free | Different provider (OpenRouter) for rate limit resilience |
| **Fallback 2** | Kimi K2.5 Free | General purpose, balance |
| **Heartbeat** | GLM 4.7 Free | Multilingual, cost-effective for frequent checks |
| **Subtasks/Subagents** | Kimi K2.5 Free | Balanced capability for secondary tasks |

### Free Models Available

| Model | ID | Best For |
|-------|-----|----------|
| **MiniMax M2.1 Free** | `opencode/minimax-m2.1-free` | Complex reasoning, coding (Primary) |
| **Trinity Large Free** | `openrouter/arcee-ai/trinity-large-preview:free` | High-quality OpenRouter option (Fallback 1) |
| **Kimi K2.5 Free** | `opencode/kimi-k2.5-free` | General purpose, balance (Fallback 2) |

## Fallback Strategy

### Provider Diversification (v1.2.0)

This version implements **provider diversification** to maximize resilience against rate limits and service disruptions:

```json
"fallbacks": [
  "openrouter/arcee-ai/trinity-large-preview:free",  // Different provider (OpenRouter)
  "opencode/kimi-k2.5-free"                           // Same provider as primary (OpenCode)
]
```

**Why Provider Diversification Matters:**
- **Rate limit isolation:** If OpenCode experiences rate limits, OpenRouter models remain available (and vice versa)
- **First fallback from different provider:** Trinity Large on OpenRouter ensures continuity even if all OpenCode models are rate-limited
- **Maximum resilience:** By spreading across providers, you avoid a single point of failure

**Fallback triggers:**
- Rate limits exceeded
- Auth failures
- Timeouts
- Provider unavailability

### Fallback Behavior by Provider

- If **OpenCode models** fail → tries OpenRouter fallback first (Trinity Large), then back to OpenCode (Kimi)
- If **OpenRouter model** fails → tries OpenCode fallback (Kimi)
- This cross-provider approach ensures at least one model is usually available

## Per-Task Configuration

### Heartbeat (Every 30 min)

```json
"heartbeat": {
  "every": "30m",
  "model": "opencode/gpt-5-nano"
}
```

Use the cheapest model for frequent, lightweight checks.

### Subtasks/Subagents

```json
"subagents": {
  "model": "opencode/kimi-k2.5-free"
}
```

Good balance for secondary tasks that need reasonable capability.

### Complete Example

```json
{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": [
          "openrouter/arcee-ai/trinity-large-preview:free",
          "opencode/kimi-k2.5-free"
        ]
      },
      "models": {
        "opencode/minimax-m2.1-free": { "alias": "MiniMax M2.1" },
        "opencode/kimi-k2.5-free": { "alias": "Kimi K2.5" },
        "openrouter/arcee-ai/trinity-large-preview:free": { "alias": "Trinity Large" }
      },
      "heartbeat": {
        "every": "30m",
        "model": "opencode/glm-4.7-free"
      },
      "subagents": {
        "model": "opencode/kimi-k2.5-free"
      }
    }
  }
}
```

## Applying Configuration

Use OpenClaw CLI:

```bash
openclaw config.patch --raw '{
  "agents": {
    "defaults": {
      "model": {
        "primary": "opencode/minimax-m2.1-free",
        "fallbacks": ["openrouter/arcee-ai/trinity-large-preview:free", "opencode/kimi-k2.5-free"]
      },
      "heartbeat": { "model": "opencode/glm-4.7-free" },
      "subagents": { "model": "opencode/kimi-k2.5-free" }
    }
  }
}'
```

## Best Practices

1. **Provider diversification** - Always have your first fallback from a different provider (e.g., OpenRouter) to avoid rate limits affecting all models
2. **Keep fallbacks minimal** - 2-3 well-chosen fallbacks are better than many
3. **Match model to task** - Don't use MiniMax for simple checks
4. **Test fallback order** - Put more capable models first, with provider diversification
5. **Monitor usage** - Track which models get used most

## Troubleshooting

**Authentication errors (401/403)?**
- Check that you have **both** API keys configured:
  - OpenCode Zen API key for OpenCode models
  - OpenRouter API key for Trinity Large and OpenRouter models
- Verify keys are valid and have not expired

**Rate limits still occurring?**
- Add provider diversification (ensure first fallback is from different provider)
- Consider reducing heartbeat frequency

**Responses too slow?**
- Move GPT 5 Nano higher in fallback chain
- Use simpler model for subtasks

**Model not available?**
- Check model ID format: `opencode/model-id-free` or `openrouter/provider/model:free`
- Verify model is still free (check [models.md](models.md))
- Ensure you have the correct API key for the provider

**OpenRouter models not working?**
- Verify OpenRouter API key is configured
- Check OpenRouter account has credits/access
- Some models may have additional access requirements

## References

### [models.md](models.md)
Complete reference of all free models with capabilities, providers, performance comparisons, and error handling.

### [templates.md](templates.md)
Ready-to-use configuration templates for different use cases (minimal, complete, cost-optimized, performance-optimized).

### [examples/usage.md](examples/usage.md)
Practical examples showing how to use this skill in real scenarios.
