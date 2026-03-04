# Prompt Engineering Anti-Patterns and Quality Standards

## Common Anti-Patterns to Avoid

### 1. Ambiguous Instructions

**What it looks like:**
```
"Write a good analysis"
"Handle this appropriately"  
"Process the data correctly"
"Make it better"
```

**Why it fails:**
- "Good," "appropriate," and "correct" mean different things to different people
- LLM has to guess at intent
- Results are inconsistent and unpredictable

**How to fix:**
```
Instead of: "Write a good analysis"
Use: "Write a 500-word technical analysis covering:
1. Current performance metrics
2. Identified bottlenecks
3. Three specific improvement recommendations"
```

### 2. Contradictory Requirements

**What it looks like:**
```
"Be extremely thorough but keep it brief"
"Be creative but don't deviate from the template"
"Give me all the details but make it simple"
```

**Why it fails:**
- Creates impossible constraints
- Forces the model to choose which instruction to prioritize
- Results satisfy neither requirement well

**How to fix:**
- Clarify priorities explicitly
- Use conditional logic
- Separate into multiple prompts if needed

```
Instead of: "Be thorough but brief"
Use: "Provide a brief overview (2-3 sentences) first, then detailed analysis (500 words) below"
```

### 3. Assumed Context

**What it looks like:**
```
"Fix the problem in this code"  (without specifying what problem)
"Write a report on the usual metrics" (without defining "usual")
"Use the standard format" (without providing the standard)
```

**Why it fails:**
- LLM lacks access to implicit knowledge
- Forced to make assumptions
- Results miss the mark

**How to fix:**
- Make all context explicit
- Define all terms
- Provide necessary background

```
Instead of: "Fix the problem"
Use: "Fix the null pointer exception occurring on line 47 when user input is empty"
```

### 4. Over-Engineering

**What it looks like:**
```
"First, consider the philosophical implications, then analyze from three perspectives using the framework I'll describe, ensuring each perspective considers both historical and future contexts..."
[Continues for 500+ words for a simple classification task]
```

**Why it fails:**
- Wastes tokens
- Increases chance of confusion
- Makes maintenance difficult
- Slower response times

**How to fix:**
- Start simple, add complexity only if needed
- Match technique complexity to task complexity
- Test if simpler versions work first

```
Instead of: [Complex multi-step framework for simple task]
Use: "Classify this customer feedback as: Positive, Negative, or Neutral"
```

### 5. Biased Examples

**What it looks like:**
```
Example 1: Input: "Service was terrible" → Output: "URGENT: Critical issue"
Example 2: Input: "Took forever" → Output: "URGENT: Critical issue"  
Example 3: Input: "Not happy" → Output: "URGENT: Critical issue"
[All examples show same pattern]
```

**Why it fails:**
- Model overfits to the pattern
- Loses ability to differentiate
- Misclassifies edge cases

**How to fix:**
- Provide diverse examples
- Include edge cases
- Show full range of outputs

```
Example 1: "Service was terrible" → "URGENT: Critical issue"
Example 2: "Minor typo on page" → "Low: Cosmetic"
Example 3: "Works but could be faster" → "Medium: Performance"
```

### 6. Kitchen Sink Approach

**What it looks like:**
```
"Analyze this from every possible angle including but not limited to technical, business, legal, ethical, environmental, social, political, and philosophical perspectives..."
```

**Why it fails:**
- Dilutes focus
- Creates overwhelming output
- Important insights get buried
- Wastes processing time

**How to fix:**
- Focus on relevant perspectives only
- Prioritize what matters most
- Can always ask for additional analysis later

```
Instead of: "Analyze from every angle"
Use: "Analyze the technical feasibility and business impact"
```

### 7. Unclear Success Criteria

**What it looks like:**
```
"Summarize this document"
"Review this code"
"Improve this text"
```

**Why it fails:**
- No clear endpoint
- Can't measure success
- Results vary widely

**How to fix:**
- Define what success looks like
- Provide measurable criteria
- Specify deliverables

```
Instead of: "Summarize this document"
Use: "Create a 3-bullet executive summary focusing on key decisions needed, risks, and timeline"
```

### 8. False Precision

**What it looks like:**
```
"Rate this on a scale of 1-100"
"Give me exactly 7.5 examples"
"Estimate to 3 decimal places"
```

**Why it fails:**
- Implies precision that doesn't exist
- Creates false confidence
- Distinctions become meaningless

**How to fix:**
- Use appropriate granularity
- Acknowledge uncertainty
- Use ranges when appropriate

```
Instead of: "Rate 1-100"
Use: "Rate as: Poor, Fair, Good, or Excellent"
```

### 9. Prompt Stuffing

**What it looks like:**
```
"You are an expert in everything with 50 years of experience in all fields who always gives perfect answers and never makes mistakes and always considers every possibility..."
```

**Why it fails:**
- Doesn't actually improve performance
- Wastes tokens
- Can trigger overconfidence
- Reduces clarity

**How to fix:**
- Use specific, relevant expertise only
- Focus on actual requirements
- Test if additions actually help

```
Instead of: "You are an expert in everything..."
Use: "As a senior Python developer, review this code for security issues"
```

### 10. Copy-Paste Without Adaptation

