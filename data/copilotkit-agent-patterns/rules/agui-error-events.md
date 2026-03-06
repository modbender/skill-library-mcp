---
title: Always Emit Error Events on Failure
impact: HIGH
impactDescription: silent failures leave the frontend hanging with no feedback
tags: agui, error, events, failure
---

## Always Emit Error Events on Failure

When an agent encounters an error, always emit a `RUN_ERROR` event before stopping. Without it, the frontend hangs indefinitely waiting for `RUN_FINISHED`, and the user sees no feedback about what went wrong.

**Incorrect (error swallowed, frontend hangs):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  try {
    const result = await riskyOperation()
    yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
    yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: result }
    yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  } catch (error) {
    console.error(error)
    // Frontend never knows the run failed
  }
}
```

**Correct (error event notifies frontend):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  try {
    const result = await riskyOperation()
    yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
    yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: result }
    yield { type: "TEXT_MESSAGE_END", messageId: "1" }
    yield { type: "RUN_FINISHED" }
  } catch (error) {
    yield { type: "RUN_ERROR", message: error.message, code: "OPERATION_FAILED" }
  }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)
