# Prompt Engineering Techniques Catalog

## Foundation Techniques

### Clear Instructions

Making instructions specific and unambiguous to reduce interpretation errors.

**When to use:**
- Always - this is the foundation of all good prompts
- Especially critical for analytical or structured tasks

**Implementation:**
- Replace vague terms with specific criteria
- Define success conditions explicitly  
- Eliminate ambiguous qualifiers

**Examples:**

Bad: "Write a good analysis"
Good: "Write a 500-word analysis covering strengths, weaknesses, and recommendations"

Bad: "Handle this appropriately"
Good: "If the input is valid, process it; if invalid, return an error message with specific issue"

### Context Provision

Providing background information to help the model understand the task's purpose and constraints.

**When to use:**
- When output will be used in specific ways
- When particular constraints aren't obvious
- When motivation helps clarify intent

**Implementation:**
- Explain why the task matters
- Describe how output will be used
- Clarify any special requirements

**Example:**
"This summary will be read aloud by a text-to-speech engine, so avoid abbreviations and special characters that are difficult to pronounce."

### Role Setting

Assigning a specific perspective or expertise level to shape responses.

**When to use:**
- Tasks requiring domain expertise
- When consistent tone/voice matters
- Educational or explanatory content

**Implementation:**
- Choose roles that align with task requirements
- Be specific about expertise level
- Include relevant constraints of that role

**Examples:**
- "As a senior security engineer, review this code for vulnerabilities"
- "As a patient teacher, explain this concept to a beginner"
- "As a technical writer, document this API"

### Output Format Specification

Explicitly defining the structure and format of desired outputs.

**When to use:**
- Structured data outputs (JSON, tables, lists)
- Consistent formatting requirements
- Integration with other systems

**Implementation:**
- Provide explicit format templates
- Include examples of correct format
- Specify separators, delimiters, structure

**Example:**
```
Format your response as:
TITLE: [Brief title]
PRIORITY: [High/Medium/Low]
DESCRIPTION: [2-3 sentences]
NEXT STEPS: [Bullet list]
```

## Advanced Techniques

### Chain-of-Thought Prompting

Requesting step-by-step reasoning before providing final answers.

**When to use:**
- Complex reasoning tasks
- Mathematical problems
- Multi-step analysis
- When transparency matters

**Implementation variants:**
- "Think step-by-step"
- "Show your reasoning"
- "Explain how you arrived at this answer"
- "Work through this methodically"

**Example:**
"Analyze this business proposal step-by-step:
1. First, identify the key assumptions
2. Then evaluate each assumption's validity
3. Finally, provide your overall assessment"

### Few-Shot Learning

Providing examples of input-output pairs to demonstrate patterns.

**When to use:**
- Novel or unique formats
- Specific style requirements
- Complex patterns hard to describe
- Boundary case clarification

**Optimal example counts:**
- 0 shots: Well-understood tasks
- 1 shot: Simple pattern demonstration
- 2-3 shots: Most common, shows variety
- 4+ shots: Complex patterns or high precision needed

**Example structure:**
```
Input: "The product arrived damaged"
Output: Category: Shipping Issue | Sentiment: Negative | Priority: High

Input: "Love the new features!"
Output: Category: Product Feedback | Sentiment: Positive | Priority: Low

Input: "Can't log into my account"
Output: Category: Technical Support | Sentiment: Neutral | Priority: High
```

### Self-Consistency Checking

Having the model verify and validate its own outputs.

**When to use:**
- High-stakes decisions
- Error-prone tasks
- Complex calculations
- Critical analysis

**Implementation patterns:**
- "Double-check your work for errors"
- "Verify this meets all requirements"
- "Review for consistency and completeness"
- "Identify any potential issues with this approach"

**Multi-pass example:**
```
1. Generate initial solution
2. "Now review your solution for errors or improvements"
3. "Provide the final, corrected version"
```

### Progressive Refinement

Building complex outputs through iterative steps.

**When to use:**
- Long-form content creation
- Complex problem solving
- Multi-faceted analysis
- Quality improvement

**Implementation:**
```
"First, create an outline of key points"
"Now expand each point into a paragraph"
"Finally, review and polish the complete text"
```

### Guided Reasoning

