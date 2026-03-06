---
title: Split Context by Domain
impact: MEDIUM
impactDescription: granular context updates avoid re-sending unchanged data
tags: state, context, granularity, optimization
---

## Split Context by Domain

Instead of one large `useCopilotReadable` call, split context into multiple calls by domain. This way, only the changed domain's context gets re-sent to the agent, reducing token usage and improving response quality.

**Incorrect (single monolithic context):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

function Dashboard() {
  const user = useUser()
  const projects = useProjects()
  const notifications = useNotifications()

  useCopilotReadable({
    description: "Everything",
    value: `User: ${user.name}, Role: ${user.role}. 
Projects: ${JSON.stringify(projects)}. 
Notifications: ${notifications.length} unread.`,
  })

  return <DashboardView />
}
```

**Correct (split context by domain):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

function Dashboard() {
  const user = useUser()
  const projects = useProjects()
  const notifications = useNotifications()

  useCopilotReadable({
    description: "Current user information",
    value: { userName: user.name, role: user.role },
  })

  useCopilotReadable({
    description: "User's projects",
    value: { projects: projects.map(p => ({ id: p.id, name: p.name, status: p.status })) },
  })

  useCopilotReadable({
    description: "Notification status",
    value: { unreadCount: notifications.length },
  })

  return <DashboardView />
}
```

Reference: [useCopilotReadable](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotReadable)
