---
name: pscale-backup
description: Create, list, show, and delete branch backups. Use when creating database backups, restoring from backups, managing backup lifecycle, or scheduling automated backups. Triggers on backup, restore, database backup, backup branch.
---

# pscale backup

Create, list, show, and delete branch backups.

## Common Commands

```bash
# Create backup
pscale backup create <database> <branch>

# List backups
pscale backup list <database> <branch>

# Show backup details
pscale backup show <database> <branch> <backup-id>

# Delete backup
pscale backup delete <database> <branch> <backup-id>
```

## Workflows

### Backup Before Migration

```bash
# Create backup before schema changes
pscale backup create my-database main

# Proceed with migration
pscale deploy-request deploy my-database 1

# If issues, restore from backup (contact PlanetScale support)
```

## Related Skills

- **pscale-branch** - Backup specific branches
- **pscale-deploy-request** - Backup before deploying

## References

See `references/commands.md` for complete command reference.
