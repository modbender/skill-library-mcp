---
title: Keep State Snapshots Minimal and Serializable
impact: MEDIUM
impactDescription: large or non-serializable state causes transmission failures
tags: state, serialization, payload, size
---

## Keep State Snapshots Minimal and Serializable

State snapshots are serialized as JSON and sent over the wire. Keep them minimal — include only the state the frontend needs to render UI. Avoid including non-serializable values (functions, class instances) or large datasets.

**Incorrect (non-serializable and bloated state):**

```typescript
yield {
  type: "STATE_SNAPSHOT",
  snapshot: {
    dbConnection: pool,
    fullDataset: await fetchAllRecords(),
    processFn: (x: any) => x.toString(),
    internalBuffer: Buffer.alloc(1024),
  },
}
```

**Correct (minimal, serializable state):**

```typescript
yield {
  type: "STATE_SNAPSHOT",
  snapshot: {
    recordCount: 1500,
    processedCount: 750,
    status: "processing",
    lastProcessedId: "rec_abc123",
  },
}
```

Reference: [AG-UI Protocol](https://docs.ag-ui.com/concepts/events)
