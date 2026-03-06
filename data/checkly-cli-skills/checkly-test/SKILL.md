---
name: checkly-test
description: Test Checkly checks locally using npx checkly test command, including filtering, reporters, retry strategies, and debugging workflows. Use when testing checks before deployment, validating changes, debugging failures, or running checks in CI/CD. Triggers on checkly test, test checks, run checks locally, check validation, debug checks.
---

# checkly test

Test Checkly checks locally with `npx checkly test`.

## Quick start

```bash
# Test all checks
npx checkly test

# Test specific check
npx checkly test __checks__/api.check.ts

# Test with verbose output
npx checkly test --verbose

# Test in specific location
npx checkly test --location=eu-west-1
```

## How it works

`npx checkly test` executes your checks in Checkly's runtime environment (same as production) but does NOT deploy or schedule them. Perfect for:
- ✅ Pre-deployment validation
- ✅ CI/CD integration
- ✅ Local development iteration
- ✅ Debugging check failures

## Command reference

```bash
npx checkly test [file-pattern] [options]
```

### Options

| Flag | Description |
|------|-------------|
| `--location=<location>` | Run in specific datacenter (e.g., `us-east-1`) |
| `--verbose, -v` | Show full check output and logs |
| `--reporter=<type>` | Output format: `list`, `dot`, `ci`, `github`, `json` |
| `--retries=<n>` | Retry failed checks (0-3) |
| `--config=<path>` | Path to checkly.config.ts |
| `--verify-runtime-dependencies` | Validate npm package versions |
| `--env-file=<path>` | Load environment variables from file |
| `--grep=<pattern>` | Filter checks by name pattern |

## Workflows

### Basic testing

```bash
# Test everything
npx checkly test

# Output:
# Parsing your project... done
# Running 3 checks in us-east-1.
# 
# __checks__/api.check.ts
#  ✔ API Status Check (234ms)
# __checks__/homepage.spec.ts  
#  ✔ Homepage Check (2.1s)
# __checks__/login.spec.ts
#  ✔ Login Flow (3.4s)
#
# 3 passed, 3 total
```

### Test specific checks

```bash
# Single file
npx checkly test __checks__/api.check.ts

# Multiple files
npx checkly test __checks__/api.check.ts __checks__/homepage.spec.ts

# Pattern matching
npx checkly test __checks__/api-*.check.ts

# By name (grep)
npx checkly test --grep="Homepage"
```

### Verbose debugging

```bash
npx checkly test --verbose

# Shows:
# - Request/response details (API checks)
# - Console logs (browser checks)
# - Screenshots (on failure)
# - Full stack traces
# - Environment variables used
```

### Testing in different locations

```bash
# Test from EU datacenter
npx checkly test --location=eu-west-1

# Test from multiple locations (requires configuration)
# Set in checkly.config.ts:
checks: {
  locations: ['us-east-1', 'eu-west-1'],
}
```

### CI/CD integration

```yaml
# GitHub Actions
name: Test Checks
on: [push]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-node@v3
        with:
          node-version: '20'
      
      - run: npm ci
      - run: npx checkly test
        env:
          CHECKLY_API_KEY: ${{ secrets.CHECKLY_API_KEY }}
          CHECKLY_ACCOUNT_ID: ${{ secrets.CHECKLY_ACCOUNT_ID }}
```

### Test with retries

```bash
# Retry failed checks once
npx checkly test --retries=1

# Useful for flaky tests or network issues
```

### Environment variables

```bash
# Inline
API_BASE_URL=https://staging.example.com npx checkly test

# From .env file
npx checkly test --env-file=.env.test

# .env.test
API_BASE_URL=https://staging.example.com
API_KEY=test-key-123
```

## Reporters

### List reporter (default)

```bash
npx checkly test --reporter=list

# Detailed output with timings
```

### Dot reporter

```bash
npx checkly test --reporter=dot

# Compact: . = pass, F = fail
```

### CI reporter

```bash
npx checkly test --reporter=ci

# Optimized for CI logs
```

### GitHub reporter

```bash
npx checkly test --reporter=github

# Generates GitHub Actions annotations
```

### JSON reporter

```bash
npx checkly test --reporter=json > results.json

# Machine-readable output
```

## Testing strategies

### Local-first workflow

```bash
# 1. Write Playwright test
cat > __checks__/new-feature.spec.ts

# 2. Test locally with Playwright (fastest)
npx playwright test __checks__/new-feature.spec.ts

# 3. Validate in Checkly runtime
npx checkly test __checks__/new-feature.spec.ts

# 4. Deploy when passing
npx checkly deploy
```

### Pre-deployment validation

```bash
# Run full test suite before deploy
npx checkly test && npx checkly deploy --force
```

### Debugging failures

```bash
# 1. Run with verbose output
npx checkly test __checks__/failing.spec.ts --verbose

# 2. Check for common issues:
#    - API endpoint changed?
#    - Auth token expired?
#    - Selector changed (browser checks)?
#    - Environment variable missing?

# 3. Test locally first (browser checks)
npx playwright test __checks__/failing.spec.ts --headed

# 4. Compare environments
#    - Local vs Checkly runtime
#    - Check Node.js version
#    - Check npm package versions
```

## Troubleshooting

### "No checks found to test"

**Solution**:
```bash
# Check configuration
npx checkly validate

# Verify files exist
ls -la __checks__/

# Check checkMatch pattern in checkly.config.ts
```

### "Check failed: Connection timeout"

**Causes**:
- Endpoint not accessible from Checkly locations
- Firewall blocking Checkly IPs
- Endpoint genuinely down

**Solution**:
```bash
# Test from different location
npx checkly test --location=eu-west-1

# For private endpoints, use private locations
```

### "Module not found" errors

**Cause**: npm package not available in Checkly runtime

**Solution**:
```bash
# Validate dependencies
npx checkly test --verify-runtime-dependencies

# See supported packages:
# https://www.checklyhq.com/docs/runtimes/
```

### Flaky tests

**Solution**:
```bash
# Enable retries
npx checkly test --retries=2

# Or configure in checkly.config.ts:
checks: {
  retryStrategy: RetryStrategyBuilder.fixedStrategy({
    maxAttempts: 2,
    baseBackoffSeconds: 60,
  }),
}
```

## Testing vs Deploying

| Command | Purpose | Scheduled | Billed |
|---------|---------|-----------|--------|
| `npx checkly test` | Validation | ❌ No | ❌ No* |
| `npx checkly deploy` | Production monitoring | ✅ Yes | ✅ Yes |

*Test runs count towards your account's test run limit but are not billed separately.

## Related Skills

- See `checkly-deploy` for deploying checks after testing
- See `checkly-checks` for creating checks to test
- See `checkly-playwright` for Playwright-specific testing
- See `checkly-advanced` for retry strategies and reporters
