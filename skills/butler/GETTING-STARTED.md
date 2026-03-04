# Getting Started with Butler

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Access to API keys (auto-loaded from workspace)

## Installation

### Option 1: From GitHub (for external users)

```bash
git clone https://github.com/zoro-jiro-san/butler.git
cd butler
npm install
npm run build
npm test
```

### Option 2: From Workspace (for OpenClaw users)

```bash
cd ~/.openclaw/workspace/butler
npm install
npm run build
npm test
```

## Quick Start

### 1. Basic Token Allocation

```typescript
import { Butler } from 'butler';

const butler = new Butler();

// Allocate tokens for a simple task
const allocation = butler.allocateTokens('PRD-simple.md');

if (allocation.success) {
  console.log(`
✅ Allocation Successful:
   Provider: ${allocation.provider}
   Tokens: ${allocation.allocated}
   Cost: $${allocation.cost_estimate.toFixed(2)}
  `);
}
```

### 2. Spawn Agents for Complex Work

```typescript
import { Butler } from 'butler';

const butler = new Butler();

async function analyzeData() {
  const results = await butler.spawnAgent(
    'DataAnalysis',
    'Extract data, clean records, analyze patterns, write summary',
    200000, // total tokens
    {
      maxConcurrent: 3,     // run 3 agents in parallel
      retryOnFailure: true, // retry failed tasks
      maxRetries: 2
    }
  );

  // Get aggregated results
  const summary = butler.aggregateTaskResults(results[0].taskId);
  
  console.log(`
📊 Analysis Complete:
   Success Rate: ${summary.successRate.toFixed(1)}%
   Tokens Used: ${summary.totalTokensUsed}
   Details: ${JSON.stringify(summary.details, null, 2)}
  `);
}

analyzeData().catch(console.error);
```

### 3. Monitor Token Usage

```typescript
import { Butler } from 'butler';

const butler = new Butler();

// Get comprehensive status
const status = butler.getStatus();

console.log(`
📊 Token Status:
   Total Keys: ${status.tokens.total_keys}
   Active Sessions: ${status.tokens.active_sessions}
   Pending Alerts: ${status.tokens.pending_alerts}
`);

// Get available keys
const keys = butler.getAvailableKeys();
console.log(`Available keys: ${keys.length}`);
keys.forEach(key => {
  console.log(`  - ${key.id}: ${key.provider}`);
});

// Monitor usage by provider
Object.entries(status.tokens.keys_by_provider).forEach(([provider, stats]: any) => {
  const usage = ((stats.used_today / stats.total_capacity) * 100).toFixed(1);
  console.log(`${provider}: ${usage}% used`);
});
```

## Common Patterns

### Pattern 1: Simple Task with Default Settings

```typescript
const results = await butler.spawnAgent(
  'SimpleTask',
  'Do one thing quickly',
  50000
);
```

### Pattern 2: Complex Task with Full Options

```typescript
const results = await butler.spawnAgent(
  'ComplexTask',
  'Research deeply, analyze carefully, write thoroughly',
  500000,
  {
    maxConcurrent: 5,      // More parallel agents
    retryOnFailure: true,
    maxRetries: 3,         // More aggressive retries
    timeoutMs: 600000      // 10 minute timeout
  }
);
```

## Testing Your Setup

### Run Full Test Suite

```bash
npm test                # Run all tests
npm run test:watch    # Watch mode (re-run on changes)
npm run test:coverage # Generate coverage report
```

### Verify Build

```bash
npm run build
# Check dist/ folder for compiled JavaScript
```

## Troubleshooting

### Issue: "No keys available"

**Solution:** Wait for daily reset, or use smaller token requests

### Issue: "Cannot find module 'butler'"

**Solution:** Run `npm install` and `npm run build` first

## Next Steps

1. **Read Full Documentation:** [docs/SKILL.md](./SKILL.md)
2. **Understand Architecture:** [docs/ARCHITECTURE.md](./ARCHITECTURE.md)
3. **Run Tests:** `npm test`
4. **Build Your App:** Use Butler in your project

---

Happy building! 🚀
