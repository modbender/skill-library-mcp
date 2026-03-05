---
name: checkly-playwright
description: Configure Playwright test suites with Checkly including playwright.config.ts integration, multiple projects, and full test suite deployment. Use when running complete Playwright test suites as checks, managing multiple browsers, or leveraging Playwright's full feature set. Triggers on playwright config, test suite, playwright project, multiple browsers.
---

# checkly playwright

Run full Playwright test suites as Checkly checks.

## Playwright Check Suite

Deploy entire Playwright test suite:

```typescript
// checkly.config.ts
export default defineConfig({
  checks: {
    playwrightConfigPath: './playwright.config.ts',
    playwrightChecks: [
      {
        name: 'E2E Test Suite',
        frequency: 10,
        testCommand: 'npm run test:e2e',
        locations: ['us-east-1', 'eu-west-1'],
        tags: ['e2e'],
      },
    ],
  },
})
```

## Playwright configuration

```typescript
// playwright.config.ts
import { defineConfig } from '@playwright/test'

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  projects: [
    { name: 'chromium', use: { browserName: 'chromium' } },
    { name: 'firefox', use: { browserName: 'firefox' } },
    { name: 'webkit', use: { browserName: 'webkit' } },
  ],
})
```

## Multiple projects

```typescript
playwrightChecks: [
  {
    name: 'Chromium Tests',
    testCommand: 'npx playwright test --project=chromium',
    frequency: 5,
  },
  {
    name: 'Cross-Browser Tests',
    testCommand: 'npx playwright test',
    frequency: 30,
  },
]
```

## Related Skills

- See `checkly-checks` for individual browser checks
- See `checkly-test` for testing Playwright checks
