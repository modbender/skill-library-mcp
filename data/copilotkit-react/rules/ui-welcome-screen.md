---
title: Provide Welcome Screen with Prompts
impact: LOW
impactDescription: users don't know what to ask without guidance
tags: ui, welcome, onboarding, prompts
---

## Provide Welcome Screen with Prompts

Configure a welcome screen with suggested prompts to guide users on what the agent can do. An empty chat box with no guidance leads to low engagement because users don't know what to ask.

**Incorrect (no welcome screen, empty chat):**

```tsx
<CopilotChat />
```

**Correct (welcome screen with actionable prompts):**

```tsx
<CopilotChat
  welcomeScreen={{
    title: "Welcome to your AI Assistant",
    description: "I can help you with your projects and tasks.",
    suggestedPrompts: [
      "Summarize my overdue tasks",
      "Draft a status update for the team",
      "Create a new task for the landing page redesign",
    ],
  }}
/>
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)
