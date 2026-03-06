# Classification Models

This document contains detailed models for complexity assessment, risk classification, confidence scoring, escalation rules, misclassification prevention, and state transitions.

## Table of Contents

- [11. Complexity Level Assignment Model](#11-complexity-level-assignment-model)
- [12. Risk Classification Model](#12-risk-classification-model)
- [13. Confidence Scoring System](#13-confidence-scoring-system)
- [14. Escalation to Clarification Rules](#14-escalation-to-clarification-rules)
- [15. Misclassification Prevention Rules](#15-misclassification-prevention-rules)
- [16. State Transition Trigger](#16-state-transition-trigger)

---

## 11. Complexity Level Assignment Model

Complexity is determined by measuring four factors and applying a scoring formula.

### Complexity Factors

| Factor | Measurement | Weight |
|--------|-------------|--------|
| Operation Count | Number of distinct operations required | 40% |
| Time Estimate | Estimated execution time | 25% |
| Dependency Count | Number of external dependencies | 20% |
| Skill Diversity | Number of different skill domains required | 15% |

### Complexity Levels

| Level | Score Range | Operations | Time | Dependencies | Skill Domains |
|-------|-------------|------------|------|--------------|---------------|
| TRIVIAL | 0-20 | 1 | <5 min | 0 | 1 |
| SIMPLE | 21-40 | 1-3 | <30 min | 1-2 | 1-2 |
| MODERATE | 41-60 | 3-10 | <2 hours | 3-5 | 2-3 |
| COMPLEX | 61-80 | 10-20 | <1 day | 6-10 | 3-5 |
| CRITICAL | 81-100 | 20+ | >1 day | 10+ | 5+ |

### Complexity Calculation Formula

```
complexity_score = (operation_score * 0.40) + 
                   (time_score * 0.25) + 
                   (dependency_score * 0.20) + 
                   (diversity_score * 0.15)
```

### Operation Scoring

| Operations | Score |
|------------|-------|
| 1 | 10 |
| 2-3 | 25 |
| 4-6 | 45 |
| 7-10 | 65 |
| 11-15 | 80 |
| 16-20 | 90 |
| 20+ | 100 |

### Time Scoring

| Time Estimate | Score |
|---------------|-------|
| <5 minutes | 10 |
| 5-15 minutes | 20 |
| 15-30 minutes | 35 |
| 30 min - 1 hour | 50 |
| 1-2 hours | 65 |
| 2-4 hours | 75 |
| 4-8 hours | 85 |
| 8+ hours | 100 |

### Dependency Scoring

| Dependencies | Score |
|--------------|-------|
| 0 | 10 |
| 1-2 | 30 |
| 3-5 | 55 |
| 6-10 | 80 |
| 10+ | 100 |

### Skill Diversity Scoring

| Domains | Score |
|---------|-------|
| 1 | 20 |
| 2 | 40 |
| 3 | 60 |
| 4 | 80 |
| 5+ | 100 |

### Complexity Assignment Examples

**Example 1: "Fix the typo in README.md"**
- Operations: 1 (edit file) → Score: 10
- Time: <5 min → Score: 10
- Dependencies: 0 → Score: 10
- Domains: 1 (documentation) → Score: 20
- **Calculation**: (10×0.40) + (10×0.25) + (10×0.20) + (20×0.15) = 4 + 2.5 + 2 + 3 = 11.5
- **Result**: TRIVIAL

**Example 2: "Create a REST API with authentication and database integration"**
- Operations: 8 (setup, models, routes, auth, validation, tests, docs, config) → Score: 65
- Time: 2-4 hours → Score: 75
- Dependencies: 5 (framework, auth lib, database, validation, testing) → Score: 55
- Domains: 4 (backend, security, database, testing) → Score: 80
- **Calculation**: (65×0.40) + (75×0.25) + (55×0.20) + (80×0.15) = 26 + 18.75 + 11 + 12 = 67.75
- **Result**: COMPLEX

---

## 12. Risk Classification Model

Risk is determined by evaluating impact scope, reversibility, and sensitivity factors.

### Risk Factors

| Factor | Description | Weight |
|--------|-------------|--------|
| Impact Scope | Breadth of affected systems/users | 35% |
| Reversibility | Ease of undoing changes | 35% |
| Data Sensitivity | Sensitivity level of involved data | 30% |

### Risk Levels

| Level | Score Range | Description | Escalation Required |
|-------|-------------|-------------|---------------------|
| MINIMAL | 0-20 | No production impact, fully reversible | No |
| LOW | 21-40 | Limited impact, easily reversible | No |
| MODERATE | 41-60 | Potential non-critical system impact | No |
| HIGH | 61-80 | Critical system impact, difficult to reverse | Yes |
| CRITICAL | 81-100 | Production impact, irreversible, security implications | Yes (Human) |

### Impact Scope Scoring

| Scope | Score |
|-------|-------|
| Single file, local only | 10 |
| Multiple files, local only | 25 |
| Single module/service | 40 |
| Multiple modules/services | 60 |
| Entire application | 80 |
| Multiple applications/infrastructure | 100 |

### Reversibility Scoring

| Reversibility | Score |
|---------------|-------|
| Fully reversible (version controlled, no data loss) | 10 |
| Mostly reversible (minor cleanup needed) | 30 |
| Partially reversible (some manual intervention) | 50 |
| Difficult to reverse (significant effort) | 75 |
| Irreversible (permanent changes) | 100 |

### Data Sensitivity Scoring

| Sensitivity | Score |
|-------------|-------|
| No data involved | 10 |
| Public/non-sensitive data | 20 |
| Internal business data | 45 |
| User data (non-PII) | 65 |
| PII/Sensitive data | 85 |
| Financial/Security credentials | 100 |

### Risk Calculation Formula

```
risk_score = (impact_score * 0.35) + 
             (reversibility_score * 0.35) + 
             (sensitivity_score * 0.30)
```

### Risk Modifiers

Apply these modifiers to the final score:

| Condition | Modifier |
|-----------|----------|
| Production environment mentioned | +15 |
| No backup/rollback plan | +10 |
| Security-related keywords present | +20 |
| User explicitly requests caution | +5 |
| First-time operation for user | +5 |

### Risk Assignment Examples

**Example 1: "Add a comment to the utility function"**
- Impact: Single file, local → 10
- Reversibility: Fully reversible → 10
- Sensitivity: No data → 10
- **Calculation**: (10×0.35) + (10×0.35) + (10×0.30) = 3.5 + 3.5 + 3 = 10
- **Result**: MINIMAL

**Example 2: "Delete the production database and recreate it"**
- Impact: Entire application → 80
- Reversibility: Irreversible → 100
- Sensitivity: Financial/Security → 100
- Modifiers: Production (+15), No backup mentioned (+10)
- **Calculation**: (80×0.35) + (100×0.35) + (100×0.30) + 25 = 28 + 35 + 30 + 25 = 118
- **Capped**: 100
- **Result**: CRITICAL

---

## 13. Confidence Scoring System

Confidence score indicates the certainty of the classification decision.

### Confidence Formula

```
confidence_score = (keyword_clarity * 0.30) + 
                   (category_match_strength * 0.25) + 
                   (input_completeness * 0.25) + 
                   (context_availability * 0.20)
```

### Confidence Factors

| Factor | Description | Measurement |
|--------|-------------|-------------|
| Keyword Clarity | Presence of clear category indicators | 0.0-1.0 |
| Category Match Strength | How well input matches category definition | 0.0-1.0 |
| Input Completeness | Whether input has all required elements | 0.0-1.0 |
| Context Availability | Availability of clarifying context | 0.0-1.0 |

### Keyword Clarity Scoring

| Indicator | Score |
|-----------|-------|
| Explicit category keyword present | 1.0 |
| Strong synonym present | 0.8 |
| Weak indicator present | 0.6 |
| No clear indicators | 0.3 |
| Conflicting indicators | 0.1 |

### Category Match Strength Scoring

| Match Level | Score |
|-------------|-------|
| Perfect match to category definition | 1.0 |
| Strong match with minor ambiguity | 0.8 |
| Moderate match with some ambiguity | 0.6 |
| Weak match with significant ambiguity | 0.4 |
| Poor match, best guess | 0.2 |

### Input Completeness Scoring

| Completeness | Score |
|--------------|-------|
| Complete: action, target, context all present | 1.0 |
| Mostly complete: minor elements missing | 0.8 |
| Partially complete: some elements missing | 0.6 |
| Incomplete: significant elements missing | 0.4 |
| Minimal: only basic elements present | 0.2 |

### Context Availability Scoring

| Context Level | Score |
|---------------|-------|
| Full context from clarification | 1.0 |
| Partial context available | 0.7 |
| Minimal context | 0.4 |
| No context available | 0.2 |

### Confidence Thresholds

| Threshold | Score | Action |
|-----------|-------|--------|
| High Confidence | ≥ 0.85 | Proceed with classification |
| Acceptable Confidence | 0.70 - 0.84 | Proceed with logging |
| Low Confidence | 0.50 - 0.69 | Route to clarification |
| Unacceptable Confidence | < 0.50 | Escalate to human review |

### Confidence Calculation Examples

**Example 1: "Write a Python function to calculate fibonacci numbers"**
- Keyword Clarity: "write" (explicit), "function" (explicit) → 1.0
- Category Match: Perfect match to CODE_GENERATION → 1.0
- Input Completeness: Action (write), target (function), context (fibonacci) → 1.0
- Context Availability: Full context from clarification → 1.0
- **Calculation**: (1.0×0.30) + (1.0×0.25) + (1.0×0.25) + (1.0×0.20) = 1.0
- **Result**: High Confidence (1.0)

**Example 2: "Help with this thing"**
- Keyword Clarity: No clear indicators → 0.3
- Category Match: Poor match, best guess → 0.2
- Input Completeness: Minimal elements → 0.2
- Context Availability: No context → 0.2
- **Calculation**: (0.3×0.30) + (0.2×0.25) + (0.2×0.25) + (0.2×0.20) = 0.09 + 0.05 + 0.05 + 0.04 = 0.23
- **Result**: Unacceptable Confidence (0.23) → Escalate

---

## 14. Escalation to Clarification Rules

Escalation routes inputs to the Clarification System when classification cannot proceed confidently.

### Automatic Escalation Triggers

| Trigger | Condition | Priority |
|---------|-----------|----------|
| Confidence Below Threshold | confidence_score < 0.50 | Critical |
| Multiple Category Tie | Tie unresolvable after all steps | High |
| Missing Required Elements | Input lacks action or target | High |
| Ambiguous Scope | Scope cannot be determined | Medium |
| Contradictory Indicators | Input contains conflicting signals | Medium |
| Unknown Technology | References unrecognized technology | Low |

### Escalation Decision Tree

```
IF confidence_score < 0.50:
    ESCALATE to human review
ELSE IF confidence_score < 0.70:
    IF clarification_possible:
        ROUTE to Clarification System
    ELSE:
        ESCALATE to human review
ELSE IF tie_breaking_failed:
    ROUTE to Clarification System
ELSE IF missing_required_elements:
    ROUTE to Clarification System
ELSE:
    PROCEED with classification
```

### Clarification Questions Generation

When escalating, generate appropriate clarification questions:

| Missing Element | Question Template |
|-----------------|-------------------|
| Action | "What would you like me to do with [target]?" |
| Target | "What specific item should I [action]?" |
| Scope | "Should this apply to [scope option A] or [scope option B]?" |
| Category | "Are you looking to [category A] or [category B]?" |

### Escalation Logging

All escalations must be logged with:

```
{
  escalation_id: UUID,
  timestamp: ISO8601,
  trigger_type: string,
  confidence_score: number,
  candidate_categories: string[],
  missing_elements: string[],
  clarification_questions: string[]
}
```

---

## 15. Misclassification Prevention Rules

Rules to prevent common classification errors.

### Prevention Rule Set

**Rule 1: Action Verb Priority**
- Primary action verb determines category over secondary verbs
- Example: "Review and fix the code" → DEBUGGING (fix is primary action)

**Rule 2: Explicit Over Implicit**
- Explicit category keywords override implicit context
- Example: "Debug the performance issue" → DEBUGGING (explicit), not REFACTORING

**Rule 3: Specificity Hierarchy**
- More specific categories override general categories
- Order: DEBUGGING > CODE_GENERATION > FILE_OPERATIONS > ANALYSIS

**Rule 4: Context Window Validation**
- Consider only the current clarified input, not historical context
- Historical context used only for secondary tags

**Rule 5: Keyword Count Threshold**
- Require minimum 2 keyword matches for category assignment
- Single keyword match requires additional context confirmation

**Rule 6: Boundary Case Handling**
- When input sits on category boundary, apply explicit boundary rules
- Document boundary decision in classification log

**Rule 7: Negation Detection**
- Detect and properly handle negated keywords
- Example: "Do NOT delete the file" → FILE_OPERATIONS (with negation flag)

**Rule 8: Temporal Indicator Handling**
- Future tense indicates planning, past tense indicates analysis
- Example: "Will deploy tomorrow" → PLANNING; "Deployed yesterday" → ANALYSIS

**Rule 9: Conditional Statement Handling**
- Conditional inputs require clarification
- Example: "If the server is down, restart it" → Escalate for clarification

**Rule 10: Multi-Input Detection**
- Detect and flag inputs containing multiple distinct requests
- Each distinct request should be classified separately

### Common Misclassification Patterns

| Incorrect Classification | Correct Classification | Prevention Rule |
|-------------------------|------------------------|-----------------|
| "Refactor the login bug" → REFACTORING | DEBUGGING | Rule 2: Explicit over implicit |
| "Write tests for the API" → CODE_GENERATION | TESTING | Rule 1: Action verb priority |
| "Analyze the code for bugs" → ANALYSIS | CODE_REVIEW | Rule 3: Specificity hierarchy |
| "Help me understand the database" → DEBUGGING | RESEARCH | Rule 5: Keyword count threshold |

### Misclassification Detection

After classification, apply detection checks:

1. **Cross-Category Validation**: Verify no other category has higher keyword match
2. **Boundary Rule Check**: Confirm boundary rules were applied correctly
3. **Confidence Alignment**: Verify confidence score aligns with classification certainty
4. **Secondary Tag Consistency**: Ensure secondary tags don't contradict primary

---

## 16. State Transition Trigger

After classification, set the appropriate state transition.

### State Transition Types

| State | Code | Condition | Next Action |
|-------|------|-----------|-------------|
| CLASSIFIED | CLS | confidence ≥ 0.70, no escalation triggers | Route to Task Decomposition |
| NEEDS_CLARIFICATION | NCL | confidence < 0.70, clarification possible | Route to Clarification System |
| ESCALATED | ESC | confidence < 0.50 OR risk = CRITICAL | Route to Human Review |
| REJECTED | REJ | Invalid or unclassifiable input | Return error to user |

### State Transition Decision Matrix

| Confidence | Risk Level | Has Ambiguity | State Transition |
|------------|------------|---------------|------------------|
| ≥ 0.85 | Any | No | CLASSIFIED |
| 0.70-0.84 | MINIMAL/LOW | No | CLASSIFIED |
| 0.70-0.84 | MODERATE+ | No | CLASSIFIED (with logging) |
| 0.70-0.84 | Any | Yes | NEEDS_CLARIFICATION |
| 0.50-0.69 | Any | No | NEEDS_CLARIFICATION |
| 0.50-0.69 | HIGH/CRITICAL | Any | ESCALATED |
| < 0.50 | Any | Any | ESCALATED |
| Any | CRITICAL | Any | ESCALATED |

### State Transition Output

```
{
  state_transition: "CLS" | "NCL" | "ESC" | "REJ",
  transition_reason: string,
  transition_timestamp: ISO8601,
  next_system: "task_decomposition" | "clarification" | "human_review" | "error_handler",
  routing_priority: "immediate" | "high" | "normal" | "low"
}
```

### Routing Priority Assignment

| State | Routing Priority |
|-------|------------------|
| CLASSIFIED (CRITICAL complexity) | immediate |
| CLASSIFIED (COMPLEX complexity) | high |
| CLASSIFIED (MODERATE complexity) | normal |
| CLASSIFIED (SIMPLE/TRIVIAL complexity) | low |
| NEEDS_CLARIFICATION | high |
| ESCALATED | immediate |
| REJECTED | normal |