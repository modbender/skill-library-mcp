---
title: Provide Rich Context for Suggestions
impact: LOW
impactDescription: suggestions without context are generic and irrelevant
tags: suggestions, context, relevance
---

## Provide Rich Context for Suggestions

Suggestions are only as good as the context available. Combine `useConfigureSuggestions` (v2) with `useCopilotReadable` to give the suggestion engine enough information to produce relevant, actionable suggestions.

**Incorrect (suggestions without context):**

```tsx
import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

function TaskBoard() {
  useConfigureSuggestions({
    instructions: "Suggest helpful actions",
    maxSuggestions: 3,
  })

  return <Board />
}
```

**Correct (suggestions enriched with context):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";
import { useConfigureSuggestions } from "@copilotkit/react-core/v2";

function TaskBoard() {
  const tasks = useTasks()
  const overdue = tasks.filter(t => t.isOverdue)

  useCopilotReadable({
    description: "Task board state",
    value: {
      totalTasks: tasks.length,
      overdueTasks: overdue.map(t => ({ id: t.id, title: t.title, dueDate: t.dueDate })),
      currentSprint: "Sprint 14",
    },
  })

  useConfigureSuggestions({
    instructions: "Suggest actions based on overdue tasks and sprint progress. Prioritize urgent items.",
    maxSuggestions: 3,
    available: "after-first-message",
  })

  return <Board tasks={tasks} />
}
```

Reference: [useConfigureSuggestions (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useConfigureSuggestions)
