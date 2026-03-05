---
title: Use useFrontendTool render Prop for Simple UI
impact: MEDIUM
impactDescription: reduces boilerplate for common component-rendering patterns
tags: tool, rendering, useFrontendTool, simplification
---

## Use useFrontendTool render Prop for Simple UI

When a tool call needs both side effects and UI rendering, use `useFrontendTool` with its optional `render` prop instead of registering separate `useFrontendTool` and `useRenderTool` hooks. This keeps the tool definition in one place.

**Incorrect (separate hooks for a simple tool):**

```tsx
import { useFrontendTool, useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

const schema = z.object({ name: z.string(), email: z.string() });

useFrontendTool({
  name: "show_user_card",
  parameters: schema,
  handler: async ({ name, email }) => {
    return `Showing card for ${name}`
  },
})

useRenderTool({
  name: "show_user_card",
  parameters: schema,
  render: ({ parameters, status }) => {
    if (status !== "complete") return <UserCardSkeleton />
    return <UserCard name={parameters.name} email={parameters.email} />
  },
})
```

**Correct (single useFrontendTool with render prop):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useFrontendTool({
  name: "show_user_card",
  parameters: z.object({ name: z.string(), email: z.string() }),
  handler: async ({ name, email }) => {
    return `Showing card for ${name}`
  },
  render: ({ name, args, status, result }) => {
    if (status !== "complete") return <UserCardSkeleton />
    return <UserCard name={args.name} email={args.email} />
  },
})
```

In v1, `useCopilotAction` similarly combines `handler` and `render` in one definition.

Reference: [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)
