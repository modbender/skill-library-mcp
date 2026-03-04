# Prompt Improvement Examples Library

## Example 1: Customer Support Email Response

### Before (Poor)
```
Respond to customer emails appropriately.
```

**Problems:**
- No definition of "appropriately"
- No structure or format specified
- No tone guidance
- Missing context about company/product

### After (Improved)
```
Respond to customer support emails following these guidelines:

**Tone**: Professional, empathetic, and solution-focused
**Length**: 100-200 words
**Structure**:
1. Acknowledge their concern
2. Apologize if appropriate  
3. Provide clear solution or next steps
4. Include timeline if applicable
5. Thank them for their patience

**Key Principles**:
- Never blame the customer
- Always offer a path forward
- Escalate to human if: legal issues, threats, or requests for refunds >$500

**Example Response Format**:
"Thank you for contacting us about [issue]. I understand how [acknowledge frustration].

[Solution or explanation]

[Next steps with timeline]

We appreciate your patience as we resolve this. Please let me know if you need any clarification."
```

**Why It's Better:**
- Clear structure and format
- Specific tone guidance
- Concrete examples
- Defined escalation criteria
- Measurable length requirement

---

## Example 2: Code Review

### Before (Vague)
```
Review this code and provide feedback.
```

**Problems:**
- No focus areas specified
- No format for feedback
- Unclear what constitutes an issue
- No priority levels

### After (Comprehensive)
```
Review the provided code focusing on these areas:

## Review Checklist

### 1. Security (Priority: HIGH)
- [ ] SQL injection vulnerabilities
- [ ] XSS possibilities  
- [ ] Authentication bypass risks
- [ ] Sensitive data exposure
- [ ] Input validation issues

### 2. Performance (Priority: MEDIUM)
- [ ] O(n²) or worse algorithms
- [ ] Unnecessary database queries
- [ ] Memory leaks
- [ ] Missing indexes on queried fields

### 3. Code Quality (Priority: MEDIUM)
- [ ] Functions over 50 lines
- [ ] Duplicate code blocks
- [ ] Dead code
- [ ] Missing error handling

### 4. Best Practices (Priority: LOW)
- [ ] Naming conventions
- [ ] Comment quality
- [ ] Test coverage

## Output Format
For each issue found:
```
FILE: [filename:line_number]
SEVERITY: [Critical/High/Medium/Low]
CATEGORY: [Security/Performance/Quality/Practice]
ISSUE: [Specific description]
SUGGESTION: [How to fix]
EXAMPLE: [Code snippet if helpful]
```

Skip categories with no issues. Focus on Critical and High severity first.
```

**Why It's Better:**
- Structured checklist approach
- Clear priorities
- Specific issue types to check
- Consistent output format
- Actionable feedback structure

---

## Example 3: Content Summarization

### Before (Unclear)
```
Summarize this article.
```

**Problems:**
- No length specified
- No focus areas
- No format requirements
- Purpose unknown

### After (Targeted)
```
Create an executive summary of this article for busy executives who need to make a decision.

**Requirements**:
- Length: 3-5 bullet points, 1-2 sentences each
- Focus: Business implications and required actions
- Exclude: Technical implementation details
- Include: Key risks, opportunities, and timeline

**Format**:
• **Main Finding**: [Core discovery or conclusion]
• **Business Impact**: [How this affects the organization]  
• **Risk/Opportunity**: [What to watch for]
• **Recommended Action**: [What decision is needed]
• **Timeline**: [When action is required]

If the article doesn't contain business implications, note: "Article is primarily technical/theoretical with limited immediate business application."
```

**Why It's Better:**
- Clear audience and purpose
- Specific length constraints
- Defined focus areas
- Structured output format
- Fallback for irrelevant content

---

## Example 4: Data Analysis

### Before (Incomplete)
```
Analyze this sales data.
```

**Problems:**
- No specific metrics requested
- No time period specified
- Output format unclear
- No context for interpretation

### After (Detailed)
```
Analyze the sales data to inform Q2 strategy planning:

## Analysis Requirements

### 1. Trend Analysis
Calculate month-over-month growth rates for:
- Total revenue
- Units sold
- Average order value
- Customer count

### 2. Performance Metrics
Identify:
- Top 5 performing products (by revenue)
- Bottom 5 performing products (by units)
- Customer segments with highest growth
- Regions exceeding/missing targets

### 3. Anomaly Detection
Flag any:
- Unusual spikes or drops (>30% change)
- Seasonal patterns
- Data quality issues (missing values, outliers)

### 4. Insights & Recommendations
Provide:
- 3 key findings that require action
- 2 opportunities for growth
- 1 primary risk to address

## Output Format
```
## Executive Summary
[2-3 sentence overview of overall performance]

