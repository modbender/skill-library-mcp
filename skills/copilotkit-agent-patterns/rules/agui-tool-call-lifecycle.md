---
title: Follow Tool Call Event Lifecycle
impact: HIGH
impactDescription: incomplete lifecycle causes frontend to hang or miss results
tags: agui, tool-call, lifecycle, events
---

## Follow Tool Call Event Lifecycle

Tool calls require a complete event lifecycle: `TOOL_CALL_START` -> `TOOL_CALL_ARGS` (streamed) -> `TOOL_CALL_END`. Missing any step causes the frontend's `useRenderTool` to hang in an incorrect status or miss the tool call entirely.

**Incorrect (missing TOOL_CALL_END, frontend stays in "executing"):**

```typescript
async function* handleToolCall(tool: string, args: object) {
  yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: tool }
  yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: JSON.stringify(args) }
  // Missing TOOL_CALL_END
}
```

**Correct (complete tool call lifecycle):**

```typescript
async function* handleToolCall(tool: string, args: object) {
  yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: tool }
  yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: JSON.stringify(args) }
  yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)
