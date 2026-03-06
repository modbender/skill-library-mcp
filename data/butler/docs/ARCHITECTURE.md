# Butler Architecture

## System Overview

Butler is composed of four main components working together as an autonomous AI economic system:

```
                        ┌─────────────────────────┐
                        │   OpenClaw Framework    │
                        │   (Task Spawning)       │
                        └────────────┬────────────┘
                                     │
                    ┌────────────────┼────────────────┐
                    │                │                │
            ┌───────▼────────┐  ┌───▼──────────┐  ┌──▼──────────┐
            │  Token Manager │  │  Orchestrator│  │  Treasury   │
            │  (Finances)    │  │  (Logistics) │  │  (Economics)│
            └────────┬───────┘  └───┬──────────┘  └──┬──────────┘
                     │              │               │
                     └──────────────┼───────────────┘
                                    │
                        ┌───────────▼───────────┐
                        │  Code Reviewer Gate   │
                        │  (Security)           │
                        └───────────┬───────────┘
                                    │
                        ┌───────────▼───────────┐
                        │  State & Audit Log    │
                        │  (Persistence)        │
                        └───────────────────────┘
```

## Component 1: Token Manager

**Role:** Finance Department for API keys

**Responsibilities:**
- Track 8 API keys across 6 providers
- Monitor token usage in real-time
- Allocate optimal keys for tasks
- Alert before exhaustion (75% threshold)
- Rotate keys automatically
- Predict cost per task

**Architecture:**

```typescript
TokenManager
├── keys: Map<keyId, APIKey>
│   ├── id: string
│   ├── provider: string
│   ├── model: string
│   ├── limits: { tokens_per_day, tokens_per_month }
│   ├── usage: { today, this_month, last_reset }
│   ├── status: 'active' | 'inactive' | 'exhausted'
│   ├── cost_per_1k_tokens: number
│   └── priority: number
│
├── allocations: Map<sessionId, Allocation>
│   ├── key_id: string
│   ├── allocated_tokens: number
│   ├── rotation_threshold: number (75%)
│   ├── used_tokens: number
│   └── status: 'active' | 'completed' | 'failed'
│
├── alerts: Array<Alert>
│   ├── type: 'rotation_needed' | 'exhausted'
│   ├── severity: 'warning' | 'critical'
│   └── session: string
│
└── history: Array<HistoryEntry>
    ├── timestamp: string
    ├── action: 'allocation' | 'rotation' | 'usage_update'
    └── details: any
```

**Key Methods:**

```typescript
estimateTokensForPRD(path: string): Estimate
  // Analyzes PRD text for complexity indicators
  // Returns: { estimated, confidence, reasoning }
  // Multipliers: code (2x), API (1.5x), integration (1.5x), sub-agents (1x)

selectKey(requiredTokens, provider?): AllocationResult
  // Selects optimal key based on:
  // 1. Priority (free tier > paid)
  // 2. Available capacity
  // 3. Cost efficiency
  // Returns allocation or alternatives

trackSession(sessionId, allocation, metadata)
  // Records allocation in persistent state
  // Enables monitoring and auditing

monitorSession(sessionId): boolean
  // Checks if usage >= threshold (75%)
  // Returns true if rotation needed
  // Creates alert if threshold exceeded

rotateKey(sessionId, newKeyId?): RotationResult
  // Moves remaining budget to new key
  // Auto-selects if not specified
  // Logs rotation event
```

**Data Flow:**

```
Task Estimate
    ↓
selectKey() ──→ Choose from available
    ↓
trackSession() ──→ Record in state
    ↓
getAvailableKeys() ──→ Filtered by capacity
    ↓
monitorSession() ──→ Check threshold
    ↓
rotateKey() (if needed)
    ↓
getStatus() ──→ Report metrics
```

**Token Allocation Algorithm:**