## Key Metrics
| Metric | Current | Previous | Change | Status |
|--------|---------|----------|--------|---------|
| Revenue| $X      | $Y       | +/-%   | ↑/↓/→  |

## Top Findings
1. [Finding]: [Data support] → [Recommendation]
2. [Finding]: [Data support] → [Recommendation]
3. [Finding]: [Data support] → [Recommendation]

## Data Quality Notes
[Any issues or limitations in the data]
```
```

**Why It's Better:**
- Specific metrics defined
- Clear analysis framework
- Structured output format
- Actionable insights required
- Data quality consideration

---

## Example 5: Creative Writing

### Before (Too Open)
```
Write a story.
```

**Problems:**
- No genre specified
- No length requirement
- No tone or style guidance
- No target audience

### After (Guided)
```
Write a short science fiction story with these parameters:

**Specifications**:
- Length: 500-750 words
- Audience: Young adults (16-25)
- Tone: Hopeful despite adversity
- Setting: Near-future Earth (2070s)

**Required Elements**:
- A technological innovation that solves one problem but creates another
- A protagonist who must choose between personal and collective good
- At least one unexpected plot twist
- An ending that's satisfying but leaves room for thought

**Style Guidelines**:
- Show character through action, not exposition
- Use sensory details to establish setting
- Keep technical explanations brief and accessible
- Start in media res (middle of action)

**Avoid**:
- Info-dumping about the future world
- Clichéd "it was all a dream" endings
- Excessive technical jargon
- Preaching about current issues
```

**Why It's Better:**
- Clear creative constraints
- Specific requirements that guide without restricting
- Target audience defined
- Quality markers included
- Common pitfalls identified

---

## Example 6: Bug Report Analysis

### Before (Minimal)
```
What's wrong with this bug report?
```

**Problems:**
- No evaluation criteria
- No specific aspects to check
- No suggested improvements
- No format for response

### After (Systematic)
```
Evaluate this bug report for completeness and clarity:

## Bug Report Quality Checklist

### Required Information
Check if present and rate quality (Present/Missing/Unclear):
- [ ] Bug title: Descriptive and specific
- [ ] Environment: OS, browser, version, etc.
- [ ] Steps to reproduce: Numbered, specific actions
- [ ] Expected behavior: What should happen
- [ ] Actual behavior: What actually happens
- [ ] Error messages: Exact text or screenshots
- [ ] Frequency: Always/Sometimes/Once
- [ ] Impact: Who's affected and how severely
- [ ] Workaround: If any exists

### Clarity Assessment
- Is the issue clearly distinguishable from intended behavior?
- Could a developer reproduce this without asking questions?
- Are technical terms used correctly?

### Improvements Needed
For each missing/unclear element, suggest specific improvement:
```
MISSING: [Element]
ADD: "[Suggested text/information to include]"

UNCLEAR: [Element]  
CURRENT: "[Current text]"
IMPROVE TO: "[Suggested revision]"
```

### Overall Rating
- [ ] Ready for development (all info present and clear)
- [ ] Needs minor clarification (specify what)
- [ ] Needs major revision (too many issues)

Prioritize the top 3 improvements that would most help developers.
```

**Why It's Better:**
- Systematic evaluation criteria
- Specific elements to check
- Constructive improvement format
- Clear rating system
- Prioritization included

---

## Example 7: Research Question Refinement

### Before (Broad)
```
Make this research question better.
```

**Problems:**
- No criteria for "better"
- No context about research field
- No methodology consideration
- No scope guidance

### After (Structured)
```
Refine this research question for an academic thesis:

## Research Question Evaluation

### 1. Current Assessment
Evaluate the existing question on:
- **Specificity**: Is it narrow enough to be answerable?
- **Measurability**: Can outcomes be objectively assessed?
- **Relevance**: Does it address a gap in current knowledge?
- **Feasibility**: Can it be researched with available resources?
- **Clarity**: Is it unambiguous and well-defined?

### 2. Refinement Process
Transform the question by:

**From Abstract to Specific**:
- Identify vague terms and replace with precise ones
- Add geographical, temporal, or demographic boundaries
- Specify the type of relationship being investigated

**From Broad to Focused**:
- Original: "How does technology affect education?"
- Refined: "How does daily tablet use (>2 hours) affect reading comprehension scores in 4th grade students in urban public schools?"

**Adding Research Components**:
- Independent variable(s)
- Dependent variable(s)
- Population/sample
- Timeframe
- Context/setting

### 3. Output Format
```
ORIGINAL QUESTION: [As provided]

