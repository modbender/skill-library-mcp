# Comprehensive Quality Evaluation Framework

## Quality Dimensions

### 1. Clarity (明確性)

**Definition**: Instructions are unambiguous and leave no room for misinterpretation.

**Evaluation Criteria:**
- **Specificity**: Every requirement is concrete and measurable
- **Language**: Uses precise terminology, avoids vague qualifiers
- **Structure**: Logical organization with clear sections
- **Examples**: Illustrations align perfectly with instructions

**Scoring Rubric:**
- **Excellent (5)**: Crystal clear, impossible to misunderstand
- **Good (4)**: Generally clear with minor ambiguities
- **Adequate (3)**: Mostly clear but requires some interpretation
- **Poor (2)**: Multiple unclear sections
- **Failing (1)**: Fundamentally ambiguous

**Assessment Questions:**
- Could a different person achieve the same result?
- Are there multiple valid interpretations?
- Would translation preserve the meaning?

### 2. Completeness (完全性)

**Definition**: All necessary information for task execution is present.

**Evaluation Criteria:**
- **Context**: Background and purpose are provided
- **Inputs**: Input format and constraints specified
- **Outputs**: Expected deliverables clearly defined
- **Edge Cases**: Exceptional scenarios addressed
- **Error Handling**: Failure modes considered

**Scoring Rubric:**
- **Excellent (5)**: Anticipates all scenarios
- **Good (4)**: Covers main cases and common exceptions
- **Adequate (3)**: Handles typical cases
- **Poor (2)**: Missing critical information
- **Failing (1)**: Insufficient to complete task

**Assessment Questions:**
- What assumptions must the model make?
- Are there scenarios not covered?
- Is error handling defined?

### 3. Consistency (一貫性)

**Definition**: No contradictions exist within the prompt.

**Evaluation Criteria:**
- **Internal Alignment**: All parts work together
- **Terminology**: Same terms used throughout
- **Examples**: Examples match instructions
- **Priority**: Clear hierarchy when tradeoffs exist

**Scoring Rubric:**
- **Excellent (5)**: Perfect alignment throughout
- **Good (4)**: Minor terminology variations
- **Adequate (3)**: Some inconsistency but intent clear
- **Poor (2)**: Conflicting requirements
- **Failing (1)**: Major contradictions

**Assessment Questions:**
- Do any instructions conflict?
- Are priorities explicit?
- Do examples support instructions?

### 4. Efficiency (効率性)

**Definition**: Achieves goals with minimal complexity and tokens.

**Evaluation Criteria:**
- **Conciseness**: No unnecessary words
- **Token Usage**: Optimal for task complexity
- **Cognitive Load**: Easy to process
- **Reusability**: Components can be extracted

**Scoring Rubric:**
- **Excellent (5)**: Minimal tokens for maximum effect
- **Good (4)**: Efficient with minor redundancy
- **Adequate (3)**: Acceptable length
- **Poor (2)**: Unnecessarily verbose
- **Failing (1)**: Extremely wasteful

**Assessment Questions:**
- Can anything be removed without loss?
- Is complexity justified by task needs?
- Are there repeated concepts?

### 5. Robustness (堅牢性)

**Definition**: Handles unexpected inputs and edge cases gracefully.

**Evaluation Criteria:**
- **Error Tolerance**: Graceful degradation
- **Input Validation**: Checks assumptions
- **Flexibility**: Adapts to variations
- **Recovery**: Clear fallback behavior

**Scoring Rubric:**
- **Excellent (5)**: Handles all edge cases elegantly
- **Good (4)**: Most exceptions covered
- **Adequate (3)**: Common errors handled
- **Poor (2)**: Brittle with many failure points
- **Failing (1)**: Breaks with any deviation

**Assessment Questions:**
- What happens with invalid input?
- How does it handle ambiguity?
- Are there single points of failure?

### 6. Maintainability (保守性)

**Definition**: Easy to understand, modify, and extend.

**Evaluation Criteria:**
- **Documentation**: Design decisions explained
- **Modularity**: Clear component separation
- **Versioning**: Change tracking possible
- **Extensibility**: Easy to add features

**Scoring Rubric:**
- **Excellent (5)**: Self-documenting and modular
- **Good (4)**: Clear structure, easy to modify
- **Adequate (3)**: Modifiable with effort
- **Poor (2)**: Difficult to change safely
- **Failing (1)**: Monolithic and opaque

**Assessment Questions:**
- Can someone else modify this?
- Are components reusable?
- Is the design rationale clear?

### 7. Effectiveness (有効性)

**Definition**: Achieves intended goals reliably.

**Evaluation Criteria:**
- **Goal Achievement**: Meets objectives
- **Reliability**: Consistent results
- **Quality**: Output meets standards
- **Performance**: Appropriate speed/cost

**Scoring Rubric:**
- **Excellent (5)**: Exceeds expectations consistently
- **Good (4)**: Reliably meets goals
- **Adequate (3)**: Generally successful
- **Poor (2)**: Sporadic success
- **Failing (1)**: Fails to achieve goals

**Assessment Questions:**
- Does it solve the actual problem?
- How consistent are results?
- Is output quality acceptable?

## Evaluation Process

