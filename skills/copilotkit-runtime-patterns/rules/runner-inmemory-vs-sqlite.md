---
title: Use Persistent Storage for Production Threads
impact: HIGH
impactDescription: in-memory state loses all conversation history on restart
tags: runner, persistence, threads, production
---

## Use Persistent Storage for Production Threads

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
