# OpenCode Zen Free Models Reference

> **⚠️ API Keys Required:**
> - **OpenCode models:** Requires OpenCode Zen API key
> - **OpenRouter models:** Requires OpenRouter API key
>
> Configure both keys in your OpenCode settings for full fallback coverage.

## Complete Model List

### MiniMax M2.1 Free (Primary)
- **ID:** `opencode/minimax-m2.1-free`
- **Provider:** MiniMax (via OpenCode)
- **Best for:** Complex coding tasks, reasoning, multi-step workflows
- **Context:** Large context window
- **Strengths:** Strong coding capability, good reasoning

### Trinity Large Free (Fallback 1 - Different Provider)
- **ID:** `openrouter/arcee-ai/trinity-large-preview:free`
- **Provider:** Arcee AI (via OpenRouter)
- **Best for:** Complex reasoning, coding, multi-step workflows
- **Context:** Large context window
- **Strengths:** High-quality model, **different provider** for rate limit resilience
- **Why Fallback 1:** Being on OpenRouter, this model remains available when OpenCode models are rate-limited

### Kimi K2.5 Free (Fallback 2)
- **ID:** `opencode/kimi-k2.5-free`
- **Provider:** Moonshot AI (Kimi) (via OpenCode)
- **Best for:** General purpose, balanced performance
- **Context:** Large context window
- **Strengths:** Good all-around model, reliable responses

### GLM 4.7 Free
- **ID:** `opencode/glm-4.7-free`
- **Provider:** Zhipu AI (GLM)
- **Best for:** Multilingual tasks, alternative provider fallback
- **Context:** Medium-large context
- **Strengths:** Multilingual support, different provider ecosystem

### GPT 5 Nano
- **ID:** `opencode/gpt-5-nano`
- **Provider:** OpenAI
- **Best for:** Simple tasks, high-frequency operations, quick checks
- **Context:** Smaller context window
- **Strengths:** Fastest responses, lowest cost

## Provider Information

### OpenCode (MiniMax, Moonshot AI/Kimi)
- Primary provider for free models
- Requires OpenCode Zen API key
- Models: MiniMax M2.1, Kimi K2.5

### OpenRouter (Arcee AI/Trinity Large)
- **Different provider** from OpenCode
- Aggregation platform with multiple model providers
- Trinity Large: Arcee AI's large language model
- Focus: High-quality reasoning and coding
- **Requires OpenRouter API key** (separate from OpenCode Zen)
- **Key benefit:** Rate limits on OpenCode do NOT affect OpenRouter models

## Rate Limits by Model

| Model | Typical Rate Limits | Notes |
|-------|--------------------|-------|
| MiniMax M2.1 Free | Medium | Most popular free model |
| Trinity Large Free | Medium | **Different provider** - available when OpenCode is rate-limited |
| Kimi K2.5 Free | Medium-High | Good availability within OpenCode |

## Performance Comparison

| Model | Speed | Capability | Provider Diversification |
|-------|-------|------------|-------------------------|
| MiniMax M2.1 Free | Medium | Highest | Primary (OpenCode) |
| Trinity Large Free | Medium | High | Fallback 1 (OpenRouter) ✅ |
| Kimi K2.5 Free | Medium-High | High | Fallback 2 (OpenCode) |

## Configuration Tips

### For High-Volume Tasks
```
Primary: MiniMax M2.1 Free (OpenCode)
Fallback 1: Trinity Large Free (OpenRouter) ✅ Provider Diversification
Fallback 2: Kimi K2.5 Free (OpenCode)
```

### For Critical Tasks
```
Primary: MiniMax M2.1 Free (OpenCode)
Fallback 1: Trinity Large Free (OpenRouter) ✅ Provider Diversification
Fallback 2: Kimi K2.5 Free (OpenCode)
(Ensure at least one fallback is from different provider)
```

### For Cost-Sensitive Setups
```
Primary: GPT 5 Nano
Fallbacks: Kimi K2.5 Free → Trinity Large Free → MiniMax M2.1 Free
(Use cheapest first, upgrade only if needed)
```

## Error Handling

### Common Errors and Responses

1. **Rate Limit (429)**
   - Action: Try next fallback immediately
   - Prevention: More fallbacks configured

2. **Auth Error (401/403)**
   - **OpenCode models:** Check OpenCode Zen API key
   - **OpenRouter models:** Check OpenRouter API key
   - Action: Try next fallback (may be from different provider)

3. **Timeout (408/504)**
   - Action: Try next fallback
   - Prevention: Check network, reduce request size

4. **Model Not Found (404)**
   - Action: Remove from fallback chain
   - Check: Model ID and availability
   - OpenRouter models may require additional access/credits

5. **Provider-Specific Errors**
   - OpenCode errors: Verify OpenCode Zen API key and subscription
   - OpenRouter errors: Verify OpenRouter API key has credits

### Health Check Commands

```bash
# Check OpenCode models available
opencode models

# Check current configuration
openclaw config.get

# Verify gateway health
openclaw health
```

## Model Aliases

Set friendly names in configuration:

```json
"models": {
  "opencode/minimax-m2.1-free": { "alias": "MiniMax" },
  "openrouter/arcee-ai/trinity-large-preview:free": { "alias": "Trinity Large" },
  "opencode/kimi-k2.5-free": { "alias": "Kimi" }
}
```

## Migration from OpenRouter FreeRide

If migrating from the OpenRouter FreeRide skill:

**Before:**
```json
"model": {
  "primary": "openrouter/qwen/qwen3-coder:free",
  "fallbacks": ["openrouter/free:free"]
}
```

**After (OpenCode Zen with OpenRouter fallback - v1.2.0):**
```json
"model": {
  "primary": "opencode/minimax-m2.1-free",
  "fallbacks": ["openrouter/arcee-ai/trinity-large-preview:free", "opencode/kimi-k2.5-free"]
}
```

**Key differences:**
- Uses OpenCode Zen credentials (plus optional OpenRouter API key)
- **Provider diversification:** First fallback is on OpenRouter (different provider)
- High-quality free options with cross-provider resilience
- Simplified 2-fallback chain

**API Keys Needed:**
- OpenCode Zen API key (primary)
- OpenRouter API key (required for Trinity Large fallback)
