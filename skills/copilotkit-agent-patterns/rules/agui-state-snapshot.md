---
title: Emit STATE_SNAPSHOT for Frontend Sync
impact: HIGH
impactDescription: without snapshots, frontend state drifts from agent state
tags: agui, state, snapshot, sync
---

## Emit STATE_SNAPSHOT for Frontend Sync

Emit `STATE_SNAPSHOT` events to synchronize agent state with the frontend. The frontend uses these snapshots to update shared state via `useAgent`. Without them, the UI shows stale data that doesn't reflect agent progress.

**Incorrect (no state snapshots, frontend shows stale data):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  const results = await performResearch(input.query)
  // Frontend never sees the results until run finishes
  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: "Done researching." }
  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

**Correct (state snapshot keeps frontend in sync):**

```typescript
async function* handleRun(input: RunInput) {
  yield { type: "RUN_STARTED" }
  yield { type: "STATE_SNAPSHOT", snapshot: { status: "researching", results: [] } }

  const results = await performResearch(input.query)
  yield { type: "STATE_SNAPSHOT", snapshot: { status: "complete", results } }

  yield { type: "TEXT_MESSAGE_START", messageId: "1", role: "assistant" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "1", delta: `Found ${results.length} results.` }
  yield { type: "TEXT_MESSAGE_END", messageId: "1" }
  yield { type: "RUN_FINISHED" }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)
