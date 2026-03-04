---
domain: openclaw-examiner
topic: question-bank
priority: high
ttl: 90d
---

# OpenClaw Examiner Question Bank

## Question Metadata

Each question in the bank includes:
- **ID**: Unique identifier (dimension-difficulty-number)
- **Dimension**: One of 8 capability dimensions
- **Difficulty**: Easy, Medium, Hard
- **Type**: Execution, Knowledge, Analysis, Code, Creative
- **Time Limit**: Recommended completion time
- **Criteria**: Scoring rubric with weights
- **Reference Answer**: Ideal response for comparison

## Dimension 1: Information Retrieval

### IR-EASY-001: Web Search with Constraints
**Difficulty**: Easy
**Type**: Execution
**Time Limit**: 3 minutes

**Question**:
Search for information about the latest release of OpenClaw Agent (version 1.0.0 or later). Find:
1. Release date
2. Major new features
3. Breaking changes from previous version
4. Migration requirements

**Constraints**:
- Only use official sources (GitHub, official docs, npm)
- Provide URLs for all information
- Summarize each finding in one sentence

**Answer Format**:
```json
{
  "questionId": "IR-EASY-001",
  "answer": {
    "releaseDate": "YYYY-MM-DD",
    "majorFeatures": [
      {"feature": "...", "url": "..."},
      {"feature": "...", "url": "..."}
    ],
    "breakingChanges": [
      {"change": "...", "url": "..."}
    ],
    "migrationRequirements": {
      "description": "...",
      "url": "..."
    }
  },
  "sources": ["url1", "url2", "url3"],
  "toolsUsed": ["@botlearn/google-search"]
}
```

**Scoring Criteria**:
- Relevance (0.35): All information relevant to OpenClaw 1.0.0
- Completeness (0.30): All 4 required sections present
- Source Quality (0.20): Official, authoritative sources
- Efficiency (0.15): Concise, well-organized results

---

### IR-MED-001: Multi-Source Information Synthesis
**Difficulty**: Medium
**Type**: Analysis
**Time Limit**: 8 minutes

**Question**:
Research and compare the following three AI agent frameworks:
1. OpenClaw Agent
2. LangChain
3. AutoGPT

For each framework, find:
- Core philosophy/architecture
- Primary use cases
- Key advantages
- Main limitations

Then create a comparison table highlighting when to choose each framework.

**Answer Format**:
```json
{
  "questionId": "IR-MED-001",
  "answer": {
    "frameworks": {
      "openclaw": {
        "philosophy": "...",
        "useCases": ["...", "..."],
        "advantages": ["...", "..."],
        "limitations": ["...", "..."]
      },
      "langchain": { /* same structure */ },
      "autogpt": { /* same structure */ }
    },
    "comparisonTable": {
      "bestFor": {
        "openclaw": "...",
        "langchain": "...",
        "autogpt": "..."
      },
      "idealUser": {
        "openclaw": "...",
        "langchain": "...",
        "autogpt": "..."
      }
    }
  },
  "sources": ["url1", "url2", ...],
  "toolsUsed": ["@botlearn/google-search"]
}
```

**Scoring Criteria**:
- Relevance (0.30): Accurate framework information
- Completeness (0.30): All required fields for each framework
- Source Quality (0.20): Diverse, authoritative sources
- Synthesis Quality (0.20): Meaningful comparison, not just listing

---

## Dimension 2: Content Understanding

### CU-EASY-001: Document Summarization
**Difficulty**: Easy
**Type**: Analysis
**Time Limit**: 5 minutes

**Question**:
Read the following technical documentation excerpt and provide:

**Document**: [Agent Memory System Documentation provided]

Tasks:
1. Summarize the core purpose in one sentence
2. Extract 3 key features
3. Identify the target audience
4. List any prerequisites mentioned

