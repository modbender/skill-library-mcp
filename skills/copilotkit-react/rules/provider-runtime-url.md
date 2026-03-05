---
title: Always Configure runtimeUrl
impact: CRITICAL
impactDescription: agents will not connect without a runtime URL
tags: provider, setup, configuration
---

## Always Configure runtimeUrl

The `CopilotKit` provider requires a `runtimeUrl` to connect to your agent backend. Without it, all agent interactions silently fail. The runtime URL points to your CopilotKit runtime endpoint that bridges frontend and agent.

**Incorrect (no runtime URL, agents can't connect):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit>
      <CopilotChat />
      <MyApp />
    </CopilotKit>
  )
}
```

**Correct (runtime URL configured):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <CopilotChat />
      <MyApp />
    </CopilotKit>
  )
}
```

For Copilot Cloud, use `publicApiKey` instead of `runtimeUrl`:

```tsx
<CopilotKit publicApiKey="ck_pub_...">
  <CopilotChat />
  <MyApp />
</CopilotKit>
```

Reference: [CopilotKit Provider](https://docs.copilotkit.ai/reference/v1/components/CopilotKit)
