---
name: checkly-config
description: Configure Checkly CLI projects with checkly.config.ts including project settings, check defaults, file discovery patterns, runtime configuration, and Playwright integration. Use when setting up new projects, configuring check discovery, setting global defaults, or troubleshooting project structure. Triggers on checkly.config, configuration, project setup, check discovery, defaults.
---

# checkly config

Configure Checkly CLI projects with `checkly.config.ts`.

## Quick start

```typescript
// checkly.config.ts
import { defineConfig } from 'checkly'

export default defineConfig({
  projectName: 'My App',
  logicalId: 'my-app-monitoring',
  repoUrl: 'https://github.com/acme/my-app',
  checks: {
    frequency: 5,
    locations: ['us-east-1', 'eu-west-1'],
    tags: ['production', 'api'],
    runtimeId: '2025.04',
    checkMatch: '**/__checks__/**/*.check.{js,ts}',
    browserChecks: {
      testMatch: '**/__checks__/**/*.spec.{js,ts}',
    },
  },
})
```

## Configuration file structure

### Required properties

```typescript
{
  projectName: string,    // Display name in Checkly UI
  logicalId: string,      // Unique project identifier
}
```

**Example:**
```typescript
export default defineConfig({
  projectName: 'E-commerce API',
  logicalId: 'ecommerce-api-prod',
})
```

### Check defaults

Configure defaults that apply to all checks:

```typescript
{
  checks: {
    frequency: number,              // Minutes between checks (1, 5, 10, 15, 30, 60, etc.)
    locations: string[],            // Checkly datacenter locations
    tags: string[],                 // Tags for organization
    runtimeId: string,              // Runtime version (e.g., '2025.04')
    
    // File discovery
    checkMatch: string | string[],  // Pattern for check files
    ignoreDirectoriesMatch: string[], // Directories to skip
    
    // Alert settings
    alertChannels: AlertChannel[],  // Default alert channels
    
    // Retry configuration
    retryStrategy: RetryStrategy,   // Default retry behavior
  }
}
```

**Example with comprehensive defaults:**
```typescript
import { defineConfig, RetryStrategyBuilder } from 'checkly'

export default defineConfig({
  projectName: 'Production Monitoring',
  logicalId: 'prod-monitoring',
  checks: {
    frequency: 5,
    locations: ['us-east-1', 'us-west-1', 'eu-west-1'],
    tags: ['production', 'critical'],
    runtimeId: '2025.04',
    
    retryStrategy: RetryStrategyBuilder.fixedStrategy({
      baseBackoffSeconds: 60,
      maxAttempts: 2,
      maxDurationSeconds: 600,
      sameRegion: true,
    }),
    
    checkMatch: '**/__checks__/**/*.check.{js,ts}',
    ignoreDirectoriesMatch: ['**/node_modules/**', '**/.git/**'],
  },
})
```

### Browser check configuration

Auto-discover Playwright spec files as browser checks:

```typescript
{
  checks: {
    browserChecks: {
      testMatch: string | string[],  // Pattern to match spec files
      frequency: number,              // Override default frequency
      locations: string[],            // Override default locations
      tags: string[],                 // Additional tags
    }
  }
}
```

**Example:**
```typescript
export default defineConfig({
  checks: {
    frequency: 10,
    locations: ['us-east-1'],
    
    browserChecks: {
      testMatch: '**/__checks__/**/*.spec.{js,ts}',
      frequency: 5,  // Browser checks run more frequently
      tags: ['e2e', 'browser'],
    },
  },
})
```

### Playwright Check Suite

Configure full Playwright test suite as a single check:

```typescript
{
  checks: {
    playwrightConfigPath: string,    // Path to playwright.config.ts
    include: string | string[],       // Additional files to bundle
    
    playwrightChecks: [
      {
        name: string,
        frequency: number,
        testCommand: string,          // Command to run tests
        locations: string[],
        tags: string[],
      }
    ],
  }
}
```

