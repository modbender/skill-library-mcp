# TypeScript QC Profile

## Project Detection

TypeScript project if any of these exist:
- `tsconfig.json`
- `package.json` with TypeScript in dependencies
- `.ts` or `.tsx` files

## Monorepo Detection

Check for monorepo structure in order:

### pnpm Workspaces
```bash
if [ -f "pnpm-workspace.yaml" ]; then
    echo "pnpm monorepo detected"
    # List workspaces
    pnpm list --recursive --depth 0
fi
```

### npm/Yarn Workspaces
```bash
if grep -q '"workspaces"' package.json 2>/dev/null; then
    echo "npm/yarn workspaces detected"
    # List packages
    jq -r '.workspaces[]' package.json
fi
```

### Nx
```bash
if [ -f "nx.json" ]; then
    echo "Nx monorepo detected"
    # List projects
    npx nx show projects
fi
```

### Turborepo
```bash
if [ -f "turbo.json" ]; then
    echo "Turborepo detected"
    # List packages
    ls -d packages/*/package.json apps/*/package.json 2>/dev/null
fi
```

### Lerna (legacy)
```bash
if [ -f "lerna.json" ]; then
    echo "Lerna monorepo detected"
    npx lerna list
fi
```

### Monorepo QC Strategy

For monorepos, run QC per package or use workspace-aware commands:

```bash
# pnpm - run in all packages
pnpm -r run lint
pnpm -r run test

# Nx - run affected only
npx nx affected --target=lint
npx nx affected --target=test

# Turborepo
npx turbo run lint test

# Changed packages only (CI mode)
pnpm -r --filter "...[origin/main]" run test
```

## Test Runner Detection

Check in order:
1. `vitest.config.ts` or `vitest` in devDependencies → `npx vitest`
2. `jest.config.ts/js` or `jest` in devDependencies → `npx jest`
3. `package.json` → `scripts.test` → use that command
4. Fallback: `npm test`

### With Coverage
```bash
# Vitest
npx vitest --coverage

# Jest
npx jest --coverage --coverageReporters=json-summary

# Parse coverage
cat coverage/coverage-summary.json | jq '.total.lines.pct'
```

## Phase 3: Static Analysis with eslint

### Standard Check

Use project's eslint config if available:
```bash
npx eslint . --format json --output-file /tmp/eslint-report.json
```

If no eslint config exists:
```bash
npx eslint . --no-eslintrc \
  --parser @typescript-eslint/parser \
  --plugin @typescript-eslint \
  --rule '{"no-unused-vars":"warn","no-console":"warn","no-debugger":"error"}'
```

### Fix Mode
```bash
npx eslint . --fix
```

### Monorepo eslint
```bash
# Root config for shared rules
npx eslint . --config .eslintrc.js

# Or per-package
pnpm -r run lint

# Nx
npx nx run-many --target=lint --all
```

### Key Rules to Check

| Rule | What it catches |
|------|-----------------|
| `no-unused-vars` | Unused variables/imports |
| `no-console` | console.log in production code |
| `no-debugger` | debugger statements |
| `@typescript-eslint/no-explicit-any` | Untyped `any` usage |
| `@typescript-eslint/no-non-null-assertion` | Unsafe `!` assertions |
| `@typescript-eslint/strict-boolean-expressions` | Truthy/falsy bugs |

## Phase 3.5: Type Checking

```bash
# Full type check without emit
npx tsc --noEmit

# Specific project in monorepo
npx tsc --project packages/core/tsconfig.json --noEmit

# All projects (Nx)
npx nx run-many --target=typecheck --all

# Parse errors
npx tsc --noEmit 2>&1 | grep -c "error TS"
```

### Strict Mode Verification

Check if strict mode is enabled:
```bash
grep -q '"strict": true' tsconfig.json && echo "Strict mode enabled" || echo "Warning: strict mode disabled"
```

## Smoke Test Patterns

### API Endpoint (Express/Fastify)
```typescript
import request from 'supertest';
import { app } from './app';

async function smokeTestApi() {
  const res = await request(app).get('/health');
  if (res.status !== 200) throw new Error('Health check failed');
  
  const apiRes = await request(app).get('/api/v1/version');
  if (apiRes.status !== 200) throw new Error('API version failed');
  
  return 'PASS';
}
```

### Module Import
```typescript
async function smokeTestImports() {
  const { MainService } = await import('./services/main');
  const service = new MainService();
  if (!service) throw new Error('MainService instantiation failed');
  return 'PASS';
}
```

### Database Connection
```typescript
import { createConnection } from './db';

async function smokeTestDatabase() {
  const conn = await createConnection(':memory:');
  await conn.query('SELECT 1');
  await conn.close();
  return 'PASS';
}
```

### React Component (without DOM)
```typescript
import { renderToString } from 'react-dom/server';
import { App } from './App';

function smokeTestReactApp() {
  const html = renderToString(<App />);
  if (!html.includes('<div')) throw new Error('App render failed');
  return 'PASS';
}
```

### CLI Tool
```typescript
import { execSync } from 'child_process';

function smokeTestCli() {
  const output = execSync('npx my-cli --help', { encoding: 'utf8' });
  if (!output.includes('Usage:')) throw new Error('CLI help failed');
  return 'PASS';
}
```

## Build Check

```bash
# TypeScript compilation
npx tsc --noEmit

# Full build
npm run build

# Check for build output
ls -la dist/ build/ out/ 2>/dev/null

# Monorepo build
npx turbo run build
# or
npx nx run-many --target=build --all
```

Record: build success/failure, total errors, total warnings.

## Package Audit

```bash
# npm
npm audit --json

# pnpm
pnpm audit --json

# yarn
yarn audit --json
```

Report: total vulnerabilities by severity (critical/high/moderate/low).

## UI Verification

### React/Vue Build
```bash
# Should complete without error
npm run build

# Check for type errors in components
npx tsc --project tsconfig.json --noEmit
```

### Next.js
```bash
# Build and export
npx next build

# Check for static issues
npx next lint
```

### Storybook (if present)
```bash
# Build storybook (catches import/render errors)
npx storybook build --quiet
```

## Changed Files Only (CI Mode)

For pull request CI, only check changed files:

```bash
# Get changed TypeScript files
CHANGED=$(git diff --name-only origin/main...HEAD -- '*.ts' '*.tsx')

# Lint only changed files
echo "$CHANGED" | xargs npx eslint

# Type check is always full project (TypeScript needs full context)
npx tsc --noEmit
```
