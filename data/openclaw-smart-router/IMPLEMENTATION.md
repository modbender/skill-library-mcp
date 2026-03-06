# Smart Router - Task Analysis & Model Selection Implementation

## Overview

This implementation provides intelligent task analysis and model selection for the OpenClaw Smart Router. It analyzes incoming requests to determine task complexity and type, then selects the optimal model based on multiple factors including complexity, budget constraints, historical patterns, and performance metrics.

## Files Implemented

### 1. `src/analyzer.js` - TaskAnalyzer Class (478 lines)

**Purpose:** Analyzes incoming requests to determine task complexity and type.

**Key Methods:**

- `analyzeTask(requestData)` - Main analysis entry point
  - Returns: Analysis object with complexity score, task type, token estimates, and features

- `calculateComplexity(requestData)` - Complexity scoring (0.0-1.0)
  - Base: 0.5
  - Has code blocks: +0.3
  - Has errors: +0.2
  - Reasoning keywords: +0.25
  - Context > 5000 chars: +0.15
  - Has data/numbers: +0.2
  - Simple query < 500 chars: -0.3
  - Generic question: -0.2

- `classifyTaskType(requestData)` - Task classification
  - Returns: 'code', 'debugging', 'reasoning', 'query', or 'writing'
  - Priority: debugging > code > reasoning > writing > query

**Feature Detection Methods:**

- `hasCodeBlocks(text)` - Detects code blocks, inline code, code structures
- `hasErrorMessages(text)` - Detects error keywords, stack traces, error codes
- `hasReasoningKeywords(text)` - Detects analytical/reasoning language (needs 2+ keywords)
- `hasDataPatterns(text)` - Detects data keywords, metrics, JSON/arrays
- `isSimpleQuery(text)` - Pattern matching for simple questions
- `isGenericQuestion(text)` - Pattern matching for greetings/confirmations

**Utility Methods:**

- `estimateTokens(text)` - Approximates tokens using text.length / 4
- `extractKeywords(text)` - Extracts top keywords for pattern learning
- `getHistoricalPatterns(agentWallet, currentAnalysis, limit)` - Retrieves similar past tasks from routing_decisions table

**Keyword Sets:**

- Reasoning: analyze, explain, evaluate, compare, optimize, debug, etc. (24 keywords)
- Error: error, exception, bug, crash, warning, etc. (17 keywords)
- Code: function, class, import, async, return, etc. (20 keywords)
- Data: data, metrics, statistics, calculate, query, etc. (15 keywords)

### 2. `src/selector.js` - ModelSelector Class (621 lines)

**Purpose:** Selects the optimal model based on task analysis, budget, patterns, and performance.

**Key Methods:**

- `selectModel(taskAnalysis, agentWallet, options)` - Main selection entry point
  - Returns: Selection object with model, provider, reason, confidence, estimated cost, score breakdown

- `scoreModels(taskAnalysis, budgetStatus, patterns, options)` - Scores all available models
  - Returns: Sorted array of scored models

**Scoring Algorithm:**

Weighted scoring system (weights must sum to 1.0):
- Complexity match: 40% - How well model matches task complexity
- Budget constraint: 30% - Budget availability and cost efficiency
- Pattern match: 20% - Historical pattern matching
- Performance: 10% - Historical success rate

**Individual Scoring Methods:**

- `scoreComplexityMatch(taskAnalysis, model)` - 0.0-1.0
  - Perfect match (1.0) if complexity within model's ideal range
  - Distance penalty for out-of-range
  - Bonus +0.2 if model strengths match task type

- `scoreBudgetConstraint(taskAnalysis, model, budgetStatus, options)` - 0.0-1.0
  - Returns 0.0 if over max_cost option
  - Strong preference for cheaper models if >80% budget utilized
  - Blend of cost efficiency (70%) and availability (30%)

- `scorePatternMatch(taskAnalysis, model, patterns)` - 0.0-1.0
  - Success rate with model for similar tasks
  - Bonus +0.3 if preferred model for task type
  - Returns 0.5 if no historical data

