---
title: Provide Only Relevant Context
impact: MEDIUM
impactDescription: excessive context wastes tokens and confuses agents
tags: state, context, performance, tokens
---

## Provide Only Relevant Context

Only provide context that the agent needs for its current task. Dumping entire app state into context wastes LLM tokens, increases latency, and can confuse the agent with irrelevant information.

**Incorrect (entire app state as context):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

function App() {
  const appState = useAppStore()

  useCopilotReadable({
    description: "Application state",
    value: JSON.stringify(appState),
  })

  return <Dashboard />
}
```

**Correct (only relevant context for the current view):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

function ProjectView({ projectId }: { projectId: string }) {
  const project = useProject(projectId)
  const tasks = useTasks(projectId)

  useCopilotReadable({
    description: "Current project details",
    value: {
      name: project.name,
      status: project.status,
      activeTasks: tasks.filter(t => t.status === "active").length,
      userRole: project.currentUserRole,
    },
  })

  return <ProjectDashboard project={project} tasks={tasks} />
}
```

Reference: [useCopilotReadable](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotReadable)
