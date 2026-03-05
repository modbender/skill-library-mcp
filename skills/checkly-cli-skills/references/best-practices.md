# Checkly CLI Best Practices

## Project Organization

### Directory Structure

```
my-monitoring-project/
├── checkly.config.ts        # Global configuration
├── __checks__/              # Check definitions
│   ├── api/
│   │   ├── auth.check.ts
│   │   └── users.check.ts
│   ├── browser/
│   │   ├── homepage.spec.ts
│   │   └── login.spec.ts
│   └── utils/
│       ├── groups.ts        # Shared check groups
│       ├── alerts.ts        # Shared alert channels
│       └── helpers.ts       # Shared utilities
├── playwright.config.ts     # Playwright configuration
└── package.json
```

### Naming Conventions

**Logical IDs**: Use descriptive, kebab-case names
```typescript
// ✅ Good
new ApiCheck('api-auth-status', { ... })
new ApiCheck('api-users-list', { ... })

// ❌ Bad
new ApiCheck('check1', { ... })
new ApiCheck('temp', { ... })
```

**File Names**: Match purpose
```
✅ api-auth.check.ts
✅ homepage-load.spec.ts
❌ test1.ts
❌ check.ts
```

## Configuration

### Use Configuration Hierarchy

```typescript
// checkly.config.ts - global defaults
checks: {
  frequency: 10,
  locations: ['us-east-1'],
}

// groups.ts - group overrides
export const criticalChecks = new CheckGroup('critical', {
  frequency: 1,  // More frequent
})

// check.ts - check overrides
new ApiCheck('super-critical', {
  group: criticalChecks,
  frequency: 0.5,  // Every 30 seconds
})
```

### Environment Variables

**Local Development**:
```bash
# .env.local (add to .gitignore)
API_TOKEN=dev-token-123
TEST_EMAIL=test@example.com
```

**Production (CI/CD)**:
```bash
# Use encrypted secrets
CHECKLY_API_KEY=cu_xxx
CHECKLY_ACCOUNT_ID=12345
API_TOKEN=prod-token-xyz
```

## Check Creation

### API Checks

**Use assertions, not just status codes**:
```typescript
// ✅ Good
assertions: [
  AssertionBuilder.statusCode().equals(200),
  AssertionBuilder.responseTime().lessThan(500),
  AssertionBuilder.jsonBody('$.status').equals('ok'),
  AssertionBuilder.jsonBody('$.data').isArray(),
]

// ❌ Limited
assertions: [
  AssertionBuilder.statusCode().equals(200),
]
```

### Browser Checks

**Use data-testid attributes**:
```typescript
// ✅ Robust
await page.click('[data-testid="submit-button"]')

// ❌ Fragile
await page.click('.btn.btn-primary')
```

**Add waits for dynamic content**:
```typescript
// ✅ Good
await page.waitForSelector('[data-testid="dashboard"]')
await expect(page.locator('[data-testid="user-name"]')).toBeVisible()

// ❌ Flaky
await page.click('button')
// Immediately check for result without waiting
```

## Testing

### Test Locally First

```bash
# 1. Playwright local execution (fastest)
npx playwright test __checks__/new-feature.spec.ts

# 2. Checkly runtime validation
npx checkly test __checks__/new-feature.spec.ts

# 3. Deploy to production
npx checkly deploy --force
```

### CI/CD Integration

```yaml
# Test on all branches, deploy only on main
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - run: npx checkly test
  
  deploy:
    needs: test
    if: github.ref == 'refs/heads/main'
    steps:
      - run: npx checkly deploy --force
```

## Version Control

### .gitignore

```gitignore
node_modules/
.env
.env.local
*.jpg
*.png
test-results/
playwright-report/
```

### Commit Practices

```bash
# Meaningful commit messages
git commit -m "Add API health check for auth service"
git commit -m "Update browser check timeouts for slow networks"

# Not
git commit -m "Update check"
git commit -m "Fix"
```

## Security

### Secrets Management

**Never commit secrets**:
```typescript
// ❌ Never do this
new ApiCheck('check', {
  environmentVariables: [
    { key: 'API_KEY', value: 'hardcoded-secret-key' },
  ],
})

// ✅ Load from environment
new ApiCheck('check', {
  environmentVariables: [
    { key: 'API_KEY', value: process.env.API_KEY!, locked: true },
  ],
})
```

**Use locked variables for secrets**:
```typescript
{
  key: 'API_KEY',
  value: process.env.API_KEY!,
  locked: true,  // Hides value in UI and logs
}
```

## Performance

### Optimize Check Frequency

```typescript
// Critical: every minute
frequency: 1,

// Important: every 5 minutes
frequency: 5,

// Normal: every 10-15 minutes
frequency: 10,

// Low priority: hourly
frequency: 60,
```

### Minimize Check Count

Use groups and patterns instead of duplicate checks:

```typescript
// ✅ Good: reusable pattern
const endpoints = ['users', 'products', 'orders']
endpoints.forEach(endpoint => {
  new ApiCheck(`api-${endpoint}`, {
    group: apiChecks,
    request: { url: `${API_URL}/${endpoint}` },
  })
})

// ❌ Bad: duplicate configuration
new ApiCheck('api-users', { ... })
new ApiCheck('api-products', { ... })
new ApiCheck('api-orders', { ... })
```

## Troubleshooting

### Enable Verbose Output

```bash
npx checkly test --verbose
```

### Verify Runtime Dependencies

```bash
npx checkly test --verify-runtime-dependencies
```

### Check Configuration

```bash
npx checkly validate
```

## Related Resources

- [Checkly Documentation](https://www.checklyhq.com/docs/)
- [Playwright Documentation](https://playwright.dev/)
- [GitHub Actions Examples](https://github.com/checkly/checkly-ci-examples)
