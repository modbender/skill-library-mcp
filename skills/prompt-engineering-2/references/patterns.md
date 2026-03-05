# Common Prompt Patterns Library

## Analysis Patterns

### Comprehensive Analysis Pattern
```markdown
Analyze [SUBJECT] considering the following dimensions:

1. **Technical Aspects**: Examine implementation, performance, and scalability
2. **Business Impact**: Assess costs, benefits, and ROI
3. **Risk Assessment**: Identify potential issues and mitigation strategies
4. **Recommendations**: Provide actionable next steps

For each dimension:
- Present key findings
- Support with evidence
- Rate importance (High/Medium/Low)

Conclude with a prioritized action plan.
```

### SWOT Analysis Pattern
```markdown
Conduct a SWOT analysis of [SUBJECT]:

**Strengths** (Internal, Positive)
- List 3-5 key strengths
- Explain how each provides advantage

**Weaknesses** (Internal, Negative)  
- List 3-5 key weaknesses
- Suggest improvement strategies

**Opportunities** (External, Positive)
- List 3-5 opportunities
- Describe how to capitalize on each

**Threats** (External, Negative)
- List 3-5 threats
- Propose mitigation approaches

Synthesize findings into strategic recommendations.
```

### Root Cause Analysis Pattern
```markdown
Investigate the root cause of [PROBLEM]:

1. **Problem Statement**: Clearly define what went wrong
2. **Timeline**: When did it start? What changed?
3. **5 Whys Analysis**: 
   - Why did X happen? Because...
   - Why did that happen? Because...
   (Continue until root cause found)
4. **Contributing Factors**: Secondary issues that worsened the problem
5. **Recommendations**: Specific fixes for root cause and prevention

Focus on systemic issues, not individual blame.
```

## Creation Patterns

### Content Creation Pattern
```markdown
Create [CONTENT TYPE] about [TOPIC] with these specifications:

**Audience**: [Describe target readers]
**Tone**: [Professional/Casual/Technical/Friendly]
**Length**: [Word/paragraph count]
**Purpose**: [Inform/Persuade/Entertain/Educate]

Structure:
1. Hook/Introduction (grab attention)
2. Main Points (3-5 key messages)
3. Supporting Details (evidence, examples)
4. Conclusion (call-to-action or summary)

Include:
- Concrete examples
- Relevant statistics (if applicable)
- Clear transitions between sections
```

### Step-by-Step Tutorial Pattern
```markdown
Create a tutorial for [TASK]:

**Prerequisites**: What users need before starting
**Outcome**: What they'll achieve

## Steps:
1. **[Action Verb + Specific Task]**
   - Detailed instructions
   - Expected result
   - Common issues and solutions

2. **[Next Step]**
   - Instructions
   - Verification method
   - Troubleshooting tips

(Continue for all steps...)

**Final Checklist**:
□ Verify [outcome 1]
□ Check [outcome 2]
□ Test [functionality]

**Next Steps**: Where to go from here
```

### Documentation Pattern
```markdown
Document [SYSTEM/PROCESS/API]:

# Overview
Brief description and purpose

# Getting Started
Minimum requirements and setup

# Core Concepts
Key terms and principles explained

# Usage
## Basic Example
[Simple use case with code/steps]

## Advanced Usage
[Complex scenarios]

# Reference
## Parameters/Options
| Name | Type | Description | Default |
|------|------|-------------|---------|
| [param] | [type] | [desc] | [value] |

## Common Issues
| Problem | Solution |
|---------|----------|
| [issue] | [fix] |

# FAQ
Common questions with answers
```

## Review Patterns

