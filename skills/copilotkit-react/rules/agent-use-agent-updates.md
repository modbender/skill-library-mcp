---
title: Specify useAgent Update Subscriptions
impact: HIGH
impactDescription: prevents unnecessary re-renders from agent state changes
tags: agent, hooks, performance, useAgent
---

## Specify useAgent Update Subscriptions

The `useAgent` hook (v2) accepts an `updates` array that controls which agent changes trigger a React re-render. By default it subscribes to all updates (`OnMessagesChanged`, `OnStateChanged`, `OnRunStatusChanged`). Only subscribe to the updates your component actually needs to avoid excessive re-renders.

**Incorrect (subscribes to all updates, causes re-render storms):**

```tsx
import { useAgent } from "@copilotkit/react-core/v2";

function AgentStatus() {
  const { agent } = useAgent({ agentId: "researcher" })

  return <div>Running: {agent.isRunning ? "yes" : "no"}</div>
}
```

**Correct (subscribes only to run status changes):**

```tsx
import { useAgent } from "@copilotkit/react-core/v2";

function AgentStatus() {
  const { agent } = useAgent({
    agentId: "researcher",
    updates: ["OnRunStatusChanged"],
  })

  return <div>Running: {agent.isRunning ? "yes" : "no"}</div>
}
```

Available update types:
- `"OnMessagesChanged"` - re-render when messages update
- `"OnStateChanged"` - re-render when agent state changes
- `"OnRunStatusChanged"` - re-render when run status changes

Reference: [useAgent Hook (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useAgent)
