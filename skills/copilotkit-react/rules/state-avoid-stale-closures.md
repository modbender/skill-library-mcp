---
title: Avoid Stale Closures in Tool Handlers
impact: HIGH
impactDescription: stale closures cause tools to operate on outdated state
tags: state, closures, handlers, useFrontendTool
---

## Avoid Stale Closures in Tool Handlers

Tool handlers registered with `useFrontendTool` (v2) or `useCopilotAction` (v1) capture variables from their closure. If state changes between registration and invocation, the handler sees stale values. Use functional state updates or refs to always access current state.

**Incorrect (stale closure captures initial items):**

```tsx
import { useCopilotAction } from "@copilotkit/react-core";

function TodoPanel() {
  const [items, setItems] = useState<string[]>([])

  useCopilotAction({
    name: "add_todo",
    parameters: [{ name: "title", type: "string", description: "Todo title" }],
    handler: async ({ title }) => {
      setItems([...items, title])
    },
  })

  return <TodoList items={items} />
}
```

**Correct (functional update always uses current state):**

```tsx
import { useCopilotAction } from "@copilotkit/react-core";

function TodoPanel() {
  const [items, setItems] = useState<string[]>([])

  useCopilotAction({
    name: "add_todo",
    parameters: [{ name: "title", type: "string", description: "Todo title" }],
    handler: async ({ title }) => {
      setItems(prev => [...prev, title])
    },
  })

  return <TodoList items={items} />
}
```

Reference: [useCopilotAction](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotAction) | [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)
