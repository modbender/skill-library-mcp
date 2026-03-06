---
title: Choose Appropriate Chat Layout
impact: MEDIUM
impactDescription: wrong layout choice degrades UX for the use case
tags: ui, chat, CopilotSidebar, CopilotPopup, layout
---

## Choose Appropriate Chat Layout

Choose `CopilotSidebar` for persistent, always-visible agent interaction (e.g., copilot-assisted workflows). Choose `CopilotPopup` for on-demand, quick interactions. Choose `CopilotChat` for inline, embedded chat in a specific page section.

**Incorrect (popup for a workflow that needs persistent chat):**

```tsx
function ProjectWorkspace() {
  return (
    <div>
      <ProjectBoard />
      <CopilotPopup />
    </div>
  )
}
```

**Correct (sidebar for persistent workflow assistance):**

```tsx
function ProjectWorkspace() {
  return (
    <CopilotSidebar
      defaultOpen={true}
      labels={{ title: "Project Assistant" }}
    >
      <ProjectBoard />
    </CopilotSidebar>
  )
}
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)
