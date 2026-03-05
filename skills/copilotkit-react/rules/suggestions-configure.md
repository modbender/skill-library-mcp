---
title: Configure Suggestion Generation
impact: LOW
impactDescription: unconfigured suggestions are generic and unhelpful
tags: suggestions, configuration, useConfigureSuggestions
---

## Configure Suggestion Generation

Use `useConfigureSuggestions` (v2) or `useCopilotChatSuggestions` (v1) to control how and when suggestions are generated. Without configuration, suggestions may be too generic or generated at inappropriate times, wasting LLM calls.

**Incorrect (no suggestion configuration):**

```tsx
import { CopilotKit } from "@copilotkit/react-core";

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit">
      <CopilotSidebar>
        <Dashboard />
      </CopilotSidebar>
    </CopilotKit>
  )
}
```

**Correct (v2 configured suggestion generation):**

```tsx
import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

function Dashboard() {
  useConfigureSuggestions({
    instructions: "Suggest actions relevant to the user's current project and recent activity.",
    maxSuggestions: 3,
    available: "after-first-message",
  })

  return <DashboardView />
}
```

**Correct (v1 alternative):**

```tsx
import { useCopilotChatSuggestions } from "@copilotkit/react-ui";

function Dashboard() {
  useCopilotChatSuggestions({
    instructions: "Suggest actions relevant to the user's current project.",
    maxSuggestions: 3,
  })

  return <DashboardView />
}
```

Reference: [useConfigureSuggestions (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useConfigureSuggestions) | [useCopilotChatSuggestions (v1)](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotChatSuggestions)
