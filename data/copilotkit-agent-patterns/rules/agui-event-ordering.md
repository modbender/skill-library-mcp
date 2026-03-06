---
title: Emit AG-UI Events in Correct Order
impact: CRITICAL
impactDescription: wrong event order causes broken streaming and lost messages
tags: agui, events, ordering, protocol
---

## Emit AG-UI Events in Correct Order

AG-UI events must follow a strict ordering: `RUN_STARTED` -> content events -> `RUN_FINISHED`. Text messages require `TEXT_MESSAGE_START` -> `TEXT_MESSAGE_CONTENT` (one or more) -> `TEXT_MESSAGE_END`. Out-of-order events cause the frontend to drop messages or display corrupted content.

**Incorrect (missing start event, content before start):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "TEXT_MESSAGE_CONTENT", delta: "Hello" }
  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

**Correct (proper event ordering):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: "Hello" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: " world" }
  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)
