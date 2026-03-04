---
title: Use Tool Calls for Approval Gates
impact: MEDIUM
impactDescription: custom events for approvals break the standard AG-UI flow
tags: hitl, approval, tool-calls, gates
---

## Use Tool Calls for Approval Gates

Implement human-in-the-loop approval gates as tool calls that the frontend renders with `useRenderTool`, rather than custom event types. This keeps the approval flow within the standard AG-UI protocol and lets you use CopilotKit's built-in HITL handling.

**Incorrect (custom event type for approval):**

```typescript
yield { type: "CUSTOM_EVENT", eventType: "APPROVAL_NEEDED", data: { action: "delete_records", count: 50 } }
// Frontend has no standard way to handle this
```

**Correct (tool call triggers frontend approval UI):**

```typescript
yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "confirm_deletion" }
yield {
  type: "TOOL_CALL_ARGS",
  toolCallId: "tc_1",
  delta: JSON.stringify({ action: "delete_records", count: 50, message: "Delete 50 records?" }),
}
yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
```

Reference: [Human-in-the-Loop](https://docs.copilotkit.ai/guides/human-in-the-loop)
