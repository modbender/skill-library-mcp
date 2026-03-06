# GitHub Actions + `vercel deploy --prebuilt` Guide

Build in GitHub Actions, deploy pre-built output to Vercel. Full control over caching, testing, and parallelism.

---

## Why This Pattern?

| Aspect | Vercel Native Build | GitHub Actions + Prebuilt |
|--------|-------------------|--------------------------|
| **Cache control** | Vercel-managed, per-branch | Full control, cross-branch |
| **Parallelism** | Sequential (build then deploy) | Parallel (test + build + lint) |
| **Build machines** | Standard or Turbo | GitHub-hosted or self-hosted runners |
| **Queue** | Shared build queue | No queue (unlimited Actions concurrency) |
| **Custom steps** | Limited (build command only) | Anything you want |
| **Cost** | Build minutes | GitHub Actions minutes (2,000 free/month) |

---

## Prerequisites

1. **Vercel CLI** installed in CI
2. **Vercel project linked** (you'll need project ID and org ID)
3. **Vercel token** for authentication

### Getting Credentials

```bash
# Install Vercel CLI locally
npm i -g vercel

# Link your project (creates .vercel/project.json)
vercel link

# Get your token from https://vercel.com/account/tokens
# Create a token with appropriate scope
```

You'll need these as GitHub secrets:
- `VERCEL_TOKEN` — your Vercel API token
- `VERCEL_ORG_ID` — from `.vercel/project.json`
- `VERCEL_PROJECT_ID` — from `.vercel/project.json`

---

## Production Deploy Workflow

```yaml
# .github/workflows/deploy-production.yml
name: Deploy to Production

on:
  push:
    branches: [main]

concurrency:
  group: production-deploy
  cancel-in-progress: false  # Don't cancel production deploys

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm test
      - run: pnpm lint

  deploy:
    runs-on: ubuntu-latest
    needs: test  # Only deploy if tests pass
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Install Vercel CLI
        run: pnpm add -g vercel

      - name: Pull Vercel environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build project
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy prebuilt output
        run: |
          DEPLOY_URL=$(vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }})
          echo "Deployed to: $DEPLOY_URL"
          echo "DEPLOY_URL=$DEPLOY_URL" >> $GITHUB_ENV
```

---

## Preview Deploy Workflow

```yaml
# .github/workflows/deploy-preview.yml
name: Deploy Preview

on:
  pull_request:
    types: [opened, synchronize, reopened]

concurrency:
  group: preview-${{ github.head_ref }}
  cancel-in-progress: true  # Cancel outdated preview builds

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v4

      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Install Vercel CLI
        run: pnpm add -g vercel

      - name: Pull Vercel environment
        run: vercel pull --yes --environment=preview --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build project
        run: vercel build --token=${{ secrets.VERCEL_TOKEN }}

      - name: Deploy prebuilt output
        id: deploy
        run: |
          DEPLOY_URL=$(vercel deploy --prebuilt --token=${{ secrets.VERCEL_TOKEN }})
          echo "url=$DEPLOY_URL" >> $GITHUB_OUTPUT

      - name: Comment PR with deploy URL
        uses: actions/github-script@v7
        with:
          script: |
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body: `🚀 Preview deployed: ${{ steps.deploy.outputs.url }}`
            });
```

---

## Advanced: Parallel Test + Build

Run tests and build simultaneously, only deploy if both pass:

```yaml
# .github/workflows/deploy-parallel.yml
name: Parallel Test & Deploy

on:
  push:
    branches: [main]

env:
  VERCEL_ORG_ID: ${{ secrets.VERCEL_ORG_ID }}
  VERCEL_PROJECT_ID: ${{ secrets.VERCEL_PROJECT_ID }}

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm test

  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile
      - run: pnpm lint

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pnpm/action-setup@v4
      - uses: actions/setup-node@v4
        with:
          node-version: 22
          cache: 'pnpm'
      - run: pnpm install --frozen-lockfile

      - name: Install Vercel CLI
        run: pnpm add -g vercel

      - name: Pull Vercel environment
        run: vercel pull --yes --environment=production --token=${{ secrets.VERCEL_TOKEN }}

      - name: Build project
        run: vercel build --prod --token=${{ secrets.VERCEL_TOKEN }}

      - name: Upload build artifact
        uses: actions/upload-artifact@v4
        with:
          name: vercel-output
          path: .vercel/output
          retention-days: 1

  deploy:
    runs-on: ubuntu-latest
    needs: [test, lint, build]  # All three must pass
    steps:
      - uses: actions/checkout@v4

      - name: Install Vercel CLI
        run: npm i -g vercel

      - name: Download build artifact
        uses: actions/download-artifact@v4
        with:
          name: vercel-output
          path: .vercel/output

      - name: Deploy prebuilt output
        run: |
          DEPLOY_URL=$(vercel deploy --prebuilt --prod --token=${{ secrets.VERCEL_TOKEN }})
          echo "Deployed to: $DEPLOY_URL"
```

---

## Caching Strategies

### pnpm Store Cache

The `actions/setup-node` with `cache: 'pnpm'` handles basic dependency caching. For more control:

```yaml
- name: Get pnpm store directory
  id: pnpm-cache
  run: echo "STORE_PATH=$(pnpm store path)" >> $GITHUB_OUTPUT

- uses: actions/cache@v4
  with:
    path: ${{ steps.pnpm-cache.outputs.STORE_PATH }}
    key: ${{ runner.os }}-pnpm-store-${{ hashFiles('**/pnpm-lock.yaml') }}
    restore-keys: |
      ${{ runner.os }}-pnpm-store-
```

### Framework Build Cache

Cache framework-specific build artifacts across runs:

```yaml
# SvelteKit
- uses: actions/cache@v4
  with:
    path: .svelte-kit
    key: ${{ runner.os }}-sveltekit-${{ hashFiles('src/**', 'svelte.config.js') }}
    restore-keys: |
      ${{ runner.os }}-sveltekit-

# Next.js
- uses: actions/cache@v4
  with:
    path: .next/cache
    key: ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-${{ hashFiles('src/**') }}
    restore-keys: |
      ${{ runner.os }}-nextjs-${{ hashFiles('**/package-lock.json') }}-
```

---

## Disabling Vercel's Git Integration

When using GitHub Actions for builds, you should disable Vercel's automatic Git-triggered builds to avoid duplicate deployments.

### Option 1: Disable in Vercel Dashboard

Project Settings → Git → uncheck "Auto-deploy" for all branches.

### Option 2: Ignored Build Step (Safer)

Keep the Git integration but skip all builds:

```json
// vercel.json
{
  "ignoreCommand": "exit 0"
}
```

This way Vercel still creates deployment records but doesn't run builds. Your GitHub Actions handle the actual building and deploying.

### Option 3: Selective

Only disable for specific branches:

```json
{
  "git": {
    "deploymentEnabled": {
      "main": false,
      "feature/*": false
    }
  }
}
```

---

## Troubleshooting

### "No Output Directory" Error

Make sure `vercel build` completed successfully and `.vercel/output/` exists before running `vercel deploy --prebuilt`.

### Environment Variables Missing

`vercel pull` downloads env vars into `.vercel/.env.*` files. Make sure this step runs before `vercel build`.

### Token Permissions

Create a Vercel token with sufficient scope:
- For personal projects: any token works
- For team projects: token must belong to a team member with deploy permissions
- Scope the token to the specific team if possible

### Build Output Too Large

GitHub Actions artifacts have a 500MB limit (10GB for paid plans). If your `.vercel/output` is huge:
- Check for unnecessary files in the output
- Use `.vercelignore` to exclude test fixtures, docs, etc.
- Consider if all routes need to be serverless functions (prerender more)

### Concurrent Deployments

Use GitHub Actions `concurrency` groups to prevent race conditions:

```yaml
concurrency:
  group: deploy-${{ github.ref }}
  cancel-in-progress: true  # For previews
  # cancel-in-progress: false  # For production
```
