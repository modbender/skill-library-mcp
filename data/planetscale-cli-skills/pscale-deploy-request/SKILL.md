---
name: pscale-deploy-request
description: Create, review, deploy, and revert schema changes via deploy requests. Use when deploying schema migrations to production, reviewing database changes before deployment, managing deploy request lifecycle, or reverting deployed changes. Essential for safe production schema deployments. Triggers on deploy request, schema deployment, deploy schema, review deployment, revert deployment, production migration.
---

# pscale deploy-request

Create, review, diff, revert, and manage deploy requests for schema changes.

## Common Commands

```bash
# Create deploy request from branch
pscale deploy-request create <database> <branch-name>

# List deploy requests
pscale deploy-request list <database>

# Show deploy request details
pscale deploy-request show <database> <number>

# View deploy request diff
pscale deploy-request diff <database> <number>

# Deploy (apply changes)
pscale deploy-request deploy <database> <number>

# Close without deploying
pscale deploy-request close <database> <number>

# Revert deployed changes
pscale deploy-request revert <database> <number>
```

## Workflows

### Complete Schema Migration (Recommended)

This is the safest way to deploy schema changes to production:

```bash
# 1. Create development branch
pscale branch create my-database feature-schema-v2 --from main

# 2. Make schema changes
pscale shell my-database feature-schema-v2
# ... execute ALTER TABLE, etc.

# 3. Review changes locally
pscale branch diff my-database feature-schema-v2

# 4. Create deploy request
pscale deploy-request create my-database feature-schema-v2

# 5. Review deploy request diff
pscale deploy-request diff my-database 1

# 6. Deploy to production
pscale deploy-request deploy my-database 1

# 7. Verify deployment
pscale deploy-request show my-database 1
```

### Review Before Deploy

```bash
# List pending deploy requests
pscale deploy-request list <database> --state open

# Show details
pscale deploy-request show <database> <number>

# View schema diff
pscale deploy-request diff <database> <number>

# Deploy if approved
pscale deploy-request deploy <database> <number>
```

### Revert Deployment

If a deployed schema change causes issues:

```bash
# View deployment status
pscale deploy-request show <database> <number>

# Revert the deployment
pscale deploy-request revert <database> <number>

# Verify revert
pscale deploy-request show <database> <number>
```

## Decision Trees

### Should I deploy or close?

```
Deploy request ready?
├─ Schema changes tested → Deploy
├─ Changes need revision → Close and create new DR from updated branch
├─ Changes no longer needed → Close
└─ Breaking changes detected → Close, fix in branch, create new DR
```

### Should I revert?

```
After deployment issues?
├─ Production errors caused by schema → Revert immediately
├─ Data integrity issues → Revert, then investigate
├─ Performance degradation → Revert if severe
└─ Minor issues / non-urgent → Leave deployed, fix forward
```

## Troubleshooting

### Deploy request creation fails

**Error:** "No schema changes detected"

**Cause:** Branch schema matches production

**Solution:**
```bash
# Verify schema diff exists
pscale branch diff <database> <branch-name>

# If no diff, make schema changes first
pscale shell <database> <branch-name>
```

### "Cannot deploy: conflicts detected"

**Cause:** Production schema changed since branch creation

**Solution:**
```bash
# Close conflicting deploy request
pscale deploy-request close <database> <number>

# Refresh branch schema
pscale branch refresh-schema <database> <branch-name>

# Create new deploy request
pscale deploy-request create <database> <branch-name>
```

### Deploy fails midway

**Error:** Deployment started but failed

**Solution:**
```bash
# Check deploy request status
pscale deploy-request show <database> <number>

# If partially deployed, may need to revert
pscale deploy-request revert <database> <number>

# Contact PlanetScale support for stuck deployments
```

### Cannot close deploy request

**Error:** "Deploy request is deployed"

**Cause:** Already deployed requests cannot be closed

**Solution:**
```bash
# Deployed requests can only be reverted
pscale deploy-request revert <database> <number>
```

## Deploy Request States

| State | Description | Actions Available |
|-------|-------------|-------------------|
| `open` | Pending deployment | deploy, close, diff, review |
| `in_progress` | Currently deploying | (wait for completion) |
| `complete` | Successfully deployed | revert, show |
| `closed` | Closed without deploying | (none - read-only) |
| `reverted` | Deployed then reverted | (none - read-only) |

## Related Skills

- **pscale-branch** - Create branches for deploy requests
- **drizzle-kit** - Generate migration SQL for schema changes
- **gitlab-cli-skills** - GitLab MR integration (link deploy request to MR)

## Best Practices

1. **Always review diff** before deploying (`pscale deploy-request diff`)
2. **Test schema in branch** before creating deploy request
3. **Use descriptive names** for branches (matches MR/issue number)
4. **Deploy during maintenance windows** for breaking changes
5. **Have rollback plan** - know how to revert
6. **Monitor after deployment** - watch for errors
7. **Clean up old deploy requests** - close stale ones

## Automation

See `scripts/deploy-schema-change.sh` for complete automation:

```bash
# Automated deploy workflow
./scripts/deploy-schema-change.sh \
  --database my-database \
  --branch feature-schema-v2 \
  --auto-approve
```

## Integration with Drizzle

Common pattern for Drizzle ORM users:

```bash
# 1. Edit your schema.sql file
# 2. Create PlanetScale branch
pscale branch create my-database <branch-name>

# 3. Apply schema changes
pscale shell my-database <branch-name> < schema.sql

# 4. Create deploy request
pscale deploy-request create my-database <branch-name>

# 5. Deploy
pscale deploy-request deploy my-database <number>

# 6. Pull schema back to Drizzle
pnpm drizzle-kit introspect

# 7. Review and apply generated schema
```

## References

See `references/commands.md` for complete `pscale deploy-request` command reference.
