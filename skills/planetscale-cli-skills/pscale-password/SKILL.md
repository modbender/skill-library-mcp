---
name: pscale-password
description: Create, list, and delete branch connection passwords. Use when creating connection strings for applications, managing database credentials, generating passwords for local development, or rotating credentials. Triggers on password, connection string, database credentials, create password.
---

# pscale password

Create, list, and delete branch passwords for database connections.

## Common Commands

```bash
# Create password
pscale password create <database> <branch> <password-name>

# List passwords
pscale password list <database> <branch>

# Delete password
pscale password delete <database> <branch> <password-id>
```

## Workflows

### Application Connection

```bash
# Create password for production app
pscale password create my-database main production-app

# Returns connection string:
# mysql://username:password@host/database

# Use in application environment variables
export DATABASE_URL="mysql://..."
```

### Local Development

```bash
# Create temporary password for local dev
pscale password create my-db main local-dev

# Delete when done
pscale password delete my-db main <password-id>
```

## Troubleshooting

### Password not working

**Solution:** Delete and recreate password (may have expired)

```bash
pscale password list <database> <branch>
pscale password delete <database> <branch> <old-id>
pscale password create <database> <branch> new-name
```

## Related Skills

- **pscale-service-token** - For CI/CD authentication (preferred over passwords)
- **pscale-database** - Database management

## References

See `references/commands.md` for complete command reference.
