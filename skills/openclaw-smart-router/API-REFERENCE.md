# Smart Router API Reference

Quick reference for TaskAnalyzer and ModelSelector classes.

## TaskAnalyzer

### Constructor

```javascript
const analyzer = new TaskAnalyzer(storage);
```

**Parameters:**
- `storage` - RouterStorage instance

### Methods

#### `analyzeTask(requestData)`

Analyze a task to determine complexity and type.

**Parameters:**
- `requestData` - Object with:
  - `prompt` (string) - User prompt
  - `message` (string) - Alternative to prompt
  - `context` (string) - Additional context
  - `files` (array) - Optional file list
  - `conversation_history` (array) - Optional conversation history

**Returns:** Promise<Object>
```javascript
{
  analysis_id: "uuid",
  timestamp: "2026-02-12T...",
  complexity_score: 0.75,        // 0.0-1.0
  task_type: "code",             // 'code' | 'debugging' | 'reasoning' | 'query' | 'writing'
  estimated_tokens: 1500,
  has_code: true,
  has_errors: false,
  has_reasoning: false,
  is_multi_turn: false,
  keywords: ["function", "async", ...],
  prompt_length: 250,
  context_length: 1000
}
```

#### `calculateComplexity(requestData)`

Calculate complexity score for a request.

**Parameters:**
- `requestData` - Same as analyzeTask

**Returns:** Number (0.0-1.0)

**Scoring Rules:**
- Base: 0.5
- +0.3 if has code blocks
- +0.2 if has errors
- +0.25 if has reasoning keywords
- +0.15 if context > 5000 chars
- +0.2 if has data patterns
- -0.3 if simple query < 500 chars
- -0.2 if generic question

#### `classifyTaskType(requestData)`

Classify the task type.

**Parameters:**
- `requestData` - Same as analyzeTask

**Returns:** String ('code' | 'debugging' | 'reasoning' | 'query' | 'writing')

**Classification Priority:**
1. debugging - if has error messages
2. code - if has code blocks or code keywords
3. reasoning - if has reasoning keywords
4. writing - if mentions write/create/document
5. query - default for simple questions

#### `hasCodeBlocks(text)` → Boolean

