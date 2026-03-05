---
title: Set maxSteps to Prevent Infinite Loops
impact: CRITICAL
impactDescription: unbounded agents can loop indefinitely, consuming tokens and time
tags: architecture, maxSteps, safety, loops
---

## Set maxSteps to Prevent Infinite Loops

Always set `maxSteps` on agents to limit the number of tool-call cycles. Without a limit, an agent that repeatedly calls tools without converging on an answer will loop indefinitely, consuming tokens and blocking the user.

**Incorrect (no step limit, potential infinite loop):**

```typescript
const agent = new BuiltInAgent({
  name: "data_processor",
  tools: [queryTool, transformTool, validateTool],
})
```

**Correct (step limit prevents runaway execution):**

```typescript
const agent = new BuiltInAgent({
  name: "data_processor",
  tools: [queryTool, transformTool, validateTool],
  maxSteps: 10,
})
```

Choose a `maxSteps` value based on the expected complexity of your agent's workflow. Simple Q&A agents may need 3-5 steps; complex multi-tool workflows may need 10-20.

Reference: [BuiltInAgent](https://docs.copilotkit.ai/reference/runtime/built-in-agent)
