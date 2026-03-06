---
title: Use onBeforeRequest for Auth and Logging
impact: MEDIUM
impactDescription: centralizes cross-cutting concerns before agent execution
tags: middleware, onBeforeRequest, auth, logging
---

## Use onBeforeRequest for Auth and Logging

Use the `onBeforeRequest` middleware hook to handle authentication, logging, and context injection before the agent processes a request. This centralizes cross-cutting concerns and keeps agent code focused on business logic.

**Incorrect (auth logic inside each agent):**

```typescript
class ResearchAgent {
  async run(input: RunInput) {
    const token = input.headers?.authorization
    if (!verifyToken(token)) throw new Error("Unauthorized")
  }
}
```

**Correct (auth in onBeforeRequest middleware):**

```typescript
import { CopilotRuntime } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  middleware: {
    onBeforeRequest: async (options) => {
      const { threadId, runId, inputMessages, properties } = options
      const token = properties?.authToken
      if (!token || !await verifyToken(token)) {
        throw new Error("Unauthorized")
      }
    },
  },
})
```

Pass auth tokens from the frontend via the `properties` prop on `CopilotKit`:

```tsx
<CopilotKit runtimeUrl="/api/copilotkit" properties={{ authToken: session.token }}>
```

Reference: [CopilotRuntime](https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime)
