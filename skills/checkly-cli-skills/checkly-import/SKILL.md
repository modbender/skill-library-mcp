---
name: checkly-import
description: Import existing Checkly checks from the web UI into code using npx checkly import plan. Use when migrating from UI-managed checks to Monitoring as Code, or pulling existing infrastructure into version control. Triggers on import checks, migrate to code, import from UI, checkly import.
---

# checkly import

Import existing checks from Checkly UI to code.

## Quick start

```bash
# Import all checks from your account
npx checkly import plan

# Review generated files
git diff

# Commit imported checks
git add .
git commit -m "Import existing monitoring checks"
```

## How it works

1. ✅ Connects to your Checkly account
2. ✅ Fetches all existing checks
3. ✅ Generates TypeScript/JavaScript code
4. ✅ Creates directory structure
5. ✅ Writes files to disk

## Workflow

### 1. Prepare project

```bash
# Create new project if needed
npm create checkly@latest
cd my-monitoring-project

# Or use existing project
cd existing-project
npm install --save-dev checkly
```

### 2. Run import

```bash
npx checkly import plan
```

**Output:**
```
Importing checks from account "Acme Corp"...

Found 15 checks to import:
  - 8 API checks
  - 5 Browser checks
  - 2 Heartbeat monitors

Generating files...
  ✓ __checks__/api-status.check.ts
  ✓ __checks__/homepage.spec.ts
  ✓ __checks__/login.spec.ts
  ...

Import complete! Next steps:
  1. Review generated files
  2. Test locally: npx checkly test
  3. Commit to version control
```

### 3. Review imported code

```bash
# Review what was generated
git status
git diff

# Test imported checks
npx checkly test
```

### 4. Sync with UI

```bash
# Deploy to sync state
npx checkly deploy --force
```

## Post-import workflow

### Option 1: Keep UI and code in sync

```bash
# Deploy keeps checks updated from code
npx checkly deploy --force
```

### Option 2: Disable UI management

After import, manage everything from code:
1. Import existing checks
2. Deploy from code
3. Disable UI editing (Checkly account settings)
4. All changes via code + CI/CD

## Troubleshooting

### Import conflicts

If you have existing check files:

```bash
# Backup existing
git commit -m "Backup before import"

# Import
npx checkly import plan

# Resolve conflicts manually
git diff
```

### Missing dependencies

Generated code may reference packages:

```bash
npm install @playwright/test
```

## Related Skills

- See `checkly-deploy` to deploy imported checks
- See `checkly-test` to validate imported checks