**What it looks like:**
Using the exact same prompt across different contexts without modification.

**Why it fails:**
- Misses context-specific needs
- Sub-optimal for specific use case
- May include irrelevant instructions

**How to fix:**
- Adapt prompts to specific context
- Test and refine for your use case
- Remove irrelevant portions

## Quality Evaluation Framework

### Clarity Score

**High Clarity:**
- ✓ Every instruction has one interpretation
- ✓ Success criteria explicitly defined
- ✓ Technical terms defined or avoided
- ✓ Conditions and exceptions specified

**Low Clarity:**
- ✗ Uses vague qualifiers (good, appropriate, etc.)
- ✗ Ambiguous pronouns or references
- ✗ Implicit assumptions
- ✗ Undefined acronyms or jargon

### Completeness Score

**High Completeness:**
- ✓ All necessary context provided
- ✓ Input format specified
- ✓ Output format defined
- ✓ Edge cases addressed
- ✓ Error handling defined

**Low Completeness:**
- ✗ Missing critical information
- ✗ Undefined variables or parameters
- ✗ No format specification
- ✗ Edge cases ignored

### Consistency Score

**High Consistency:**
- ✓ No contradictory instructions
- ✓ Uniform tone and style
- ✓ Clear prioritization
- ✓ Aligned examples

**Low Consistency:**
- ✗ Conflicting requirements
- ✗ Mixed terminology
- ✗ Unclear priorities
- ✗ Mismatched examples

### Efficiency Score

**High Efficiency:**
- ✓ Concise without losing clarity
- ✓ No redundant instructions
- ✓ Appropriate detail level
- ✓ Optimal token usage

**Low Efficiency:**
- ✗ Unnecessary repetition
- ✗ Over-explanation of obvious points
- ✗ Excessive examples
- ✗ Verbose phrasing

### Robustness Score

**High Robustness:**
- ✓ Handles unexpected inputs gracefully
- ✓ Clear fallback behavior
- ✓ Validates assumptions
- ✓ Error recovery defined

**Low Robustness:**
- ✗ Breaks with edge cases
- ✗ No error handling
- ✗ Assumes perfect inputs
- ✗ Single point of failure

## Quality Checklist

Before finalizing any prompt, verify:

### Essential Checks
- [ ] Can someone unfamiliar with the task understand what to do?
- [ ] Are all success criteria measurable?
- [ ] Have you tested with edge cases?
- [ ] Is every instruction necessary?
- [ ] Do examples cover the full range of cases?

### Optimization Checks
- [ ] Can any section be simplified without losing meaning?
- [ ] Are tokens being used efficiently?
- [ ] Is the structure logical and easy to follow?
- [ ] Have you removed redundant instructions?

### Robustness Checks
- [ ] What happens with unexpected input?
- [ ] Are error messages helpful?
- [ ] Can the prompt handle variations?
- [ ] Is graceful degradation possible?

### Maintenance Checks
- [ ] Will others understand how to modify this?
- [ ] Are design decisions documented?
- [ ] Is versioning strategy clear?
- [ ] Can parts be reused elsewhere?

## Red Flags in Prompt Design

Watch for these warning signs:

### Language Red Flags
- "Just do what's best"
- "You know what I mean"
- "The usual way"
- "Be smart about it"
- "Try to figure out"

### Structural Red Flags
- Instructions scattered throughout
- No clear sections or organization
- Examples that don't match instructions
- Multiple ways to interpret requirements

### Logic Red Flags
- "Always do X, except sometimes do Y"
- Circular dependencies
- Undefined decision criteria
- No clear stopping point

### Complexity Red Flags
- Nested conditions beyond 2 levels
- More than 5 distinct requirements
- Multiple competing objectives
- Excessive use of "but," "however," "except"

## Fixing Common Problems

### Problem: Inconsistent Outputs
**Diagnosis:** Check for ambiguous language, missing examples, unclear success criteria
**Solution:** Add specific examples, define exact requirements, use consistent terminology

### Problem: Wrong Format
**Diagnosis:** Format not specified, examples don't match description
**Solution:** Provide template, show exact format, validate against examples

### Problem: Missing Information
**Diagnosis:** Assumed context, incomplete instructions
**Solution:** Make all context explicit, provide all necessary information

### Problem: Over/Under Detail
**Diagnosis:** No length constraints, unclear audience
**Solution:** Specify exact length/detail level, define target audience

### Problem: Off-Topic Responses
**Diagnosis:** Scope not defined, too much flexibility
**Solution:** Add explicit boundaries, list what to exclude, narrow focus

## Testing Your Prompts

### Minimum Test Cases

1. **Happy Path:** Normal, expected input
2. **Edge Cases:** Boundary conditions
3. **Error Cases:** Invalid or problematic input
4. **Ambiguous Cases:** Input that could be interpreted multiple ways
5. **Stress Test:** Maximum complexity input

### Evaluation Criteria

For each test, assess:
- Did it produce correct output?
- Was the format correct?
- Were all requirements met?
- How consistent are multiple runs?
- What failed and why?

### Iteration Process

1. Run initial tests
2. Identify failure patterns
3. Hypothesize root cause
4. Make minimal fix
5. Retest all cases
6. Document what changed and why