---
title: Register Wildcard Renderer as Fallback
impact: MEDIUM
impactDescription: prevents missing UI when agent calls unregistered tools
tags: tool, rendering, wildcard, fallback
---

## Register Wildcard Renderer as Fallback

Register a wildcard `"*"` renderer with `useRenderTool` to catch tool calls that don't have a dedicated renderer. Without a fallback, unregistered tool calls render nothing in the chat, confusing users.

**Incorrect (no fallback, unknown tools render blank):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "show_chart",
  parameters: z.object({ data: z.array(z.number()) }),
  render: ({ parameters }) => <Chart data={parameters.data} />,
})
```

**Correct (wildcard fallback for unknown tools):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "show_chart",
  parameters: z.object({ data: z.array(z.number()) }),
  render: ({ parameters }) => <Chart data={parameters.data} />,
})

useRenderTool({
  name: "*",
  render: ({ name, parameters, status }) => (
    <GenericToolCard
      toolName={name}
      args={parameters}
      isLoading={status === "inProgress"}
    />
  ),
})
```

Reference: [useRenderTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useRenderTool)
