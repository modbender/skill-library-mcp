---
title: Handle Middleware Errors Gracefully
impact: MEDIUM
impactDescription: unhandled middleware errors crash the runtime for all users
tags: middleware, error, handling, resilience
---

## Handle Middleware Errors Gracefully

Wrap middleware logic in try/catch to prevent individual request failures from crashing the entire runtime. Log errors and re-throw with appropriate context instead of letting raw exceptions propagate.

**Incorrect (unhandled error crashes runtime):**

```typescript
import { CopilotRuntime } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  middleware: {
    onBeforeRequest: async (options) => {
      const user = await fetchUser(options.properties?.userId)
      // If fetchUser throws, the entire runtime crashes
    },
  },
})
```

**Correct (graceful error handling):**

```typescript
import { CopilotRuntime } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  middleware: {
    onBeforeRequest: async (options) => {
      try {
        const user = await fetchUser(options.properties?.userId)
        if (!user) {
          throw new Error("User not found")
        }
      } catch (error) {
        console.error("Middleware error:", error)
        throw new Error("Authentication failed")
      }
    },
  },
})
```

Reference: [CopilotRuntime](https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime)
