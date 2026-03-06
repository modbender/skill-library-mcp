---
title: Preserve State When Resuming After Approval
impact: MEDIUM
impactDescription: lost state after resume forces the agent to redo work
tags: hitl, resume, state, persistence
---

## Preserve State When Resuming After Approval

When an agent pauses for human input and then resumes, ensure all intermediate state is preserved. Losing state forces the agent to redo expensive computations, wasting time and tokens.

**Incorrect (state lost after human approval pause):**

```typescript
async function* handleRun(input: RunInput) {
  const analysis = await performExpensiveAnalysis(input.data)
  yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "confirm_action" }
  // ... wait for approval
  // After resume: analysis variable is gone, must recompute
}
```

**Correct (state persisted across pause/resume):**

```typescript
async function* handleRun(input: RunInput) {
  const analysis = await performExpensiveAnalysis(input.data)

  yield {
    type: "STATE_SNAPSHOT",
    snapshot: { analysis, phase: "awaiting_approval" },
  }

  yield { type: "TOOL_CALL_START", toolCallId: "tc_1", toolName: "confirm_action" }
  yield { type: "TOOL_CALL_ARGS", toolCallId: "tc_1", delta: JSON.stringify({ summary: analysis.summary }) }
  yield { type: "TOOL_CALL_END", toolCallId: "tc_1" }
}
```

Reference: [Human-in-the-Loop](https://docs.copilotkit.ai/guides/human-in-the-loop)