**Example:**
```typescript
export default defineConfig({
  checks: {
    playwrightConfigPath: './playwright.config.ts',
    include: ['./fixtures/**/*.json'],
    
    playwrightChecks: [
      {
        name: 'E2E Test Suite',
        frequency: 10,
        testCommand: 'npm run test:e2e',
        locations: ['us-east-1', 'eu-west-1'],
        tags: ['e2e', 'critical'],
      },
    ],
  },
})
```

### CLI configuration

Configure CLI behavior:

```typescript
{
  cli: {
    runLocation: string,            // Default location for 'npx checkly test'
    privateRunLocation: string,     // Private location slug
    verbose: boolean,               // Show full logs
    reporters: string[],            // Default reporters
    retries: number,                // Test retry attempts (0-3)
  }
}
```

**Example:**
```typescript
export default defineConfig({
  cli: {
    runLocation: 'us-east-1',
    verbose: false,
    reporters: ['list'],
    retries: 1,
  },
})
```

## File discovery patterns

### Check discovery

The CLI discovers check files using glob patterns:

| Pattern | Default | Discovers |
|---------|---------|-----------|
| `checkMatch` | `**/*.check.{js,ts}` | Explicit check definition files |
| `browserChecks.testMatch` | (none) | Auto-created browser checks from specs |
| `multiStepChecks.testMatch` | (none) | Auto-created multi-step checks |

**Examples:**

```typescript
// Discover checks in specific directory
checks: {
  checkMatch: '**/__checks__/**/*.check.ts',
}

// Multiple patterns
checks: {
  checkMatch: [
    '**/__checks__/**/*.check.ts',
    '**/monitoring/**/*.check.ts',
  ],
}

// Auto-discover browser checks
checks: {
  browserChecks: {
    testMatch: '**/__checks__/**/*.spec.ts',
  },
}
```

### Ignore patterns

Exclude directories from discovery:

```typescript
checks: {
  ignoreDirectoriesMatch: [
    '**/node_modules/**',
    '**/.git/**',
    '**/dist/**',
    '**/build/**',
  ],
}
```

**Note**: `node_modules` and `.git` are always ignored by default.

## Configuration hierarchy

Configuration values cascade from global to specific:

```
1. Checkly account defaults (lowest priority)
   ↓
2. checkly.config.ts defaults
   ↓
3. CheckGroup properties
   ↓
4. Individual check properties (highest priority)
```

**Example:**

```typescript
// checkly.config.ts - global defaults
export default defineConfig({
  checks: {
    frequency: 10,
    locations: ['us-east-1'],
  },
})

// check-group.ts - group overrides
const criticalChecks = new CheckGroup('critical-checks', {
  frequency: 5,  // More frequent than default
})

// api-check.ts - check-level override
new ApiCheck('auth-api', {
  name: 'Auth API',
  frequency: 1,  // Most frequent - overrides group and global
  group: criticalChecks,
  // locations inherited from config (us-east-1)
})
```

## Location configuration

### Available locations

Common Checkly datacenter locations:

| Region | Location Code |
|--------|---------------|
| US East (N. Virginia) | `us-east-1` |
| US West (California) | `us-west-1` |
| Europe (Ireland) | `eu-west-1` |
| Europe (Paris) | `eu-central-1` |
| Asia Pacific (Singapore) | `ap-southeast-1` |
| Asia Pacific (Tokyo) | `ap-northeast-1` |
| South America (São Paulo) | `sa-east-1` |

**Example:**
```typescript
checks: {
  locations: ['us-east-1', 'eu-west-1', 'ap-southeast-1'],
}
```

### Private locations

For on-premise or private network monitoring:

```typescript
checks: {
  privateLocations: ['my-vpc-location'],
}

cli: {
  privateRunLocation: 'my-vpc-location',  // For testing
}
```

## Runtime configuration

### Runtime versions

Specify Node.js runtime and available npm packages:

```typescript
checks: {
  runtimeId: '2025.04',  // Latest runtime
}
```

**Runtime version format**: `YYYY.MM`

