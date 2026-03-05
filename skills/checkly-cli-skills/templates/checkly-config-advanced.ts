// Advanced Checkly Configuration Template
import { defineConfig, RetryStrategyBuilder } from 'checkly'

export default defineConfig({
  projectName: 'Production Monitoring',
  logicalId: 'prod-monitoring',
  repoUrl: 'https://github.com/your-org/your-repo',
  checks: {
    frequency: 5,
    locations: ['us-east-1', 'us-west-1', 'eu-west-1', 'ap-southeast-1'],
    tags: ['production', 'critical'],
    runtimeId: '2025.04',
    
    retryStrategy: RetryStrategyBuilder.fixedStrategy({
      baseBackoffSeconds: 60,
      maxAttempts: 2,
      maxDurationSeconds: 600,
      sameRegion: true,
    }),
    
    checkMatch: '**/__checks__/**/*.check.{js,ts}',
    ignoreDirectoriesMatch: ['**/node_modules/**', '**/.git/**', '**/dist/**'],
    
    browserChecks: {
      testMatch: '**/__checks__/**/*.spec.{js,ts}',
      frequency: 5,
      tags: ['browser', 'e2e'],
    },
    
    playwrightConfigPath: './playwright.config.ts',
    playwrightChecks: [
      {
        name: 'E2E Test Suite',
        frequency: 10,
        testCommand: 'npm run test:e2e',
        locations: ['us-east-1', 'eu-west-1'],
        tags: ['e2e', 'full-suite'],
      },
    ],
  },
  cli: {
    runLocation: 'us-east-1',
    verbose: false,
    reporters: ['list'],
    retries: 1,
  },
})
