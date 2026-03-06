---
title: Use Appropriate Input Mode
impact: LOW
impactDescription: wrong input mode creates friction for the interaction type
tags: ui, input, mode, configuration
---

## Use Appropriate Input Mode

Set the `inputMode` prop to match your use case. Use `"text"` for general chat, `"voice"` for hands-free workflows, and `"multi"` to let users switch between text and voice.

**Incorrect (default text mode for a driving assistant):**

```tsx
function DrivingAssistant() {
  return (
    <CopilotChat
      labels={{ title: "Navigation Assistant" }}
    />
  )
}
```

**Correct (voice mode for hands-free interaction):**

```tsx
function DrivingAssistant() {
  return (
    <CopilotChat
      inputMode="voice"
      labels={{ title: "Navigation Assistant" }}
    />
  )
}
```

Reference: [Chat Components](https://docs.copilotkit.ai/reference/components/chat)
