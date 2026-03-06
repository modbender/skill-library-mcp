---
title: Use onAfterRequest for Response Logging
impact: LOW
impactDescription: enables response logging and cleanup without modifying agents
tags: middleware, onAfterRequest, response, cleanup
---

## Use onAfterRequest for Response Logging

Use the `onAfterRequest` middleware hook for logging completed requests, tracking usage metrics, or cleaning up resources. This runs after the agent response has completed.

**Incorrect (logging inside agent, couples concerns):**

```typescript
class ResearchAgent {
  async run(input: RunInput) {
    const start = Date.now()
    // ... agent logic
    console.log(`Agent took ${Date.now() - start}ms`)
    await cleanupTempFiles()
  }
}
```

**Correct (onAfterRequest for logging and cleanup):**

```typescript
import { CopilotRuntime } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  middleware: {
    onAfterRequest: async (options) => {
      const { threadId, runId, inputMessages, outputMessages, properties } = options
      await logUsage({
        threadId,
        runId,
        inputCount: inputMessages.length,
        outputCount: outputMessages.length,
        userId: properties?.userId,
      })
    },
  },
})
```

Reference: [CopilotRuntime](https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime)
