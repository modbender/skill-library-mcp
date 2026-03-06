---
name: volcengine-network-dns
description: DNS record management on Volcengine networking services. Use when users need zone record query/update, traffic routing changes, or DNS propagation troubleshooting.
---

# volcengine-network-dns

Manage DNS records with strict change scoping and verification steps.

## Execution Checklist

1. Confirm domain zone, record type, and target value.
2. Query existing records before modifications.
3. Apply add/update/delete operation with TTL constraints.
4. Validate propagation using authoritative and recursive checks.

## Safety Rules

- Avoid blind overwrite; diff against existing records.
- Keep rollback values in output.
- Minimize TTL before migration windows.

## References

- `references/sources.md`
