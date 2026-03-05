# Specification: Add arcee-ai/trinity-large-preview:free Fallback

## Overview
Update the freeride-opencode skill to add `arcee-ai/trinity-large-preview:free` via OpenRouter as an additional fallback option.

## Changes Summary
- **New Model**: arcee-ai/trinity-large-preview:free (via OpenRouter)
- **Model ID**: `openrouter/arcee-ai/trinity-large-preview:free`
- **Position**: Added as second fallback option (after Kimi K2.5 Free, before GLM 4.7 Free)
- **Version**: Bump from 1.0.0 to 1.1.0

## Model Details
- **Provider**: OpenRouter
- **Model**: arcee-ai/trinity-large-preview
- **Tier**: Free
- **Best for**: Complex reasoning, coding tasks, multi-step workflows
- **Strengths**: Additional high-quality option from different provider (OpenRouter)

## Configuration Changes

### Updated Fallback Chain
```json
"fallbacks": [
  "opencode/kimi-k2.5-free",                                    // 2nd priority (high capability)
  "openrouter/arcee-ai/trinity-large-preview:free",             // NEW: 3rd priority
  "opencode/glm-4.7-free",                                       // 4th priority (multilingual)
  "opencode/gpt-5-nano"                                          // 5th priority (fastest/cheapest)
]
```

### Updated Model Aliases
```json
"models": {
  "opencode/minimax-m2.1-free": { "alias": "MiniMax M2.1" },
  "opencode/kimi-k2.5-free": { "alias": "Kimi K2.5" },
  "openrouter/arcee-ai/trinity-large-preview:free": { "alias": "Trinity Large" },
  "opencode/glm-4.7-free": {},
  "opencode/gpt-5-nano": {}
}
```

## Files to Update
1. **SKILL.md**: Update version, documentation, examples, and model table
2. **references/models.md**: Add new model entry with details
3. **references/templates.md**: Update fallback chains in all templates

## Priority Rationale
1. MiniMax M2.1 Free - Best overall free model
2. Kimi K2.5 Free - Strong alternative
3. **Trinity Large (NEW)** - New high-quality OpenRouter option
4. GLM 4.7 Free - Multilingual/alternative provider
5. GPT 5 Nano - Fastest, cheapest fallback

## Backward Compatibility
- Existing configurations without the new model will continue to work
- New installations get enhanced fallback coverage
- No breaking changes to API or configuration structure