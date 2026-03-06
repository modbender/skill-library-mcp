---
name: Cypress
slug: cypress
version: 1.0.0
homepage: https://clawic.com/skills/cypress
description: Write reliable E2E and component tests with Cypress avoiding flaky selectors, race conditions, and CI failures.
metadata: {"clawdbot":{"emoji":"🌲","requires":{"bins":["npx"]},"os":["linux","darwin","win32"]}}
---

## Setup

On first use, read `setup.md` for integration guidelines.

## When to Use

User needs E2E tests, component tests, or API tests with Cypress. Agent writes tests, debugs flaky specs, configures CI/CD, and creates custom commands.

## Architecture

Project tests live in the standard Cypress structure:

```
cypress/
├── e2e/              # E2E test specs
├── component/        # Component tests (if enabled)
├── fixtures/         # Test data JSON files
├── support/
│   ├── commands.ts   # Custom commands
│   ├── e2e.ts        # E2E support file
│   └── component.ts  # Component support file
└── downloads/        # Downloaded files during tests
cypress.config.ts     # Main configuration
```

## Quick Reference

| Topic | File |
|-------|------|
| Setup process | `setup.md` |
| Memory template | `memory-template.md` |
| Selectors & queries | `selectors.md` |
| Custom commands | `commands.md` |
| Network & API | `network.md` |
| CI/CD configuration | `ci.md` |

## Core Rules

### 1. Selectors: data-testid First
```typescript
// ✅ Resilient — survives refactors
cy.get('[data-testid="submit-btn"]')
cy.get('[data-cy="user-list"]')

// ❌ Fragile — breaks on style/structure changes
cy.get('.btn-primary.submit')
cy.get('#root > div > form > button:nth-child(3)')
cy.get('button').contains('Submit')  // OK for text, not structure
```

**Priority order:** `data-testid` > `data-cy` > `aria-*` > text content > CSS selectors.

### 2. Never Use Fixed Waits
```typescript
// ❌ Flaky and slow
cy.wait(3000)
cy.get('.loader').should('exist')
cy.wait(2000)

// ✅ Wait for actual state
cy.get('.loader').should('not.exist')
cy.get('[data-testid="results"]').should('be.visible')
cy.intercept('GET', '/api/users').as('getUsers')
cy.wait('@getUsers')
```

### 3. Intercept Network Requests
```typescript
// Setup intercepts BEFORE triggering actions
cy.intercept('POST', '/api/login', { statusCode: 200, body: { token: 'abc' } }).as('login')
cy.get('[data-testid="login-btn"]').click()
cy.wait('@login')
```

### 4. One Assertion Focus per Test
```typescript
// ✅ Clear failure message
it('shows error on invalid email', () => {
  cy.get('[data-testid="email"]').type('invalid')
  cy.get('[data-testid="submit"]').click()
  cy.get('[data-testid="email-error"]').should('contain', 'Valid email required')
})

// ❌ Multiple concerns — unclear which failed
it('validates the entire form', () => {
  // Tests 5 different validation rules
})
```

### 5. Commands for Repeated Actions
```typescript
// cypress/support/commands.ts
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.session([email, password], () => {
    cy.visit('/login')
    cy.get('[data-testid="email"]').type(email)
    cy.get('[data-testid="password"]').type(password)
    cy.get('[data-testid="submit"]').click()
    cy.url().should('include', '/dashboard')
  })
})

// Usage
cy.login('user@example.com', 'password123')
```

### 6. Fixtures for Test Data
```json
// cypress/fixtures/user.json
{
  "validUser": { "email": "test@example.com", "password": "Test123!" },
  "adminUser": { "email": "admin@example.com", "password": "Admin123!" }
}
```

```typescript
cy.fixture('user').then((users) => {
  cy.login(users.validUser.email, users.validUser.password)
})
```

### 7. Isolation: Reset State Before Tests
```typescript
beforeEach(() => {
  cy.intercept('GET', '/api/notifications', { body: [] })
  cy.clearCookies()
  cy.clearLocalStorage()
  // Or: cy.task('db:seed') if using database reset
})
```

## Common Traps

| Trap | Consequence | Fix |
|------|-------------|-----|
| `cy.wait(ms)` fixed delays | Flaky tests, slow CI | Use `cy.intercept().as()` + `cy.wait('@alias')` |
| CSS selectors for actions | Break on redesign | Use `data-testid` attributes |
| Test interdependence | One failure cascades | Each test must setup its own state |
| Asserting too early | False positives | Chain `.should()` to auto-retry |
| Forgetting `baseUrl` | Hardcoded URLs everywhere | Set `baseUrl` in config |
| Skipping viewport tests | Mobile bugs in prod | Add `cy.viewport()` tests |
| Ignoring retry-ability | Flaky assertions | Use Cypress queries, not jQuery |

## Debugging

### Time Travel
Click any command in the Command Log to see DOM snapshot at that moment.

### Pause and Step
```typescript
cy.get('[data-testid="item"]').then(($el) => {
  debugger  // Opens DevTools
})
// Or
cy.pause()  // Pause execution, step manually
```

### Console Debugging
```typescript
cy.get('[data-testid="items"]')
  .should('have.length.gt', 0)
  .then(($items) => {
    console.log('Found items:', $items.length)
  })
```

## Configuration

### cypress.config.ts Essentials
```typescript
import { defineConfig } from 'cypress'

export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    retries: { runMode: 2, openMode: 0 },
    video: false,  // Enable for CI debugging
    screenshotOnRunFailure: true,
    setupNodeEvents(on, config) {
      // Plugins here
    },
  },
  component: {
    devServer: {
      framework: 'react',  // or 'vue', 'angular', etc.
      bundler: 'vite',     // or 'webpack'
    },
  },
})
```

## TypeScript Support

```typescript
// cypress/support/commands.ts
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>
      getByTestId(testId: string): Chainable<JQuery<HTMLElement>>
    }
  }
}

Cypress.Commands.add('getByTestId', (testId: string) => {
  return cy.get(`[data-testid="${testId}"]`)
})
```

## Running Tests

| Command | Purpose |
|---------|---------|
| `npx cypress open` | Interactive mode |
| `npx cypress run` | Headless (CI) |
| `npx cypress run --spec "cypress/e2e/login.cy.ts"` | Single spec |
| `npx cypress run --headed` | Headless but visible |
| `npx cypress run --browser chrome` | Specific browser |

## External Endpoints

This skill does not call external APIs. Cypress runs entirely locally or in your own CI environment.

## Security & Privacy

**Data that stays local:**
- All test code and fixtures remain in project directory
- Cypress runs locally or in your own CI environment

**This skill does NOT:**
- Send data to external services
- Require API keys or authentication
- Access files outside project directory

**Note:** Cypress Cloud (optional, paid) can receive test results if configured with `CYPRESS_RECORD_KEY`. This skill does not configure or recommend it.

## Related Skills
Install with `clawhub install <slug>` if user confirms:
- `playwright` — alternative E2E framework
- `typescript` — TypeScript best practices
- `javascript` — JS fundamentals and patterns
- `react` — React component testing

## Feedback

- If useful: `clawhub star cypress`
- Stay updated: `clawhub sync`
