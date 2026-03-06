---
title: Isolate State Per Thread
impact: HIGH
impactDescription: shared state across threads causes cross-user data leaks
tags: state, thread, isolation, multi-tenant
---

## Isolate State Per Thread

Each conversation thread must have its own isolated state. Sharing state across threads causes one user's data to leak into another user's conversation, especially in multi-tenant environments.

**Incorrect (global state shared across all threads):**

```typescript
const globalState = { results: [], status: "idle" }

class ResearchAgent {
  async run(input: RunInput) {
    globalState.status = "running"
    globalState.results = await search(input.query)
  }
}
```

**Correct (state isolated per thread):**

```typescript
class ResearchAgent {
  async run(input: RunInput) {
    const threadState = {
      results: [] as SearchResult[],
      status: "running" as const,
    }

    threadState.results = await search(input.query)
    threadState.status = "complete"

    yield { type: "STATE_SNAPSHOT", snapshot: threadState }
  }
}
```

Reference: [Thread Management](https://docs.copilotkit.ai/guides/threads)
