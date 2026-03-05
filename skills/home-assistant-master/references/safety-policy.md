# Safety Policy (Home Assistant Master)

## Default posture
- Read-only unless user explicitly requests an action.
- Any write requires explicit confirmation.

## Risk tiers
- **Tier 0 (read-only):** states, history, traces, logs, diagnostics.
- **Tier 1 (low-risk writes):** lights/media/helpers/scripts/scenes.
- **Tier 2 (sensitive):** locks, alarms, garage, cameras, access controls.
- **Tier 3 (platform):** restart/reload/update/restore/backups.

## Mandatory controls
- Preview intended change before execution.
- Confirmation phrase for Tier 1+.
- Two-step confirmation for Tier 2/3.
- Post-action verification and audit-style summary.

## Deny-by-default examples
- Mass entity changes without scope confirmation.
- Security-disabling changes.
- Secret/token exposure.
