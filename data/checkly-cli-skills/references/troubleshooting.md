# Common Issues and Solutions

## Authentication

### "Could not find Checkly credentials"

```bash
# Solution 1: Interactive login
npx checkly login

# Solution 2: Environment variables
export CHECKLY_API_KEY="cu_xxx"
export CHECKLY_ACCOUNT_ID="12345"
```

### "401 Unauthorized"

1. Verify credentials:
   ```bash
   npx checkly whoami
   ```

2. Regenerate API key in Checkly UI if expired

3. Check that API key has correct permissions

## Configuration

### "No checks found"

1. Check file paths:
   ```bash
   find . -name "*.check.ts" -o -name "*.spec.ts"
   ```

2. Update `checkMatch` pattern in checkly.config.ts

3. Verify files aren't in ignored directories

### "Duplicate logical ID"

Ensure logical IDs are unique:

```typescript
// ❌ Duplicate
new ApiCheck('my-check', { ... })
new ApiCheck('my-check', { ... })  // Error!

// ✅ Unique
new ApiCheck('api-auth-check', { ... })
new ApiCheck('api-users-check', { ... })
```

## Runtime Issues

### "Module not found"

Package not available in Checkly runtime:

```bash
# Check supported packages
npx checkly test --verify-runtime-dependencies
```

See [Checkly Runtimes](https://www.checklyhq.com/docs/runtimes/)

### "Check timeout"

1. Increase timeout (browser checks):
   ```typescript
   test('slow check', async ({ page }) => {
     test.setTimeout(60000)  // 60 seconds
     // ...
   })
   ```

2. Check endpoint accessibility from Checkly locations

## Browser Checks

### Selector Not Found

```typescript
// ❌ Fragile
await page.click('.button')

// ✅ Robust
await page.click('[data-testid="submit-button"]')
await page.click('button:has-text("Submit")')
```

### Flaky Tests

Add explicit waits:

```typescript
// Wait for network idle
await page.waitForLoadState('networkidle')

// Wait for specific element
await page.waitForSelector('[data-testid="content"]')

// Wait for condition
await page.waitForFunction(() => document.readyState === 'complete')
```

## Deployment

### "Validation errors"

```bash
# Show all errors
npx checkly validate

# Fix errors in code
# Re-validate
npx checkly validate
```

### "Quota exceeded"

- Upgrade Checkly plan
- Delete unused checks in UI
- Optimize check frequency

## API Checks

### Assertion Failures

Use verbose mode to debug:

```bash
npx checkly test --verbose
```

Shows full request/response details.

### Environment Variable Not Working

```typescript
// ✅ Correct usage
request: {
  url: '{{API_BASE_URL}}/users',
  headers: [
    { key: 'Authorization', value: 'Bearer {{API_TOKEN}}' },
  ],
}

environmentVariables: [
  { key: 'API_BASE_URL', value: 'https://api.example.com' },
  { key: 'API_TOKEN', value: process.env.API_TOKEN! },
]
```

## Getting Help

1. **Check CLI version**:
   ```bash
   npx checkly --version
   ```

2. **Enable verbose logging**:
   ```bash
   npx checkly test --verbose
   ```

3. **Community & Support**:
   - [Checkly Community](https://community.checklyhq.com/)
   - [GitHub Issues](https://github.com/checkly/checkly-cli/issues)
   - [Checkly Support](https://www.checklyhq.com/support/)