```
Input: requiredTokens, preferredProvider
  ↓
1. Filter available keys
   - Only active keys
   - Only with > 10k tokens available
  ↓
2. Filter by provider (if specified)
   - Expand search if no matches
  ↓
3. Filter by capacity
   - Only keys with >= requiredTokens
  ↓
4. Sort candidates
   - Priority (higher = better)
   - Capacity (more = better)
   - Cost (lower = better)
  ↓
5. Select first (best)
   - Calculate rotation_threshold = 75% of required
   - Calculate cost_estimate
   - Calculate available_capacity
  ↓
Output: AllocationResult { success, key_id, provider, allocated, ... }
```

## Component 2: Agent Orchestrator

**Role:** Logistics Manager for task execution

**Responsibilities:**
- Decompose complex tasks into sub-tasks
- Spawn OpenClaw sub-agents
- Allocate budget to each sub-task
- Manage concurrent execution
- Aggregate results
- Handle failures and retries

**Architecture:**

```typescript
AgentOrchestrator
├── tasks: Map<taskId, AgentTask>
│   ├── id: string
│   ├── name: string
│   ├── description: string
│   ├── totalBudget: number
│   ├── subTasks: SubTask[]
│   ├── maxConcurrent: number
│   ├── retryOnFailure: boolean
│   ├── maxRetries: number
│   └── timeoutMs: number
│
├── results: Map<taskId, TaskResult[]>
│   ├── taskId: string
│   ├── subTaskId: string
│   ├── status: 'success' | 'failure' | 'pending'
│   ├── tokensUsed: number
│   ├── result?: any
│   ├── error?: string
│   └── duration: number
│
├── activeSessions: Map<sessionId, AgentSpawnResult>
│   ├── sessionId: string
│   ├── provider: string
│   ├── allocatedBudget: number
│   └── status: 'running' | 'completed' | 'failed'
│
└── tokenManager: TokenManager (reference)
```

**Task Decomposition Algorithm:**

```
Input: Task with description
  ↓
IF task.subTasks provided:
  Use provided sub-tasks
ELSE:
  1. Split description by spaces
  2. Scan for keywords: research, analyze, write, validate, etc.
  3. Create sub-task when keyword found
  4. Set estimatedTokens = word_count / 0.75
  5. Set priority = 'medium' (default)
  6. Set dependencies = previous sub-task (sequential)
  ↓
Output: SubTask[]
  - Each has id, description, estimatedTokens, priority, dependencies
```

**Budget Allocation Algorithm:**

```
Input: Task with subTasks and totalBudget
  ↓
1. Calculate total estimated tokens
   totalEstimated = sum(subTask.estimatedTokens)
  ↓
2. For each subTask:
   a. Get priority multiplier:
      - low: 0.5x
      - medium: 1.0x
      - high: 1.5x
      - critical: 2.0x
   
   b. Calculate weighted tokens:
      weighted = estimatedTokens * multiplier
   
   c. Calculate allocation:
      allocation = (weighted / totalEstimated) * totalBudget
      (rounded up to nearest 100)
  ↓
3. Return Map<subTaskId, allocatedTokens>
```

**Execution Flow:**

```
executeTask(task)
  ↓
1. Decompose task
   └─ subTasks = decomposeTask(task)
  ↓
2. Allocate budget
   └─ allocation = allocateBudget(task)
  ↓
3. Spawn agents (with concurrency control)
   for each subTask:
     └─ If inFlight.size < maxConcurrent:
         └─ spawnSubAgent(task, subTask, budget)
  ↓
4. Wait for dependencies
   └─ waitForDependencies(subTask.dependencies, results)
  ↓
5. Collect results
   └─ taskResults.push({
       taskId, subTaskId, status,
       tokensUsed, result, error
     })
  ↓
6. Aggregate
   └─ results.set(task.id, taskResults)
  ↓
Output: TaskResult[]
```

**Sub-Agent Spawning:**

```typescript
spawnSubAgent(task, subTask, budget)
  ↓
1. Select key from TokenManager
   allocation = tokenManager.selectKey(budget)
  ↓
2. Create session ID
   sessionId = `butler-${task.id}-${subTask.id}-${time}`
  ↓
3. Track session
   tokenManager.trackSession(sessionId, allocation, {
     prd: subTask.description,
     agent_name: `agent-${task.name}`
   })
  ↓
4. Spawn OpenClaw sub-agent (framework integration)
   - Label: butler-${taskName}
   - Thinking level: high
   - Model: allocation.model
   - Budget: allocation.allocated tokens
  ↓
5. Return session info
   {
     success: true,
     sessionId,
     provider,
     allocatedBudget,
     keyId
   }
```

