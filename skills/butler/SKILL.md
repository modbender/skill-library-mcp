# Butler - AI Agent Treasury & Orchestration Skill

## Overview

**Butler** is an OpenClaw skill that transforms AI agents into autonomous economic entities. It manages multi-provider token budgets, spawns sub-agents for complex tasks, and automatically handles token purchases when budgets deplete.

Think of Butler as your **AI Agent CFO** that:
- 💰 Tracks token budgets across 8 API keys and 6 providers
- 🚀 Spawns sub-agents with automatic budget allocation
- 🔄 Rotates keys when approaching limits
- 📊 Aggregates results from parallel workers
- 🛡️ Integrates with Code Reviewer for security

## Quick Start

### Installation

```bash
npm install butler
# or
yarn add butler
```

### Basic Usage

```typescript
import { Butler } from 'butler';

// Initialize
const butler = new Butler();

// Allocate tokens for a task
const allocation = butler.allocateTokens('PRD-my-task.md', 'anthropic');
console.log(`✅ Allocated ${allocation.allocated} tokens on ${allocation.provider}`);

// Spawn agents for complex work
const results = await butler.spawnAgent(
  'DataAnalysis',
  'Analyze sales data and write report',
  100000, // tokens
  { maxConcurrent: 3, retryOnFailure: true }
);

// Get status
const status = butler.getStatus();
console.log(`🎯 Status:`, status);
```

## Features

### 1. Token Management

Butler tracks 8 API keys across 6 providers with real-time usage monitoring:

```typescript
// Get available keys
const keys = butler.getAvailableKeys();
// [
//   { id: 'nvidia-1', provider: 'nvidia', model: 'llama-3.1', ... },
//   { id: 'anthropic-1', provider: 'anthropic', model: 'claude-sonnet', ... },
//   { id: 'groq-1', provider: 'groq', model: 'llama-3.1', ... },
//   ...
// ]

// Estimate tokens for PRD
const estimate = butler.allocateTokens('PRD-integration.md');
// Analyzes PRD complexity and recommends optimal allocation

// Monitor usage
const status = butler.monitorUsage();
// { keys_by_provider: { nvidia: {...}, anthropic: {...}, ... } }
```

**Supported Providers:**
- **Nvidia** (3 keys, 5M tokens/day each) - Free tier ✅
- **Groq** (1 key, 10M tokens/day) - Free tier ✅
- **Anthropic** (1 key, 1M tokens/day) - Current model
- **OpenAI** (1 key, 500k tokens/day)
- **OpenRouter** (1 key, 2M tokens/day)
- **Sokosumi** (1 key) - Custom/research

**Total Capacity:** 28.5M tokens/day

### 2. Agent Orchestration

Spawn multiple sub-agents with automatic task decomposition and budget allocation:

```typescript
// Simple spawn (auto-decompose)
const results = await butler.spawnAgent(
  'ComplexResearch',
  `Research AI agent frameworks:
   1. Gather information from 5+ sources
   2. Analyze capabilities and limitations  
   3. Write detailed comparison report
   4. Validate findings with expert review`,
  250000 // tokens
);

// Advanced spawn with options
const results = await butler.spawnAgent(
  'DataPipeline',
  'Extract, transform, validate, load data',
  500000,
  {
    maxConcurrent: 4,        // Run up to 4 sub-agents in parallel
    retryOnFailure: true,    // Retry failed sub-tasks
    maxRetries: 3,           // Up to 3 retry attempts
    timeoutMs: 600000        // 10 minute timeout per sub-agent
  }
);

// Get results
results.forEach(result => {
  console.log(`Sub-task ${result.subTaskId}:`);
  console.log(`  Status: ${result.status}`);
  console.log(`  Tokens: ${result.tokensUsed}`);
  if (result.error) console.log(`  Error: ${result.error}`);
});
```

**Task Decomposition Algorithm:**
```
Input: "Research AI frameworks, analyze patterns, write report"
         ↓
1. Keyword detection: "research", "analyze", "write"
         ↓
2. Sub-task creation:
   - Subtask 1: "research AI frameworks" (30% budget)
   - Subtask 2: "analyze patterns" (40% budget)
   - Subtask 3: "write report" (30% budget)
         ↓
3. Priority boost (if specified)
         ↓
4. Concurrent execution (respects maxConcurrent)
         ↓
5. Result aggregation
```

