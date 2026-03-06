---
title: Handle Bidirectional State Conflicts
impact: MEDIUM
impactDescription: unhandled conflicts cause data loss or UI flicker
tags: state, conflicts, bidirectional, resolution
---

## Handle Bidirectional State Conflicts

CopilotKit supports bidirectional state sync — both the frontend and agent can modify shared state. When both sides update simultaneously, implement conflict resolution logic to prevent data loss.

**Incorrect (agent blindly overwrites frontend state):**

```typescript
async function* updateTasks(agentTasks: Task[]) {
  yield {
    type: "STATE_SNAPSHOT",
    snapshot: { tasks: agentTasks },
  }
}
```

**Correct (merge strategy preserves both-side changes):**

```typescript
async function* updateTasks(agentTasks: Task[], frontendState: AppState) {
  const mergedTasks = agentTasks.map(agentTask => {
    const frontendTask = frontendState.tasks.find(t => t.id === agentTask.id)
    if (frontendTask && frontendTask.updatedAt > agentTask.updatedAt) {
      return frontendTask
    }
    return agentTask
  })

  yield {
    type: "STATE_SNAPSHOT",
    snapshot: { tasks: mergedTasks },
  }
}
```

Reference: [State Management](https://docs.copilotkit.ai/guides/state-management)
