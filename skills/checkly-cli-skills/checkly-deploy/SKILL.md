---
name: checkly-deploy
description: Deploy Checkly checks to production with npx checkly deploy, including force deployment, preview changes, and CI/CD integration strategies. Use when deploying monitoring checks, updating production configuration, or integrating with deployment pipelines. Triggers on checkly deploy, deploy checks, production deployment, CI/CD deployment.
---

# checkly deploy

Deploy checks to Checkly cloud with `npx checkly deploy`.

## Quick start

```bash
# Deploy with confirmation prompt
npx checkly deploy

# Force deploy (skip prompt)
npx checkly deploy --force

# Preview changes without deploying
npx checkly validate
```

## How deployment works

`npx checkly deploy`:
1. ✅ Parses your project
2. ✅ Validates all checks
3. ✅ Bundles code and dependencies
4. ✅ Shows preview of changes
5. ⚠️  Asks for confirmation
6. ✅ Creates/updates resources in Checkly cloud
7. ✅ Schedules checks to run continuously

## Command reference

```bash
npx checkly deploy [options]
```

### Options

| Flag | Description |
|------|-------------|
| `--force, -f` | Skip confirmation prompt |
| `--config=<path>` | Path to checkly.config.ts |
| `--verify-runtime-dependencies` | Validate npm package compatibility |

## Deployment workflows

### Interactive deployment

```bash
npx checkly deploy

# Output:
# Parsing your project... done
# 
# Changes to be deployed:
#   + 2 checks to create
#   ~ 1 check to update
#   - 0 checks to delete
#
# Do you want to deploy? (y/N)
```

Type `y` to confirm, `n` to cancel.

### Force deployment (CI/CD)

```bash
npx checkly deploy --force

# No confirmation prompt
# Useful for automated pipelines
```

### Preview changes

```bash
# Validate without deploying
npx checkly validate

# Shows what would be deployed
# Catches errors before deployment
```

## CI/CD integration

### GitHub Actions

```yaml
name: Deploy Checks

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - name: Install dependencies
        run: npm ci
      
      - name: Test checks
        env:
          CHECKLY_API_KEY: ${{ secrets.CHECKLY_API_KEY }}
          CHECKLY_ACCOUNT_ID: ${{ secrets.CHECKLY_ACCOUNT_ID }}
        run: npx checkly test
      
      - name: Deploy checks
        env:
          CHECKLY_API_KEY: ${{ secrets.CHECKLY_API_KEY }}
          CHECKLY_ACCOUNT_ID: ${{ secrets.CHECKLY_ACCOUNT_ID }}
        run: npx checkly deploy --force
```

### GitLab CI

```yaml
deploy-checks:
  stage: deploy
  only:
    - main
  script:
    - npm ci
    - npx checkly test
    - npx checkly deploy --force
  variables:
    CHECKLY_API_KEY: $CHECKLY_API_KEY
    CHECKLY_ACCOUNT_ID: $CHECKLY_ACCOUNT_ID
```

### Deploy on application deployment

```bash
#!/bin/bash
# deploy-app-and-monitoring.sh

# Deploy application
./deploy-app.sh

# Deploy updated monitoring checks
npx checkly deploy --force

echo "✅ Application and monitoring deployed"
```

## Deployment strategies

### Test before deploy

```bash
# Validate locally first
npx checkly test

# Deploy only if tests pass
if [ $? -eq 0 ]; then
  npx checkly deploy --force
fi
```

### Staged deployment

```bash
# 1. Deploy to staging project
CHECKLY_ACCOUNT_ID=$STAGING_ACCOUNT npx checkly deploy --force

# 2. Run smoke tests
npm run smoke-tests

# 3. Deploy to production
CHECKLY_ACCOUNT_ID=$PROD_ACCOUNT npx checkly deploy --force
```

### Feature branch testing

```yaml
# GitHub Actions - test on PRs, deploy on main
on:
  pull_request:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npx checkly test  # Test on all branches
        env:
          CHECKLY_API_KEY: ${{ secrets.CHECKLY_API_KEY }}
          CHECKLY_ACCOUNT_ID: ${{ secrets.CHECKLY_ACCOUNT_ID }}
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'  # Deploy only on main
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - run: npm ci
      - run: npx checkly deploy --force
        env:
          CHECKLY_API_KEY: ${{ secrets.CHECKLY_API_KEY }}
          CHECKLY_ACCOUNT_ID: ${{ secrets.CHECKLY_ACCOUNT_ID }}
```

## What gets deployed

### Created resources

- ✅ New checks (API, Browser, Multi-Step, Monitors)
- ✅ Check groups
- ✅ Alert channel subscriptions
- ✅ Private location assignments
- ✅ Retry strategies
- ✅ Environment variables

### Updated resources

- ✅ Check configuration changes
- ✅ Schedule changes (frequency, locations)
- ✅ Code changes (for checks with scripts)
- ✅ Alert channel assignments

### NOT deployed

- ❌ Alert channel definitions (configure in UI)
- ❌ Private location infrastructure (configure in UI)
- ❌ Account-level settings
- ❌ Team/user management

## Deployment preview

Before deployment, Checkly shows a summary:

```
Changes to be deployed:

+ Create checks:
  • homepage-check (Browser)
  • api-status-check (API)

~ Update checks:
  • login-flow-check (Browser)
    - frequency: 10 → 5 minutes
    - locations: +eu-west-1

- Delete checks:
  (none)

+ Create groups:
  • critical-checks

~ Update groups:
  (none)
```

## Troubleshooting

### "No changes to deploy"

**Cause**: All checks already deployed and up-to-date

**Solution**: This is normal. Only deploy when you have changes.

### "Cannot deploy: validation errors"

**Solution**:
```bash
# Check validation errors
npx checkly validate

# Fix errors in your code
# Re-run validate until no errors

# Deploy
npx checkly deploy
```

### "Quota exceeded" errors

**Cause**: Account plan limits reached (checks, locations, etc.)

**Solution**:
- Upgrade your Checkly plan
- Delete unused checks in UI
- Contact Checkly support

### Deploy hangs or times out

**Solution**:
```bash
# Check network connectivity
curl https://api.checklyhq.com/health

# Verify authentication
npx checkly whoami

# Try again with verbose output
npx checkly deploy --force
```

## Related Skills

- See `checkly-test` to test before deploying
- See `checkly-import` to import existing checks
- See `checkly-checks` for check creation
- See `checkly-auth` for CI/CD authentication
