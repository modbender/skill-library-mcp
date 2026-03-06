---
title: Handle All Tool Call Statuses
impact: HIGH
impactDescription: unhandled statuses cause blank UI or missing loading states
tags: tool, rendering, status, streaming
---

## Handle All Tool Call Statuses

Tool renders receive a `status` field with three possible values: `inProgress`, `executing`, and `complete`. Handle all three to provide proper loading states, execution feedback, and final results. Ignoring statuses causes jarring UI transitions.

**Incorrect (only handles complete, no loading state):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "search_results",
  parameters: z.object({ query: z.string(), results: z.array(z.string()) }),
  render: ({ parameters }) => {
    return <ResultsList results={parameters.results} />
  },
})
```

**Correct (handles all three statuses):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "search_results",
  parameters: z.object({ query: z.string(), results: z.array(z.string()) }),
  render: ({ parameters, status }) => {
    if (status === "inProgress") {
      return <SearchSkeleton query={parameters.query} />
    }
    if (status === "executing") {
      return <SearchProgress query={parameters.query} />
    }
    return <ResultsList results={parameters.results} />
  },
})
```

The same status values apply to v1's `useCopilotAction` render prop.

Reference: [useRenderTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useRenderTool)