### Step 1: Initial Assessment
```
For each quality dimension:
1. Read through the prompt completely
2. Score against rubric (1-5)
3. Note specific issues found
4. Identify improvement opportunities
```

### Step 2: Weighted Scoring
```
Assign weights based on use case:

High-Stakes (medical, financial, legal):
- Robustness: 30%
- Clarity: 25%
- Completeness: 20%
- Consistency: 15%
- Others: 10%

Creative Tasks:
- Effectiveness: 30%
- Clarity: 20%
- Efficiency: 20%
- Others: 30%

Production Systems:
- Robustness: 25%
- Maintainability: 25%
- Efficiency: 20%
- Others: 30%
```

### Step 3: Testing Protocol

**Test Suite Design:**
```
1. Baseline Test (expected input)
2. Edge Case Tests:
   - Minimum valid input
   - Maximum complexity
   - Boundary conditions
3. Error Tests:
   - Invalid input
   - Missing information
   - Contradictory requirements
4. Variation Tests:
   - Different phrasings
   - Alternative formats
   - Unexpected combinations
```

### Step 4: Results Analysis

**Performance Matrix:**
```
| Test Case | Expected | Actual | Pass/Fail | Notes |
|-----------|----------|--------|-----------|-------|
| Baseline  | [...]    | [...]  | ✓/✗       | [...] |
| Edge 1    | [...]    | [...]  | ✓/✗       | [...] |
| Error 1   | [...]    | [...]  | ✓/✗       | [...] |
```

### Step 5: Improvement Recommendations

**Priority Matrix:**
```
High Impact + Easy: Do immediately
High Impact + Hard: Plan for next version  
Low Impact + Easy: Do if time permits
Low Impact + Hard: Skip or defer
```

## Quality Metrics

### Quantitative Metrics

**Token Efficiency Ratio (TER):**
```
TER = Output Quality / Token Count
Higher is better
```

**Consistency Score (CS):**
```
CS = Successful Runs / Total Runs
Target: >0.95 for production
```

**Error Rate (ER):**
```
ER = Failed Cases / Total Test Cases
Target: <0.05 for critical tasks
```

**Clarity Index (CI):**
```
CI = Clear Instructions / Total Instructions
Target: 1.0 (every instruction clear)
```

### Qualitative Metrics

**Readability Assessment:**
- Can non-experts understand?
- Is technical language necessary?
- Are sections well-organized?

**Adaptability Assessment:**
- How easily can it be modified?
- Can it handle requirement changes?
- Is it portable across models?

**User Experience Assessment:**
- Is it pleasant to work with?
- Does it inspire confidence?
- Is documentation helpful?

## Optimization Strategies

### For Clarity Issues
1. Replace vague terms with specifics
2. Add concrete examples
3. Define all technical terms
4. Use consistent terminology
5. Structure with clear headings

### For Completeness Issues
1. Add missing context
2. Specify all formats
3. Document edge cases
4. Include error handling
5. Define success criteria

### For Consistency Issues
1. Align examples with instructions
2. Standardize terminology
3. Resolve contradictions
4. Clarify priorities
5. Unify style throughout

### For Efficiency Issues
1. Remove redundancy
2. Combine similar instructions
3. Simplify complex sentences
4. Use bulleted lists
5. Eliminate unnecessary examples

### For Robustness Issues
1. Add input validation
2. Define fallback behavior
3. Handle edge cases
4. Include error messages
5. Test with variations

### For Maintainability Issues
1. Add documentation
2. Modularize components
3. Create clear sections
4. Include change log
5. Explain design decisions

## Benchmarking Standards

### Industry Baselines

**By Use Case:**
- Customer Service: Clarity > Efficiency > Robustness
- Content Creation: Effectiveness > Clarity > Efficiency  
- Data Analysis: Completeness > Consistency > Robustness
- Code Generation: Completeness > Robustness > Clarity

**By Deployment:**
- Development: Effectiveness > Maintainability
- Testing: Completeness > Robustness  
- Production: Robustness > Efficiency
- Research: Effectiveness > Clarity

### Maturity Levels

**Level 1 - Ad Hoc:**
- Basic functionality
- Minimal structure
- Frequent failures

**Level 2 - Repeatable:**
- Consistent format
- Some error handling
- Documented process

**Level 3 - Defined:**
- Clear standards
- Comprehensive testing
- Version control

**Level 4 - Managed:**
- Metrics tracked
- Continuous improvement
- Automated testing

**Level 5 - Optimized:**
- Data-driven refinement
- Predictive optimization
- Self-improving systems

## Continuous Improvement

### Feedback Loop
1. Deploy prompt
2. Collect performance data
3. Analyze failure patterns
4. Generate hypotheses
5. Test improvements
6. Validate changes
7. Update documentation
8. Repeat

### Version Control Strategy
```
v1.0.0 - Initial release
v1.0.1 - Bug fix (typo correction)
v1.1.0 - Minor improvement (added example)
v2.0.0 - Major revision (restructured approach)
```

### A/B Testing Framework
```
Control: Current prompt version
Variant: Modified prompt
Metrics: Success rate, quality score, user satisfaction
Duration: Until statistical significance
Decision: Adopt if >10% improvement
```

### Documentation Requirements
- Change rationale
- Test results
- Known issues
- Migration notes
- Performance data