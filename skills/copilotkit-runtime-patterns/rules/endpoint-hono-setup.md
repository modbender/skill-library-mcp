---
title: Configure Hono Endpoint for Edge
impact: HIGH
impactDescription: Hono enables edge runtime deployment for lower latency
tags: endpoint, hono, edge, setup
---

## Configure Hono Endpoint for Edge

Use Hono for edge runtime deployments (Cloudflare Workers, Vercel Edge). Hono's lightweight design and Web Standard APIs make it ideal for edge CopilotKit runtimes.

**Incorrect (no service adapter, no CORS):**

```typescript
import { Hono } from "hono"
import { CopilotRuntime } from "@copilotkit/runtime"

const app = new Hono()
const runtime = new CopilotRuntime()

app.all("/api/copilotkit", (c) => {
  return runtime.handler()(c.req.raw)
})
```

**Correct (Hono with CORS and proper adapter):**

```typescript
import { Hono } from "hono"
import { cors } from "hono/cors"
import {
  CopilotRuntime,
  OpenAIAdapter,
} from "@copilotkit/runtime"

const app = new Hono()
app.use("/api/copilotkit/*", cors({ origin: process.env.FRONTEND_URL }))

const serviceAdapter = new OpenAIAdapter()
const runtime = new CopilotRuntime()

app.all("/api/copilotkit", async (c) => {
  const response = await runtime.process({
    serviceAdapter,
    request: c.req.raw,
  })
  return response
})

export default app
```

Reference: [Self Hosting](https://docs.copilotkit.ai/guides/self-hosting)
