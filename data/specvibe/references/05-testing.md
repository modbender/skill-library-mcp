# SpecVibe Reference: Testing

Automated testing is the foundation of building reliable software. It provides a safety net that allows you to refactor code and add new features with confidence.

## 1. The Testing Pyramid

Structure your tests according to the testing pyramid:

- **Unit Tests (Base)**: The majority of your tests. They are small, fast, and test a single function or component in isolation.
- **Integration Tests (Middle)**: Test how multiple units work together. For example, testing a service layer method that calls the data access layer.
- **End-to-End (E2E) Tests (Top)**: A small number of tests that simulate a real user journey through the entire application, from the UI to the database.

## 2. Unit Tests

- **Focus**: Test a single, isolated piece of logic.
- **Mocks and Stubs**: Use mocking libraries (like Vitest's `vi.mock`) to replace external dependencies (e.g., database calls, API requests) with predictable fakes. This ensures your test is isolated.
- **Coverage**: Aim for high unit test coverage (>80%) on all critical business logic.

```typescript
// Example: Unit test for a simple utility function
import { expect, test } from 'vitest';
import { slugify } from './utils';

test('should convert a string to a slug', () => {
  expect(slugify('Hello World!')).toBe('hello-world');
});
```

## 3. Integration Tests

- **Focus**: Test the interaction between multiple components or layers.
- **Real Dependencies**: Use a real test database (e.g., a separate Docker container) for integration tests. This provides much higher confidence than using mocks.
- **API Testing**: The most valuable integration tests for a web application are API tests. Use a library like `supertest` to make HTTP requests to your running application and assert the responses.

```typescript
// Example: API integration test
import { expect, test } from 'vitest';
import request from 'supertest';
import { app } from './app'; // Your Express app

test('GET /users/:id should return a user', async () => {
  const response = await request(app).get('/users/123');
  expect(response.status).toBe(200);
  expect(response.body.id).toBe('123');
});
```

## 4. End-to-End (E2E) Tests

- **Focus**: Simulate a complete user workflow.
- **Use a Framework**: Use a modern E2E testing framework like Playwright or Cypress. These tools control a real browser to interact with your application just like a user would.
- **Test the Happy Path**: E2E tests are slow and brittle. Focus on testing the most critical user journeys (e.g., user registration, creating a project, completing a purchase).

```typescript
// Example: Playwright E2E test
import { test, expect } from '@playwright/test';

test('should allow a user to sign up', async ({ page }) => {
  await page.goto('/signup');
  await page.fill('input[name="email"]', 'test@example.com');
  await page.fill('input[name="password"]', 'password123');
  await page.click('button[type="submit"]');
  await expect(page.locator('h1')).toHaveText('Welcome!');
});
```

## Best Practices

- **Test-Driven Development (TDD)**: Write a failing test *before* you write the implementation code. This forces you to think about requirements and edge cases first.
- **Run Tests in CI**: All tests MUST be run automatically in your CI/CD pipeline on every commit. A broken build should prevent code from being merged or deployed.
