---
title: Use Provider/Model String Format for Model Selection
impact: HIGH
impactDescription: hardcoded model names break when switching providers
tags: architecture, model, provider-agnostic
---

## Use Provider/Model String Format for Model Selection

Use the `"provider/model"` string format when specifying models for `BuiltInAgent`. This allows swapping between OpenAI, Anthropic, or other providers without changing the underlying agent architecture. Use environment variables for flexibility across environments.

**Incorrect (ambiguous model name without provider):**

```typescript
import { BuiltInAgent } from "@copilotkit/runtime/v2"

const agent = new BuiltInAgent({
  name: "writer",
  model: "gpt-4o",
})
```

**Correct (explicit provider/model format):**

```typescript
import { BuiltInAgent } from "@copilotkit/runtime/v2"

const agent = new BuiltInAgent({
  name: "writer",
  model: process.env.LLM_MODEL || "openai/gpt-4o",
})
```

**Correct (environment-based model selection):**

```typescript
import { BuiltInAgent } from "@copilotkit/runtime/v2"

const MODEL_MAP: Record<string, string> = {
  fast: "openai/gpt-4o-mini",
  powerful: "openai/gpt-4o",
  anthropic: "anthropic/claude-sonnet-4-20250514",
}

const modelKey = process.env.MODEL_TIER || "powerful"

const agent = new BuiltInAgent({
  name: "writer",
  model: MODEL_MAP[modelKey],
})
```

Reference: [Self Hosting](https://docs.copilotkit.ai/guides/self-hosting)
