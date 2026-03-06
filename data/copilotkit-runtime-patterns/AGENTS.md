# CopilotKit Runtime Patterns

**Version 2.0.0**  
CopilotKit  
February 2026

> **Note:**  
> This document is mainly for agents and LLMs to follow when maintaining,  
> generating, or refactoring CopilotKit codebases. Humans  
> may also find it useful, but guidance here is optimized for automation  
> and consistency by AI-assisted workflows.

---

## Abstract

Server-side runtime configuration patterns for CopilotKit. Contains 15 rules covering Express/Hono/Next.js endpoint setup with CopilotRuntime and service adapters, agent registration via remoteEndpoints, middleware hooks (onBeforeRequest/onAfterRequest), security configuration, and performance optimization.

---

## Table of Contents

1. [Endpoint Setup](#1-endpoint-setup) — **CRITICAL**
   - 1.1 [Configure Express Endpoint with CORS](#11-configure-express-endpoint-with-cors)
   - 1.2 [Configure Hono Endpoint for Edge](#12-configure-hono-endpoint-for-edge)
   - 1.3 [Set Up Next.js API Route Handler](#13-set-up-nextjs-api-route-handler)
2. [Agent Configuration](#2-agent-configuration) — **HIGH**
   - 2.1 [Configure Multi-Agent Routing](#21-configure-multi-agent-routing)
   - 2.2 [Register Agents via Remote Endpoints](#22-register-agents-via-remote-endpoints)
   - 2.3 [Use Persistent Storage for Production Threads](#23-use-persistent-storage-for-production-threads)
3. [Middleware](#3-middleware) — **MEDIUM**
   - 3.1 [Handle Middleware Errors Gracefully](#31-handle-middleware-errors-gracefully)
   - 3.2 [Use onAfterRequest for Response Logging](#32-use-onafterrequest-for-response-logging)
   - 3.3 [Use onBeforeRequest for Auth and Logging](#33-use-onbeforerequest-for-auth-and-logging)
4. [Security](#4-security) — **HIGH**
   - 4.1 [Authenticate Before Agent Execution](#41-authenticate-before-agent-execution)
   - 4.2 [Configure CORS for Specific Origins](#42-configure-cors-for-specific-origins)
   - 4.3 [Rate Limit by User or API Key](#43-rate-limit-by-user-or-api-key)
5. [Performance](#5-performance) — **MEDIUM**
   - 5.1 [Prevent Proxy Buffering of Streams](#51-prevent-proxy-buffering-of-streams)

---

## 1. Endpoint Setup

**Impact: CRITICAL**

Correct endpoint configuration is required for CopilotKit to function. Misconfigured endpoints cause connection failures or broken streaming.

### 1.1 Configure Express Endpoint with CORS

**Impact: CRITICAL (missing CORS or wrong path blocks all frontend connections)**

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

### 1.2 Configure Hono Endpoint for Edge

**Impact: HIGH (Hono enables edge runtime deployment for lower latency)**

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

### 1.3 Set Up Next.js API Route Handler

**Impact: CRITICAL (incorrect route handler config breaks streaming in Next.js)**

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

---

## 2. Agent Configuration

**Impact: HIGH**

Agent runners manage agent lifecycle and state persistence. Choosing the wrong runner causes data loss or memory leaks.

### 2.1 Configure Multi-Agent Routing

**Impact: HIGH (ambiguous routing sends requests to wrong agents)**

When registering multiple agents, ensure each has a unique name that matches the `agent` prop or `agentId` used in the frontend. The runtime routes requests based on this name. Duplicate names cause unpredictable routing.

**Incorrect (single endpoint, no way to distinguish agents):**

```typescript
import { CopilotRuntime } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  remoteEndpoints: [
    { url: "http://localhost:8000" },
  ],
})

// Frontend has no way to select a specific agent
```

**Correct (agents accessible via frontend agent prop):**

```typescript
import { CopilotRuntime } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  remoteEndpoints: [
    { url: process.env.LANGGRAPH_URL || "http://localhost:8000" },
  ],
})

// Frontend selects agent via the agent prop:
// <CopilotKit runtimeUrl="/api/copilotkit" agent="researcher">
// or via useAgent:
// useAgent({ agentId: "researcher" })
```

The runtime discovers available agents from the remote endpoint and routes based on the `agent`/`agentId` specified by the frontend.

Reference: [Multi-Agent Flows](https://docs.copilotkit.ai/coagents/multi-agent-flows)

### 2.2 Register Agents via Remote Endpoints

**Impact: MEDIUM (missing agent registration prevents proper routing and discovery)**

Register your agents with the runtime using `remoteEndpoints`. This enables the runtime to discover available agents, route requests to the correct agent, and provide agent metadata to the frontend.

**Incorrect (no agent endpoints configured):**

```typescript
import { CopilotRuntime, OpenAIAdapter } from "@copilotkit/runtime"

const runtime = new CopilotRuntime()
```

**Correct (remote endpoints configured for LangGraph agents):**

```typescript
import { CopilotRuntime, OpenAIAdapter } from "@copilotkit/runtime"

const runtime = new CopilotRuntime({
  remoteEndpoints: [
    {
      url: process.env.LANGGRAPH_URL || "http://localhost:8000",
    },
  ],
})
```

The runtime handles agent discovery and routing automatically when remote endpoints are configured. The frontend specifies which agent to use via the `agent` prop on `CopilotKit` or `agentId` in `useAgent`.

Reference: [Copilot Runtime](https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime)

### 2.3 Use Persistent Storage for Production Threads

**Impact: HIGH (in-memory state loses all conversation history on restart)**

In production, configure thread persistence so conversation history survives server restarts. CopilotKit supports thread management for persisting conversations. Without persistence, every deployment wipes all conversation history.

**Incorrect (no thread persistence, state lost on deploy):**

```typescript
import { CopilotRuntime, OpenAIAdapter, copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime"

const serviceAdapter = new OpenAIAdapter()
const runtime = new CopilotRuntime()
```

**Correct (configure thread persistence for production):**

```typescript
import { CopilotRuntime, OpenAIAdapter, copilotRuntimeNextJSAppRouterEndpoint } from "@copilotkit/runtime"

const serviceAdapter = new OpenAIAdapter()
const runtime = new CopilotRuntime({
  remoteEndpoints: [
    {
      url: process.env.LANGGRAPH_URL || "http://localhost:8000",
    },
  ],
})
```

For CoAgents (LangGraph), conversation persistence is handled by the LangGraph checkpointer, which stores state in its own database. Configure your LangGraph deployment with a persistent checkpointer for production.

Reference: [Self Hosting](https://docs.copilotkit.ai/guides/self-hosting)

---

## 3. Middleware

**Impact: MEDIUM**

Middleware hooks for request/response processing. Used for auth, logging, context injection, and response modification.

### 3.1 Handle Middleware Errors Gracefully

**Impact: MEDIUM (unhandled middleware errors crash the runtime for all users)**

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

### 3.2 Use onAfterRequest for Response Logging

**Impact: LOW (enables response logging and cleanup without modifying agents)**

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

### 3.3 Use onBeforeRequest for Auth and Logging

**Impact: MEDIUM (centralizes cross-cutting concerns before agent execution)**

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

---

## 4. Security

**Impact: HIGH**

Security patterns for production CopilotKit deployments. Unprotected endpoints expose your LLM and agent capabilities to abuse.

### 4.1 Authenticate Before Agent Execution

**Impact: CRITICAL (unauthenticated endpoints expose LLM capabilities to anyone)**

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

### 4.2 Configure CORS for Specific Origins

**Impact: HIGH (wildcard CORS exposes your LLM endpoint to any website)**

Never use wildcard (`*`) CORS in production. Specify the exact frontend origin(s) that should be allowed to access your CopilotKit runtime. Wildcard CORS lets any website send requests to your endpoint, potentially abusing your LLM quota.

**Incorrect (wildcard CORS, open to abuse):**

```typescript
app.use(cors({ origin: "*" }))
```

**Correct (specific origin in production):**

```typescript
const allowedOrigins = process.env.NODE_ENV === "production"
  ? [process.env.FRONTEND_URL!]
  : ["http://localhost:3000", "http://localhost:5173"]

app.use(cors({ origin: allowedOrigins }))
```

Reference: [Security](https://docs.copilotkit.ai/guides/security)

### 4.3 Rate Limit by User or API Key

**Impact: HIGH (unbounded access lets single users exhaust LLM budget)**

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

---

## 5. Performance

**Impact: MEDIUM**

Optimization patterns for runtime performance, streaming, and resource management.

### 5.1 Prevent Proxy Buffering of Streams

**Impact: MEDIUM (buffered streams cause long delays before first token appears)**

CopilotKit uses Server-Sent Events (SSE) for streaming. Reverse proxies (Nginx, Cloudflare) may buffer the response, causing long delays before the first token reaches the client. Set headers to disable buffering.

**Incorrect (no streaming headers, proxy buffers response):**

```typescript
import { CopilotRuntime, OpenAIAdapter, copilotRuntimeNodeHttpEndpoint } from "@copilotkit/runtime"

// No anti-buffering headers configured
app.use("/api/copilotkit", handler)
```

**Correct (disable proxy buffering for streaming):**

```typescript
app.use("/api/copilotkit", (req, res, next) => {
  res.setHeader("X-Accel-Buffering", "no")
  res.setHeader("Cache-Control", "no-cache, no-transform")
  res.setHeader("Content-Type", "text/event-stream")
  next()
}, handler)
```

For Nginx, also add to your server config:
```
proxy_buffering off;
```

Reference: [Self Hosting](https://docs.copilotkit.ai/guides/self-hosting)

---

## References

- https://docs.copilotkit.ai
- https://github.com/CopilotKit/CopilotKit
- https://docs.copilotkit.ai/reference/v1/classes/CopilotRuntime
- https://docs.copilotkit.ai/guides/self-hosting
- https://docs.copilotkit.ai/guides/security
- https://docs.copilotkit.ai/coagents/multi-agent-flows
