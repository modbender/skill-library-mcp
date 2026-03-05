# OpenClaw Mode Matrix

Use this matrix to choose the correct setup branch.

| Dimension | Local Mode | Hosted Mode |
|---|---|---|
| Primary path | Install + onboard on operator machine | Clone repo + provider deploy |
| Best for | Single operator, private workflows, rapid trial | Team/shared access, durable operations |
| Infra ownership | Local machine/WSL resources | Cloud account + provider runtime |
| Exposure defaults | Private-first | Provider ingress with explicit auth controls |
| Required profile | `local` | `hosted-fly`, `hosted-render`, `hosted-railway`, `hosted-hetzner`, `hosted-gcp` |
| Rollback model | Restore local config/state snapshot | Redeploy prior revision + restore persisted state |

## Decision Rules
1. If user wants minimal setup and no cloud account, prefer `local`.
2. If user needs always-on access, team usage, or managed ingress, prefer `hosted`.
3. If user has no rollback owner/runbook, block `prod` in either mode.

## Mode-Specific Hard Stops

### Local
- No profile validation pass for `local`
- Public exposure requested without gateway protections

### Hosted
- Provider-specific profile validation fails
- Persistent volume/state not configured before traffic
- Public ingress configured without token/auth boundaries
