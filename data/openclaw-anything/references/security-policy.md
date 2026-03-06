# OpenClaw Security Policy

Default stance: least privilege. Do not chain high-risk actions unattended.

## Low-risk (default)
status · doctor · version · health · logs · dashboard · config read · docs search
channels list/status · models list/status · memory status/search · skills list
plugins list/info/doctor · hooks list/info/check · sandbox list/explain
sessions · approvals get · system presence/heartbeat

## High-risk Categories

| Category | Commands | Gate |
|----------|----------|------|
| Shell/Exec | `exec` tool, nodes invoke/run | Full |
| Device/Sensor | pairing, devices approve/rotate/revoke, camera snap/clip, screen record, location get | Full |
| Browser | All browser interaction commands, evaluate (JS exec) | Full |
| Automation | cron add/edit/rm/run, webhooks gmail, dns setup --apply | Full |
| Plugin/Hook | plugins install/enable, hooks install/enable | Sub-cmd |
| Security | security audit --fix | Full |
| Secrets | secrets apply | Sub-cmd |
| Sandbox | sandbox recreate | Sub-cmd |

## Wrapper Enforcement
`scripts/openclaw.sh` blocks high-risk via `OPENCLAW_WRAPPER_ALLOW_RISKY=1` (session-scoped).

Granular gating:
- `plugin`: only `install` and `enable` gated
- `hooks`: only `install` and `enable` gated
- `secrets`: only `apply` gated
- `sandbox`: only `recreate` gated
- All others in table above: fully gated

## Required Controls
- Explicit consent per high-risk step
- Prefer read-only before mutating
- Gateway: keep loopback unless remote intentional
- Verify node identity before approving
- Use `security audit` periodically
