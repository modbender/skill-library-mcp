---
title: Write Descriptive Context Values
impact: HIGH
impactDescription: vague context produces vague agent responses
tags: agent, context, useCopilotReadable, quality
---

## Write Descriptive Context Values

When using `useCopilotReadable` to provide context to your agent, supply specific, descriptive values that help the agent understand the current application state. Vague or minimal context leads to generic agent responses that don't match the user's situation.

**Incorrect (vague context, agent lacks understanding):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

useCopilotReadable({
  description: "Current page",
  value: "dashboard",
})
```

**Correct (specific context with relevant details):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

useCopilotReadable({
  description: "Current project dashboard state",
  value: {
    projectName: project.name,
    totalTasks: tasks.length,
    overdueTasks: tasks.filter(t => t.status === "overdue").length,
    userRole: "admin",
  },
})
```

In v2, you can also provide context via `useAgent` shared state:

```tsx
import { useAgent } from "@copilotkit/react-core/v2";

const { agent } = useAgent({ agentId: "researcher" });
agent.setState({ projectName: project.name, taskCount: tasks.length });
```

Reference: [useCopilotReadable](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotReadable)