### 3. Budget Allocation

Automatic budget allocation based on task complexity and priority:

```typescript
// High-priority task gets more budget
const task = {
  totalBudget: 100000,
  subTasks: [
    {
      id: 'low-priority-task',
      estimatedTokens: 50000,
      priority: 'low'      // 0.5x multiplier = 25k tokens
    },
    {
      id: 'critical-task',
      estimatedTokens: 50000,
      priority: 'critical' // 2.0x multiplier = 100k tokens (capped)
    }
  ]
};

// Allocation: { 'low-priority-task': 33k, 'critical-task': 67k }
```

**Priority Multipliers:**
- `low`: 0.5x (50% of estimated)
- `medium`: 1.0x (100% of estimated)
- `high`: 1.5x (150% of estimated)
- `critical`: 2.0x (200% of estimated)

### 4. Automatic Rotation

Keys rotate at 75% threshold to prevent exhaustion:

```typescript
// Automatic tracking and alerts
const status = butler.getStatus();
// When session reaches 75% of allocated budget:
// ✅ Alert issued
// 🔄 New key auto-selected
// 📊 Session updated with new key
// 📝 Change logged to history

// Manual rotation if needed
butler.rotateKey('session-id-123', 'anthropic-1');
```

### 5. Result Aggregation

Automatic aggregation of results from parallel agents:

```typescript
const results = await butler.spawnAgent('ComplexTask', 'task description', 100000);

// After execution, aggregate results:
const aggregated = butler.aggregateTaskResults(results[0].taskId);
// {
//   taskId: 'task-...',
//   totalSubTasks: 5,
//   successful: 4,
//   failed: 1,
//   totalTokensUsed: 87500,
//   successRate: 80,
//   details: [
//     { id: 'subtask-1', status: 'success', tokensUsed: 18000 },
//     { id: 'subtask-2', status: 'success', tokensUsed: 22000 },
//     { id: 'subtask-3', status: 'success', tokensUsed: 19500 },
//     { id: 'subtask-4', status: 'success', tokensUsed: 21000 },
//     { id: 'subtask-5', status: 'failure', tokensUsed: 7000, error: 'timeout' }
//   ]
// }
```

## Examples

### Example 1: Token Allocation for Complex Task

```typescript
import { Butler } from 'butler';

const butler = new Butler();

// Create PRD file
const prd = `
# AI Agent Integration Task

## Requirements
- Integrate OpenAI API
- Build agent orchestration
- Write unit tests
- Deploy to production

## Constraints
- Budget: $100/day
- Timeline: 1 week
- Team: 2 engineers
`;

fs.writeFileSync('PRD-integration.md', prd);

// Get smart allocation
const allocation = butler.allocateTokens('PRD-integration.md');

if (allocation.success) {
  console.log(`
✅ Recommended:
   Key: ${allocation.key_id} (${allocation.provider})
   Budget: ${allocation.allocated.toLocaleString()} tokens
   Cost: $${allocation.cost_estimate.toFixed(2)}
   Rotate at: ${allocation.rotation_threshold.toLocaleString()} tokens
   Available: ${allocation.available_capacity.toLocaleString()} tokens
  `);
}
```

### Example 2: Parallel Agent Execution

```typescript
import { Butler } from 'butler';

const butler = new Butler();

async function analyzeDataset() {
  const results = await butler.spawnAgent(
    'DatasetAnalysis',
    `
    1. Extract data from sources
    2. Clean and validate data
    3. Run statistical analysis
    4. Create visualizations
    5. Write findings report
    `,
    300000,
    { maxConcurrent: 3, retryOnFailure: true }
  );

  // Process results
  const aggregated = butler.aggregateTaskResults(results[0].taskId);
  
  console.log(`
📊 Analysis Complete:
   Successful: ${aggregated.successful}/${aggregated.totalSubTasks}
   Success Rate: ${aggregated.successRate.toFixed(1)}%
   Total Tokens: ${aggregated.totalTokensUsed.toLocaleString()}
  `);

  return aggregated;
}

analyzeDataset().then(result => {
  console.log('Results:', result.details);
});
```

