---
title: Emit Tool Calls That Map to useRenderTool
impact: MEDIUM
impactDescription: mismatched tool names cause blank renders in the frontend
tags: genui, tool-call, useRenderTool, mapping
---

## Emit Tool Calls That Map to useRenderTool

When emitting tool calls that should render UI in the frontend, ensure the `toolName` matches exactly what the frontend has registered with `useRenderTool`. Mismatched names cause the tool call to render nothing.

**Incorrect (tool name mismatch between agent and frontend):**

```typescript
// Agent emits:
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "showWeather" }

// Frontend registers:
useRenderTool({ name: "show_weather", render: ({ args }) => <WeatherCard {...args} /> })
// Names don't match — nothing renders
```

**Correct (matching tool names):**

```typescript
// Agent emits:
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "show_weather" }

// Frontend registers:
useRenderTool({ name: "show_weather", render: ({ args }) => <WeatherCard {...args} /> })
```

Establish a naming convention (e.g., `snake_case`) and share tool name constants between agent and frontend.

Reference: [Generative UI](https://docs.copilotkit.ai/guides/generative-ui)
