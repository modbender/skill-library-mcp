---
title: Register Agents via Remote Endpoints
impact: MEDIUM
impactDescription: missing agent registration prevents proper routing and discovery
tags: runner, agents, registration, remoteEndpoints
---

## Register Agents via Remote Endpoints

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
