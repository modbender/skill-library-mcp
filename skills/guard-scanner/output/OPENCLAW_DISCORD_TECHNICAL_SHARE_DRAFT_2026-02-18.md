# OpenClaw Community Technical Share (no-promo)

## Title
Runtime Security Hook Pattern for OpenClaw (`agent:before_tool_call`) — warn-first, backward-compatible

## Body
Sharing an implementation pattern we validated in production-like workflows.

### Context
- Install-time static scan and runtime hook checks are complementary.
- Current OpenClaw hook runtime is effectively warn-first for tool-call risk controls.

### Minimal schema extension proposal
```ts
interface InternalHookEvent {
  cancel?: boolean;
  cancelReason?: string;
  policyMode?: "warn" | "balanced" | "strict";
}
```

### Recommended mode semantics
- `warn`: append messages/log only
- `balanced`: cancel HIGH/CRITICAL matches
- `strict`: cancel any policy hit

### Reference hook structure
- `HOOK.md` with `events: ["agent:before_tool_call"]`
- `handler.ts` reads tool-call context, applies policy, emits warning/cancel fields

### Why this helps
- Backward-compatible by default
- Enables gradual rollout from observability to enforcement
- Matches practical security operation: monitor -> tune -> enforce

### Validation status
- Local regression tests passing (56/56)
- Docs-ready draft prepared: `projects/guard-scanner/docs/OPENCLAW_HOOK_SCHEMA_REFERENCE_DRAFT.md`

If maintainers agree on the direction, this can be shipped as docs reference first, then runtime enforcement once cancel support is available.