Providing specific reasoning frameworks or methodologies.

**When to use:**
- Structured analysis tasks
- Decision making
- Evaluation tasks
- Problem diagnosis

**Example frameworks:**
- SWOT analysis for business evaluation
- Root cause analysis for problems
- Pro/con lists for decisions
- Priority matrices for task management

### Metacognitive Prompting

Asking the model to reflect on its own thinking process.

**When to use:**
- Complex reasoning tasks
- Identifying potential biases
- Improving answer quality
- Educational contexts

**Implementation:**
- "What assumptions are you making?"
- "What evidence supports this conclusion?"
- "What alternative interpretations exist?"
- "Rate your confidence in this answer and explain why"

## Specialized Techniques

### Constitutional Prompting

Embedding principles and values to guide behavior.

**When to use:**
- Ethical considerations important
- Consistent policy adherence needed
- Safety-critical applications

**Implementation:**
```
"Follow these principles:
1. Prioritize user safety
2. Avoid harmful content
3. Respect privacy
4. Provide balanced perspectives"
```

### Tree of Thoughts

Exploring multiple reasoning paths before selecting the best.

**When to use:**
- Complex problem solving
- Creative tasks with multiple solutions
- Strategic planning
- When optimal path isn't obvious

**Implementation:**
```
"Consider three different approaches to this problem:
Approach 1: [Description]
Approach 2: [Description]
Approach 3: [Description]
Now evaluate each and choose the best, explaining why"
```

### Prompt Chaining

Breaking complex tasks into sequential prompts.

**When to use:**
- Tasks exceeding single prompt capacity
- Multi-stage workflows
- When intermediate results need validation
- Complex transformations

**Example chain:**
1. Extract key information → 
2. Analyze patterns → 
3. Generate recommendations →
4. Format report

### Negative Examples

Showing what NOT to do alongside positive examples.

**When to use:**
- Preventing specific errors
- Clarifying boundaries
- Style differentiation
- Avoiding unwanted patterns

**Implementation:**
```
Correct: "The analysis reveals three key factors..."
Incorrect: "I think maybe there could be some factors..."
```

## Technique Selection Matrix

| Task Type | Primary Technique | Secondary Technique | Avoid |
|-----------|------------------|-------------------|--------|
| Creative Writing | Role Setting | Few-Shot | Over-constraining |
| Data Analysis | Chain-of-Thought | Output Format Spec | Vague success criteria |
| Code Review | Structured Steps | Self-Consistency | Missing context |
| Summarization | Clear Constraints | Progressive Refinement | No length guidance |
| Q&A | Context Provision | Self-Consistency | Assuming knowledge |
| Classification | Few-Shot | Clear Criteria | Ambiguous categories |
| Translation | Role + Examples | Quality Checks | No style guidance |
| Debugging | Systematic Analysis | Tree of Thoughts | Jumping to conclusions |

## Combining Techniques

Effective prompts often combine multiple techniques:

### Example: Technical Documentation
- Role Setting (technical writer)
- Clear Structure (sections and format)
- Progressive Refinement (outline → draft → polish)
- Self-Consistency (technical accuracy check)

### Example: Problem Solving
- Chain-of-Thought (systematic reasoning)
- Tree of Thoughts (explore options)
- Self-Consistency (verify solution)
- Metacognitive (confidence assessment)

### Example: Content Moderation
- Constitutional (safety principles)
- Few-Shot (edge cases)
- Clear Criteria (violation types)
- Self-Consistency (double-check decisions)

## Technique Anti-Patterns

### Over-Engineering
Using complex techniques for simple tasks wastes tokens and adds confusion.

### Technique Conflicts
Some techniques work poorly together (e.g., extreme brevity + chain-of-thought).

### Context Overload
Too many examples or too much background can distract from core task.

### Ambiguous Prioritization
When multiple techniques suggest different approaches, clarify which takes precedence.

## Adaptation Guidelines

Techniques should be adapted based on:

1. **Model Capabilities**: Newer models handle complexity better
2. **Task Requirements**: Match technique complexity to task needs
3. **User Expertise**: Adjust for who will use/maintain the prompt
4. **Performance Constraints**: Balance quality with speed/cost
5. **Error Tolerance**: High-stakes tasks need more validation techniques