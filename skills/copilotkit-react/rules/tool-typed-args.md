---
title: Define Zod Schemas for Tool Args
impact: HIGH
impactDescription: enables type-safe rendering and partial arg streaming
tags: tool, rendering, zod, type-safety
---

## Define Zod Schemas for Tool Args

When using `useRenderTool` (v2), always define a Zod schema for the `parameters` field. This enables type-safe access to tool arguments and allows CopilotKit to stream partial arguments while the tool call is in progress, giving users real-time feedback.

**Incorrect (no schema, parameters are untyped):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";

useRenderTool({
  name: "show_weather",
  render: ({ parameters, status }) => {
    return (
      <WeatherCard
        city={parameters.city}
        temp={parameters.temperature}
      />
    )
  },
})
```

**Correct (Zod schema provides type safety and streaming):**

```tsx
import { useRenderTool } from "@copilotkit/react-core/v2";
import { z } from "zod";

useRenderTool({
  name: "show_weather",
  parameters: z.object({
    city: z.string(),
    temperature: z.number(),
    condition: z.enum(["sunny", "cloudy", "rainy"]),
  }),
  render: ({ parameters, status }) => {
    if (status === "inProgress") {
      return <WeatherCardSkeleton city={parameters.city} />
    }
    return (
      <WeatherCard
        city={parameters.city}
        temp={parameters.temperature}
        condition={parameters.condition}
      />
    )
  },
})
```

The Zod schema enables:
- TypeScript inference for `parameters` in the render function
- Partial parameters during `inProgress` status (for streaming UI)
- Validation before `executing` and `complete` statuses

In v1, use `useCopilotAction` with `render` and plain parameter arrays instead.

Reference: [useRenderTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useRenderTool)