Detects:
- Markdown code blocks (```)
- Inline code (>3 backticks)
- Code structures (function, class, etc.)
- Code patterns (braces + keywords)

#### `hasErrorMessages(text)` → Boolean

Detects:
- Error keywords (error, exception, bug, crash, etc.)
- Stack traces (at ... line:col)
- Error codes (EXX, XXXError)

#### `hasReasoningKeywords(text)` → Boolean

Requires 2+ reasoning keywords:
- analyze, explain, evaluate, compare
- decide, optimize, tradeoffs
- debug, troubleshoot, investigate

#### `estimateTokens(text)` → Number

Approximates tokens using `Math.ceil(text.length / 4)`

#### `extractKeywords(text)` → Array<String>

Extracts top keywords (frequency-based, filtered stop words)

#### `getHistoricalPatterns(agentWallet, currentAnalysis, limit)` → Promise<Array>

Retrieves similar past tasks from database.

**Parameters:**
- `agentWallet` - Agent identifier
- `currentAnalysis` - Current analysis object
- `limit` - Max results (default: 50)

---

## ModelSelector

### Constructor

```javascript
const selector = new ModelSelector(storage);
```

**Parameters:**
- `storage` - RouterStorage instance

### Methods

#### `selectModel(taskAnalysis, agentWallet, options)`

Select optimal model for a task.

**Parameters:**
- `taskAnalysis` - Analysis object from TaskAnalyzer
- `agentWallet` - Agent identifier
- `options` - Optional config:
  - `force_model` (string) - Force specific model
  - `max_cost` (number) - Maximum cost in USD
  - `exclude_models` (array) - Models to exclude

**Returns:** Promise<Object>
```javascript
{
  selection_id: "uuid",
  timestamp: "2026-02-12T...",
  model: "claude-sonnet-4-5",
  provider: "anthropic",
  reason: "balanced complexity, optimized for code",
  confidence: 0.87,
  estimated_cost: 0.00375,
  model_details: { ... },
  score_breakdown: {
    complexity_match: 0.95,
    budget_constraint: 0.88,
    pattern_match: 0.75,
    performance: 0.82,
    total: 0.87
  },
  alternatives: [
    { model: "claude-haiku-4-5", score: 0.72, estimated_cost: 0.00125 },
    { model: "gpt-5.2", score: 0.69, estimated_cost: 0.00500 }
  ]
}
```

#### `scoreModels(taskAnalysis, budgetStatus, patterns, options)` → Promise<Array>

Score all available models.

**Returns:** Array of scored models sorted by total_score (descending)

#### Scoring Methods

##### `scoreComplexityMatch(taskAnalysis, model)` → Number (0.0-1.0)

Scores how well model matches task complexity.
- Perfect (1.0) if complexity in model's range
- Distance penalty for out-of-range
- +0.2 bonus if strengths match task type

##### `scoreBudgetConstraint(taskAnalysis, model, budgetStatus, options)` → Number (0.0-1.0)

Scores based on budget constraints.
- 0.0 if over max_cost
- Strong preference for cheap if >80% budget used
- Blend: cost efficiency (70%) + availability (30%)

##### `scorePatternMatch(taskAnalysis, model, patterns)` → Number (0.0-1.0)

Scores based on historical patterns.
- Success rate for similar tasks
- +0.3 if preferred for task type
- 0.5 if no historical data

##### `scorePerformance(model, taskType)` → Promise<Number> (0.0-1.0)

Scores based on 30-day performance.
- Weighted: success rate (60%) + avg quality (40%)
- 0.6 for untested models

#### Utility Methods

##### `estimateCost(model, estimatedTokens)` → Number

Estimates cost in USD.
- Assumes 3:1 input:output ratio
- Uses model's per-1K token pricing

##### `getSelectionReason(score, taskAnalysis, budgetStatus)` → String

Generates human-readable reason.

Examples:
- "high complexity task, optimized for code, premium tier"
- "simple query, cost-efficient, economy tier"
- "balanced complexity, learned from similar tasks, balanced tier"

##### `getBudgetStatus(agentWallet)` → Promise<Object>

Gets current budget status (integrates with Cost Governor).

**Returns:**
```javascript
{
  daily_limit: 10.0,
  daily_spent: 2.5,
  daily_remaining: 7.5,
  daily_utilization: 0.25,
  circuit_breaker_active: false
}
```

##### `getHistoricalPatterns(agentWallet, taskAnalysis)` → Promise<Object>

Retrieves historical patterns for similar tasks.

**Returns:**
```javascript
{
  similar_tasks: [
    { model: "claude-sonnet-4-5", success: true, quality_score: 0.85 },
    ...
  ],
  preferred_models: {
    "code": "claude-sonnet-4-5",
    "reasoning": "gpt-5.2"
  }
}
```

##### `storeSelection(agentWallet, taskAnalysis, selection)` → Promise<void>

Stores selection in database for learning.

##### `updateSelectionResults(selectionId, results)` → Promise<void>

Updates with actual results for learning.

**Parameters:**
- `selectionId` - decision_id from selection
- `results` - Object:
  - `actual_tokens` (number)
  - `actual_cost` (number)
  - `success` (boolean)
  - `quality_score` (number, 0.0-1.0)
  - `response_time_ms` (number)

##### `getModel(modelName)` → Object | null

Gets model definition by name.

##### `getAllModels()` → Array<Object>

Returns all available models.

---

## Available Models

### claude-opus-4-5 (Premium)
- **Complexity Range:** 0.7-1.0
- **Strengths:** reasoning, code, debugging
- **Pricing:** $0.015/$0.075 per 1K tokens (prompt/completion)
- **Max Tokens:** 200,000
- **Best For:** Complex reasoning, advanced debugging, high-quality code generation

### claude-sonnet-4-5 (Balanced)
- **Complexity Range:** 0.4-0.8
- **Strengths:** code, reasoning, writing
- **Pricing:** $0.003/$0.015 per 1K tokens
- **Max Tokens:** 200,000
- **Best For:** Most tasks, balanced cost/quality

### claude-haiku-4-5 (Economy)
- **Complexity Range:** 0.0-0.5
- **Strengths:** query, writing
- **Pricing:** $0.0008/$0.004 per 1K tokens
- **Max Tokens:** 200,000
- **Best For:** Simple queries, quick responses, high volume

### gpt-5.2 (Balanced)
- **Complexity Range:** 0.5-0.9
- **Strengths:** reasoning, code, writing
- **Pricing:** $0.010/$0.030 per 1K tokens
- **Max Tokens:** 128,000
- **Best For:** Alternative to Sonnet, competitive quality

### gemini-2.5-pro (Competitive)
- **Complexity Range:** 0.5-0.9
- **Strengths:** reasoning, code, data
- **Pricing:** $0.005/$0.015 per 1K tokens
- **Max Tokens:** 1,000,000
- **Best For:** Cost-effective complex tasks, large context

---

## Scoring Weights

The selector uses weighted scoring:

- **Complexity Match:** 40% - How well model fits task complexity
- **Budget Constraint:** 30% - Cost efficiency and availability
- **Pattern Match:** 20% - Historical success patterns
- **Performance:** 10% - Historical performance metrics

Total score range: 0.0-1.0 (higher is better)

---

## Usage Examples

### Basic Analysis and Selection

```javascript
import { RouterStorage } from './src/storage.js';
import { TaskAnalyzer } from './src/analyzer.js';
import { ModelSelector } from './src/selector.js';

const storage = new RouterStorage('./router.db');
storage.initialize();

const analyzer = new TaskAnalyzer(storage);
const selector = new ModelSelector(storage);

// Analyze request
const analysis = await analyzer.analyzeTask({
  prompt: "Debug this error: TypeError at line 42",
  context: "Stack trace: ..."
});

// Select model
const selection = await selector.selectModel(
  analysis,
  'agent-wallet-xyz'
);

console.log(`Selected: ${selection.model} - ${selection.reason}`);
console.log(`Cost: $${selection.estimated_cost.toFixed(6)}`);
```

### With Budget Constraints

```javascript
const selection = await selector.selectModel(
  analysis,
  'agent-wallet-xyz',
  { max_cost: 0.01 }  // Max $0.01 per request
);
```

### Force Specific Model

```javascript
const selection = await selector.selectModel(
  analysis,
  'agent-wallet-xyz',
  { force_model: 'claude-opus-4-5' }
);
```

### Update with Results (Learning)

```javascript
await selector.updateSelectionResults(selection.selection_id, {
  actual_tokens: 1250,
  actual_cost: 0.00375,
  success: true,
  quality_score: 0.9,
  response_time_ms: 1500
});
```

---

## Error Handling

Both classes handle errors gracefully:

- **TaskAnalyzer:** Returns default analysis (0.5 complexity, 'query' type) on error
- **ModelSelector:** Falls back to claude-sonnet-4-5 on error
- All database errors are logged but don't crash

Always wrap in try-catch for production:

```javascript
try {
  const analysis = await analyzer.analyzeTask(request);
  const selection = await selector.selectModel(analysis, wallet);
  // Use selection...
} catch (error) {
  console.error('Routing failed:', error);
  // Fallback to default model
}
```

---

**Last Updated:** 2026-02-12
**Version:** 1.0.0