### Code Review Pattern
```markdown
Review this code for:

**Security**:
- Input validation
- Authentication/authorization
- Data exposure risks
- Injection vulnerabilities

**Performance**:
- Algorithm efficiency
- Resource usage
- Bottlenecks
- Optimization opportunities

**Maintainability**:
- Code clarity
- Documentation
- Design patterns
- Technical debt

**Best Practices**:
- Language conventions
- Error handling
- Testing coverage
- Logging

For each issue found:
- Location: [file:line]
- Severity: [High/Medium/Low]
- Issue: [description]
- Fix: [specific suggestion]
```

### Document Review Pattern
```markdown
Review this document for:

1. **Content Quality**
   - Accuracy of information
   - Completeness of coverage
   - Logical flow

2. **Clarity**
   - Ambiguous statements
   - Technical jargon usage
   - Sentence complexity

3. **Structure**
   - Organization effectiveness
   - Section balance
   - Navigation ease

4. **Style**
   - Consistency
   - Tone appropriateness
   - Grammar/spelling

Provide:
- Specific issues with location
- Suggested improvements
- Overall assessment
```

## Problem-Solving Patterns

### Debugging Pattern
```markdown
Debug [ISSUE]:

**Symptoms**: What is observed?
**Expected Behavior**: What should happen?
**Actual Behavior**: What actually happens?

**Diagnostic Steps**:
1. Verify inputs are correct
2. Check recent changes
3. Test in isolation
4. Review error messages/logs
5. Identify pattern/conditions

**Hypothesis**: Most likely cause based on evidence

**Solution**:
- Immediate fix
- Root cause resolution
- Prevention measures

**Verification**: How to confirm fix works
```

### Decision-Making Pattern
```markdown
Help decide between [OPTIONS]:

For each option, evaluate:

**Option: [NAME]**
- Pros: [List benefits]
- Cons: [List drawbacks]
- Costs: [Time, money, resources]
- Risks: [What could go wrong]
- Success Probability: [High/Medium/Low]

**Comparison Matrix**:
| Criteria | Weight | Option A | Option B | Option C |
|----------|--------|----------|----------|----------|
| [Factor] | [1-5]  | [Score]  | [Score]  | [Score]  |

**Recommendation**: [Choice with reasoning]
**Contingency**: If recommended option fails, then...
```

## Transformation Patterns

### Summarization Pattern
```markdown
Summarize [CONTENT] with these requirements:

**Length**: [X words/paragraphs/bullets]
**Focus**: [Key aspects to emphasize]
**Audience**: [Who will read this]
**Purpose**: [Why they need this summary]

Include:
- Main thesis/conclusion
- Key supporting points
- Critical data/evidence
- Action items (if any)

Exclude:
- Minor details
- Redundant information
- Technical jargon (unless required)
```

### Translation Pattern (Style/Tone)
```markdown
Transform this text from [CURRENT STYLE] to [TARGET STYLE]:

**Current**: [Formal/Technical/Casual/etc.]
**Target**: [Desired style]
**Audience**: [Who will read]
**Context**: [Where/how it will be used]

Maintain:
- Core message
- Key information
- Factual accuracy

Adjust:
- Vocabulary level
- Sentence structure  
- Tone/voice
- Examples/references
```

### Format Conversion Pattern
```markdown
Convert [INPUT FORMAT] to [OUTPUT FORMAT]:

**Input Structure**:
[Describe current format]

**Output Requirements**:
[Describe target format]

**Mapping Rules**:
- Field X → Field Y
- Combine A+B → C
- Transform D using [rule]

**Validation**:
- Ensure no data loss
- Verify format compliance
- Check special characters/escaping
```

## Extraction Patterns

### Information Extraction Pattern
```markdown
Extract the following from [SOURCE]:

**Required Information**:
1. [Field/Category]: [Description of what to find]
2. [Field/Category]: [Description]
3. [Field/Category]: [Description]

**Format**:
- If found: Include exact value/quote
- If not found: Mark as "Not specified"
- If ambiguous: Note all possibilities

**Output Structure**:
[Specify JSON, table, list format]
```

