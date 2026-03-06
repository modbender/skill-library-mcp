---
title: Use Text Messages for Status Updates
impact: LOW
impactDescription: status updates that aren't tool calls should use text messages, not fake tool calls
tags: genui, activity, messages, status
---

## Use Text Messages for Status Updates

Use lightweight text messages for status updates that don't correspond to tool calls (e.g., "Searching...", "Analyzing results..."). Don't create fake tool calls just to show status — this causes unnecessary rendering and confusing UI in the chat.

**Incorrect (fake tool call for a status message):**

```typescript
yield { type: "TOOL_CALL_START", toolCallId: "tc_status", toolName: "show_status" }
yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_status", delta: '{"message":"Searching..."}' }
yield { type: "TOOL_CALL_END", toolCallId: "tc_status" }
```

**Correct (text message for status updates):**

```typescript
yield { type: "TEXT_MESSAGE_START", messageId: "status_1", role: "assistant" }
yield { type: "TEXT_MESSAGE_CONTENT", messageId: "status_1", delta: "Searching databases..." }
yield { type: "TEXT_MESSAGE_END", messageId: "status_1" }

// For CoAgents using LangGraph, emit state updates instead:
// await copilotkit_emit_state(config, { status: "searching" })
```

For CoAgents, the recommended approach is to emit agent state via `copilotkit_emit_state` and render the status in the frontend using `useCoAgentStateRender`.

Reference: [Generative UI](https://docs.copilotkit.ai/coagents/generative-ui/agentic)
