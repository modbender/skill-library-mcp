---
title: Always Pass agentId for Multi-Agent
impact: HIGH
impactDescription: without agentId, requests route to wrong agent or fail
tags: agent, hooks, multi-agent, routing
---

## Always Pass agentId for Multi-Agent

When your application has multiple agents, always specify `agentId` in hooks like `useAgent` and `useFrontendTool`, or use the `agent` prop on the `CopilotKit` provider. Without it, CopilotKit cannot route requests to the correct agent, causing unexpected behavior or errors.

**Incorrect (no agentId, ambiguous routing):**

```tsx
import { useAgent, useFrontendTool } from "@copilotkit/react-core/v2";

function ResearchPanel() {
  const { agent } = useAgent({})

  useFrontendTool({
    name: "save_result",
    handler: async ({ result }) => saveToDb(result),
  })

  return <button onClick={() => agent.runAgent()}>Go</button>
}
```

**Correct (explicit agentId for routing):**

```tsx
import { useAgent, useFrontendTool } from "@copilotkit/react-core/v2";

function ResearchPanel() {
  const { agent } = useAgent({ agentId: "researcher" })

  useFrontendTool({
    name: "save_result",
    agentId: "researcher",
    handler: async ({ result }) => saveToDb(result),
  })

  return <button onClick={() => agent.runAgent()}>Go</button>
}
```

Reference: [useAgent Hook](https://docs.copilotkit.ai/reference/v2/hooks/useAgent)
