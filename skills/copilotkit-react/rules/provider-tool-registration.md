---
title: Register Tools via Hooks Inside Provider
impact: MEDIUM
impactDescription: hooks provide dynamic registration and proper lifecycle management
tags: provider, tools, hooks, registration
---

## Register Tools via Hooks Inside Provider

Register tools using `useCopilotAction` (v1) or `useFrontendTool` (v2) hooks inside components that are children of `CopilotKit`, rather than passing tool definitions as props. Hook-based registration ties tool availability to component lifecycle and enables dynamic tool sets.

**Incorrect (static tool props on provider):**

```tsx
const tools = [
  { name: "search", handler: searchFn, description: "Search docs" }
]

function App() {
  return (
    <CopilotKit runtimeUrl="/api/copilotkit" tools={tools}>
      <MyApp />
    </CopilotKit>
  )
}
```

**Correct (hook-based registration inside provider, v1):**

```tsx
import { useCopilotAction } from "@copilotkit/react-core";

function MyApp() {
  useCopilotAction({
    name: "search",
    description: "Search the documentation",
    parameters: [{ name: "query", type: "string", description: "Search query" }],
    handler: async ({ query }) => {
      return await searchDocs(query)
    },
  })

  return <Dashboard />
}
```

**Correct (hook-based registration inside provider, v2 with Zod):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

function MyApp() {
  useFrontendTool({
    name: "search",
    description: "Search the documentation",
    parameters: z.object({ query: z.string().describe("Search query") }),
    handler: async ({ query }) => {
      return await searchDocs(query)
    },
  })

  return <Dashboard />
}
```

Reference: [useCopilotAction](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotAction) | [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)
