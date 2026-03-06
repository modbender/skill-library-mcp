---
title: Set Timeouts with Fallback Behavior
impact: MEDIUM
impactDescription: agents waiting forever for human input block resources indefinitely
tags: hitl, timeout, fallback, safety
---

## Set Timeouts with Fallback Behavior

When waiting for human input, always set a timeout with fallback behavior. Without it, an unresponsive user causes the agent to hang indefinitely, consuming server resources and blocking the thread.

**Incorrect (wait forever for human response):**

```typescript
const approval = await waitForHumanApproval(toolCallId)
if (approval.approved) {
  await deleteRecords()
}
```

**Correct (timeout with safe fallback):**

```typescript
const approval = await Promise.race([
  waitForHumanApproval(toolCallId),
  timeout(60_000).then(() => ({ approved: false, reason: "timeout" })),
])

if (approval.approved) {
  await deleteRecords()
} else {
  yield { type: "TEXT_MESSAGE_START", messageId: "m1", role: "assistant" }
  yield { type: "TEXT_MESSAGE_CONTENT", messageId: "m1", delta: "Action timed out. No changes were made." }
  yield { type: "TEXT_MESSAGE_END", messageId: "m1" }
}
```

Reference: [Human-in-the-Loop](https://docs.copilotkit.ai/guides/human-in-the-loop)
