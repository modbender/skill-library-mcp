---
title: useRenderTool for Display, useFrontendTool for Effects
impact: HIGH
impactDescription: mixing concerns causes side effects during streaming or double execution
tags: tool, rendering, useFrontendTool, useRenderTool, separation
---

## useRenderTool for Display, useFrontendTool for Effects

Use `useRenderTool` when you only need to display UI in response to a tool call. Use `useFrontendTool` when the tool call should trigger side effects (API calls, state mutations, navigation). Mixing them causes side effects to fire during streaming or display-only tools to swallow return values.

**Incorrect (side effects in a render tool):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";

useRenderTool({
  name: "create_ticket",
  render: ({ parameters, status }) => {
    if (status === "complete") {
      createTicketInDb(parameters)
    }
    return <TicketCard {...parameters} />
  },
})
```

**Correct (separate render from effects):**

```tsx
import { useFrontendTool, useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

const ticketSchema = z.object({
  title: z.string(),
  priority: z.enum(["low", "medium", "high"]),
});

useFrontendTool({
  name: "create_ticket",
  parameters: ticketSchema,
  handler: async ({ title, priority }) => {
    const ticket = await createTicketInDb({ title, priority })
    return `Created ticket ${ticket.id}`
  },
})

useRenderTool({
  name: "create_ticket",
  parameters: ticketSchema,
  render: ({ parameters, status }) => {
    if (status === "inProgress") return <TicketSkeleton />
    return <TicketCard title={parameters.title} priority={parameters.priority} />
  },
})
```

In v1, use `useCopilotAction` with both `handler` and `render` props on the same action.

Reference: [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool) | [useRenderTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useRenderTool)
