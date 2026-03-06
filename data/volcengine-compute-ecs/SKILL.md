---
name: volcengine-compute-ecs
description: Manage Volcengine ECS instances and related resources. Use when users need instance inventory, lifecycle operations, troubleshooting, or automation templates for ECS.
---

# volcengine-compute-ecs

Operate ECS resources safely with clear scope, dry-run style checks, and auditable output.

## Execution Checklist

1. Confirm region, account scope, and instance filters.
2. Query inventory before mutating operations.
3. Execute lifecycle actions (start/stop/reboot) only with explicit target IDs.
4. Return action summary with instance IDs and status.

## Safety Rules

- Prefer read-only commands first.
- Batch operations by region and tag.
- Record pre/post status for rollback.

## References

- `references/sources.md`
