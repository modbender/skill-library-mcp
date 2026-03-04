---
title: Configure the agent Prop for Agent Routing
impact: CRITICAL
impactDescription: without agent prop, requests may route to wrong agent or use default behavior
tags: provider, agent, routing, configuration
---

## Configure the agent Prop for Agent Routing

When using CoAgents (LangGraph, CrewAI), set the `agent` prop on `CopilotKit` to specify which agent handles requests. Without it, requests use default routing which may not match the agent you intend.

**Incorrect (no agent specified, ambiguous routing):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <MyApp />
    </CopilotKit>
  )
}
```

**Correct (agent explicitly configured):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit
      runtimeUrl="/api/copilotkit"
      agent="sample_agent"
    >
      <MyApp />
    </CopilotKit>
  )
}
```

When using Copilot Cloud with `publicApiKey`, the same `agent` prop applies:

```tsx
<CopilotKit publicApiKey="ck_pub_..." agent="sample_agent">
  <MyApp />
</CopilotKit>
```

Reference: [CopilotKit Provider](https://docs.copilotkit.ai/reference/v1/components/CopilotKit)
