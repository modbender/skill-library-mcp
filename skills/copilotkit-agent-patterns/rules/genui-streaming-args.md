---
title: Stream Tool Args for Real-Time UI
impact: MEDIUM
impactDescription: streaming args enables progressive UI rendering during tool calls
tags: genui, streaming, args, real-time
---

## Stream Tool Args for Real-Time UI

Stream tool call arguments incrementally via multiple `TOOL_CALL_ARGS` events rather than sending the complete JSON at once. This enables the frontend to render partial UI (skeletons, progressive content) while the agent is still generating arguments.

**Incorrect (all args sent at once, no streaming UI):**

```typescript
const args = { city: "San Francisco", temperature: 68, forecast: ["sunny", "partly cloudy", "sunny"] }
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "show_weather" }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: JSON.stringify(args) }
yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
```

**Correct (args streamed incrementally for progressive UI):**

```typescript
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "show_weather" }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: '{"city":"San' }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: ' Francisco","temperature":' }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: '68,"forecast":["sunny",' }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: '"partly cloudy","sunny"]}' }
yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
```

Reference: [Generative UI](https://docs.copilotkit.ai/guides/generative-ui)
