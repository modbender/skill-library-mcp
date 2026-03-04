---
title: Handle Suggestion Loading States
impact: LOW
impactDescription: unhandled loading causes layout shift when suggestions appear
tags: suggestions, loading, UI, state
---

## Handle Suggestion Loading States

When rendering suggestions in the UI, use the `useSuggestions` hook (v2) to access loading state and prevent layout shifts. Suggestions are generated asynchronously and may take a moment to appear.

**Incorrect (no loading state, content jumps when suggestions load):**

```tsx
function SuggestionBar({ suggestions }: { suggestions: string[] }) {
  return (
    <div className="suggestions">
      {suggestions.map(s => (
        <button key={s}>{s}</button>
      ))}
    </div>
  )
}
```

**Correct (useSuggestions hook with loading state):**

```tsx
import { useSuggestions } from "@copilotkit/react-core/v2";

function SuggestionBar() {
  const { suggestions, isLoading } = useSuggestions()

  return (
    <div className="suggestions" style={{ minHeight: 48 }}>
      {isLoading ? (
        <SuggestionSkeleton count={3} />
      ) : (
        suggestions.map(s => (
          <button key={s.title} onClick={() => /* send s.message */}>
            {s.title}
          </button>
        ))
      )}
    </div>
  )
}
```

Reference: [useSuggestions (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useSuggestions)
