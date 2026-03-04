---
title: Configure Multi-Agent Routing
impact: HIGH
impactDescription: ambiguous routing sends requests to wrong agents
tags: runner, multi-agent, routing, agentId
---

## Configure Multi-Agent Routing

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
