---
name: input-classification-system
description: Deterministic rule-based system for classifying clarified input into a single primary task category and assigning execution complexity. Use when the Main Agent needs to categorize user requests before task decomposition, route tasks to appropriate handlers, assess complexity and risk levels, or determine if clarification is needed. Triggers after clarification is complete and before decomposition begins.
---

# Input Classification System

## 1. Skill Name

**Input Classification System**

Identifier: `input-classification-system`

## 2. Version

**1.0**

This is the initial release of the Input Classification System skill.

## 3. Skill Purpose

Provide a deterministic, rule-based classification system that enables the Main Agent to categorize clarified user input into exactly one primary task category, assign execution complexity, assess risk level, and determine confidence score before any task decomposition or execution planning occurs.

**Measurable Objectives:**
- Achieve 100% single-category classification (no ambiguous multi-category outputs)
- Provide deterministic tie-breaking for all edge cases
- Assign complexity levels using measurable thresholds
- Calculate confidence scores with explicit formulas
- Route ambiguous inputs to clarification with specific triggers

## 4. What This Skill Does

- Classifies clarified input into exactly one primary category from a fixed list
- Assigns complexity level based on measurable operation counts and time estimates
- Calculates risk level based on impact scope and reversibility criteria
- Computes confidence score using explicit scoring factors
- Determines if input requires additional clarification
- Sets the appropriate state transition after classification
- Applies deterministic tie-breaking logic when multiple categories match
- Validates that input has been clarified before classification
- Logs all classification decisions with full context
- Provides secondary tags for additional context (maximum 3)
- Enforces boundary definitions between categories
- Triggers escalation for high-risk or low-confidence classifications
- Prevents misclassification through explicit rules
- Outputs structured ClassificationResult for downstream systems
- Maintains audit trail for all classification decisions

## 5. What This Skill Must Not Do

- Must not perform task decomposition or breakdown
- Must not solve or execute any tasks
- Must not create execution plans or strategies
- Must not apply emotional reasoning or sentiment analysis
- Must not assign multiple primary categories to a single input
- Must not overlap with Clarification System responsibilities
- Must not modify the original input content
- Must not make assumptions about user intent without explicit indicators
- Must not skip complexity assessment for any classification
- Must not bypass risk assessment for any classification
- Must not assign confidence scores below threshold without escalation
- Must not classify inputs that have not been clarified first
- Must not use probabilistic or non-deterministic classification methods
- Must not ignore tie-breaking rules when categories conflict
- Must not proceed to execution without setting state transition

## 6. Activation Conditions

This skill activates when ALL of the following conditions are met:

1. **Clarification Complete**: Input has been processed by the Clarification System and marked as clarified
2. **No Pending Questions**: No outstanding clarification questions remain
3. **Classification Not Yet Performed**: Input has not been previously classified
4. **Valid Input Structure**: Input contains recognizable task indicators

**Pre-Activation Checklist:**
- [ ] Input marked as "clarified" by Clarification System
- [ ] No clarification questions pending
- [ ] Input contains actionable request
- [ ] Input is not empty or malformed

**Do NOT activate if:**
- Input is still being clarified
- Input is a clarification question itself
- Input is a response to a clarification question
- Input has already been classified

## 7. Classification Categories

The following 15 categories form the fixed classification list:

| Category | Code | Description |
|----------|------|-------------|
| CODE_GENERATION | CG | Writing, modifying, or generating source code |
| CODE_REVIEW | CR | Reviewing, analyzing, or auditing existing code |
| DEBUGGING | DB | Identifying and fixing bugs, errors, or issues |
| DATA_ANALYSIS | DA | Analyzing, processing, or visualizing data |
| FILE_OPERATIONS | FO | Reading, writing, moving, or managing files |
| DOCUMENTATION | DC | Creating or updating documentation |
| REFACTORING | RF | Restructuring code without changing behavior |
| TESTING | TS | Writing, running, or managing tests |
| DEPLOYMENT | DP | Deploying applications or infrastructure |
| RESEARCH | RS | Investigating, searching, or gathering information |
| CONFIGURATION | CF | Setting up or modifying configurations |
| COMMUNICATION | CM | Drafting messages, emails, or communications |
| CONVERSION | CV | Transforming data or files between formats |
| ANALYSIS | AN | General analysis not covered by other categories |
| PLANNING | PL | Creating plans, strategies, or roadmaps |

**Category Priority Order (for tie-breaking):**
1. DEBUGGING (highest - immediate attention needed)
2. DEPLOYMENT
3. CODE_GENERATION
4. REFACTORING
5. TESTING
6. CODE_REVIEW
7. DATA_ANALYSIS
8. CONFIGURATION
9. FILE_OPERATIONS
10. CONVERSION
11. DOCUMENTATION
12. RESEARCH
13. ANALYSIS
14. COMMUNICATION
15. PLANNING (lowest)

## 8. Category Boundary Definitions

### CODE_GENERATION vs CODE_REVIEW
- **CODE_GENERATION**: Input requests creating new code or modifying existing code
- **CODE_REVIEW**: Input requests analysis of existing code without modifications
- **Boundary**: If modification is implied, classify as CODE_GENERATION

