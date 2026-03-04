# OpenClaw Hook Schema Reference Draft (Issue #18677)

Updated: 2026-02-18

## Goal
Provide a docs-ready, backward-compatible reference implementation for runtime security hooks.

## Proposed Event Extension

```ts
interface InternalHookEvent {
  // existing fields
  cancel?: boolean;
  cancelReason?: string;
  policyMode?: "warn" | "balanced" | "strict";
}
```

### Compatibility
- Existing hooks continue to work without changes.
- If cancel fields are absent, runtime behavior is unchanged.

## Policy Semantics
- `warn`: never block, log + user warning only
- `balanced`: block HIGH/CRITICAL confidence matches
- `strict`: block any matched policy rule

## Reference `HOOK.md`

```md
---
name: security-runtime-guard
description: "Reference runtime guard hook for tool-call safety"
metadata:
  { "openclaw": { "emoji": "🛡️", "events": ["agent:before_tool_call"] } }
---

# security-runtime-guard

Reference implementation for cancel/veto-enabled runtime checks.
```

## Reference `handler.ts`

```ts
import type { HookHandler } from "../../src/hooks/hooks.js";

const HIGH_RISK = [/curl\s+.*\|\s*sh/i, /reverse\s*shell/i, /169\.254\.169\.254/];

const handler: HookHandler = async (event) => {
  if (event.type !== "agent" || event.action !== "before_tool_call") return;

  const mode = event.policyMode ?? "warn";
  const text = JSON.stringify(event.context ?? {});
  const hit = HIGH_RISK.find((re) => re.test(text));
  if (!hit) return;

  event.messages.push(`🛡️ Runtime guard detected risky pattern: ${hit}`);

  if (mode === "warn") return;

  // balanced/strict: cancellation path
  event.cancel = true;
  event.cancelReason =
    mode === "strict"
      ? "Blocked by strict runtime policy"
      : "Blocked by balanced runtime policy (high-risk pattern)";
};

export default handler;
```

## Notes for Docs
1. Document that some releases may still be warn-only until cancel support lands.
2. Recommend combining install-time static scan + runtime guard:
   - Install-time: `guard-scanner`
   - Runtime: internal hook guard
3. Add troubleshooting section for false positives (context-aware suppression).