### Example 3: Error Handling & Retries

```typescript
import { Butler } from 'butler';

const butler = new Butler();

async function reliableProcessing() {
  try {
    const results = await butler.spawnAgent(
      'RobustProcessing',
      'Process data with validation and error handling',
      200000,
      {
        retryOnFailure: true,
        maxRetries: 3,  // Retry up to 3 times
        maxConcurrent: 2,
        timeoutMs: 120000  // 2 minute timeout
      }
    );

    const aggregated = butler.aggregateTaskResults(results[0].taskId);

    if (aggregated.failed > 0) {
      console.log(`⚠️  ${aggregated.failed} sub-tasks failed:`);
      aggregated.details
        .filter((d: any) => d.status === 'failure')
        .forEach((d: any) => {
          console.log(`   - ${d.id}: ${d.error}`);
        });

      // Optionally retry failed tasks
      await butler.retryFailedTasks(results[0].taskId);
    }

    return aggregated;
  } catch (error) {
    console.error('Task failed:', error);
    throw error;
  }
}

reliableProcessing();
```

### Example 4: Monitoring Token Usage

```typescript
import { Butler } from 'butler';

const butler = new Butler();

// Check current status
const status = butler.getStatus();

console.log(`
📊 Token Status:
   Total Keys: ${status.tokens.total_keys}
   Active: ${status.tokens.active_keys}
   Sessions: ${status.tokens.active_sessions}
   Pending Alerts: ${status.tokens.pending_alerts}
`);

// Get detailed provider breakdown
Object.entries(status.tokens.keys_by_provider).forEach(([provider, stats]: any) => {
  const usage = ((stats.used_today / stats.total_capacity) * 100).toFixed(1);
  console.log(`
${provider.toUpperCase()}:
   Capacity: ${stats.total_capacity.toLocaleString()} tokens/day
   Used: ${stats.used_today.toLocaleString()} (${usage}%)
   Remaining: ${stats.remaining.toLocaleString()}
   Cost: $${stats.cost_today.toFixed(2)}
  `);
});

// Available keys for next allocation
const available = butler.getAvailableKeys();
console.log(`\nAvailable keys: ${available.length}`);
available.forEach(key => {
  console.log(`   - ${key.id} (${key.provider}): ${key.limits.tokens_per_day.toLocaleString()} tokens/day`);
});
```

## API Reference

### Butler Class

#### `constructor(keysPath?: string, statePath?: string)`
Initialize Butler with optional custom paths for API keys and state.

#### `allocateTokens(prdPath: string, preferredProvider?: string): AllocationResult`
Analyze PRD and recommend optimal token allocation.

**Returns:**
```typescript
{
  success: boolean;
  key_id?: string;        // Recommended key ID
  key?: string;           // API key
  provider?: string;      // Provider name
  model?: string;         // Model to use
  allocated?: number;     // Allocated tokens
  rotation_threshold?: number;  // Alert threshold (75%)
  available_capacity?: number;  // Current available tokens
  cost_estimate?: number; // Estimated cost
}
```

#### `spawnAgent(name: string, description: string, budget: number, options?: AgentOptions): Promise<TaskResult[]>`
Spawn sub-agents for task execution.

**Options:**
```typescript
{
  maxConcurrent?: number;    // Default: 3
  retryOnFailure?: boolean;  // Default: true
  maxRetries?: number;       // Default: 2
  timeoutMs?: number;        // Default: 300000
}
```

**Returns:** Array of task results with status, tokens used, and errors.

#### `getStatus(): Status`
Get comprehensive system status.

#### `getAvailableKeys(): APIKey[]`
List all available API keys.

#### `monitorUsage(): MonitorStatus`
Get detailed token usage by provider.

#### `rotateKey(sessionId: string, newKeyId?: string): RotationResult`
Manually rotate to different API key.

#### `aggregateTaskResults(taskId: string): AggregatedResult`
Aggregate results from completed tasks.

#### `retryFailedTasks(taskId: string): Promise<TaskResult[]>`
Retry failed sub-tasks.

## Architecture

See [ARCHITECTURE.md](./ARCHITECTURE.md) for detailed system design.