### Key Points Extraction Pattern
```markdown
Identify the key points from [CONTENT]:

**Criteria for "Key"**:
- Central to main argument
- Frequently emphasized
- Unique insights
- Actionable items

**For each point**:
- Main idea (1 sentence)
- Supporting evidence
- Relevance/importance
- Page/section reference

Limit to [NUMBER] most important points.
```

## Validation Patterns

### Fact-Checking Pattern
```markdown
Verify the claims in [CONTENT]:

For each factual claim:
1. **Claim**: [Quote exact statement]
2. **Classification**: [Fact/Opinion/Speculation]
3. **Verification**: 
   - True/False/Unverifiable
   - Confidence level
   - Source/reasoning
4. **Context**: Missing context that changes interpretation

Summary:
- Total claims: X
- Verified: Y
- False: Z
- Unverifiable: W
```

### Quality Assurance Pattern
```markdown
Perform QA check on [DELIVERABLE]:

**Checklist**:
□ Meets all requirements
□ Follows specified format
□ Contains no errors
□ Internally consistent
□ Complete and comprehensive

**Test Cases**:
1. [Scenario]: [Expected] → [Actual] [Pass/Fail]
2. [Scenario]: [Expected] → [Actual] [Pass/Fail]

**Issues Found**:
- Priority 1 (Must fix): [List]
- Priority 2 (Should fix): [List]
- Priority 3 (Nice to have): [List]

**Overall Status**: [Ready/Needs Work/Major Issues]
```

## Interaction Patterns

### Q&A Pattern
```markdown
Answer questions about [TOPIC]:

**Approach**:
1. Acknowledge the question
2. Provide direct answer first
3. Add relevant context
4. Give examples if helpful
5. Suggest related topics

**Constraints**:
- Assume [knowledge level] audience
- Keep answers under [length]
- Focus on practical application
- Admit uncertainty when applicable
```

### Explanation Pattern
```markdown
Explain [CONCEPT] to [AUDIENCE]:

**Start with**: Simple analogy or real-world connection
**Build up**: From basic to complex
**Include**: 
- Why it matters
- How it works
- Common misconceptions
- Practical examples

**Avoid**:
- Unnecessary jargon
- Assumed knowledge
- Abstract theory without examples

**Check Understanding**:
"This means that..." [rephrase in simple terms]
```

## Pattern Combination Examples

### Complex Analysis (Multiple Patterns)
```markdown
Analyze [SYSTEM] comprehensively:

Part 1: Current State (Extraction Pattern)
- Extract key metrics and configuration

Part 2: Problem Identification (Root Cause Pattern)
- Identify issues and their causes

Part 3: Solution Options (Decision Pattern)
- Evaluate potential improvements

Part 4: Recommendations (Documentation Pattern)
- Document proposed changes with implementation guide
```

### Content Development (Layered Patterns)
```markdown
Create article about [TOPIC]:

Phase 1: Research (Extraction Pattern)
- Gather key information from sources

Phase 2: Outline (Structure Pattern)
- Organize into logical sections

Phase 3: Draft (Creation Pattern)
- Write full content

Phase 4: Review (Review Pattern)
- Self-edit for quality

Phase 5: Polish (Transformation Pattern)
- Adjust tone and style for audience
```

## Pattern Selection Guide

| Goal | Recommended Pattern | When to Use |
|------|-------------------|--------------|
| Understand something | Analysis Pattern | Complex systems, problems |
| Create content | Creation Pattern | Articles, documentation |
| Fix problems | Debugging Pattern | Errors, issues |
| Make decisions | Decision Pattern | Multiple options exist |
| Improve existing work | Review Pattern | Quality assurance needed |
| Extract insights | Extraction Pattern | Large content sources |
| Verify accuracy | Validation Pattern | Claims need checking |
| Explain concepts | Explanation Pattern | Teaching/clarifying |
| Change format/style | Transformation Pattern | Adaptation needed |