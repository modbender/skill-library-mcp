---
title: Authenticate Before Agent Execution
impact: CRITICAL
impactDescription: unauthenticated endpoints expose LLM capabilities to anyone
tags: security, auth, middleware, authentication
---

## Authenticate Before Agent Execution

Always authenticate requests before they reach the agent. An unauthenticated CopilotKit endpoint lets anyone invoke your agents and consume your LLM tokens. Use the `onBeforeRequest` middleware or external auth middleware to validate tokens.

**Incorrect (no auth, open to public):**

```typescript
import { CopilotRuntime, OpenAIAdapter, copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime"

const runtime = new CopilotRuntime()
const serviceAdapter = new OpenAIAdapter()

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime, serviceAdapter, endpoint: "/api/copilotkit",
  })
  return handleRequest(req)
}
```

**Correct (JWT auth via properties and middleware):**

```typescript
import { CopilotRuntime, OpenAIAdapter, copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  middleware: {
    onBeforeRequest: async (options) => {
      const token = options.properties?.authToken
      if (!token) throw new Error("Missing authentication token")

      const payload = await verifyJwt(token)
      if (!payload) throw new Error("Invalid token")
    },
  },
})

const serviceAdapter = new OpenAIAdapter()

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime, serviceAdapter, endpoint: "/api/copilotkit",
  })
  return handleRequest(req)
}
```

Pass the auth token from the frontend:

```tsx
<CopilotKit runtimeUrl="/api/copilotkit" properties={{ authToken: session.token }} />
```

Reference: [CopilotRuntime](https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime)
