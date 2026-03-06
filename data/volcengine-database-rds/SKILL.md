---
name: volcengine-database-rds
description: Operate Volcengine RDS instances and database workflows. Use when users need provisioning guidance, connectivity checks, performance troubleshooting, or backup/restore procedures.
---

# volcengine-database-rds

Handle RDS tasks with safe operational order: inspect, validate, change, verify.

## Execution Checklist

1. Confirm engine type, region, and instance identifier.
2. Check connectivity, security rules, and parameter group.
3. Execute target operation (query, tune, backup, restore).
4. Return status, metrics, and next recommended action.

## Safety Rules

- Prefer snapshots before high-risk changes.
- Surface parameter drift before applying updates.
- Separate read-only diagnostics from write operations.

## References

- `references/sources.md`
