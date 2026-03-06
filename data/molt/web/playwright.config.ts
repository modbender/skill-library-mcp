import { defineConfig, devices } from '@playwright/test';

/**
 * Base URL configuration:
 * - Local dev:  BASE_URL=http://localhost:5173 (default)
 * - Production: BASE_URL=https://moltfundme.com
 *
 * API URL configuration:
 * - Local dev:  API_URL=http://localhost:8000 (default)
 * - Production: API_URL=https://moltfundme.com (nginx proxies /api to backend)
 */
const BASE_URL = process.env.BASE_URL || 'http://localhost:5173';

export default defineConfig({
  testDir: './e2e/tests',
  /* Run tests in files in parallel */
  fullyParallel: true,
  /* Fail the build on CI if you accidentally left test.only in the source code. */
  forbidOnly: !!process.env.CI,
  /* Retry on CI only */
  retries: process.env.CI ? 2 : 0,
  /* Opt out of parallel tests on CI. */
  workers: process.env.CI ? 1 : undefined,
  /* Reporter to use. See https://playwright.dev/docs/test-reporters */
  reporter: 'html',
  /* Shared settings for all the projects below. See https://playwright.dev/docs/api/class-testoptions. */
  use: {
    /* Base URL to use in actions like `await page.goto('/')`. */
    baseURL: BASE_URL,
    /* Collect trace when retrying the failed test. See https://playwright.dev/docs/trace-viewer */
    trace: 'on-first-retry',
    screenshot: 'only-on-failure',
    /* Increase timeout for slow operations */
    actionTimeout: 30000,
  },
  
  /* Test timeout - longer for production (network latency) */
  timeout: BASE_URL.includes('localhost') ? 60000 : 90000,

  /* Configure projects for major browsers */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },

    {
      name: 'firefox',
      use: { ...devices['Desktop Firefox'] },
    },

    {
      name: 'webkit',
      use: { ...devices['Desktop Safari'] },
    },
  ],

  /* Global setup */
  globalSetup: './e2e/global-setup.ts',
});
