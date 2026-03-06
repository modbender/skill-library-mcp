---
title: Stabilize Tool Handler References
impact: MEDIUM
impactDescription: unstable handler references cause tool re-registration churn
tags: agent, hooks, useCallback, performance
---

## Stabilize Tool Handler References

When passing handler functions to `useFrontendTool` (v2) or `useCopilotAction` (v1), wrap them with `useCallback` to maintain stable references. Unstable function references trigger unnecessary tool re-registrations, which can interrupt in-flight agent tool calls.

**Incorrect (new handler created every render):**

```tsx
import { useFrontendTool } from "@copilotkit/react-core/v2";

function DocumentEditor({ docId }: { docId: string }) {
  useFrontendTool(
    {
      name: "update_document",
      handler: async ({ content }) => {
        await updateDoc(docId, content)
      },
    },
    [docId],
  )

  return <Editor docId={docId} />
}
```

**Correct (stable handler via useCallback):**

```tsx
import { useCallback } from "react";
import { useFrontendTool } from "@copilotkit/react-core/v2";

function DocumentEditor({ docId }: { docId: string }) {
  const handler = useCallback(
    async ({ content }: { content: string }) => {
      await updateDoc(docId, content)
    },
    [docId]
  )

  useFrontendTool(
    {
      name: "update_document",
      handler,
    },
    [docId],
  )

  return <Editor docId={docId} />
}
```

Reference: [useFrontendTool (v2)](https://docs.copilotkit.ai/reference/v2/hooks/useFrontendTool)
