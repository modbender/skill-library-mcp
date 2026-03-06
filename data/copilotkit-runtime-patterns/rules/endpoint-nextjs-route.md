---
title: Set Up Next.js API Route Handler
impact: CRITICAL
impactDescription: incorrect route handler config breaks streaming in Next.js
tags: endpoint, nextjs, api-route, streaming
---

## Set Up Next.js API Route Handler

For Next.js App Router, create an API route at `app/api/copilotkit/route.ts`. Use `copilotRuntimeNextJSAppRouterEndpoint` to create the handler. Ensure the route allows sufficient duration for streaming responses.

**Incorrect (wrong class, no service adapter):**

```typescript
// app/api/copilotkit/route.ts
import { CopilotRuntime } from "@copilotkit/runtime"

const runtime = new CopilotRuntime()

export async function POST(req: Request) {
  return runtime.handler(req)
}
```

**Correct (proper Next.js endpoint with adapter):**

```typescript
// app/api/copilotkit/route.ts
import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNextJSAppRouterEndpoint,
} from "@copilotkit/runtime"
import { NextRequest } from "next/server"

const serviceAdapter = new OpenAIAdapter()
const runtime = new CopilotRuntime()

export const POST = async (req: NextRequest) => {
  const { handleRequest } = copilotRuntimeNextJSAppRouterEndpoint({
    runtime,
    serviceAdapter,
    endpoint: "/api/copilotkit",
  })

  return handleRequest(req)
}
```

For serverless platforms with short timeouts, increase the function timeout:

```json
// vercel.json
{
  "functions": {
    "api/copilotkit/**/*": {
      "maxDuration": 60
    }
  }
}
```

Reference: [Self Hosting](https://docs.copilotkit.ai/guides/self-hosting)
