---
name: oc-full-ops-audit-recipe
description: End-to-end OpenClaw audit and remediation recipe for gateway, channels, nodes, security, and memory sync.
---

# OC Full Ops Audit Recipe

## Goal
Provide a repeatable audit workflow that ends with verified fixes and documented memory updates.

## Audit flow
1. Baseline: status/health/gateway/security/nodes.
2. Classify findings: critical, warning, info.
3. Apply fixes in risk order with rollback points.
4. Re-run checks and compare deltas.
5. Write outcomes to daily memory + shared memory.

## Deliverables
- Audit summary table
- Fix actions and verification
- Residual risks and priority plan

## Usage notes
- Prefer read-only checks first.
- Group disruptive changes behind explicit approval.
- Keep outputs concise and operational.