**Result Aggregation:**

```
aggregateResults(taskId)
  ↓
For each TaskResult in results[taskId]:
  - Count successes
  - Count failures
  - Sum tokensUsed
  - Calculate successRate = success / total * 100
  - Create details array with each result
  ↓
Return:
{
  taskId,
  totalSubTasks: count,
  successful: count,
  failed: count,
  totalTokensUsed: number,
  successRate: number,
  details: [
    { id, status, tokensUsed, error }
  ]
}
```

## Component 3: Butler (Main API)

**Role:** Chief Financial Officer

**Responsibilities:**
- Unified interface to Token Manager and Orchestrator
- High-level API for common operations
- Status reporting
- Version management

**Architecture:**

```typescript
Butler
├── tokenManager: TokenManager
├── orchestrator: AgentOrchestrator
└── version: string = '0.1.0'

Methods:
├── allocateTokens(prd, provider?) → AllocationResult
├── spawnAgent(name, description, budget, options?) → TaskResult[]
├── getStatus() → Status
├── getAvailableKeys() → APIKey[]
├── monitorUsage() → MonitorStatus
├── rotateKey(sessionId, newKeyId?) → RotationResult
├── aggregateTaskResults(taskId) → AggregatedResult
└── retryFailedTasks(taskId) → TaskResult[]
```

**State Management:**

```
Butler State
├── token-manager-state.json
│   ├── timestamp
│   ├── keys: { keyId: { usage, status } }
│   ├── allocations: { sessionId: { ... } }
│   ├── alerts: [...]
│   └── history: [...]
│
└── Persistence
    ├── Auto-save after each operation
    ├── Daily reset of token counters
    └── Permanent history log
```

## Component 4: Security Gate

**Role:** Security & Compliance Officer

**Responsibilities:**
- Pre-commit code scanning
- Credential leak prevention
- Secure state file handling
- Audit logging

**Integration Points:**

```
Git Commit
  ↓
Code Reviewer (pre-commit hook)
  ├─ Scan staged files
  ├─ Check for API keys (sk-, nvapi-, etc.)
  ├─ Check for credentials (.env, *-keys.json)
  ├─ Check for sensitive patterns
  ↓
IF issues found:
  ├─ Block commit
  ├─ Report issues
  └─ Wait for fix
ELSE:
  ├─ Allow commit
  └─ Proceed with push
```

**Best Practices:**

```bash
# 1. Always use private repos
gh repo create butler --private

# 2. Git will auto-run Code Reviewer
git add .
git commit -m "Add feature"  # Blocked if credentials found

# 3. Fix issues
vim .gitignore  # Add api-keys.json

# 4. Commit again
git add .
git commit -m "Add feature"  # Now passes

# 5. Push (only to private repos)
git push origin main

# 6. After review, make public
# GitHub Settings → Private → Public
```

## Data Flow Examples

### Example 1: Token Allocation

```
User Input:
  butler.allocateTokens('PRD-integration.md', 'anthropic')
  
Step 1: Estimate tokens
  ├─ Read file: "Integrate API, write tests, deploy"
  ├─ Analyze: 150 words, has code, has integration
  ├─ Calculate: base 200 * 2.5x multiplier = 500 estimated
  └─ Confidence: 0.8
  
Step 2: Select key
  ├─ Filter: active keys with > 500 tokens available
  ├─ Filter: provider == 'anthropic'
  ├─ Sort: priority, capacity, cost
  └─ Select: anthropic-1
  
Step 3: Calculate rotation threshold
  └─ 500 * 0.75 = 375 tokens (alert at this usage)
  
Output:
{
  success: true,
  key_id: 'anthropic-1',
  provider: 'anthropic',
  allocated: 500,
  rotation_threshold: 375,
  available_capacity: 950000,
  cost_estimate: 0.0075
}
```

### Example 2: Task Execution

