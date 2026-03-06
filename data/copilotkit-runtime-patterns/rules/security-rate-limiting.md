---
title: Rate Limit by User or API Key
impact: HIGH
impactDescription: unbounded access lets single users exhaust LLM budget
tags: security, rate-limiting, abuse, budget
---

## Rate Limit by User or API Key

Add rate limiting to your CopilotKit runtime endpoint to prevent individual users from exhausting your LLM budget. Rate limit by authenticated user ID or API key, not just IP address (which doesn't work behind proxies/VPNs).

**Incorrect (no rate limiting):**

```typescript
import { CopilotRuntime, OpenAIAdapter, copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime"

const runtime = new CopilotRuntime()
// Anyone can make unlimited requests
```

**Correct (rate limiting via middleware):**

```typescript
import { RateLimiterMemory } from "rate-limiter-flexible"
import { CopilotRuntime, OpenAIAdapter } from "@copilotkit/runtime"

const limiter = new RateLimiterMemory({
  points: 50,
  duration: 60,
})

const runtime = new CopilotRuntime({
  middleware: {
    onBeforeRequest: async (options) => {
      const userId = options.properties?.userId
      if (!userId) throw new Error("Unauthorized")

      try {
        await limiter.consume(userId)
      } catch {
        throw new Error("Rate limit exceeded")
      }
    },
  },
})
```

Reference: [CopilotRuntime](https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime)
