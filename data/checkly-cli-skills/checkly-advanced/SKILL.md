---
name: checkly-advanced
description: Advanced Checkly CLI features including retry strategies, reporters, environment variables, bundling, and custom patterns. Use when implementing complex retry logic, customizing test output, managing secrets, or troubleshooting advanced scenarios. Triggers on retry strategy, reporter, environment variables, bundling, advanced configuration.
---

# checkly advanced

Advanced Checkly CLI features and patterns.

## Retry Strategies

### Fixed retry

```typescript
import { RetryStrategyBuilder } from 'checkly/constructs'

retryStrategy: RetryStrategyBuilder.fixedStrategy({
  baseBackoffSeconds: 60,
  maxAttempts: 2,
  maxDurationSeconds: 600,
  sameRegion: true,
})
```

### Linear backoff

```typescript
retryStrategy: RetryStrategyBuilder.linearStrategy({
  baseBackoffSeconds: 30,
  maxAttempts: 3,
  maxDurationSeconds: 600,
  sameRegion: false,
})
```

### Exponential backoff

```typescript
retryStrategy: RetryStrategyBuilder.exponentialStrategy({
  baseBackoffSeconds: 10,
  maxAttempts: 5,
  maxDurationSeconds: 1800,
  sameRegion: true,
})
```

### Conditional retries

```typescript
// Retry only on network errors (API checks only)
retryStrategy: RetryStrategyBuilder.fixedStrategy({
  maxAttempts: 2,
  onlyOn: 'NETWORK_ERROR',
})
```

## Reporters

### List reporter (default)

```bash
npx checkly test --reporter=list
```

### Dot reporter (compact)

```bash
npx checkly test --reporter=dot
```

### JSON reporter

```bash
npx checkly test --reporter=json > results.json
```

### GitHub Actions reporter

```bash
npx checkly test --reporter=github
```

### CI reporter

```bash
npx checkly test --reporter=ci
```

## Environment Variables

### Global variables

```typescript
// checkly.config.ts
checks: {
  environmentVariables: [
    { key: 'API_URL', value: 'https://api.example.com' },
    { key: 'API_KEY', value: process.env.API_KEY!, locked: true },
  ],
}
```

### Group-level variables

```typescript
const group = new CheckGroup('api-group', {
  environmentVariables: [
    { key: 'SERVICE', value: 'api' },
  ],
})
```

### Check-level variables

```typescript
new ApiCheck('check', {
  environmentVariables: [
    { key: 'ENDPOINT', value: '/status' },
  ],
})
```

## Validation Options

```bash
# Verify runtime dependencies
npx checkly test --verify-runtime-dependencies

# Show verbose output
npx checkly test --verbose

# Validate without running
npx checkly validate
```

## Custom patterns

### Dynamic check generation

```typescript
const endpoints = ['users', 'products', 'orders']

endpoints.forEach(endpoint => {
  new ApiCheck(`${endpoint}-api`, {
    name: `${endpoint} API`,
    request: {
      url: `https://api.example.com/${endpoint}`,
    },
  })
})
```

### Shared alert configurations

```typescript
// alerts.ts
export const criticalAlerts = [emailChannel, slackChannel, pagerduty]

// check.ts
new ApiCheck('critical-check', {
  alertChannels: criticalAlerts,
})
```

## Related Skills

- See `checkly-constructs` for construct system details
- See `checkly-test` for testing options
- See `checkly-checks` for applying advanced features
