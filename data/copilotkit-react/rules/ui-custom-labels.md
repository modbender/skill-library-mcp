---
title: Customize Labels for Your Domain
impact: LOW
impactDescription: default labels feel generic and reduce user trust
tags: ui, labels, customization, branding
---

## Customize Labels for Your Domain

Always customize the `labels` prop on chat components to match your application's domain. Default labels like "How can I help?" feel generic and don't build user confidence in the agent's capabilities.

**Incorrect (default labels, generic feel):**

```tsx
<CopilotSidebar>
  <MyApp />
</CopilotSidebar>
```

**Correct (domain-specific labels):**

```tsx
<CopilotSidebar
  labels={{
    title: "Sales Assistant",
    placeholder: "Ask about leads, deals, or forecasts...",
    initial: "I can help you analyze your pipeline, draft outreach, or update deal stages.",
  }}
>
  <MyApp />
</CopilotSidebar>
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)
