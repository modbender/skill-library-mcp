# System Integration

This document contains integration specifications, failure conditions, logging requirements, and example classification scenarios.

## Table of Contents

- [17. Interaction with Other Systems](#17-interaction-with-other-systems)
- [18. Failure Conditions](#18-failure-conditions)
- [19. Logging Requirements](#19-logging-requirements)
- [20. Example Classification Scenarios](#20-example-classification-scenarios)

---

## 17. Interaction with Other Systems

The Input Classification System interacts with multiple upstream and downstream systems.

### System Integration Map

```
┌─────────────────────┐
│   Clarification     │ ────► INPUT (Clarified)
│      System         │
└─────────────────────┘
          │
          ▼
┌─────────────────────┐
│    INPUT            │
│ CLASSIFICATION      │ ◄─── THIS SKILL
│    SYSTEM           │
└─────────────────────┘
          │
          ├──────────────────────┬──────────────────────┐
          ▼                      ▼                      ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│     Task        │    │  Clarification  │    │     Human       │
│  Decomposition  │    │     System      │    │     Review      │
│    (CLASSIFIED) │    │(NEEDS_CLARIF.)  │    │   (ESCALATED)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Upstream Systems

#### Clarification System

**Relationship**: Predecessor system that prepares input for classification.

**Interface Contract**:
- **Input**: Clarified input with `clarification_status: "complete"`
- **Required Fields**: `clarified_input`, `clarification_id`, `original_input`
- **Handoff Protocol**: Classification activates only after clarification marks input as complete

**Data Received**:
```
{
  clarification_id: UUID,
  original_input: string,
  clarified_input: string,
  clarification_status: "complete",
  clarification_timestamp: ISO8601,
  clarification_questions_asked: string[],
  clarification_responses: string[]
}
```

**Boundary Rules**:
- Classification MUST NOT re-clarify already clarified inputs
- Classification MUST NOT modify clarified input content
- Classification MUST preserve clarification_id for audit trail

### Downstream Systems

#### Task Decomposition System

**Relationship**: Successor system for successfully classified inputs.

**Interface Contract**:
- **Trigger**: State transition = CLASSIFIED
- **Required Fields**: Full ClassificationResult object
- **Handoff Protocol**: Route with classification_id for traceability

**Data Provided**:
```
{
  classification_id: UUID,
  primary_category: string,
  secondary_tags: string[],
  complexity_level: string,
  risk_level: string,
  confidence_score: number,
  clarified_input: string,
  routing_priority: string
}
```

**Integration Notes**:
- Task Decomposition should respect complexity_level for planning
- Task Decomposition should consider risk_level for execution safeguards
- Secondary tags inform decomposition about related work areas

#### Clarification System (Return Path)

**Relationship**: Return path for inputs needing additional clarification.

**Interface Contract**:
- **Trigger**: State transition = NEEDS_CLARIFICATION
- **Required Fields**: classification_id, clarification_trigger, candidate_categories
- **Handoff Protocol**: Return with specific clarification questions

**Data Provided**:
```
{
  classification_id: UUID,
  clarification_trigger: string,
  candidate_categories: string[],
  missing_elements: string[],
  suggested_questions: string[],
  previous_clarification_id: UUID
}
```

**Integration Notes**:
- Clarification System should use suggested_questions as starting point
- Previous clarification context must be preserved
- Classification will be re-attempted after clarification completes

#### Human Review Queue

**Relationship**: Escalation path for high-risk or low-confidence inputs.

**Interface Contract**:
- **Trigger**: State transition = ESCALATED
- **Required Fields**: Full ClassificationResult with escalation reason
- **Handoff Protocol**: Add to priority queue with routing_priority

**Data Provided**:
```
{
  classification_id: UUID,
  escalation_reason: string,
  confidence_score: number,
  risk_level: string,
  candidate_categories: string[],
  clarified_input: string,
  classification_attempt: object,
  routing_priority: "immediate" | "high"
}
```

**Integration Notes**:
- Human reviewers can override classification
- Override decisions should be logged for system improvement
- CRITICAL risk always routes to immediate priority queue

#### Error Handler

**Relationship**: Handler for rejected or failed classifications.

**Interface Contract**:
- **Trigger**: State transition = REJECTED
- **Required Fields**: classification_id, rejection_reason

**Data Provided**:
```
{
  classification_id: UUID,
  rejection_reason: string,
  original_input: string,
  error_details: object
}
```

### System Communication Protocol

| From | To | Protocol | Format |
|------|-----|----------|--------|
| Clarification System | Classification | Direct handoff | JSON object |
| Classification | Task Decomposition | Event queue | JSON object |
| Classification | Clarification System | Return queue | JSON object |
| Classification | Human Review | Priority queue | JSON object |
| Classification | Error Handler | Error queue | JSON object |

### Timing Requirements

| Operation | Max Latency |
|-----------|-------------|
| Classification processing | < 100ms |
| State transition | < 10ms |
| Downstream routing | < 50ms |
| Total end-to-end | < 200ms |

---

## 18. Failure Conditions

Defined failure conditions and their handling strategies.

### Classification Failure Types

| Failure Type | Code | Description | Recovery Strategy |
|--------------|------|-------------|-------------------|
| EMPTY_INPUT | F01 | Input is empty or null | Return REJECTED |
| MALFORMED_INPUT | F02 | Input structure is invalid | Return REJECTED |
| UNCLARIFIED_INPUT | F03 | Input not marked as clarified | Return to Clarification |
| CATEGORY_MATCH_FAILURE | F04 | No category matches input | Escalate to human |
| TIE_BREAKING_FAILURE | F05 | Cannot resolve category tie | Route to clarification |
| CONFIDENCE_CALCULATION_ERROR | F06 | Error in confidence calculation | Use conservative estimate |
| TIMEOUT | F07 | Classification exceeds time limit | Use default category |
| SYSTEM_OVERLOAD | F08 | Downstream system unavailable | Queue for retry |

### Failure Handling Procedures

#### F01: EMPTY_INPUT

**Detection**: Input string is empty, null, or whitespace only.

**Response**:
```
{
  state_transition: "REJECTED",
  rejection_reason: "EMPTY_INPUT",
  error_message: "Input cannot be empty",
  user_message: "Please provide a request for me to help with."
}
```

#### F02: MALFORMED_INPUT

**Detection**: Input contains unparseable characters, exceeds length limits, or has invalid encoding.

**Response**:
```
{
  state_transition: "REJECTED",
  rejection_reason: "MALFORMED_INPUT",
  error_message: "Input format is invalid",
  user_message: "Your request contains invalid characters or formatting. Please rephrase."
}
```

#### F03: UNCLARIFIED_INPUT

**Detection**: Input lacks `clarification_status: "complete"` marker.

**Response**:
```
{
  state_transition: "REJECTED",
  rejection_reason: "UNCLARIFIED_INPUT",
  error_message: "Input has not been clarified",
  routing: "Return to Clarification System"
}
```

#### F04: CATEGORY_MATCH_FAILURE

**Detection**: No category has keyword match score > 0.1.

**Response**:
```
{
  state_transition: "ESCALATED",
  escalation_reason: "CATEGORY_MATCH_FAILURE",
  confidence_score: 0.0,
  candidate_categories: [],
  suggested_action: "Human review required - no category match"
}
```

#### F05: TIE_BREAKING_FAILURE

**Detection**: Multiple categories have identical scores after all tie-breaking steps.

**Response**:
```
{
  state_transition: "NEEDS_CLARIFICATION",
  clarification_trigger: "TIE_BREAKING_FAILURE",
  candidate_categories: [tied_categories],
  suggested_questions: [
    "Are you looking to [category A action] or [category B action]?"
  ]
}
```

#### F06: CONFIDENCE_CALCULATION_ERROR

**Detection**: Error in confidence formula calculation (e.g., missing factor data).

**Recovery**: Use conservative confidence estimate of 0.5.

**Response**:
```
{
  confidence_score: 0.5,
  confidence_note: "Calculated using fallback due to missing factor data",
  missing_factors: [list of missing factors],
  state_transition: determined_by_other_factors
}
```

#### F07: TIMEOUT

**Detection**: Classification processing exceeds 100ms limit.

**Recovery**: Use default ANALYSIS category with low confidence.

**Response**:
```
{
  primary_category: "ANALYSIS",
  confidence_score: 0.4,
  state_transition: "NEEDS_CLARIFICATION",
  clarification_trigger: "TIMEOUT_FALLBACK",
  note: "Classification timed out, using default category"
}
```

#### F08: SYSTEM_OVERLOAD

**Detection**: Downstream system (Task Decomposition, etc.) is unavailable.

**Recovery**: Queue classification result for retry.

**Response**:
```
{
  state_transition: "CLASSIFIED",
  queued: true,
  queue_reason: "Downstream system unavailable",
  retry_after: 5000,  // milliseconds
  max_retries: 3
}
```

### Failure Logging

All failures must be logged with:

```
{
  failure_id: UUID,
  failure_type: string,
  failure_code: string,
  timestamp: ISO8601,
  input_hash: string,  // SHA-256 of input for tracking
  recovery_action: string,
  recovery_successful: boolean
}
```

---

## 19. Logging Requirements

Comprehensive logging requirements for audit, debugging, and improvement.

### Log Levels

| Level | Usage | Retention |
|-------|-------|-----------|
| DEBUG | Detailed classification steps | 7 days |
| INFO | Classification completions | 30 days |
| WARNING | Low confidence, escalations | 90 days |
| ERROR | Failures, rejections | 1 year |
| AUDIT | All classification decisions | 2 years |

### Required Log Fields

Every log entry must include:

```
{
  log_id: UUID,
  timestamp: ISO8601,
  log_level: "DEBUG" | "INFO" | "WARNING" | "ERROR" | "AUDIT",
  classification_id: UUID,
  clarification_id: UUID,
  input_hash: string,
  primary_category: string,
  secondary_tags: string[],
  complexity_level: string,
  risk_level: string,
  confidence_score: number,
  state_transition: string,
  processing_time_ms: number
}
```

### Log Events

#### Classification Started (DEBUG)

Logged when classification begins processing.

```
{
  event: "CLASSIFICATION_STARTED",
  classification_id: UUID,
  clarification_id: UUID,
  input_length: number,
  input_hash: string
}
```

#### Category Evaluation (DEBUG)

Logged for each category evaluated.

```
{
  event: "CATEGORY_EVALUATION",
  classification_id: UUID,
  category: string,
  keyword_matches: string[],
  keyword_count: number,
  match_score: number
}
```

#### Tie-Breaking Applied (DEBUG)

Logged when tie-breaking logic is invoked.

```
{
  event: "TIE_BREAKING_APPLIED",
  classification_id: UUID,
  tied_categories: string[],
  tie_breaking_step: string,
  winner: string
}
```

#### Classification Complete (INFO)

Logged when classification successfully completes.

```
{
  event: "CLASSIFICATION_COMPLETE",
  classification_id: UUID,
  primary_category: string,
  secondary_tags: string[],
  complexity_level: string,
  risk_level: string,
  confidence_score: number,
  state_transition: string,
  processing_time_ms: number
}
```

#### Low Confidence Warning (WARNING)

Logged when confidence is below acceptable threshold.

```
{
  event: "LOW_CONFIDENCE_WARNING",
  classification_id: UUID,
  confidence_score: number,
  threshold: number,
  primary_category: string,
  contributing_factors: object
}
```

#### Escalation Triggered (WARNING)

Logged when input is escalated.

```
{
  event: "ESCALATION_TRIGGERED",
  classification_id: UUID,
  escalation_reason: string,
  confidence_score: number,
  risk_level: string,
  candidate_categories: string[]
}
```

#### Classification Failed (ERROR)

Logged when classification fails.

```
{
  event: "CLASSIFICATION_FAILED",
  classification_id: UUID,
  failure_type: string,
  failure_code: string,
  error_message: string,
  input_hash: string
}
```

#### Audit Trail (AUDIT)

Complete audit record for every classification.

```
{
  event: "CLASSIFICATION_AUDIT",
  classification_id: UUID,
  clarification_id: UUID,
  timestamp: ISO8601,
  original_input_hash: string,
  clarified_input_hash: string,
  classification_result: {
    primary_category: string,
    secondary_tags: string[],
    complexity_level: string,
    risk_level: string,
    confidence_score: number,
    state_transition: string
  },
  classification_factors: {
    keyword_clarity: number,
    category_match_strength: number,
    input_completeness: number,
    context_availability: number
  },
  tie_breaking_applied: boolean,
  escalation_triggered: boolean,
  processing_time_ms: number
}
```

### Log Storage Requirements

- **Format**: JSON Lines (one JSON object per line)
- **Compression**: Logs older than 7 days should be compressed
- **Encryption**: AUDIT logs must be encrypted at rest
- **Access**: DEBUG/INFO logs accessible to system admins; AUDIT logs require audit role

### Log Analysis Queries

**Most common categories (last 24 hours)**:
```
SELECT primary_category, COUNT(*) 
FROM classification_logs 
WHERE timestamp > NOW() - INTERVAL 24 HOUR 
GROUP BY primary_category 
ORDER BY COUNT(*) DESC
```

**Average confidence by category**:
```
SELECT primary_category, AVG(confidence_score) 
FROM classification_logs 
WHERE log_level = 'AUDIT' 
GROUP BY primary_category
```

**Escalation rate**:
```
SELECT 
  COUNT(CASE WHEN state_transition = 'ESCALATED' THEN 1 END) as escalations,
  COUNT(*) as total,
  (escalations / total) * 100 as escalation_rate
FROM classification_logs
WHERE timestamp > NOW() - INTERVAL 7 DAY
```

---

## 20. Example Classification Scenarios

Complete worked examples demonstrating the classification system.

### Scenario 1: Simple Code Generation

**Input**: "Write a Python function to calculate the factorial of a number"

**Pre-Classification Check**:
- Clarification status: complete ✓
- Input not empty ✓
- Input structure valid ✓

**Step 1: Category Evaluation**

| Category | Keyword Matches | Count | Score |
|----------|-----------------|-------|-------|
| CODE_GENERATION | write, function, calculate | 3 | 0.95 |
| DATA_ANALYSIS | calculate | 1 | 0.30 |
| FILE_OPERATIONS | (none) | 0 | 0.10 |
| DOCUMENTATION | (none) | 0 | 0.10 |

**Step 2: Primary Category Selection**
- Highest score: CODE_GENERATION (0.95)
- No tie-breaking required

**Step 3: Secondary Tags**
- DATA_ANALYSIS: score 0.30 < threshold 0.5 → Not included
- Result: No secondary tags

**Step 4: Complexity Assessment**
- Operations: 1 (write function) → Score: 10
- Time: <5 min → Score: 10
- Dependencies: 0 → Score: 10
- Domains: 1 (coding) → Score: 20
- **Calculation**: (10×0.40) + (10×0.25) + (10×0.20) + (20×0.15) = 11.5
- **Result**: TRIVIAL

**Step 5: Risk Assessment**
- Impact: Single file, local → 10
- Reversibility: Fully reversible → 10
- Sensitivity: No data → 10
- **Calculation**: (10×0.35) + (10×0.35) + (10×0.30) = 10
- **Result**: MINIMAL

**Step 6: Confidence Calculation**
- Keyword Clarity: Explicit keywords → 1.0
- Category Match: Perfect match → 1.0
- Input Completeness: Complete → 1.0
- Context Availability: Full → 1.0
- **Calculation**: (1.0×0.30) + (1.0×0.25) + (1.0×0.25) + (1.0×0.20) = 1.0
- **Result**: 1.0 (High Confidence)

**Step 7: State Transition**
- Confidence ≥ 0.85 → CLASSIFIED
- Risk = MINIMAL → No escalation

**Final ClassificationResult**:
```json
{
  "primary_category": "CODE_GENERATION",
  "secondary_tags": [],
  "complexity_level": "TRIVIAL",
  "risk_level": "MINIMAL",
  "confidence_score": 1.0,
  "requires_clarification": false,
  "clarification_trigger": null,
  "state_transition": "CLASSIFIED",
  "classification_timestamp": "2026-02-22T08:15:00Z",
  "classification_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

---

### Scenario 2: Multi-Task with Tie-Breaking

**Input**: "Debug the authentication error in the login module and write unit tests for the fix"

**Pre-Classification Check**:
- Clarification status: complete ✓
- Input not empty ✓
- Input structure valid ✓

**Step 1: Category Evaluation**

| Category | Keyword Matches | Count | Score |
|----------|-----------------|-------|-------|
| DEBUGGING | debug, error | 2 | 0.85 |
| TESTING | write, unit tests | 2 | 0.80 |
| CODE_GENERATION | write, fix | 2 | 0.70 |
| CODE_REVIEW | (none) | 0 | 0.10 |

**Step 2: Primary Category Selection**
- Highest scores: DEBUGGING (0.85), TESTING (0.80)
- Close scores, apply tie-breaking

**Tie-Breaking Step 1: Keyword Dominance**
- DEBUGGING: 2 keywords
- TESTING: 2 keywords
- Still tied

**Tie-Breaking Step 2: Action Verb Analysis**
- Primary action verb: "Debug" (first verb in input)
- "Debug" maps to DEBUGGING
- Winner: DEBUGGING

**Step 3: Secondary Tags**
- TESTING: score 0.80 > threshold 0.5 → Include
- CODE_GENERATION: score 0.70 > threshold 0.5 → Include
- Result: [TESTING, CODE_GENERATION]

**Step 4: Complexity Assessment**
- Operations: 4 (debug, fix, write tests, verify) → Score: 45
- Time: 30 min - 1 hour → Score: 50
- Dependencies: 2 (test framework, auth module) → Score: 30
- Domains: 2 (debugging, testing) → Score: 40
- **Calculation**: (45×0.40) + (50×0.25) + (30×0.20) + (40×0.15) = 18 + 12.5 + 6 + 6 = 42.5
- **Result**: MODERATE

**Step 5: Risk Assessment**
- Impact: Single module → 40
- Reversibility: Mostly reversible → 30
- Sensitivity: User data (auth) → 65
- **Calculation**: (40×0.35) + (30×0.35) + (65×0.30) = 14 + 10.5 + 19.5 = 44
- **Result**: MODERATE

**Step 6: Confidence Calculation**
- Keyword Clarity: Explicit keywords → 1.0
- Category Match: Strong match → 0.8
- Input Completeness: Complete → 1.0
- Context Availability: Full → 1.0
- **Calculation**: (1.0×0.30) + (0.8×0.25) + (1.0×0.25) + (1.0×0.20) = 0.30 + 0.20 + 0.25 + 0.20 = 0.95
- **Result**: 0.95 (High Confidence)

**Step 7: State Transition**
- Confidence ≥ 0.85 → CLASSIFIED
- Risk = MODERATE → No escalation

**Final ClassificationResult**:
```json
{
  "primary_category": "DEBUGGING",
  "secondary_tags": ["TESTING", "CODE_GENERATION"],
  "complexity_level": "MODERATE",
  "risk_level": "MODERATE",
  "confidence_score": 0.95,
  "requires_clarification": false,
  "clarification_trigger": null,
  "state_transition": "CLASSIFIED",
  "classification_timestamp": "2026-02-22T08:16:00Z",
  "classification_id": "550e8400-e29b-41d4-a716-446655440002"
}
```

---

### Scenario 3: High-Risk Production Deployment

**Input**: "Deploy the new payment processing service to production and migrate existing user payment data"

**Pre-Classification Check**:
- Clarification status: complete ✓
- Input not empty ✓
- Input structure valid ✓

**Step 1: Category Evaluation**

| Category | Keyword Matches | Count | Score |
|----------|-----------------|-------|-------|
| DEPLOYMENT | deploy, production, service | 3 | 0.95 |
| DATA_ANALYSIS | data, migrate | 2 | 0.60 |
| CODE_GENERATION | (none) | 0 | 0.10 |
| FILE_OPERATIONS | (none) | 0 | 0.10 |

**Step 2: Primary Category Selection**
- Highest score: DEPLOYMENT (0.95)
- No tie-breaking required

**Step 3: Secondary Tags**
- DATA_ANALYSIS: score 0.60 > threshold 0.5 → Include
- Result: [DATA_ANALYSIS]

**Step 4: Complexity Assessment**
- Operations: 8 (deploy, configure, migrate, verify, rollback plan, monitor, test, document) → Score: 65
- Time: 4-8 hours → Score: 85
- Dependencies: 6 (payment gateway, database, monitoring, load balancer, SSL, backup) → Score: 80
- Domains: 4 (deployment, database, security, monitoring) → Score: 80
- **Calculation**: (65×0.40) + (85×0.25) + (80×0.20) + (80×0.15) = 26 + 21.25 + 16 + 12 = 75.25
- **Result**: COMPLEX

**Step 5: Risk Assessment**
- Impact: Multiple applications → 100
- Reversibility: Difficult to reverse → 75
- Sensitivity: Financial/Security → 100
- Modifiers: Production (+15), Security keywords (+20)
- **Calculation**: (100×0.35) + (75×0.35) + (100×0.30) + 35 = 35 + 26.25 + 30 + 35 = 126.25
- **Capped**: 100
- **Result**: CRITICAL

**Step 6: Confidence Calculation**
- Keyword Clarity: Explicit keywords → 1.0
- Category Match: Perfect match → 1.0
- Input Completeness: Complete → 1.0
- Context Availability: Full → 1.0
- **Calculation**: (1.0×0.30) + (1.0×0.25) + (1.0×0.25) + (1.0×0.20) = 1.0
- **Result**: 1.0 (High Confidence)

**Step 7: State Transition**
- Confidence ≥ 0.85 → Would be CLASSIFIED
- BUT Risk = CRITICAL → Override to ESCALATED

**Final ClassificationResult**:
```json
{
  "primary_category": "DEPLOYMENT",
  "secondary_tags": ["DATA_ANALYSIS"],
  "complexity_level": "COMPLEX",
  "risk_level": "CRITICAL",
  "confidence_score": 1.0,
  "requires_clarification": false,
  "clarification_trigger": null,
  "state_transition": "ESCALATED",
  "classification_timestamp": "2026-02-22T08:17:00Z",
  "classification_id": "550e8400-e29b-41d4-a716-446655440003"
}
```

**Escalation Record**:
```json
{
  "escalation_id": "660e8400-e29b-41d4-a716-446655440003",
  "classification_id": "550e8400-e29b-41d4-a716-446655440003",
  "escalation_reason": "CRITICAL_RISK_LEVEL",
  "routing_priority": "immediate",
  "next_system": "human_review",
  "suggested_review_actions": [
    "Verify deployment checklist completion",
    "Confirm backup and rollback procedures",
    "Review data migration plan",
    "Obtain approval from payment system owner"
  ]
}
```

---

### Scenario 4: Ambiguous Input Requiring Clarification

**Input**: "Help with the database"

**Pre-Classification Check**:
- Clarification status: complete ✓
- Input not empty ✓
- Input structure valid ✓

**Step 1: Category Evaluation**

| Category | Keyword Matches | Count | Score |
|----------|-----------------|-------|-------|
| DEBUGGING | (none) | 0 | 0.15 |
| DATA_ANALYSIS | database | 1 | 0.35 |
| FILE_OPERATIONS | (none) | 0 | 0.15 |
| RESEARCH | help | 1 | 0.30 |
| CONFIGURATION | database | 1 | 0.30 |

**Step 2: Primary Category Selection**
- Highest score: DATA_ANALYSIS (0.35)
- Score below threshold (0.5)
- Multiple categories with similar low scores

**Step 3: Confidence Calculation**
- Keyword Clarity: Weak indicator → 0.3
- Category Match: Weak match → 0.4
- Input Completeness: Missing action and context → 0.3
- Context Availability: Minimal → 0.4
- **Calculation**: (0.3×0.30) + (0.4×0.25) + (0.3×0.25) + (0.4×0.20) = 0.09 + 0.10 + 0.075 + 0.08 = 0.345
- **Result**: 0.345 (Unacceptable Confidence)

**Step 4: State Transition**
- Confidence < 0.50 → ESCALATED or NEEDS_CLARIFICATION
- Clarification possible → NEEDS_CLARIFICATION

**Final ClassificationResult**:
```json
{
  "primary_category": null,
  "secondary_tags": [],
  "complexity_level": null,
  "risk_level": null,
  "confidence_score": 0.345,
  "requires_clarification": true,
  "clarification_trigger": "LOW_CONFIDENCE_AMBIGUOUS_INPUT",
  "state_transition": "NEEDS_CLARIFICATION",
  "classification_timestamp": "2026-02-22T08:18:00Z",
  "classification_id": "550e8400-e29b-41d4-a716-446655440004"
}
```

**Clarification Request**:
```json
{
  "classification_id": "550e8400-e29b-41d4-a716-446655440004",
  "clarification_trigger": "LOW_CONFIDENCE_AMBIGUOUS_INPUT",
  "candidate_categories": ["DATA_ANALYSIS", "DEBUGGING", "CONFIGURATION", "RESEARCH"],
  "missing_elements": ["action", "scope"],
  "suggested_questions": [
    "What would you like to do with the database? (query, fix, configure, analyze)",
    "Which database are you referring to?",
    "Is there a specific issue you're experiencing?"
  ]
}