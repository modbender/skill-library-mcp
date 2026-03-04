---
title: Stream Text Incrementally
impact: HIGH
impactDescription: sending entire response at once defeats streaming UX
tags: agui, streaming, text, incremental
---

## Stream Text Incrementally

Emit `TEXT_MESSAGE_CONTENT` events with small deltas as they become available, rather than buffering the entire response and sending it at once. Incremental streaming gives users real-time feedback and perceived performance.

**Incorrect (buffer entire response, send at once):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }

  const fullResponse = await generateFullResponse(input)
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: fullResponse }

  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

**Correct (stream incrementally as tokens arrive):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }

  for await (const chunk of streamResponse(input)) {
    yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: chunk }
  }

  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)
