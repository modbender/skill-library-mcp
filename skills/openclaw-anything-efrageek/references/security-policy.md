# OpenClaw Security Policy

Last verified: 2026-02-17.

## Purpose Constraint
This skill exists to operate OpenClaw safely as a CLI wrapper plus documentation aid.
It is not a blanket authorization for privileged or autonomous actions.

## Approval Model
- Low-risk read operations may run by default.
- High-risk operations require explicit user approval for each action.
- Do not chain high-risk actions into unattended workflows by default.

## High-risk Categories
- Shell execution features (`exec`) that can run arbitrary commands
- Elevated privilege flows
- Sub-agent delegation with inherited environment/context
- Plugin install from external sources
- Cron add/remove/force-run operations
- Browser automation on arbitrary remote sites
- Device pairing and sensor access (camera/audio/location)

## Required Controls
- Principle of least privilege
- Explicit, contextual consent before each high-risk step
- Prefer read-only checks before any mutating action
- Use trusted plugin sources only
- Keep gateway bound to loopback unless remote access is intentional

## Wrapper Enforcement
`bash scripts/openclaw.sh` blocks high-risk command groups unless:
- `OPENCLAW_WRAPPER_ALLOW_RISKY=1`

This opt-in is session-scoped and should be set only when required.
