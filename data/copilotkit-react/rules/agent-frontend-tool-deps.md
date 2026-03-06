---
title: Declare Dependency Arrays for useFrontendTool
impact: MEDIUM
impactDescription: missing deps cause stale closures or infinite re-registrations
tags: agent, hooks, useFrontendTool, dependencies
---

## Declare Dependency Arrays for useFrontendTool

`useFrontendTool` (v2) and `useCopilotAction` (v1) accept a dependency array that controls when the tool re-registers. Without it, the tool re-registers on every render. Include all values from the component scope that the handler uses.

**Incorrect (no deps, re-registers every render):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";

function TaskPanel({ projectId }: { projectId: string }) {
  useFrontendTool({
    name: "create_task",
    handler: async ({ title }) => {
      await createTask(projectId, title)
    },
  })

  return <TaskList projectId={projectId} />
}
```

**Correct (deps array controls re-registration):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";

function TaskPanel({ projectId }: { projectId: string }) {
  useFrontendTool(
    {
      name: "create_task",
      handler: async ({ title }) => {
        await createTask(projectId, title)
      },
    },
    [projectId],
  )

  return <TaskList projectId={projectId} />
}
```

Reference: [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)