- `scorePerformance(model, taskType)` - 0.0-1.0
  - Queries routing_decisions for last 30 days
  - Combines success rate (60%) and avg quality (40%)
  - Returns 0.6 for untested models (slight positive bias)

**Model Definitions:**

5 models configured with complexity ranges, strengths, and pricing:

1. **claude-opus-4-5** (Premium)
   - Complexity: 0.7-1.0
   - Strengths: reasoning, code, debugging
   - Cost: $0.015/$0.075 per 1K tokens

2. **claude-sonnet-4-5** (Balanced)
   - Complexity: 0.4-0.8
   - Strengths: code, reasoning, writing
   - Cost: $0.003/$0.015 per 1K tokens

3. **claude-haiku-4-5** (Economy)
   - Complexity: 0.0-0.5
   - Strengths: query, writing
   - Cost: $0.0008/$0.004 per 1K tokens

4. **gpt-5.2** (Balanced)
   - Complexity: 0.5-0.9
   - Strengths: reasoning, code, writing
   - Cost: $0.010/$0.030 per 1K tokens

5. **gemini-2.5-pro** (Competitive)
   - Complexity: 0.5-0.9
   - Strengths: reasoning, code, data
   - Cost: $0.005/$0.015 per 1K tokens

**Utility Methods:**

- `estimateCost(model, estimatedTokens)` - Calculates estimated cost (assumes 3:1 input:output ratio)
- `getSelectionReason(score, taskAnalysis, budgetStatus)` - Generates human-readable reason
- `getBudgetStatus(agentWallet)` - Gets current budget status (integrates with Cost Governor)
- `getHistoricalPatterns(agentWallet, taskAnalysis)` - Retrieves similar tasks and preferred models
- `storeSelection(agentWallet, taskAnalysis, selection)` - Stores decision in routing_decisions table
- `updateSelectionResults(selectionId, results)` - Updates with actual results for learning
- `getModel(modelName)` - Gets model definition by name
- `getAllModels()` - Returns all available models

## Database Integration

Both classes integrate with the existing `routing_decisions` table schema:

```sql
CREATE TABLE routing_decisions (
  decision_id TEXT UNIQUE NOT NULL,
  agent_wallet TEXT,
  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,

  -- Task characteristics (from TaskAnalyzer)
  task_complexity REAL,
  context_length INTEGER,
  task_type TEXT,
  has_code BOOLEAN,
  has_errors BOOLEAN,
  has_data BOOLEAN,

  -- Model selection (from ModelSelector)
  selected_model TEXT NOT NULL,
  selected_provider TEXT NOT NULL,
  selection_reason TEXT,
  confidence_score REAL,
  alternatives_json TEXT,

  -- Outcome tracking (for learning)
  was_successful BOOLEAN,
  actual_tokens INTEGER,
  actual_cost_usd REAL,
  response_quality REAL,
  response_time_ms INTEGER,

  pattern_id TEXT
);
```

## Usage Example

```javascript
import { RouterStorage } from './src/storage.js';
import { TaskAnalyzer } from './src/analyzer.js';
import { ModelSelector } from './src/selector.js';

// Initialize
const storage = new RouterStorage('./smart-router.db');
storage.initialize();

const analyzer = new TaskAnalyzer(storage);
const selector = new ModelSelector(storage);

// Analyze a request
const requestData = {
  prompt: 'Analyze the tradeoffs between REST and GraphQL APIs',
  context: 'For a microservices architecture with 50+ services'
};

const analysis = await analyzer.analyzeTask(requestData);
// Returns: {
//   complexity_score: 0.85,
//   task_type: 'reasoning',
//   estimated_tokens: 250,
//   has_code: false,
//   has_errors: false,
//   has_reasoning: true,
//   ...
// }

// Select optimal model
const selection = await selector.selectModel(
  analysis,
  'agent-wallet-address',
  { max_cost: 0.01 }
);
// Returns: {
//   model: 'claude-sonnet-4-5',
//   provider: 'anthropic',
//   reason: 'balanced complexity, optimized for reasoning',
//   confidence: 0.87,
//   estimated_cost: 0.00375,
//   score_breakdown: { ... },
//   alternatives: [ ... ]
// }
```

