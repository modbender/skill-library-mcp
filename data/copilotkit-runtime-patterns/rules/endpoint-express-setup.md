---
title: Configure Express Endpoint with CORS
impact: CRITICAL
impactDescription: missing CORS or wrong path blocks all frontend connections
tags: endpoint, express, CORS, setup
---

## Configure Express Endpoint with CORS

When using Express, mount the CopilotKit runtime at a specific path and configure CORS to allow your frontend origin. Missing CORS headers cause the browser to block all requests from your React app.

**Incorrect (no CORS, no service adapter):**

```typescript
import express from "express"
import { CopilotRuntime } from "@copilotkit/runtime"

const app = express()
const runtime = new CopilotRuntime()

app.use(runtime.handler())
app.listen(3001)
```

**Correct (CORS configured, proper Express endpoint):**

```typescript
import express from "express"
import cors from "cors"
import {
  CopilotRuntime,
  OpenAIAdapter,
  copilotRuntimeNodeHttpEndpoint,
} from "@copilotkit/runtime"

const app = express()
app.use(cors({ origin: process.env.FRONTEND_URL || "http://localhost:3000" }))

const serviceAdapter = new OpenAIAdapter()
const runtime = new CopilotRuntime()

app.use("/api/copilotkit", (req, res, next) => {
  const handler = copilotRuntimeNodeHttpEndpoint({
    endpoint: "/api/copilotkit",
    runtime,
    serviceAdapter,
  })
  return handler(req, res, next)
})

app.listen(3001)
```

Reference: [Self Hosting](https://docs.copilotkit.ai/guides/self-hosting)
