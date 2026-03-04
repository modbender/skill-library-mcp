# Setup — Cypress

Read this when the project doesn't have Cypress configured or when starting fresh.

## Your Attitude

You're helping set up reliable E2E testing. The goal is tests that catch real bugs without being flaky. Keep it practical — start with the most valuable tests first.

## Priority Order

### 1. First: Project Detection

Check if Cypress exists:
```bash
# Check for existing setup
ls cypress.config.ts cypress.config.js 2>/dev/null
cat package.json | grep cypress
```

If not installed:
```bash
npm install -D cypress
npx cypress open  # First run creates folder structure
```

### 2. Then: Configuration

Create or update `cypress.config.ts`:
- Set `baseUrl` to avoid hardcoded URLs
- Configure reasonable timeouts
- Enable retries for CI stability
- Set viewport for consistent rendering

### 3. Then: Support Structure

Set up `cypress/support/commands.ts`:
- Add `getByTestId` helper command
- Add `login` command if auth exists
- TypeScript declarations for custom commands

### 4. Finally: First Test

Write one simple smoke test:
```typescript
// cypress/e2e/smoke.cy.ts
describe('App', () => {
  it('loads homepage', () => {
    cy.visit('/')
    cy.get('body').should('be.visible')
  })
})
```

Run it to verify setup works.

## What You're Building

As you set up:
- Configuration tailored to their stack (React, Vue, Next.js, etc.)
- Selector strategy that matches their codebase
- Custom commands for their common flows (login, navigation)
- CI configuration if they deploy

## When Setup is "Done"

Once you have:
1. Cypress installed and configured
2. Support file with basic commands
3. One passing test

...you're ready to write real tests. Build the test suite incrementally.

## CI Integration

If they use CI, add after initial setup:
- GitHub Actions: `.github/workflows/cypress.yml`
- GitLab CI: `.gitlab-ci.yml` with cypress job
- See `ci.md` for templates
