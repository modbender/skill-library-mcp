---
name: pscale-branch
description: Create, delete, promote, diff, and manage PlanetScale database branches. Use when creating development branches for schema changes, viewing schema diffs, promoting branches to production, or managing branch lifecycle. Essential for schema migration workflows. Triggers on branch, create branch, schema diff, promote branch, development branch, database branch.
---

# pscale branch

Create, delete, diff, and manage database branches.

## Common Commands

```bash
# Create branch from main
pscale branch create <database> <branch-name>

# Create branch from specific source
pscale branch create <database> <branch-name> --from <source-branch>

# List all branches
pscale branch list <database>

# Show branch details
pscale branch show <database> <branch-name>

# View schema diff
pscale branch diff <database> <branch-name>

# View schema
pscale branch schema <database> <branch-name>

# Delete branch
pscale branch delete <database> <branch-name>

# Promote to production
pscale branch promote <database> <branch-name>
```

## Workflows

### Schema Migration Workflow (Standard)

```bash
# 1. Create development branch
pscale branch create my-database feature-migration --from main

# 2. Make schema changes (via shell, ORM, or direct SQL)
pscale shell my-database feature-migration
# ... run ALTER TABLE, CREATE TABLE, etc.

# 3. View changes
pscale branch diff my-database feature-migration

# 4. Create deploy request (safer than direct promotion)
pscale deploy-request create my-database feature-migration

# 5. Deploy via deploy request (see pscale-deploy-request)
```

### Quick Branch for MR/PR

```bash
# Match PlanetScale branch to your MR/PR branch
BRANCH_NAME="feature-add-user-preferences"
pscale branch create my-database $BRANCH_NAME --from main
```

See `scripts/create-branch-for-mr.sh` for automation.

### Schema Comparison

```bash
# Compare branch schema with main
pscale branch diff <database> <branch-name>

# View full branch schema
pscale branch schema <database> <branch-name>

# Export schema to file
pscale branch schema <database> <branch-name> > schema.sql
```

### Branch Cleanup

```bash
# List all branches
pscale branch list <database>

# Delete merged/stale branches
pscale branch delete <database> <old-branch-name>
```

## Decision Trees

### Should I promote directly or use deploy request?

```
What's your environment?
├─ Production database → ALWAYS use deploy request (safe, reviewable)
├─ Pre-production database with team → Use deploy request (review workflow)
├─ Personal dev database → Direct promotion OK (but deploy request still safer)
└─ Experimental changes → Keep as branch, don't promote
```

### When to create a new branch?

```
What's your goal?
├─ Schema migration for feature → Create branch (from main)
├─ Testing schema changes → Create branch (isolated)
├─ Hotfix schema change → Create branch (from production)
├─ Experiment / spike → Create branch (delete after)
└─ Working on existing schema → Use existing branch
```

## Troubleshooting

### "Branch already exists"

**Solution:**
```bash
# Check existing branches
pscale branch list <database>

# Use different name or delete existing
pscale branch delete <database> <existing-branch>
```

### Schema diff shows no changes

**Causes:**
- No schema changes made yet
- Changes not committed in database session
- Comparing branch to itself

**Solution:**
```bash
# Verify schema was modified
pscale branch schema <database> <branch-name>

# Ensure you're in the right branch when making changes
pscale shell <database> <branch-name>
```

### Cannot delete branch

**Error:** "Branch is protected" or "Branch is a production branch"

**Solution:**
```bash
# Demote production branch first
pscale branch demote <database> <branch-name>

# Then delete
pscale branch delete <database> <branch-name>
```

### Branch creation fails

**Common causes:**
- Invalid branch name (spaces, special chars)
- Source branch doesn't exist
- Insufficient permissions

**Solution:**
```bash
# Use valid branch name (alphanumeric, hyphens, underscores)
pscale branch create <database> my-feature-branch --from main

# Verify source branch exists
pscale branch list <database> | grep main
```

## Related Skills

- **pscale-deploy-request** - Create deploy requests from branches (safer than direct promotion)
- **pscale-database** - Database management
- **drizzle-kit** - ORM-based schema migrations (generates SQL for pscale shell)
- **gitlab-cli-skills** - MR/PR integration (match branch names across tools)

## References

See `references/commands.md` for complete `pscale branch` command reference.

## Branch Lifecycle

```
main (production)
  │
  ├─ Create branch ──> feature-branch (development)
  │                         │
  │                         ├─ Make schema changes
  │                         ├─ Test changes
  │                         └─ Create deploy request
  │                               │
  └─ Deploy ←──────────────────────┘
```

## Best Practices

1. **Always create branches from main** for schema changes
2. **Use descriptive branch names** matching MR/PR numbers when applicable
3. **Run diff before deploy request** to review changes
4. **Delete merged branches** to keep branch list clean
5. **Use deploy requests** instead of direct promotion (reviewable, revertable)
6. **Test schema changes** in branch before deploying
