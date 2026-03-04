# Smart Router: Routing Guide

A deep dive into how OpenClaw Smart Router analyzes complexity, selects models, learns patterns, and optimizes costs.

## Table of Contents

1. [Complexity Analysis](#complexity-analysis)
2. [Model Selection Algorithm](#model-selection-algorithm)
3. [Pattern Learning Mechanics](#pattern-learning-mechanics)
4. [Budget-Aware Routing](#budget-aware-routing)
5. [Routing Decision Examples](#routing-decision-examples)
6. [Performance Optimization](#performance-optimization)
7. [Advanced Configuration](#advanced-configuration)

---

## Complexity Analysis

### Overview

Smart Router analyzes each request and assigns a complexity score from 0.0 (trivial) to 1.0 (expert-level). This score determines which model is most appropriate for the task.

### Complexity Factors

The complexity score is calculated using a weighted combination of factors:

```javascript
complexity = (
  context_length_score * 0.20 +
  task_type_score * 0.25 +
  code_presence_score * 0.15 +
  error_presence_score * 0.15 +
  query_structure_score * 0.15 +
  specificity_score * 0.10
)
```

### 1. Context Length Score (20% weight)

**Rationale:** Longer context typically indicates more complex tasks requiring better models.

```javascript
function calculateContextLengthScore(tokens) {
  if (tokens < 500) return 0.1;
  if (tokens < 1500) return 0.3;
  if (tokens < 3000) return 0.5;
  if (tokens < 5000) return 0.7;
  return 0.9;
}
```

**Examples:**
- 200 tokens (simple greeting) → 0.1
- 1000 tokens (medium discussion) → 0.3
- 4000 tokens (complex codebase context) → 0.7

### 2. Task Type Score (25% weight)

**Rationale:** Different task types have inherent complexity levels.

```javascript
const TASK_TYPE_SCORES = {
  'greeting': 0.05,
  'simple_query': 0.15,
  'writing': 0.25,
  'code_formatting': 0.30,
  'code_writing': 0.45,
  'code_refactoring': 0.55,
  'debugging': 0.65,
  'architecture': 0.75,
  'reasoning': 0.80,
  'research': 0.85,
  'novel_problem': 0.95
};

function detectTaskType(query) {
  // Pattern matching and keyword analysis
  if (/^(hi|hello|hey)\b/i.test(query)) return 'greeting';
  if (/\b(debug|error|exception|bug)\b/i.test(query)) return 'debugging';
  if (/\b(design|architect|system)\b/i.test(query)) return 'architecture';
  // ... more patterns
}
```

**Examples:**
- "Hello!" → greeting (0.05)
- "Write a function to sort an array" → code_writing (0.45)
- "Debug this race condition" → debugging (0.65)
- "Design a distributed cache" → architecture (0.75)

### 3. Code Presence Score (15% weight)

**Rationale:** Code analysis requires stronger reasoning capabilities.

```javascript
function calculateCodePresenceScore(query) {
  const codeBlockCount = (query.match(/```/g) || []).length / 2;
  const inlineCodeCount = (query.match(/`[^`]+`/g) || []).length;
  const codeLines = estimateCodeLines(query);

  let score = 0;

  if (codeBlockCount > 0) score += 0.3;
  if (codeBlockCount > 2) score += 0.2;
  if (inlineCodeCount > 5) score += 0.2;
  if (codeLines > 50) score += 0.2;
  if (codeLines > 200) score += 0.3;

  return Math.min(score, 1.0);
}
```

**Examples:**
- No code → 0.0
- Small code snippet → 0.3
- Multiple code blocks → 0.5
- Large codebase → 0.8-1.0

### 4. Error Presence Score (15% weight)

**Rationale:** Debugging errors requires sophisticated analysis.

```javascript
function calculateErrorPresenceScore(query) {
  const errorPatterns = [
    /error:/i,
    /exception:/i,
    /traceback/i,
    /stack trace/i,
    /\bat line \d+/i,
    /failed|failure/i,
    /\bnull pointer\b/i,
    /\bundefined is not/i,
    /cannot read property/i
  ];

  let score = 0;
  let matchCount = 0;

  for (const pattern of errorPatterns) {
    if (pattern.test(query)) matchCount++;
  }

  if (matchCount >= 1) score = 0.5;
  if (matchCount >= 3) score = 0.7;
  if (matchCount >= 5) score = 0.9;

  // Bonus for multiple different error types
  if (query.includes('Error:') && query.includes('at line')) {
    score += 0.1;
  }

  return Math.min(score, 1.0);
}
```

**Examples:**
- No errors → 0.0
- Single error message → 0.5
- Multiple errors with stack trace → 0.9

### 5. Query Structure Score (15% weight)

**Rationale:** Complex queries with multiple parts require better understanding.

```javascript
function calculateQueryStructureScore(query) {
  let score = 0;

  // Multiple questions
  const questionCount = (query.match(/\?/g) || []).length;
  if (questionCount > 1) score += 0.2;
  if (questionCount > 3) score += 0.2;

  // Multiple sentences
  const sentenceCount = query.split(/[.!?]+/).length;
  if (sentenceCount > 3) score += 0.2;
  if (sentenceCount > 6) score += 0.2;

  // Nested logic (if/then, when/then)
  if (/\bif\b.*\bthen\b|\bwhen\b.*\bthen\b/i.test(query)) {
    score += 0.3;
  }

  // Lists and enumerations
  if (/\b\d+\.|[a-z]\)|\n\s*[-*]/g.test(query)) {
    score += 0.2;
  }

  return Math.min(score, 1.0);
}
```

**Examples:**
- Single question → 0.0
- Multiple related questions → 0.4
- Complex multi-part query with conditions → 0.8

### 6. Specificity Score (10% weight)

**Rationale:** Vague requests need stronger models to interpret intent.

```javascript
function calculateSpecificityScore(query) {
  let vagueScore = 0;

  const vagueTerms = [
    'somehow', 'something', 'anything', 'whatever',
    'stuff', 'things', 'some way', 'figure out',
    'make it work', 'fix it', 'improve', 'better'
  ];

  for (const term of vagueTerms) {
    if (query.toLowerCase().includes(term)) {
      vagueScore += 0.15;
    }
  }

  // Specific details reduce score
  const specificPatterns = [
    /\b\d+\s*(px|em|rem|pt|%)\b/,  // Specific measurements
    /\bversion\s+\d+/i,              // Specific versions
    /\bline\s+\d+\b/,                // Specific line numbers
    /\b[A-Z][a-zA-Z]+Error\b/        // Specific error types
  ];

  let specificCount = 0;
  for (const pattern of specificPatterns) {
    if (pattern.test(query)) specificCount++;
  }

  vagueScore -= specificCount * 0.1;

  return Math.max(0, Math.min(vagueScore, 1.0));
}
```

**Examples:**
- "Fix the API endpoint at line 42 to return 404" → 0.0 (very specific)
- "Make it better" → 0.9 (very vague)
- "Improve the performance somehow" → 0.6 (moderately vague)

### Complete Complexity Calculation

**Example 1: Simple Query**
```
Query: "What's the time?"
- Context length: 20 tokens → 0.1 × 0.20 = 0.02
- Task type: simple_query → 0.15 × 0.25 = 0.0375
- Code presence: none → 0.0 × 0.15 = 0.0
- Error presence: none → 0.0 × 0.15 = 0.0
- Query structure: single question → 0.1 × 0.15 = 0.015
- Specificity: very specific → 0.0 × 0.10 = 0.0

Total complexity: 0.0725 ≈ 0.07 (Simple)
Recommended: Claude Haiku 4.5
```

**Example 2: Medium Complexity**
```
Query: "Refactor this 150-line class to use dependency injection:
[code block with 150 lines]"

- Context length: 2000 tokens → 0.5 × 0.20 = 0.10
- Task type: code_refactoring → 0.55 × 0.25 = 0.1375
- Code presence: 150 lines → 0.7 × 0.15 = 0.105
- Error presence: none → 0.0 × 0.15 = 0.0
- Query structure: clear instruction → 0.2 × 0.15 = 0.03
- Specificity: specific pattern → 0.1 × 0.10 = 0.01

Total complexity: 0.3825 ≈ 0.38 (Medium)
Recommended: Claude Sonnet 4.5
```

**Example 3: High Complexity**
```
Query: "I'm getting this error somehow in my microservices:
[multiple error stack traces]
Figure out what's causing the race condition and fix it"

- Context length: 4500 tokens → 0.7 × 0.20 = 0.14
- Task type: debugging → 0.65 × 0.25 = 0.1625
- Code presence: multiple blocks → 0.6 × 0.15 = 0.09
- Error presence: multiple errors → 0.8 × 0.15 = 0.12
- Query structure: multi-part → 0.5 × 0.15 = 0.075
- Specificity: vague ("somehow") → 0.6 × 0.10 = 0.06

Total complexity: 0.6475 ≈ 0.65 (Complex)
Recommended: Claude Opus 4.5
```

---

## Model Selection Algorithm

### Decision Tree

```
START
  │
  ├─ Is quota exceeded? (Free tier: 100/day)
  │   YES → Use default model, log quota event, suggest upgrade
  │   NO  → Continue
  │
  ├─ Calculate complexity score (0.0-1.0)
  │
  ├─ Check learned patterns
  │   Pattern exists for this task type?
  │     YES → Adjust complexity score based on pattern
  │     NO  → Continue with calculated score
  │
  ├─ Check budget constraints
  │   Budget exceeded?
  │     YES → Apply budget-constrained routing
  │     NO  → Continue with optimal routing
  │
  ├─ Select model tier based on complexity:
  │
  │   0.0 - 0.3 (Simple)
  │   ├─ Primary: Haiku / GPT-3.5 / Gemini Flash
  │   └─ Cost: ~$0.001 per request
  │
  │   0.3 - 0.6 (Medium)
  │   ├─ Primary: Sonnet / GPT-4 Turbo / Gemini Pro
  │   └─ Cost: ~$0.005 per request
  │
  │   0.6 - 0.8 (Complex)
  │   ├─ Primary: Opus / GPT-4 / Gemini Pro
  │   └─ Cost: ~$0.015 per request
  │
  │   0.8 - 1.0 (Expert)
  │   ├─ Primary: Opus / GPT-4
  │   └─ Cost: ~$0.015-0.030 per request
  │
  ├─ Check provider preferences
  │   └─ Select specific model from preferred provider
  │
  ├─ Verify model availability
  │   Model available?
  │     YES → Route to model
  │     NO  → Fallback to alternative
  │
  └─ Log decision and route request
```

### Threshold Configuration

**Default Thresholds:**
```json
{
  "thresholds": {
    "haiku_max": 0.3,
    "sonnet_min": 0.3,
    "sonnet_max": 0.6,
    "opus_min": 0.6
  }
}
```

**Adaptive Thresholds:**

Thresholds adjust based on pattern learning:

```javascript
function adjustThresholds(patterns) {
  // If Haiku is failing frequently, lower the threshold
  const haikuFailureRate = patterns.haiku.failures / patterns.haiku.total;
  if (haikuFailureRate > 0.3) {
    thresholds.haiku_max -= 0.05;  // Be more conservative
  }

  // If Opus is succeeding on lower complexity, raise Sonnet threshold
  const opusOverkillRate = patterns.opus.successOnLowComplexity / patterns.opus.total;
  if (opusOverkillRate > 0.2) {
    thresholds.sonnet_max += 0.05;  // Trust Sonnet more
  }
}
```

### Model Capabilities Matrix

```javascript
const MODEL_CAPABILITIES = {
  'claude-haiku-4-5': {
    max_complexity: 0.4,
    best_for: ['greeting', 'simple_query', 'code_formatting'],
    speed: 'fast',
    cost_per_1k_input: 0.0001,
    cost_per_1k_output: 0.0003
  },
  'claude-sonnet-4-5': {
    max_complexity: 0.7,
    best_for: ['code_writing', 'code_refactoring', 'writing', 'simple_debugging'],
    speed: 'medium',
    cost_per_1k_input: 0.0003,
    cost_per_1k_output: 0.0015
  },
  'claude-opus-4-5': {
    max_complexity: 1.0,
    best_for: ['debugging', 'architecture', 'reasoning', 'research', 'novel_problem'],
    speed: 'slower',
    cost_per_1k_input: 0.0015,
    cost_per_1k_output: 0.0075
  }
};
```

### Selection Logic

```javascript
function selectModel(complexity, taskType, budget, patterns) {
  // Check for learned patterns first
  const learnedModel = checkLearnedPatterns(taskType, complexity, patterns);
  if (learnedModel) {
    return {
      model: learnedModel,
      reasoning: 'pattern_match',
      confidence: patterns[taskType].confidence
    };
  }

  // Budget-constrained routing
  if (budget.isConstrained) {
    return selectBudgetConstrainedModel(complexity, budget);
  }

  // Optimal routing based on complexity
  if (complexity < thresholds.haiku_max) {
    return {
      model: 'claude-haiku-4-5',
      reasoning: 'simple_task',
      confidence: 0.9
    };
  } else if (complexity < thresholds.sonnet_max) {
    return {
      model: 'claude-sonnet-4-5',
      reasoning: 'medium_complexity',
      confidence: 0.85
    };
  } else {
    return {
      model: 'claude-opus-4-5',
      reasoning: 'high_complexity',
      confidence: 0.95
    };
  }
}
```

---

## Pattern Learning Mechanics

### Learning System Architecture

```
Request → Complexity Analysis → Model Selection → Response
                                      ↓
                                  Outcome
                                      ↓
                        ┌─────────────────────────┐
                        │  Was selection optimal? │
                        └───────────┬─────────────┘
                                    ↓
                        ┌────────────────────────┐
                        │  Update Pattern DB     │
                        │  - Task type           │
                        │  - Complexity range    │
                        │  - Success/failure     │
                        │  - Model used          │
                        └────────────────────────┘
                                    ↓
                        ┌────────────────────────┐
                        │  Adjust Future Routes  │
                        └────────────────────────┘
```

### Pattern Database Schema

From the migration file, patterns are stored as:

```sql
CREATE TABLE routing_patterns (
  pattern_id TEXT UNIQUE,
  agent_wallet TEXT,
  pattern_type TEXT,              -- 'task_based', 'complexity_based', 'budget_based'
  pattern_description TEXT,

  -- Matching criteria
  task_type TEXT,
  complexity_min REAL,
  complexity_max REAL,
  context_length_min INTEGER,
  context_length_max INTEGER,
  keywords_json TEXT,

  -- Recommendation
  recommended_model TEXT,
  recommended_provider TEXT,

  -- Performance
  success_count INTEGER,
  failure_count INTEGER,
  avg_cost_saved REAL,
  avg_quality REAL,
  confidence REAL,

  created_at DATETIME,
  last_used DATETIME,
  last_updated DATETIME
);
```

### Pattern Types

**1. Task-Based Patterns**

Learns optimal models for specific task types.

```javascript
{
  pattern_type: 'task_based',
  pattern_description: 'Python debugging tasks',
  task_type: 'debugging',
  keywords_json: JSON.stringify(['python', 'error', 'traceback']),
  recommended_model: 'claude-sonnet-4-5',
  success_count: 15,
  failure_count: 2,
  confidence: 0.88
}
```

**Example learning:**
```
Attempt 1: "Debug Python error" → Haiku → Failed
Attempt 2: "Debug Python error" → Haiku → Failed
Attempt 3: "Debug Python error" → Sonnet → Success
Attempt 4: "Debug Python error" → Sonnet → Success
Attempt 5: "Debug Python error" → Sonnet → Success

Pattern created:
  Task: Python debugging
  Model: Sonnet+
  Confidence: 0.8
```

**2. Complexity-Based Patterns**

Learns when calculated complexity scores are wrong.

```javascript
{
  pattern_type: 'complexity_based',
  pattern_description: 'Complexity 0.4-0.5 underestimated',
  complexity_min: 0.4,
  complexity_max: 0.5,
  recommended_model: 'claude-sonnet-4-5',  // Upgrade from Haiku
  success_count: 25,
  failure_count: 5,
  confidence: 0.83
}
```

**Example learning:**
```
Complexity 0.45 tasks:
- Haiku: 30% success rate
- Sonnet: 90% success rate

Pattern: Upgrade 0.4-0.5 complexity tasks to Sonnet
Adjustment: Lower haiku_max threshold from 0.5 to 0.4
```

**3. Budget-Based Patterns**

Learns cost-effective routing under budget constraints.

```javascript
{
  pattern_type: 'budget_based',
  pattern_description: 'Budget-constrained refactoring',
  task_type: 'code_refactoring',
  complexity_min: 0.5,
  complexity_max: 0.6,
  recommended_model: 'claude-sonnet-4-5',  // Instead of Opus
  avg_cost_saved: 0.010,
  avg_quality: 0.85,
  confidence: 0.75
}
```

**Example learning:**
```
When budget constrained:
- Task: Refactoring (complexity 0.55)
- Tried Opus: Excellent quality, too expensive
- Tried Sonnet: Good quality, 3x cheaper
- Tried Haiku: Poor quality, required rework

Pattern: Use Sonnet for medium refactoring under budget constraint
Quality score: 0.85 (acceptable)
Cost saved: $0.010 per request
```

### Pattern Matching

```javascript
function findMatchingPattern(task, complexity, context) {
  const patterns = db.query(`
    SELECT * FROM routing_patterns
    WHERE agent_wallet = ?
      AND (
        -- Task-based match
        (pattern_type = 'task_based'
         AND task_type = ?
         AND keywords_match(?, keywords_json))
        OR
        -- Complexity-based match
        (pattern_type = 'complexity_based'
         AND complexity BETWEEN complexity_min AND complexity_max)
      )
      AND confidence > 0.7
    ORDER BY confidence DESC, success_count DESC
    LIMIT 1
  `, [context.agent_wallet, task.type, task.query]);

  if (patterns.length > 0) {
    return patterns[0];
  }
  return null;
}
```

### Confidence Calculation

```javascript
function calculateConfidence(successCount, failureCount, totalAttempts) {
  const successRate = successCount / (successCount + failureCount);
  const sampleSize = successCount + failureCount;

  // Wilson score confidence interval
  const z = 1.96;  // 95% confidence
  const phat = successRate;
  const n = sampleSize;

  const denominator = 1 + (z * z) / n;
  const centerAdjusted = phat + (z * z) / (2 * n);
  const adjusted = centerAdjusted / denominator;

  const interval = (z * Math.sqrt((phat * (1 - phat) + (z * z) / (4 * n)) / n)) / denominator;

  const lowerBound = adjusted - interval;

  return Math.max(0.5, Math.min(1.0, lowerBound));
}
```

**Example:**
```
Success: 15, Failure: 2
Success rate: 88%
Sample size: 17
Confidence: 0.75 (conservative due to small sample)

Success: 150, Failure: 20
Success rate: 88%
Sample size: 170
Confidence: 0.85 (higher due to larger sample)
```

### Pattern Decay

Old patterns lose relevance over time:

```javascript
function decayPatternConfidence(pattern, daysSinceLastUse) {
  const decayRate = 0.05;  // 5% per month
  const monthsSinceUse = daysSinceLastUse / 30;

  const decayFactor = Math.exp(-decayRate * monthsSinceUse);
  pattern.confidence *= decayFactor;

  if (pattern.confidence < 0.5) {
    // Archive low-confidence patterns
    archivePattern(pattern);
  }
}
```

---

## Budget-Aware Routing

### Budget Levels

**1. Per-Request Budget**

Maximum cost for a single request.

```javascript
function checkPerRequestBudget(estimatedCost, maxCost) {
  if (estimatedCost > maxCost) {
    return {
      allowed: false,
      action: 'downgrade',
      message: `Request would cost $${estimatedCost}, max is $${maxCost}`
    };
  }
  return { allowed: true };
}
```

**Example:**
```
Max per-request: $0.50
Estimated cost for Opus: $0.015 ✓ Allowed
Estimated cost for large context: $0.60 ✗ Downgrade to Sonnet
```

**2. Daily Budget**

Limit spending per day.

```javascript
function checkDailyBudget(todaySpending, estimatedCost, dailyLimit) {
  const projectedSpending = todaySpending + estimatedCost;

  if (projectedSpending > dailyLimit) {
    const remaining = dailyLimit - todaySpending;
    return {
      allowed: false,
      action: 'constrain',
      remainingBudget: remaining,
      message: `Daily budget: $${todaySpending}/$${dailyLimit} used`
    };
  }

  // Warning if close to limit
  const percentUsed = (projectedSpending / dailyLimit) * 100;
  if (percentUsed > 80) {
    return {
      allowed: true,
      warning: `Daily budget ${percentUsed.toFixed(0)}% used`
    };
  }

  return { allowed: true };
}
```

**Example:**
```
Daily limit: $5.00
Spent today: $4.50
Next request: $0.015 (Opus) ✓ Allowed (warning: 90% used)
Next request: $0.75 ✗ Downgrade or deny
```

**3. Monthly Budget**

Limit spending per month.

```javascript
function checkMonthlyBudget(monthSpending, estimatedCost, monthlyLimit) {
  const projectedSpending = monthSpending + estimatedCost;
  const remainingDays = getRemainingDaysInMonth();

  if (projectedSpending > monthlyLimit) {
    return {
      allowed: false,
      action: 'deny_or_downgrade',
      message: `Monthly budget exceeded: $${monthSpending}/$${monthlyLimit}`
    };
  }

  // Pace calculation
  const recommendedDailyBudget = (monthlyLimit - monthSpending) / remainingDays;
  const todaySpending = getTodaySpending();

  if (todaySpending > recommendedDailyBudget * 1.5) {
    return {
      allowed: true,
      warning: `Spending above recommended pace ($${recommendedDailyBudget.toFixed(2)}/day)`
    };
  }

  return { allowed: true };
}
```

**Example:**
```
Monthly limit: $100.00
Spent this month: $75.00
Days remaining: 10
Recommended daily: $2.50

Today spent: $5.00
Warning: "Above recommended pace"
```

### Budget Strategies

**1. Conservative Strategy**

Prefer cheaper models whenever viable.

```javascript
function conservativeRouting(complexity, budget) {
  // Try cheapest model first
  if (complexity < 0.5) {
    return 'haiku';  // Even for medium-low tasks
  } else if (complexity < 0.8) {
    return 'sonnet';  // Only expensive for truly complex
  } else {
    return 'opus';
  }
}
```

**Savings:** 40-60%
**Quality trade-off:** May require occasional rework on borderline tasks

**2. Balanced Strategy (Default)**

Use recommended model, respect hard limits.

```javascript
function balancedRouting(complexity, budget) {
  const recommendedModel = getRecommendedModel(complexity);
  const estimatedCost = estimateCost(recommendedModel);

  if (budget.allows(estimatedCost)) {
    return recommendedModel;
  } else {
    // Downgrade one tier
    return downgradeModel(recommendedModel);
  }
}
```

**Savings:** 30-50%
**Quality trade-off:** Minimal, good balance

**3. Quality-First Strategy**

Prioritize best model, soft budget constraints.

```javascript
function qualityFirstRouting(complexity, budget) {
  const optimalModel = getOptimalModel(complexity);
  const estimatedCost = estimateCost(optimalModel);

  if (budget.isHardLimit && !budget.allows(estimatedCost)) {
    // Only downgrade if hard limit
    return downgradeModel(optimalModel);
  } else {
    // Use optimal even if over soft budget
    if (!budget.allows(estimatedCost)) {
      logWarning('Exceeding budget for quality');
    }
    return optimalModel;
  }
}
```

**Savings:** 10-20%
**Quality trade-off:** None, maximum quality

### Budget-Constrained Model Selection

```javascript
function selectBudgetConstrainedModel(complexity, remainingBudget) {
  const models = [
    { name: 'opus', cost: 0.015, minComplexity: 0.6 },
    { name: 'sonnet', cost: 0.005, minComplexity: 0.3 },
    { name: 'haiku', cost: 0.001, minComplexity: 0.0 }
  ];

  // Find most capable model within budget
  for (const model of models) {
    if (model.cost <= remainingBudget && complexity >= model.minComplexity) {
      return {
        model: model.name,
        reasoning: 'budget_constrained',
        tradeoff: complexity > model.minComplexity + 0.2 ? 'quality_reduced' : 'acceptable'
      };
    }
  }

  // If no model fits budget, deny or use cheapest
  return {
    model: 'haiku',
    reasoning: 'budget_exceeded',
    warning: 'Using cheapest model despite high complexity'
  };
}
```

### Cost Estimation

```javascript
function estimateCost(model, contextTokens, estimatedOutputTokens) {
  const costs = MODEL_COSTS[model];

  const inputCost = (contextTokens / 1000) * costs.input;
  const outputCost = (estimatedOutputTokens / 1000) * costs.output;

  return inputCost + outputCost;
}

// Estimate output tokens based on task
function estimateOutputTokens(taskType, complexity) {
  const baseTokens = {
    'greeting': 50,
    'simple_query': 150,
    'code_writing': 500,
    'code_refactoring': 800,
    'debugging': 600,
    'architecture': 1000,
    'reasoning': 1200
  };

  const base = baseTokens[taskType] || 300;
  const complexityMultiplier = 1 + (complexity * 0.5);

  return Math.round(base * complexityMultiplier);
}
```

**Example:**
```
Task: Code refactoring
Complexity: 0.65
Context: 2000 tokens
Estimated output: 800 × 1.325 = 1060 tokens

Sonnet cost:
  Input: (2000/1000) × $0.0003 = $0.0006
  Output: (1060/1000) × $0.0015 = $0.00159
  Total: $0.00219 ≈ $0.002

Opus cost:
  Input: (2000/1000) × $0.0015 = $0.003
  Output: (1060/1000) × $0.0075 = $0.00795
  Total: $0.01095 ≈ $0.011

Recommendation: Sonnet (5x cheaper, acceptable for complexity 0.65)
```

---

## Routing Decision Examples

### Example 1: Simple Greeting

**Input:**
```
Query: "Hello, how are you?"
Context: 50 tokens
```

**Analysis:**
```javascript
{
  complexity: {
    context_length: 0.1,
    task_type: 0.05,  // greeting
    code_presence: 0.0,
    error_presence: 0.0,
    query_structure: 0.0,
    specificity: 0.0,
    total: 0.07
  },
  task_type: 'greeting',
  budget_status: 'within_limits'
}
```

**Decision:**
```javascript
{
  selected_model: 'claude-haiku-4-5',
  selected_provider: 'anthropic',
  reasoning: 'simple_task',
  confidence: 0.95,
  estimated_cost: 0.001,
  alternatives: [
    { model: 'claude-sonnet-4-5', score: 0.3, reason: 'over-powered' },
    { model: 'claude-opus-4-5', score: 0.1, reason: 'excessive' }
  ]
}
```

**Outcome:** Success, appropriate model selected, cost optimized.

---

### Example 2: Medium Code Task

**Input:**
```
Query: "Refactor this function to be more readable and add error handling:

```javascript
function processData(data) {
  let result = [];
  for (let i = 0; i < data.length; i++) {
    result.push(data[i].value * 2);
  }
  return result;
}
```
```

**Analysis:**
```javascript
{
  complexity: {
    context_length: 0.3,     // ~1000 tokens
    task_type: 0.55,         // code_refactoring
    code_presence: 0.3,      // single code block
    error_presence: 0.0,
    query_structure: 0.2,    // clear requirements
    specificity: 0.1,        // "more readable" is vague
    total: 0.38
  },
  task_type: 'code_refactoring',
  budget_status: 'within_limits'
}
```

**Decision:**
```javascript
{
  selected_model: 'claude-sonnet-4-5',
  selected_provider: 'anthropic',
  reasoning: 'medium_complexity',
  confidence: 0.85,
  estimated_cost: 0.005,
  alternatives: [
    { model: 'claude-haiku-4-5', score: 0.4, reason: 'may_lack_nuance' },
    { model: 'claude-opus-4-5', score: 0.6, reason: 'not_necessary' }
  ]
}
```

**Outcome:** Success, Sonnet handles refactoring well, cost-effective.

---

### Example 3: Complex Debugging

**Input:**
```
Query: "I'm getting this error in my React app:

TypeError: Cannot read property 'map' of undefined
    at ProductList.render (ProductList.jsx:42)
    at processChild (react-dom.js:9841)
    at resolve (react-dom.js:9766)

And also this one:

Warning: Each child in a list should have a unique "key" prop.
    at Product (Product.jsx:12)
    at ProductList (ProductList.jsx:45)

The weird thing is it works locally but fails in production. Here's my component:

[150 lines of code]

Can you figure out what's wrong?"
```

**Analysis:**
```javascript
{
  complexity: {
    context_length: 0.7,     // ~4500 tokens
    task_type: 0.65,         // debugging
    code_presence: 0.6,      // large code block
    error_presence: 0.8,     // multiple errors
    query_structure: 0.5,    // multi-part question
    specificity: 0.4,        // "weird thing", "figure out"
    total: 0.63
  },
  task_type: 'debugging',
  budget_status: 'within_limits',
  learned_patterns: {
    match: 'react_debugging',
    recommended_model: 'claude-opus-4-5',
    confidence: 0.82
  }
}
```

**Decision:**
```javascript
{
  selected_model: 'claude-opus-4-5',
  selected_provider: 'anthropic',
  reasoning: 'complex_debugging_with_pattern',
  confidence: 0.90,
  estimated_cost: 0.018,
  pattern_applied: 'react_debugging',
  alternatives: [
    { model: 'claude-sonnet-4-5', score: 0.5, reason: 'may_miss_subtle_issues' },
    { model: 'claude-haiku-4-5', score: 0.2, reason: 'insufficient_for_debugging' }
  ]
}
```

**Outcome:** Success, Opus correctly identifies race condition and missing null check. Pattern reinforced.

---

### Example 4: Budget-Constrained

**Input:**
```
Query: "Design a microservices architecture for an e-commerce platform with high availability"
Context: 800 tokens
Daily budget: $5.00
Spent today: $4.85
```

**Analysis:**
```javascript
{
  complexity: {
    context_length: 0.3,
    task_type: 0.75,         // architecture
    code_presence: 0.0,
    error_presence: 0.0,
    query_structure: 0.3,
    specificity: 0.3,
    total: 0.78
  },
  task_type: 'architecture',
  budget_status: {
    daily_remaining: 0.15,
    recommended_model_cost: 0.020,  // Opus
    affordable: false
  }
}
```

**Decision:**
```javascript
{
  selected_model: 'claude-sonnet-4-5',
  selected_provider: 'anthropic',
  reasoning: 'budget_constrained',
  confidence: 0.65,
  estimated_cost: 0.008,
  warning: 'Downgraded from Opus due to budget constraint',
  quality_tradeoff: 'acceptable',
  alternatives: [
    { model: 'claude-opus-4-5', score: 0.9, reason: 'budget_exceeded' },
    { model: 'claude-haiku-4-5', score: 0.3, reason: 'insufficient_for_architecture' }
  ]
}
```

**Outcome:** Success with acceptable quality. Sonnet provides good architecture design, though not as comprehensive as Opus would have been. User satisfied.

---

### Example 5: Pattern Learning Success

**Input:**
```
Query: "Fix this TypeScript type error: Type 'string | null' is not assignable to type 'string'"
Context: 500 tokens
```

**Initial Routing (no pattern):**
```javascript
{
  complexity: 0.42,
  selected_model: 'claude-haiku-4-5',
  reasoning: 'medium_low_complexity'
}
// Result: Failed - Haiku suggested incorrect fix
```

**Retry:**
```javascript
{
  complexity: 0.42,
  selected_model: 'claude-sonnet-4-5',
  reasoning: 'retry_after_failure'
}
// Result: Success - Sonnet correctly identified solution
```

**Pattern Created:**
```javascript
{
  pattern_id: 'typescript_type_errors',
  pattern_type: 'task_based',
  task_type: 'debugging',
  keywords: ['typescript', 'type error', 'not assignable'],
  recommended_model: 'claude-sonnet-4-5',
  success_count: 1,
  failure_count: 0,
  confidence: 0.7  // Initially moderate
}
```

**Future Routing (pattern applied):**
```javascript
Query: "TypeScript error: Property 'foo' does not exist on type 'Bar'"

{
  complexity: 0.38,
  pattern_match: 'typescript_type_errors',
  selected_model: 'claude-sonnet-4-5',  // Upgraded from Haiku
  reasoning: 'learned_pattern',
  confidence: 0.85,
  pattern_applications: 5,
  pattern_success_rate: 100%
}
```

**Pattern Evolution:**

After 10 successful applications:
```javascript
{
  pattern_id: 'typescript_type_errors',
  success_count: 10,
  failure_count: 0,
  confidence: 0.92,  // Higher confidence
  avg_cost_saved: 0.004,  // vs using Opus
  recommendation: 'strong - always use Sonnet for TS type errors'
}
```

---

## Performance Optimization

### Caching

**Complexity Analysis Cache:**

```javascript
const complexityCache = new LRU({ max: 1000, ttl: 3600000 });  // 1 hour

function getCachedComplexity(queryHash) {
  return complexityCache.get(queryHash);
}

function cacheComplexity(queryHash, complexity) {
  complexityCache.set(queryHash, complexity);
}
```

**Pattern Matching Cache:**

```javascript
const patternCache = new LRU({ max: 500, ttl: 1800000 });  // 30 min

function getCachedPattern(taskTypeHash) {
  return patternCache.get(taskTypeHash);
}
```

### Asynchronous Learning

Learning doesn't block requests:

```javascript
async function handleRequest(query) {
  // Synchronous: Analyze and route (fast)
  const complexity = analyzeComplexity(query);
  const model = selectModel(complexity);
  const response = await routeToModel(model, query);

  // Asynchronous: Learn from result (doesn't block)
  setImmediate(() => {
    learnFromResult(query, model, response, complexity);
  });

  return response;
}
```

### Database Optimization

**Indexes:**
```sql
CREATE INDEX idx_routing_decisions_agent ON routing_decisions(agent_wallet);
CREATE INDEX idx_routing_decisions_task_type ON routing_decisions(task_type);
CREATE INDEX idx_routing_patterns_confidence ON routing_patterns(confidence DESC);
```

**Query Optimization:**
```javascript
// Instead of loading all patterns
const allPatterns = db.query('SELECT * FROM routing_patterns WHERE agent_wallet = ?');

// Load only high-confidence, recent patterns
const relevantPatterns = db.query(`
  SELECT * FROM routing_patterns
  WHERE agent_wallet = ?
    AND confidence > 0.7
    AND last_used > datetime('now', '-30 days')
  LIMIT 50
`);
```

### Parallel Processing

```javascript
async function analyzeComplexity(query) {
  // Run analysis factors in parallel
  const [
    contextScore,
    taskTypeScore,
    codeScore,
    errorScore,
    structureScore,
    specificityScore
  ] = await Promise.all([
    calculateContextLengthScore(query),
    calculateTaskTypeScore(query),
    calculateCodePresenceScore(query),
    calculateErrorPresenceScore(query),
    calculateQueryStructureScore(query),
    calculateSpecificityScore(query)
  ]);

  return combineScores(contextScore, taskTypeScore, codeScore,
                       errorScore, structureScore, specificityScore);
}
```

### Complexity Analysis Benchmarks

```
Simple query (50 tokens): ~15ms
Medium query (1000 tokens): ~35ms
Complex query (5000 tokens): ~80ms
With cache hit: ~2ms
```

### Model Selection Benchmarks

```
No pattern match: ~5ms
With pattern match: ~8ms
Budget check: ~3ms
Total overhead: <100ms per request
```

---

## Advanced Configuration

### Custom Complexity Weights

```json
{
  "complexity_weights": {
    "context_length": 0.15,
    "task_type": 0.30,
    "code_presence": 0.20,
    "error_presence": 0.15,
    "query_structure": 0.10,
    "specificity": 0.10
  }
}
```

### Custom Task Type Scores

```json
{
  "custom_task_scores": {
    "api_integration": 0.50,
    "database_optimization": 0.70,
    "ui_design": 0.35,
    "devops_automation": 0.60
  }
}
```

### Provider Preferences

```json
{
  "provider_preferences": {
    "primary": "anthropic",
    "fallback": "openai",
    "model_mapping": {
      "simple": {
        "anthropic": "claude-haiku-4-5",
        "openai": "gpt-3.5-turbo",
        "google": "gemini-1.5-flash"
      },
      "medium": {
        "anthropic": "claude-sonnet-4-5",
        "openai": "gpt-4-turbo",
        "google": "gemini-1.5-pro"
      },
      "complex": {
        "anthropic": "claude-opus-4-5",
        "openai": "gpt-4",
        "google": "gemini-1.5-pro"
      }
    }
  }
}
```

### Learning Sensitivity

```json
{
  "learning_config": {
    "min_samples_for_pattern": 3,
    "min_confidence_threshold": 0.7,
    "pattern_decay_rate": 0.05,
    "success_weight": 1.0,
    "failure_weight": 2.0,
    "enable_adaptive_thresholds": true
  }
}
```

### Budget Flexibility

```json
{
  "budget_config": {
    "strategy": "balanced",
    "flexibility": {
      "allow_exceed_for_critical": true,
      "critical_keywords": ["production", "urgent", "emergency"],
      "max_exceed_percentage": 10
    },
    "warnings": {
      "daily_threshold": 0.8,
      "monthly_threshold": 0.9
    }
  }
}
```

---

## Conclusion

Smart Router's routing decisions combine:
1. **Complexity analysis** - Multi-factor scoring of task difficulty
2. **Model selection** - Optimal model for the complexity level
3. **Pattern learning** - Adaptive routing based on historical success
4. **Budget awareness** - Cost-constrained routing when needed

The system continuously learns and improves, balancing cost savings with quality. By routing simple tasks to cheaper models and complex tasks to powerful models, it achieves 30-50% cost savings while maintaining high quality.

For more information:
- [README.md](README.md) - Main documentation
- [SKILL.md](SKILL.md) - ClawHub skill description
- [GitHub Repository](https://github.com/AtlasPA/openclaw-smart-router)