```
User Input:
  butler.spawnAgent(
    'Analysis',
    'Research market trends, analyze data, write report',
    100000,
    { maxConcurrent: 2 }
  )

Step 1: Decompose task
  └─ "research market trends"  (35k tokens)
     "analyze data"             (33k tokens)
     "write report"             (32k tokens)

Step 2: Allocate budget
  └─ By priority (all medium, so proportional):
     "research" → 35000 tokens
     "analyze"  → 33000 tokens
     "write"    → 32000 tokens

Step 3: Spawn agents (maxConcurrent: 2)
  ├─ Spawn agent 1: research (nvidia-1, 35k tokens)
  ├─ Spawn agent 2: analyze (groq-1, 33k tokens)
  └─ Wait for agent 1 to complete
  └─ Spawn agent 3: write (anthropic-1, 32k tokens)

Step 4: Aggregate results
  ├─ Task 1 (research): success, 28000 tokens
  ├─ Task 2 (analyze): success, 31000 tokens
  └─ Task 3 (write): failure, 2000 tokens (timeout)
  
Output:
{
  taskId: 'task-...',
  totalSubTasks: 3,
  successful: 2,
  failed: 1,
  totalTokensUsed: 61000,
  successRate: 66.7%,
  details: [...]
}
```

## Persistence & Recovery

### State File Structure

```json
{
  "timestamp": "2026-02-05T21:00:00Z",
  "keys": {
    "nvidia-1": {
      "usage": { "today": 500000, "this_month": 15000000 },
      "status": "active"
    },
    "anthropic-1": {
      "usage": { "today": 250000, "this_month": 7500000 },
      "status": "active"
    }
  },
  "allocations": {
    "session-xyz": {
      "key_id": "nvidia-1",
      "allocated_tokens": 100000,
      "rotation_threshold": 75000,
      "used_tokens": 45000,
      "status": "active",
      "started": "2026-02-05T20:00:00Z"
    }
  },
  "alerts": [
    {
      "id": "alert-1",
      "type": "rotation_needed",
      "severity": "warning",
      "session": "session-xyz",
      "message": "75% budget used"
    }
  ],
  "history": [
    {
      "timestamp": "2026-02-05T20:00:00Z",
      "action": "allocation",
      "session": "session-xyz",
      "key_id": "nvidia-1",
      "tokens": 100000
    }
  ]
}
```

### Daily Reset

```typescript
checkDailyReset()
  ├─ Get current date
  ├─ For each key:
  │   ├─ Get last reset date
  │   └─ If date changed:
  │       └─ Reset usage.today = 0
  │          Update last_reset timestamp
  └─ Save state
```

## Performance Characteristics

| Operation | Complexity | Time |
|-----------|-----------|------|
| selectKey() | O(n log n) | <100ms |
| decomposeTask() | O(n) | <50ms |
| allocateBudget() | O(n) | <10ms |
| spawnAgent() | O(1) | <500ms |
| aggregateResults() | O(n) | <50ms |
| getStatus() | O(n) | <100ms |

**Scaling:**
- ✅ Handles 100+ concurrent sessions
- ✅ Supports 1000+ allocations per day
- ✅ State file < 1MB for typical usage
- ✅ Memory usage: ~50MB for normal operations

## Future Enhancements (v0.2+)

### Treasury Integration
```
Butler Treasury
├── Circle USDC API
├── Balance monitoring
├── Auto-buy triggers
├── Transaction logging
└── Payment methods
    ├─ Stripe
    ├─ PayPal
    └─ Crypto faucet
```

### ML Token Prediction
```
Token Predictor
├── Historical usage analysis
├── Task complexity ML model
├── Token requirement prediction
└── Cost optimization suggestions
```

### Dashboard
```
Web Dashboard
├── Real-time token tracking
├── Agent execution monitoring
├── Cost analysis
├── Alert management
└── Configuration panel
```

---

This architecture ensures Butler is:
- **Scalable:** Handles 100+ concurrent agents
- **Reliable:** Persistent state, error recovery, retries
- **Secure:** Pre-commit scanning, credential prevention
- **Auditable:** Full history of all operations
- **Extensible:** Clear component boundaries, easy to add features

