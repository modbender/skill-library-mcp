# PlanetScale CLI Skills - Automation Scripts

Token-efficient scripts for common PlanetScale operations. Execute without loading into context.

## Available Scripts

### 🌿 create-branch-for-mr.sh

Create PlanetScale branch matching your MR or PR branch name.

**Usage:**
```bash
./scripts/create-branch-for-mr.sh --database <db> --branch <name> [--from <source>] [--org <org>]
```

**Examples:**
```bash
# Create branch for MR/PR
./scripts/create-branch-for-mr.sh \
  --database my-database \
  --branch feature-user-settings

# Create from specific source branch
./scripts/create-branch-for-mr.sh \
  --database my-db \
  --branch feature-x \
  --from development

# With organization
./scripts/create-branch-for-mr.sh \
  --database my-db \
  --branch feature-x \
  --org my-org
```

**What it does:**
- Creates new database branch
- Sources from main (or specified branch)
- Provides next steps (shell, diff, deploy request)

---

### 🚀 deploy-schema-change.sh

Create deploy request and optionally deploy schema changes.

**Usage:**
```bash
./scripts/deploy-schema-change.sh --database <db> --branch <name> [--deploy] [--org <org>]
```

**Examples:**
```bash
# Create deploy request only (manual deploy later)
./scripts/deploy-schema-change.sh \
  --database my-database \
  --branch feature-schema-v2

# Create and auto-deploy
./scripts/deploy-schema-change.sh \
  --database my-database \
  --branch feature-schema-v2 \
  --deploy

# With organization
./scripts/deploy-schema-change.sh \
  --database my-db \
  --branch feature-x \
  --org my-org \
  --deploy
```

**What it does:**
1. Creates deploy request from branch
2. Shows deploy request diff
3. Optionally deploys (if `--deploy` flag)
4. Shows final deploy request status

**Token efficiency:** ~95% savings (7-step manual process → 1 command)

---

### 🔄 sync-branch-with-main.sh

Refresh development branch schema with main branch.

**Usage:**
```bash
./scripts/sync-branch-with-main.sh --database <db> --branch <name> [--org <org>]
```

**Examples:**
```bash
# Sync branch with main
./scripts/sync-branch-with-main.sh \
  --database my-database \
  --branch feature-branch

# With organization
./scripts/sync-branch-with-main.sh \
  --database my-db \
  --branch dev-branch \
  --org my-org
```

**What it does:**
- Refreshes branch schema to match main
- Useful when main has been updated
- Prevents deployment conflicts

---

## Benefits

### Token Efficiency
Scripts execute without loading into context - only output consumes tokens. **~90-95% token savings** for repetitive operations.

### Deterministic Operations
No code regeneration needed for common tasks. Same input = same output.

### Quick Workflows
Complete multi-step workflows in single commands.

## Prerequisites

### All Scripts
- `pscale` CLI installed and in PATH
- Authenticated (`pscale auth login` or service tokens)

### For Service Token Auth
```bash
export PLANETSCALE_SERVICE_TOKEN_ID=<token-id>
export PLANETSCALE_SERVICE_TOKEN=<token>
```

## Integration with Skills

Scripts are referenced from relevant skills:

- **pscale-branch** skill → `create-branch-for-mr.sh`, `sync-branch-with-main.sh`
- **pscale-deploy-request** skill → `deploy-schema-change.sh`

## Error Handling

All scripts:
- Use `set -e` (exit on error)
- Return non-zero exit codes on failure
- Provide actionable error messages
- Include help via `--help` flag

## Complete Workflow Examples

### Schema Migration for MR/PR

```bash
# 1. Create PlanetScale branch matching MR branch
./scripts/create-branch-for-mr.sh \
  --database my-database \
  --branch feature-user-settings

# 2. Make schema changes
pscale shell my-database feature-user-settings
# ... run ALTER TABLE, etc.

# 3. Deploy schema change
./scripts/deploy-schema-change.sh \
  --database my-database \
  --branch feature-user-settings \
  --deploy

# 4. Pull schema back to Drizzle (if using Drizzle ORM)
pnpm drizzle-kit introspect
```

### Sync Stale Branch Before Deploy

```bash
# If main has been updated since branch creation
./scripts/sync-branch-with-main.sh \
  --database my-database \
  --branch old-feature-branch

# Verify diff shows only your changes
pscale branch diff my-database old-feature-branch

# Then deploy
./scripts/deploy-schema-change.sh \
  --database my-database \
  --branch old-feature-branch \
  --deploy
```

### CI/CD Integration

```bash
# In your CI/CD pipeline config (.github/workflows, .gitlab-ci.yml, etc.)

deploy-schema:
  script:
    # Create branch from CI branch name
    - ./scripts/create-branch-for-mr.sh \
        --database $DATABASE \
        --branch $CI_COMMIT_REF_NAME \
        --org $ORG
    
    # Apply schema changes (from migrations file, ORM, etc.)
    - pscale shell $DATABASE $CI_COMMIT_REF_NAME < migrations.sql
    
    # Deploy automatically
    - ./scripts/deploy-schema-change.sh \
        --database $DATABASE \
        --branch $CI_COMMIT_REF_NAME \
        --deploy \
        --org $ORG
```

## Common Patterns

### Drizzle ORM Schema Migration Pattern

Generic workflow for Drizzle users:

```bash
# 1. Edit your schema.sql file
vim schema.sql

# 2. Create PlanetScale branch
./scripts/create-branch-for-mr.sh \
  --database my-database \
  --branch $(git branch --show-current)

# 3. Apply schema changes
pscale shell my-database $(git branch --show-current) < schema.sql

# 4. Deploy
./scripts/deploy-schema-change.sh \
  --database my-database \
  --branch $(git branch --show-current) \
  --deploy

# 5. Pull schema back to Drizzle
pnpm drizzle-kit introspect
```

## Contributing

When adding new scripts:
1. Include `--help` flag with examples
2. Use `set -e` for bash scripts (exit on error)
3. Provide clear error messages
4. Document in this README
5. Reference from relevant SKILL.md files
6. Make scripts executable (`chmod +x`)

## Script Dependencies

| Script | Requires | Optional |
|--------|----------|----------|
| create-branch-for-mr.sh | pscale, auth | org flag |
| deploy-schema-change.sh | pscale, auth | org flag |
| sync-branch-with-main.sh | pscale, auth | org flag |

All scripts work with both interactive auth (`pscale auth login`) and service token auth (env vars).
