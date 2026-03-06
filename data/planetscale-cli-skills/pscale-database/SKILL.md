---
name: pscale-database
description: Create, list, show, delete, and manage PlanetScale databases. Use when creating new databases, listing available databases, viewing database details, deleting databases, or opening database shells. Triggers on database, create database, list databases, database shell, pscale shell.
---

# pscale database

Create, read, delete, and manage databases.

## Common Commands

```bash
# List all databases
pscale database list --org <org>

# Create database
pscale database create <database> --org <org>

# Show database details
pscale database show <database>

# Delete database
pscale database delete <database>

# Open database shell
pscale shell <database> <branch>
```

## Workflows

### Database Creation

```bash
# Create new database
pscale database create my-new-db --org my-org

# Create main branch (automatic)
# Create development branch
pscale branch create my-new-db development
```

### Database Shell Access

```bash
# Open shell to specific branch
pscale shell my-database main

# Execute SQL directly
pscale shell my-database main --execute "SHOW TABLES"

# Run SQL from file
pscale shell my-database main < schema.sql
```

## Troubleshooting

### Cannot create database

**Error:** "Organization limit reached"

**Solution:** Upgrade plan or delete unused databases

### Shell connection fails

**Error:** "Authentication failed"

**Solution:**
```bash
# Re-authenticate
pscale auth logout && pscale auth login

# Verify branch exists
pscale branch list <database>
```

## Related Skills

- **pscale-branch** - Manage database branches
- **pscale-password** - Create connection passwords for databases

## References

See `references/commands.md` for complete command reference.
