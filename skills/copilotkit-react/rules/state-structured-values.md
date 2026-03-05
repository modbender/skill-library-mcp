---
title: Use Structured Objects in Context
impact: MEDIUM
impactDescription: structured data enables better agent reasoning than flat strings
tags: state, context, useCopilotReadable, structured
---

## Use Structured Objects in Context

When providing context via `useCopilotReadable`, use structured objects for the `value` rather than serialized strings. Structured data helps agents parse and reason about context more reliably than free-form text.

**Incorrect (serialized string, hard for agent to parse):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

useCopilotReadable({
  description: "Cart items",
  value: `items: ${items.map(i => `${i.name}(${i.price})`).join(", ")}`,
})
```

**Correct (structured object for reliable parsing):**

```tsx
import { useCopilotReadable } from "@copilotkit/react-core";

useCopilotReadable({
  description: "Shopping cart contents",
  value: {
    cartItems: items.map(item => ({
      name: item.name,
      price: item.price,
      quantity: item.quantity,
    })),
    total: items.reduce((sum, i) => sum + i.price * i.quantity, 0),
    itemCount: items.length,
  },
})
```

Reference: [useCopilotReadable](https://docs.copilotkit.ai/reference/v1/hooks/useCopilotReadable)