**To check available runtimes:**
```bash
# Runtime info shown during test/deploy
npx checkly test
```

### Environment variables

Set environment variables for all checks:

```typescript
import { defineConfig } from 'checkly'

export default defineConfig({
  checks: {
    environmentVariables: [
      { key: 'API_BASE_URL', value: 'https://api.example.com' },
      { key: 'API_KEY', value: process.env.API_KEY!, locked: true },
    ],
  },
})
```

**Environment variable hierarchy:**
1. Check-level variables (highest priority)
2. Group-level variables
3. Global account variables (set in Checkly UI)

## Workflows

### Initial project setup

1. **Create project with scaffolding:**
   ```bash
   npm create checkly@latest
   cd my-checkly-project
   ```

2. **Edit checkly.config.ts:**
   ```typescript
   export default defineConfig({
     projectName: 'My Production Monitoring',
     logicalId: 'prod-monitoring',
     repoUrl: 'https://github.com/myorg/myapp',
     checks: {
       frequency: 5,
       locations: ['us-east-1', 'eu-west-1'],
       tags: ['production'],
       runtimeId: '2025.04',
     },
   })
   ```

3. **Test configuration:**
   ```bash
   npx checkly validate
   ```

### Migrating from auto-generated config

If CLI generates config automatically (when `playwright.config.ts` exists):

1. **Review generated config:**
   ```bash
   cat checkly.config.ts
   ```

2. **Customize settings:**
   ```typescript
   export default defineConfig({
     projectName: 'Your Project Name',  // Update this
     logicalId: 'your-project-id',      // Update this
     checks: {
       frequency: 10,
       locations: ['us-east-1'],
       playwrightConfigPath: './playwright.config.ts',
     },
   })
   ```

3. **Validate:**
   ```bash
   npx checkly validate
   ```

### Adding browser check auto-discovery

Enable auto-discovery for Playwright specs:

1. **Update checkly.config.ts:**
   ```typescript
   export default defineConfig({
     checks: {
       browserChecks: {
         testMatch: '**/__checks__/**/*.spec.ts',
       },
     },
   })
   ```

2. **Create checks directory:**
   ```bash
   mkdir -p __checks__
   ```

3. **Add Playwright specs:**
   ```bash
   # Specs are automatically discovered and deployed
   ls __checks__/*.spec.ts
   ```

4. **Test discovery:**
   ```bash
   npx checkly test
   # Should show auto-discovered checks
   ```

## Troubleshooting

### "No checks found"

**Cause**: `checkMatch` pattern doesn't match your files

**Solution**:
1. Verify file paths:
   ```bash
   find . -name "*.check.ts"
   ```

2. Update pattern in checkly.config.ts:
   ```typescript
   checks: {
     checkMatch: '**/your-directory/**/*.check.ts',
   }
   ```

3. Test:
   ```bash
   npx checkly validate --verbose
   ```

### "Cannot find module 'checkly'"

**Cause**: Missing checkly package

**Solution**:
```bash
npm install --save-dev checkly
```

### "Duplicate logical ID"

**Cause**: Two resources have the same logical ID

**Solution**:
1. Ensure `logicalId` in checkly.config.ts is unique across your account
2. Check for duplicate check IDs in your code
3. Use descriptive, unique IDs: `'my-app-homepage-check'` not `'check-1'`

### Configuration not applying

**Cause**: More specific configuration overriding defaults

**Solution**:
1. Check configuration hierarchy (check > group > config > account)
2. Verify check isn't part of a group with different settings
3. Use `--verbose` flag to see resolved configuration:
   ```bash
   npx checkly test --verbose
   ```

## Related Skills

**Getting started:**
- See `checkly-auth` for authentication before using config
- See `checkly-test` to validate your configuration
- See `checkly-deploy` to deploy configured checks

**Check creation:**
- See `checkly-checks` for creating API and browser checks
- See `checkly-playwright` for Playwright test suite configuration
- See `checkly-groups` for organizing checks with groups
