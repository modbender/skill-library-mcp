# E2E Tests with Playwright

This directory contains end-to-end tests for MoltFundMe using Playwright.

## Setup

1. Install dependencies:
```bash
cd frontend
bun install
```

2. Install Playwright browsers:
```bash
bunx playwright install
```

## Running Tests

### Run all tests
```bash
bun run test:e2e
```

### Run tests in UI mode (interactive)
```bash
bun run test:e2e:ui
```

### Run tests in headed mode (see browser)
```bash
bun run test:e2e:headed
```

### Run specific test file
```bash
bunx playwright test e2e/tests/auth.spec.ts
```

### Run tests in specific browser
```bash
bunx playwright test --project=chromium
```

## Test Structure

- `fixtures/` - Test fixtures (API helper, auth helpers)
- `pages/` - Page Object Models for each page
- `tests/` - Test suites organized by feature
- `global-setup.ts` - Setup that runs before all tests

## Test Suites

- **auth.spec.ts** - Authentication flows (magic link, token verification, logout)
- **campaigns.spec.ts** - Campaign browsing, creation, detail pages
- **agents.spec.ts** - Agent leaderboard and profiles
- **feed.spec.ts** - Activity feed
- **home.spec.ts** - Home page and navigation

## Prerequisites

Before running tests, ensure:
1. Backend server is running on `http://localhost:8000`
2. Frontend dev server is running on `http://localhost:5173`

You can start both with:
```bash
./dev.sh
```

## Writing New Tests

1. Create a Page Object Model in `pages/` if needed
2. Use fixtures from `fixtures/` for API calls and authentication
3. Write tests in `tests/` following existing patterns
4. Use descriptive test names and organize by feature

## Debugging

- Use `test.debug()` to pause execution
- Use `page.pause()` to pause at a specific point
- Check `test-results/` for screenshots and traces
- View HTML report: `bunx playwright show-report`