```
┌─────────────────────────────────────┐
│         Butler Skill                 │
├─────────────────────────────────────┤
│                                     │
│  Token Manager                      │
│  ├─ 8 API Keys (6 providers)       │
│  ├─ Real-time usage tracking        │
│  ├─ 75% threshold alerts            │
│  └─ Automatic rotation              │
│                                     │
│  Agent Orchestrator                 │
│  ├─ Task decomposition              │
│  ├─ Budget allocation               │
│  ├─ Sub-agent spawning              │
│  ├─ Parallel execution              │
│  └─ Result aggregation              │
│                                     │
│  Treasury Manager (v0.2)            │
│  ├─ USDC balance monitoring         │
│  ├─ Circle API integration          │
│  ├─ Auto-buy triggers               │
│  └─ Transaction logging             │
│                                     │
│  Security Gate                      │
│  ├─ Code Reviewer integration       │
│  ├─ Pre-commit scanning             │
│  └─ Credential leak prevention      │
│                                     │
└─────────────────────────────────────┘
```

## Configuration

### Environment Variables

```bash
# Optional - defaults to ~/.openclaw/workspace/api-keys.json
BUTLER_KEYS_PATH=/path/to/keys.json

# Optional - defaults to ~/.openclaw/workspace/token-manager-state.json
BUTLER_STATE_PATH=/path/to/state.json

# Treasury config (v0.2)
CIRCLE_API_KEY=your_circle_key
STRIPE_API_KEY=your_stripe_key
AUTO_BUY_ENABLED=true
AUTO_BUY_THRESHOLD=50    # USDC
AUTO_BUY_AMOUNT=200      # USDC
```

## Testing

Run full test suite:

```bash
npm test                  # Run all tests
npm run test:watch      # Watch mode
npm run test:coverage   # Coverage report
```

**Test Coverage:**
- ✅ 45+ test cases
- ✅ TokenManager: 15+ tests
- ✅ AgentOrchestrator: 20+ tests
- ✅ Butler integration: 15+ tests
- ✅ Mock API calls
- ✅ Error scenarios
- ✅ Load testing
- ✅ 80%+ code coverage

## Troubleshooting

### No Keys Available
```
Error: No keys available with sufficient capacity
```
**Solution:** Wait for daily reset at 00:00 UTC, or use multiple keys with smaller budgets.

### Rotation Threshold Exceeded
```
⚠️ [session-id] 75% budget used - Rotation recommended
```
**Solution:** Butler automatically rotates to next available key. Check `getStatus()` for alert details.

### Insufficient Budget for Task
```
Error: No single key has 999999 tokens available
```
**Solution:** Split task into smaller sub-tasks, or wait for daily reset.

## Security

- ✅ Code Reviewer integration prevents credential leaks
- ✅ All state files stored securely (not in git)
- ✅ API keys never logged (only IDs)
- ✅ Pre-commit hooks validate before pushing

**Best Practices:**
1. Always keep `api-keys.json` in `.gitignore`
2. Create private repositories for treasury features
3. Use Code Reviewer before committing
4. Rotate keys regularly (manual or automatic at 75%)

## Performance

- ⚡ Token allocation: <100ms
- ⚡ Agent spawning: <500ms
- ⚡ Result aggregation: O(n) complexity
- ⚡ Concurrent agents: Tested with 10+ simultaneous tasks

## Roadmap (v0.2+)

- [ ] Treasury module with USDC auto-buy
- [ ] Circle CCTP integration
- [ ] Web dashboard for monitoring
- [ ] Machine learning token prediction
- [ ] Multi-sig wallet support
- [ ] Payment splitting between agents
- [ ] Mobile app

## Support

- 📖 Docs: [docs/](./docs/)
- 🐛 Issues: [GitHub Issues](https://github.com/zoro-jiro-san/butler/issues)
- 💬 Discussions: [GitHub Discussions](https://github.com/zoro-jiro-san/butler/discussions)
- 📧 Email: support@openclaw.dev

## License

MIT - See [LICENSE](../LICENSE)

## Contributing

Contributions welcome! See [CONTRIBUTING.md](../CONTRIBUTING.md)

---

**Butler v0.1.0** | Circle USDC Hackathon | Deadline: Feb 8, 2026
