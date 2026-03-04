---
title: Include Context for User Decisions
impact: LOW
impactDescription: users can't make informed decisions without sufficient context
tags: hitl, context, decisions, UX
---

## Include Context for User Decisions

When requesting human approval or input, include enough context in the tool call args for the user to make an informed decision. Don't ask "Proceed?" — tell them exactly what will happen.

**Incorrect (vague approval request):**

```typescript
yield {
  type: "TOOL_CALL_ARGS",
  toolCallId: "tc_1",
  delta: JSON.stringify({ message: "Proceed with the operation?" }),
}
```

**Correct (detailed context for informed decision):**

```typescript
yield {
  type: "TOOL_CALL_ARGS",
  toolCallId: "tc_1",
  delta: JSON.stringify({
    action: "send_emails",
    recipientCount: 150,
    subject: "Q1 Report Update",
    estimatedCost: "$0.45",
    message: "Send 150 emails with subject 'Q1 Report Update'? Estimated cost: $0.45.",
  }),
}
```

Reference: [Human-in-the-Loop](https://docs.copilotkit.ai/guides/human-in-the-loop)
