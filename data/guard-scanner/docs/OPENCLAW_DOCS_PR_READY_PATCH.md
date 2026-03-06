# OpenClaw Docs PR-Ready Patch (Reference Implementation)

Updated: 2026-02-18
Target: `docs/automation/hooks.md` (new subsection)

## Section Title
`### Runtime Security Guard (Reference: before_tool_call)`

## Paste-ready content

```md
### Runtime Security Guard (Reference: `agent:before_tool_call`)

This reference shows a backward-compatible runtime hook pattern for tool-call safety.

#### Proposed event fields (backward-compatible)

```ts
interface InternalHookEvent {
  // existing fields
  cancel?: boolean;      // default false
  cancelReason?: string; // user-visible cancellation reason
  policyMode?: "warn" | "balanced" | "strict";
}
```

- Existing hooks remain unchanged.
- If `cancel` fields are not used/supported, behavior stays warn-only.

#### Recommended policy semantics

- `warn`: never block, only warn/log.
- `balanced`: block high-confidence dangerous patterns.
- `strict`: block any policy hit.

#### `HOOK.md`

```md
---
name: security-runtime-guard
description: "Reference runtime guard hook for tool-call safety"
metadata:
  { "openclaw": { "emoji": "🛡️", "events": ["agent:before_tool_call"] } }
---

# security-runtime-guard

Reference implementation for runtime tool-call policy checks.
```

#### `handler.ts`

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

  event.cancel = true;
  event.cancelReason =
    mode === "strict"
      ? "Blocked by strict runtime policy"
      : "Blocked by balanced runtime policy (high-risk pattern)";
};

export default handler;
```

#### Operational note

If your current OpenClaw runtime is warn-only for tool-call hooks, this reference still works as observability-first policy (`warn` mode). Enforcement activates once cancel/veto is available.
```

## Reviewer Notes
- Keeps behavior backward-compatible.
- Encourages monitor -> enforce rollout.
- Aligned with install-time + runtime defense-in-depth guidance.