## Test Results

The test suite (`test-analyzer-selector.js`) validates:

1. **Simple Query** ✓
   - Complexity: 0.20 (expected: 0.0-0.4)
   - Type: query
   - Selected: claude-haiku-4-5 (economy tier)

2. **Code Task** ✓
   - Complexity: 1.00 (high complexity correctly detected)
   - Type: code
   - Selected: gemini-2.5-pro (competitive, cost-efficient)

3. **Debugging Task** ✓
   - Complexity: 0.70 (expected: 0.6-1.0)
   - Type: debugging
   - Selected: claude-sonnet-4-5 (balanced tier)

4. **Reasoning Task** ✓
   - Complexity: 1.00 (high complexity correctly detected)
   - Type: reasoning
   - Selected: gemini-2.5-pro (optimized for reasoning)

5. **Writing Task** ✓
   - Complexity: 0.50 (expected: 0.3-0.6)
   - Type: writing
   - Selected: claude-haiku-4-5 (economy tier)

All tests pass with intelligent model selection based on task characteristics.

## Integration with SmartRouter

The classes are already integrated in `src/index.js`:

```javascript
export class SmartRouter {
  constructor(options = {}) {
    this.storage = new RouterStorage(dbPath);
    this.analyzer = new TaskAnalyzer(this.storage);
    this.selector = new ModelSelector(this.storage);
    this.learner = new PatternLearner(this.storage);
    // ...
  }

  async beforeRequest(requestId, agentWallet, requestData) {
    // 1. Analyze task
    const taskAnalysis = await this.analyzer.analyzeTask(requestData);

    // 2. Select model
    const modelSelection = await this.selector.selectModel(
      taskAnalysis,
      agentWallet,
      options
    );

    // 3. Record decision
    this.storage.recordDecision({ ... });

    // 4. Return selected model
    return modelSelection;
  }

  async afterRequest(requestId, agentWallet, request, response) {
    // Learn from outcome for future improvement
    await this.learner.learnFromOutcome(decisionId, outcome);
  }
}
```

## Key Features

### TaskAnalyzer

- ✓ Multi-factor complexity scoring
- ✓ 5 task type classification
- ✓ Feature detection (code, errors, reasoning, data)
- ✓ Token estimation
- ✓ Keyword extraction for pattern learning
- ✓ Historical pattern retrieval

### ModelSelector

- ✓ 5 model definitions with pricing
- ✓ 4-factor weighted scoring algorithm
- ✓ Budget-aware selection
- ✓ Pattern-based learning
- ✓ Performance tracking
- ✓ Alternative model suggestions
- ✓ Human-readable selection reasons
- ✓ Database integration for learning

## Performance Characteristics

- **Complexity Calculation:** O(n) where n = text length
- **Task Classification:** O(n) with early termination
- **Model Scoring:** O(m) where m = number of models (5)
- **Database Queries:** Indexed lookups on agent_wallet, task_type, timestamp
- **Memory:** Minimal - primarily keyword sets and model definitions

## Future Enhancements

Potential areas for improvement:

1. **Dynamic Pricing:** Real-time pricing updates from providers
2. **A/B Testing:** Experimental model selection for exploration
3. **User Feedback:** Incorporate explicit user satisfaction ratings
4. **Multi-Language:** Expand keyword sets for non-English tasks
5. **Custom Models:** Support for user-defined model configurations
6. **Cost Prediction:** ML-based cost prediction improvements
7. **Context Window:** Smart handling of token limit constraints

## Dependencies

- `better-sqlite3` - Database operations
- `crypto` - UUID generation for IDs
- Node.js built-ins: `os`, `path`, `fs`

## License

MIT - Part of the OpenClaw ecosystem

---

**Implementation Date:** 2026-02-12
**Version:** 1.0.0
**Status:** Complete and tested
