---
title: Emit State Snapshots at Meaningful Checkpoints
impact: HIGH
impactDescription: too frequent snapshots waste bandwidth; too rare loses real-time feel
tags: state, snapshots, frequency, checkpoints
---

## Emit State Snapshots at Meaningful Checkpoints

Emit `STATE_SNAPSHOT` events at meaningful points in the agent workflow — after completing a step, receiving results, or changing status. Avoid emitting on every token or loop iteration, which wastes bandwidth and causes excessive re-renders.

**Incorrect (snapshot on every iteration, causes re-render storms):**

```typescript
async function* processItems(items: string[]) {
  for (let i = 0; i < items.length; i++) {
    const result = await processItem(items[i])
    yield { type: "STATE_SNAPSHOT", snapshot: { processed: i + 1, total: items.length, results: [result] } }
  }
}
```

**Correct (snapshots at meaningful checkpoints):**

```typescript
async function* processItems(items: string[]) {
  yield { type: "STATE_SNAPSHOT", snapshot: { phase: "processing", total: items.length, processed: 0 } }

  const results = []
  for (const item of items) {
    results.push(await processItem(item))
  }

  yield { type: "STATE_SNAPSHOT", snapshot: { phase: "complete", total: items.length, processed: items.length, results } }
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)