ISSUES IDENTIFIED:
1. [Issue]: [Why it's problematic]
2. [Issue]: [Why it's problematic]

REFINED VERSION: [Improved question]

JUSTIFICATION: [Why this version is better]

METHODOLOGY HINT: [What research method this suggests]

ALTERNATIVE FRAMINGS:
- Option A: [Different angle]
- Option B: [Different scope]
```
```

**Why It's Better:**
- Clear evaluation criteria
- Step-by-step refinement process
- Concrete examples
- Multiple alternatives provided
- Methodology consideration

---

## Example 8: Meeting Notes to Action Items

### Before (Generic)
```
Extract action items from these meeting notes.
```

**Problems:**
- No format for action items
- No priority system
- Missing owner assignment rules
- No deadline handling

### After (Actionable)
```
Convert meeting notes into trackable action items:

## Extraction Guidelines

### Identify Action Items
Look for:
- Direct assignments: "John will..."
- Commitments: "We need to..."
- Decisions requiring follow-up: "We decided to..."
- Questions requiring research: "Find out whether..."

### Format Each Action Item
```
ACTION: [Specific task in imperative form]
OWNER: [Person responsible, or "TBD" if unclear]
DUE DATE: [Specific date, "ASAP", or "Next meeting"]
PRIORITY: [High/Medium/Low based on impact and urgency]
CONTEXT: [1 sentence about why this matters]
SUCCESS CRITERIA: [How we know it's complete]
DEPENDENCIES: [What must happen first, if anything]
```

### Prioritization Rules
- HIGH: Blocks other work, customer-facing, or deadline <1 week
- MEDIUM: Important but not urgent, deadline 1-4 weeks
- LOW: Nice-to-have, no specific deadline

### Special Handling
- If owner unclear, mark as "TBD - [likely candidates]"
- If timeline vague, interpret: "soon"=1 week, "next quarter"=3 months
- Group related items under themes
- Flag any conflicting or duplicate actions

### Output Structure
```
## Action Items from [Meeting Date]

### High Priority
1. [ACTION formatted as above]
2. [ACTION formatted as above]

### Medium Priority
1. [ACTION formatted as above]

### Low Priority
1. [ACTION formatted as above]

### Needs Clarification
- [Items where owner or specifics unclear]
```
```

**Why It's Better:**
- Clear extraction criteria
- Structured format with all necessary fields
- Priority system with rules
- Handling for ambiguous cases
- Success criteria included

---

## Common Improvement Patterns

### Pattern 1: Vague → Specific
- Replace qualitative with quantitative
- Define all subjective terms
- Add measurable success criteria
- Include concrete examples

### Pattern 2: Implicit → Explicit
- State all assumptions
- Define context and constraints
- Specify formats and structures
- Include edge case handling

### Pattern 3: Unstructured → Structured
- Add clear sections and headers
- Use consistent formatting
- Create templates for outputs
- Implement checklists

### Pattern 4: Open → Bounded
- Add length constraints
- Specify scope boundaries
- Define what to exclude
- Set clear stopping points

### Pattern 5: Single-Pass → Iterative
- Break complex tasks into steps
- Add validation phases
- Include revision loops
- Build in quality checks

## Prompt Evolution Example

Showing how a prompt improves through iterations:

### Version 1 (Basic)
```
Translate this to Spanish.
```

### Version 2 (+ Context)
```
Translate this to Spanish for a business audience in Mexico.
```

### Version 3 (+ Style)
```
Translate this to Spanish for a business audience in Mexico. 
Use formal language appropriate for corporate communications.
```

### Version 4 (+ Specifics)
```
Translate this to Spanish for a business audience in Mexico.
- Use formal "usted" throughout
- Adapt currency to Mexican pesos
- Localize dates to DD/MM/YYYY format
- Keep technical terms in English with Spanish explanation
```

### Version 5 (+ Quality Checks)
```
Translate this to Spanish for a business audience in Mexico.

Requirements:
- Use formal "usted" throughout
- Adapt currency to Mexican pesos (MXN)
- Localize dates to DD/MM/YYYY format
- Keep technical terms in English with Spanish explanation in parentheses

Quality Checks:
- Ensure no literal translations that sound unnatural
- Verify all numbers converted correctly
- Confirm appropriate level of formality throughout

Flag any sections that are culturally specific and may need adaptation beyond translation.
```

Each version builds on the previous, adding layers of specificity and quality control.