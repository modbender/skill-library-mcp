---
title: Scope Agent Config with Nested Providers
impact: HIGH
impactDescription: prevents agent configuration conflicts in multi-agent apps
tags: provider, nesting, multi-agent, configuration
---

## Scope Agent Config with Nested Providers

When different parts of your app need different agent configurations (different agents, tools, or context), nest `CopilotKit` providers to scope configuration. Inner providers inherit from outer ones but can override specific settings via the `agent` prop.

**Incorrect (single provider, all agents share config):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <ResearchPanel />
      <WritingPanel />
    </CopilotKit>
  )
}
```

**Correct (nested providers scope agent config):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <CopilotKit agent="researcher">
        <ResearchPanel />
      </CopilotKit>
      <CopilotKit agent="writer">
        <WritingPanel />
      </CopilotKit>
    </CopilotKit>
  )
}
```

Reference: [CopilotKit Provider](https://docs.copilotkit.ai/reference/v1/components/CopilotKit)