**Answer Format**:
```json
{
  "questionId": "CU-EASY-001",
  "answer": {
    "corePurpose": "One-sentence summary",
    "keyFeatures": [
      "Feature 1 with brief explanation",
      "Feature 2 with brief explanation",
      "Feature 3 with brief explanation"
    ],
    "targetAudience": "Description of who this is for",
    "prerequisites": ["Prerequisite 1", "Prerequisite 2"]
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Comprehension Accuracy (0.40): Correct understanding of document
- Insight Quality (0.30): Meaningful feature extraction
- Extraction Completeness (0.30): All tasks completed

---

### CU-MED-001: Multi-Document Synthesis
**Difficulty**: Medium
**Type**: Analysis
**Time Limit**: 10 minutes

**Question**:
You are provided with three documents about Agent development:
1. A beginner's guide to Agent architecture
2. An advanced tutorial on skill development
3. A case study of a production Agent deployment

Tasks:
1. Identify the common principles across all three documents
2. Note any contradictions between documents
3. Create a learning path for someone new to Agents
4. Recommend which document to read first and why

**Answer Format**:
```json
{
  "questionId": "CU-MED-001",
  "answer": {
    "commonPrinciples": [
      "Principle 1 with examples from documents",
      "Principle 2 with examples from documents"
    ],
    "contradictions": [
      {
        "topic": "Area of contradiction",
        "document1Position": "What doc 1 says",
        "document2Position": "What doc 2 says",
        "resolution": "How to reconcile"
      }
    ],
    "learningPath": [
      "Step 1: Read X, then practice Y",
      "Step 2: ..."
    ],
    "firstRecommendation": {
      "document": "Which to read first",
      "reasoning": "Why this order works best"
    }
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Comprehension Accuracy (0.35): Correct understanding of all documents
- Insight Quality (0.35): Meaningful synthesis and connections
- Extraction Completeness (0.30): All tasks addressed thoroughly

---

## Dimension 3: Logical Reasoning

### LR-EASY-001: Algorithm Analysis
**Difficulty**: Easy
**Type**: Analysis
**Time Limit**: 5 minutes

**Question**:
Analyze the following algorithm and answer:

```python
def find_duplicate(arr):
    seen = set()
    for item in arr:
        if item in seen:
            return item
        seen.add(item)
    return None
```

Tasks:
1. What does this algorithm do?
2. What is its time complexity?
3. What is its space complexity?
4. Identify one edge case this function doesn't handle

**Answer Format**:
```json
{
  "questionId": "LR-EASY-001",
  "answer": {
    "purpose": "What the algorithm does",
    "timeComplexity": "Big-O notation with explanation",
    "spaceComplexity": "Big-O notation with explanation",
    "edgeCase": "Description of unhandled edge case",
    "reasoning": "Step-by-step analysis of logic"
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Logical Soundness (0.40): Correct analysis
- Step Clarity (0.30): Clear reasoning steps
- Conclusion Validity (0.30): Accurate complexity and edge case

---

### LR-MED-001: Multi-Step Problem Solving
**Difficulty**: Medium
**Type**: Analysis
**Time Limit**: 10 minutes

**Question**:
You need to optimize an Agent that processes 10,000 documents. Current behavior:
- Processes 100 documents/second
- Uses 2GB memory for 1,000 documents
- Crashes after ~5,000 documents (out of memory)

Tasks:
1. Identify the root cause of the crash
2. Propose 3 different solutions
3. For each solution, analyze:
   - Pros and cons
   - Implementation complexity
   - Expected impact
4. Recommend the best solution with justification

**Answer Format**:
```json
{
  "questionId": "LR-MED-001",
  "answer": {
    "rootCause": "Analysis of why it crashes",
    "solutions": [
      {
        "name": "Solution 1",
        "description": "How it works",
        "pros": ["pro1", "pro2"],
        "cons": ["con1", "con2"],
        "complexity": "low/medium/high",
        "expectedImpact": "quantified if possible"
      }
    ],
    "recommendation": {
      "solution": "Solution 1",
      "justification": "Why this is best",
      "implementation": "High-level implementation steps"
    }
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Logical Soundness (0.35): Correct root cause and valid solutions
- Step Clarity (0.30): Clear analysis structure
- Conclusion Validity (0.35): Well-justified recommendation

---

## Dimension 4: Code Generation

### CG-EASY-001: Function Implementation
**Difficulty**: Easy
**Type**: Code
**Time Limit**: 8 minutes

**Question**:
Implement a function that validates OpenClaw Agent skill names according to these rules:
- Must start with `@botlearn/`
- Must contain only lowercase letters, numbers, and hyphens
- Must be 3-50 characters long (after prefix)
- Cannot have consecutive hyphens
- Cannot start or end with hyphen (after prefix)

Write the function with:
- Clear documentation
- Input validation
- Helpful error messages
- Unit tests

**Answer Format**:
```json
{
  "questionId": "CG-EASY-001",
  "answer": {
    "code": "Complete function implementation",
    "language": "javascript/typescript/python",
    "tests": ["Test case 1", "Test case 2", "Test case 3"],
    "explanation": "Brief explanation of approach"
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Correctness (0.40): Handles all rules correctly
- Code Quality (0.30): Clean, documented, readable
- Efficiency (0.30): Reasonable algorithmic approach

---

### CG-MED-001: Refactoring Challenge
**Difficulty**: Medium
**Type**: Code
**Time Limit**: 12 minutes

**Question**:
Refactor the following poorly written code. Issues include:
- Poor naming
- Inefficient algorithm
- No error handling
- Duplicated logic
- No documentation

```javascript
function d(a) {
  let r = [];
  for (let i = 0; i < a.length; i++) {
    for (let j = i + 1; j < a.length; j++) {
      if (a[i] + a[j] === 10) {
        r.push([a[i], a[j]]);
      }
    }
  }
  return r;
}
```

Tasks:
1. Identify all issues
2. Refactor with best practices
3. Add comprehensive documentation
4. Improve algorithm if possible
5. Add error handling

**Answer Format**:
```json
{
  "questionId": "CG-MED-001",
  "answer": {
    "issuesIdentified": [
      "Issue 1: description",
      "Issue 2: description"
    ],
    "refactoredCode": "Improved implementation",
    "improvements": {
      "naming": "How naming was improved",
      "algorithm": "How algorithm was improved",
      "documentation": "Documentation added",
      "errorHandling": "Error handling added"
    }
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Correctness (0.35): Refactored code works correctly
- Code Quality (0.40): Significant improvement in quality
- Efficiency (0.25): Better algorithmic approach

---

## Dimension 5: Creative Generation

### CR-EASY-001: Marketing Copy
**Difficulty**: Easy
**Type**: Creative
**Time Limit**: 6 minutes

**Question**:
Create marketing copy for the OpenClaw Agent framework. Target audience: Developers who are tired of managing multiple AI tools.

Requirements:
1. A compelling headline
2. 3-5 benefit bullet points
3. A call-to-action
4. Tone: Professional yet approachable
5. Length: Under 100 words

**Answer Format**:
```json
{
  "questionId": "CR-EASY-001",
  "answer": {
    "headline": "Compelling headline",
    "benefits": ["Benefit 1", "Benefit 2", "Benefit 3"],
    "callToAction": "Clear CTA",
    "fullCopy": "Complete marketing text"
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Originality (0.35): Fresh, non-cliché approach
- Relevance (0.35): Speaks to target audience's pain points
- Quality (0.30): Professional, polished copy

---

### CR-MED-001: Technical Documentation
**Difficulty**: Medium
**Type**: Creative
**Time Limit**: 10 minutes

**Question**:
Write a "Getting Started" tutorial for OpenClaw Agent. The tutorial should:
- Welcome beginners
- Explain core concepts simply
- Include a practical example
- Use analogies where helpful
- Be encouraging and accessible

Requirements:
- 500-800 words
- Include code example
- Have clear sections
- End with next steps

**Answer Format**:
```json
{
  "questionId": "CR-MED-001",
  "answer": {
    "title": "Tutorial title",
    "introduction": "Welcome and hook",
    "sections": [
      {
        "heading": "Section title",
        "content": "Section content"
      }
    ],
    "codeExample": "Practical code snippet",
    "nextSteps": "What to do after this tutorial",
    "wordCount": "Actual word count"
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Originality (0.30): Fresh, engaging approach
- Relevance (0.40): Appropriate for beginner audience
- Quality (0.30): Well-structured, clear, encouraging

---

## Dimension 6: Tool Usage

### TU-EASY-001: Skill Selection
**Difficulty**: Easy
**Type**: Knowledge
**Time Limit**: 4 minutes

**Question**:
For each of the following tasks, select the most appropriate OpenClaw skill(s) and explain your choice:

Tasks:
1. Find recent research papers on quantum computing
2. Generate a summary of a 50-page PDF
3. Write Python code to scrape a website
4. Translate a technical document to Spanish
5. Generate 10 blog post ideas about AI

**Answer Format**:
```json
{
  "questionId": "TU-EASY-001",
  "answer": {
    "task1": {
      "skills": ["@botlearn/skill-name"],
      "reasoning": "Why this skill is appropriate"
    },
    "task2": { /* same structure */ },
    "task3": { /* same structure */ },
    "task4": { /* same structure */ },
    "task5": { /* same structure */ }
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Tool Selection (0.40): Appropriate skill choices
- Parameter Configuration (0.35): Understanding of skill capabilities
- Error Handling (0.25): Awareness of limitations

---

### TU-MED-001: Skill Chaining
**Difficulty**: Medium
**Type**: Execution
**Time Limit**: 10 minutes

**Question**:
Design a workflow that uses 3+ OpenClaw skills to accomplish this task:

**Task**: Research a technical topic, summarize findings, and generate a blog post about it.

Requirements:
1. Select appropriate skills
2. Define the order of operations
3. Specify data flow between skills
4. Handle potential errors
5. Provide example commands/API calls

**Answer Format**:
```json
{
  "questionId": "TU-MED-001",
  "answer": {
    "selectedSkills": ["skill1", "skill2", "skill3"],
    "workflow": [
      {
        "step": 1,
        "skill": "skill-name",
        "action": "What this step does",
        "input": "What it receives",
        "output": "What it produces"
      }
    ],
    "errorHandling": [
      {
        "step": "Which step",
        "potentialError": "What could go wrong",
        "handling": "How to handle it"
      }
    ],
    "exampleCommands": ["command1", "command2"]
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Tool Selection (0.35): Optimal skill combination
- Parameter Configuration (0.35): Well-designed workflow
- Error Handling (0.30): Comprehensive error planning

---

## Dimension 7: Memory & Context

### MC-EASY-001: Knowledge Retrieval
**Difficulty**: Easy
**Type**: Knowledge
**Time Limit**: 3 minutes

**Question**:
Based on the OpenClaw documentation you have access to:

1. What is the purpose of the Skills system?
2. How are knowledge documents injected?
3. What is the file structure of a skill package?
4. Name three required fields in manifest.json

**Answer Format**:
```json
{
  "questionId": "MC-EASY-001",
  "answer": {
    "skillsPurpose": "Explanation of Skills system",
    "knowledgeInjection": "How knowledge is injected",
    "skillStructure": ["file1", "file2", "file3"],
    "manifestFields": ["field1", "field2", "field3"]
  },
  "toolsUsed": [],
  "confidence": "high/medium/low"
}
```

**Scoring Criteria**:
- Retrieval Accuracy (0.40): Correct information retrieved
- Context Application (0.35): Applied from documentation context
- Knowledge Synthesis (0.25): Connected related concepts

---

### MC-MED-001: Contextual Application
**Difficulty**: Medium
**Type**: Analysis
**Time Limit**: 8 minutes

**Question**:
A user has configured their OpenClaw Agent with:
- 25 installed skills
- High concurrency (50 workers)
- 2GB memory limit
- Debug logging enabled

The user reports:
- Agent is slow to respond
- Skills sometimes fail to load
- Logs are extremely large

Tasks:
1. Identify the configuration issues based on best practices
2. Recommend specific changes with values
3. Explain the reasoning for each recommendation
4. Describe the expected improvement

**Answer Format**:
```json
{
  "questionId": "MC-MED-001",
  "answer": {
    "issues": [
      {
        "setting": "Configuration setting",
        "currentValue": "Current value",
        "issue": "Why this is a problem"
      }
    ],
    "recommendations": [
      {
        "setting": "Setting to change",
        "recommendedValue": "New value",
        "reasoning": "Why this value is better",
        "expectedImpact": "What improvement to expect"
      }
    ]
  },
  "toolsUsed": [],
  "confidence": "high/medium/low"
}
```

**Scoring Criteria**:
- Retrieval Accuracy (0.35): Correct best practice retrieval
- Context Application (0.40): Applied to this specific scenario
- Knowledge Synthesis (0.25): Connected configuration elements

---

## Dimension 8: Quality & Accuracy

### QA-EASY-001: Fact Verification
**Difficulty**: Easy
**Type**: Analysis
**Time Limit**: 4 minutes

**Question**:
Verify the following claims about OpenClaw Agent:

1. "OpenClaw supports 20+ built-in skills"
2. "Skills are written in Python only"
3. "Memory system uses vector embeddings"
4. "Configuration is done via YAML files"

For each claim:
- State if it's true/false
- Provide the correct information if false
- Cite your source

**Answer Format**:
```json
{
  "questionId": "QA-EASY-001",
  "answer": {
    "claim1": {
      "claim": "Original claim",
      "verdict": "true/false/partially true",
      "correctInfo": "Correct information if false",
      "source": "Where correct info comes from"
    },
    "claim2": { /* same structure */ },
    "claim3": { /* same structure */ },
    "claim4": { /* same structure */ }
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Factual Accuracy (0.40): All verifications correct
- Completeness (0.35): All claims addressed
- Consistency (0.25): Internal consistency in answers

---

### QA-MED-001: Requirement Compliance
**Difficulty**: Medium
**Type**: Analysis
**Time Limit**: 8 minutes

**Question**:
A user requested: "Create a skill that searches Twitter for trending topics in tech."

The following response was generated. Evaluate it for:
1. Completeness against requirements
2. Factual accuracy
3. Internal consistency
4. Any errors or issues

**Response to Evaluate**: [Provided response text]

**Answer Format**:
```json
{
  "questionId": "QA-MED-001",
  "answer": {
    "completeness": {
      "metRequirements": ["Req1", "Req2"],
      "missingRequirements": ["Req3", "Req4"],
      "extraContent": ["Unnecessary content"]
    },
    "factualAccuracy": {
      "accurate": ["Fact1", "Fact2"],
      "inaccurate": [
        {"claim": "Wrong fact", "correction": "Correct fact"}
      ],
      "uncertain": ["Claims that couldn't be verified"]
    },
    "consistency": {
      "consistent": true/false,
      "inconsistencies": [
        {"statement1": "...", "statement2": "...", "conflict": "..."}
      ]
    },
    "issues": [
      {"issue": "Description", "severity": "low/medium/high"}
    ]
  },
  "toolsUsed": []
}
```

**Scoring Criteria**:
- Factual Accuracy (0.35): Correct evaluation
- Completeness (0.35): Thorough analysis
- Consistency (0.30): Logical evaluation structure

---

## Question Generation Guidelines

When adding new questions to the bank:

1. **Clear Objective**: What capability is being tested?
2. **Unambiguous**: No room for multiple interpretations
3. **Scorable**: Criteria must be objectively evaluable
4. **Independent**: Doesn't require completing other questions first
5. **Timed**: Appropriate time limit for difficulty
6. **Referenced**: Include reference answer for validation

## Difficulty Calibration

| Difficulty | Time per Question | Expected Score (untrained) |
|------------|-------------------|---------------------------|
| Easy | 3-6 minutes | 60-75% |
| Medium | 8-12 minutes | 40-60% |
| Hard | 15-20 minutes | 25-45% |

## Question Statistics Tracking

Each question should track:
- Total attempts
- Average score
- Average time spent
- Skip rate
- Common wrong answers

Use this data to continuously improve the question bank.