### CODE_GENERATION vs REFACTORING
- **CODE_GENERATION**: Creating new functionality or features
- **REFACTORING**: Restructuring existing code without new functionality
- **Boundary**: "Improve performance" without feature change = REFACTORING

### DEBUGGING vs CODE_GENERATION
- **DEBUGGING**: Input explicitly mentions errors, bugs, or failures
- **CODE_GENERATION**: Input requests new features without error context
- **Boundary**: "Fix this bug" = DEBUGGING; "Add error handling" = CODE_GENERATION

### DATA_ANALYSIS vs ANALYSIS
- **DATA_ANALYSIS**: Input involves data processing, statistics, or visualization
- **ANALYSIS**: Input involves general analysis of concepts, requirements, or situations
- **Boundary**: If data files/sets are mentioned = DATA_ANALYSIS

### FILE_OPERATIONS vs CONVERSION
- **FILE_OPERATIONS**: Input requests file management (read, write, move, delete)
- **CONVERSION**: Input requests format transformation between file types
- **Boundary**: "Convert X to Y format" = CONVERSION; "Read file X" = FILE_OPERATIONS

### RESEARCH vs ANALYSIS
- **RESEARCH**: Input requests information gathering or investigation
- **ANALYSIS**: Input requests evaluation or assessment of known information
- **Boundary**: "Find information about X" = RESEARCH; "Evaluate X" = ANALYSIS

### TESTING vs CODE_GENERATION
- **TESTING**: Input specifically requests test creation or test execution
- **CODE_GENERATION**: Input requests production code
- **Boundary**: "Write tests for X" = TESTING; "Write X with tests" = CODE_GENERATION (primary)

### CONFIGURATION vs DEPLOYMENT
- **CONFIGURATION**: Input requests setup of settings or configurations
- **DEPLOYMENT**: Input requests deployment to environments or infrastructure
- **Boundary**: Local setup = CONFIGURATION; Remote/environment setup = DEPLOYMENT

## 9. Single-Primary-Category Rule

**Rule**: Every classified input MUST have exactly one primary category.

### Enforcement Rules

1. **No Multi-Category Output**: Never output multiple primary categories
2. **Tie-Breaking Required**: When multiple categories match, apply tie-breaking logic
3. **Category Exclusivity**: Primary category is mutually exclusive with other primary categories

### Tie-Breaking Logic

When input matches multiple categories, apply in order:

**Step 1: Keyword Dominance**
- Count explicit keyword matches for each candidate category
- Category with highest keyword count wins
- If tied, proceed to Step 2

**Step 2: Action Verb Analysis**
- Identify primary action verb in input
- Map action verb to category using verb-to-category mapping
- If still tied, proceed to Step 3

**Step 3: Priority Order**
- Apply category priority order (see Section 7)
- Higher priority category wins

**Step 4: Default Fallback**
- If all steps fail, default to ANALYSIS category

### Tie-Breaking Example

Input: "Debug and fix the error in the authentication code, then add logging"

1. Keywords: DEBUGGING (debug, fix, error), CODE_GENERATION (add, logging)
2. Action Verb: "Debug" (primary action) → DEBUGGING
3. Result: DEBUGGING (primary), secondary_tags: [CODE_GENERATION]

## 10. Secondary Tag Rules

Secondary tags provide additional context without affecting primary routing.

### Rules

1. **Maximum 3 Tags**: No more than 3 secondary tags per classification
2. **No Primary Duplicate**: Secondary tags cannot duplicate primary category
3. **Related Categories Only**: Secondary tags must be from the fixed category list
4. **Relevance Threshold**: Only add tags with >50% keyword match confidence

### Secondary Tag Selection Process

1. Identify all categories with keyword matches (excluding primary)
2. Calculate relevance score for each (0.0-1.0)
3. Sort by relevance score (descending)
4. Select top 3 with score > 0.5
5. Add to ClassificationResult

### When to Apply Secondary Tags

- Input contains multiple distinct sub-tasks
- Input references multiple technology domains
- Input implies follow-up work in other categories
- Input has context from previous interactions in different categories

### When NOT to Apply Secondary Tags

- Input is single-focused with no additional context
- Relevance scores are below threshold (0.5)
- Would duplicate primary category
- Would exceed 3-tag limit

### Secondary Tag Examples

| Input | Primary | Secondary Tags |
|-------|---------|----------------|
| "Debug the API and update the docs" | DEBUGGING | [DOCUMENTATION] |
| "Refactor the auth module and add tests" | REFACTORING | [TESTING] |
| "Analyze sales data and create a report" | DATA_ANALYSIS | [DOCUMENTATION, COMMUNICATION] |
| "Fix this bug" | DEBUGGING | [] |

---

## Classification Models Reference

For detailed complexity, risk, confidence, and state transition models, see [classification-models.md](references/classification-models.md).

For system integration, failure conditions, logging, and examples, see [system-integration.md](references/system-integration.md).