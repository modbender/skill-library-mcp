---
strategy: openclaw-examiner
version: 1.0.0
steps: 9
---

# OpenClaw Examiner Strategy

## Step 1: Exam Configuration & Scope Definition

### 1.1 Determine Exam Type
Ask user to specify examination mode:
- **Full Exam**: All 8 dimensions, 40 questions, 60-90 minutes
- **Dimension-Specific**: Single dimension, 5-10 questions, 10-20 minutes
- **Quick Check**: 2-3 questions per dimension, 16-24 questions, 20-30 minutes
- **Practice Mode**: Single dimension, immediate feedback, unlimited time

### 1.2 Select Dimensions (if not Full Exam)
If custom mode, present dimension options:
```
Available Dimensions:
1. Information Retrieval    5. Creative Generation
2. Content Understanding    6. Tool Usage
3. Logical Reasoning        7. Memory & Context
4. Code Generation          8. Quality & Accuracy

Enter dimension numbers (comma-separated) or 'all' for full exam.
```

### 1.3 Configure Parameters
- **Difficulty Level**: Easy, Medium, Hard, or Mixed
- **Question Count**: How many questions per dimension
- **Time Limit**: Per question or total time
- **Pass Threshold**: Minimum score for "passing" (default: 60/100)

**Apply knowledge**: Refer to knowledge/Domain.md for dimension definitions

### 1.4 Generate Exam Profile
Create exam session configuration:
```json
{
  "sessionId": "exam-[timestamp]",
  "type": "full|dimension|quick|custom|practice",
  "dimensions": ["list of selected dimensions"],
  "questionCount": { "dimension": count },
  "difficulty": "easy|medium|hard|mixed",
  "timeLimit": "total minutes or per question",
  "passThreshold": 60
}
```

---

## Step 2: Question Selection

### 2.1 Load Question Bank
Retrieve questions from knowledge/QuestionBank.md

### 2.2 Filter by Criteria
- Dimension(s) selected
- Difficulty level specified
- Exclude recently used questions (if retaking exam)

### 2.3 Balance Question Distribution
For mixed difficulty:
- 40% Easy, 40% Medium, 20% Hard (standard distribution)
- Adjust based on user's previous performance

### 2.4 Randomize Question Order
Within each dimension, randomize to prevent pattern recognition
- Exception: Code generation questions often progress in difficulty

### 2.5 Validate Question Set
Ensure:
- No duplicate questions
- All dimensions covered (if full exam)
- Total time estimate matches configured limit
- All questions have reference answers available

**Output**: Ordered list of questions with metadata

---

## Step 3: Session Initialization

### 3.1 Create Session Record
```json
{
  "sessionId": "exam-[timestamp]",
  "startTime": null,
  "endTime": null,
  "config": { /* from Step 1 */ },
  "questions": [ /* from Step 2 */ ],
  "answers": {},
  "scores": {},
  "status": "initialized"
}
```

### 3.2 Present Exam Introduction
```markdown
# OpenClaw Capability Examination

**Session ID**: exam-[timestamp]
**Exam Type**: [type]
**Dimensions**: [count] dimensions
**Questions**: [total] questions
**Estimated Time**: [X] minutes

## Instructions
- Answer questions in the specified JSON format
- Partial answers are better than skipping
- Focus on quality over speed
- You may skip questions and return later

## Ready?
Type "START" to begin, or ask any questions before starting.
```

### 3.3 Await User Confirmation
- IF user asks questions THEN provide clarification
- IF user wants different configuration THEN return to Step 1
- WHEN user confirms THEN proceed to Step 4

---

## Step 4: Question Delivery

### 4.1 Delivery Mode Selection
**Sequential Mode** (default):
- Present one question at a time
- User must answer or skip before proceeding
- Recommended for timed exams

**Batch Mode** (optional):
- Present 3-5 questions at once
- User answers all before proceeding
- Recommended for untimed practice

### 4.2 Present Question
For each question, display:

```markdown
---
Question [X]/[N] | Dimension: [Name]
Difficulty: [Level] | Time Limit: [T] minutes | Max Score: [S]
---

## Question
[Question text]

## Context (if provided)
[Any context, data, or constraints]

## Required Answer Format
```json
{
  "questionId": "[id]",
  "answer": { /* structure specification */ },
  "toolsUsed": ["@botlearn/skill-name", ...],
  "reasoning": "[optional explanation]",
  "confidence": "high|medium|low"
}
```

## Evaluation Criteria
- Criterion 1: [description] (weight: W)
- Criterion 2: [description] (weight: W)
- Criterion 3: [description] (weight: W)

## Submit Your Answer
Provide your answer when ready, or type:
- "SKIP" to move to next question
- "TIME" to request more time
- "HELP" for a hint (affects score)
---
```

### 4.3 Track Progress
- Record question start time
- Monitor elapsed time per question
- Flag questions approaching time limit

### 4.4 Handle Special Commands
- **SKIP**: Mark as skipped, allow return later
- **TIME**: Grant extension (note in scoring)
- **HELP**: Provide hint (reduce max score by 20%)

---

## Step 5: Answer Collection & Validation

### 5.1 Receive Answer
Parse user's answer submission

### 5.2 Validate Answer Format
Check required fields:
- `questionId`: Must match current question
- `answer`: Must match required structure
- `toolsUsed`: Array (can be empty)
- Basic JSON syntax validation

**IF validation fails**:
- Specify what's missing/incorrect
- Request corrected format
- Don't penalize for format issues

### 5.3 Store Answer
```json
{
  "questionId": "[id]",
  "timestamp": "[ISO-8601]",
  "answer": { /* user's answer */ },
  "timeSpent": "[seconds]",
  "status": "answered|skipped|helped",
  "notes": "[any special circumstances]"
}
```

### 5.4 Update Progress
- Move to next question
- Or return to skipped questions
- Or proceed to scoring if complete

---

## Step 6: Scoring & Evaluation

### 6.1 Apply Rubrics
For each answered question:

**Load scoring criteria** from knowledge/Scoring.md:
- Criteria definitions
- Point scale (0-5)
- Weights

**Score each criterion**:
- **For automated criteria**: Apply validation rules
  - Code correctness: Run against tests
  - Factual accuracy: Check against knowledge base
  - Completeness: Check required fields
- **For subjective criteria**: Use pattern matching
  - Compare to reference answer
  - Assess semantic similarity
  - Check for key elements

**Calculate question score**:
```
QuestionScore = Σ(CriterionScore × Weight) × 20
```

### 6.2 Calculate Dimension Scores
```
DimensionScore = Σ(QuestionScores) / NumberOfQuestions
```

### 6.3 Calculate Overall Score
```
OverallScore = Σ(DimensionScore × DimensionWeight) / ΣWeights
```
(Equal weights: 0.125 per dimension)

### 6.4 Determine Performance Level
| Score | Level |
|-------|-------|
| 90-100 | Expert |
| 80-89 | Advanced |
| 70-79 | Proficient |
| 60-69 | Competent |
| 0-59 | Beginner |

### 6.5 Compare to Benchmarks
Load benchmark data from knowledge/Domain.md:
- Calculate percentile rank
- Compare to population mean
- Identify above/below average dimensions

**Apply knowledge**: Refer to knowledge/Scoring.md for scoring methodology

---

## Step 7: Report Generation

### 7.1 Generate Structure
Create report following format in SKILL.md:
1. Overall Score & Performance Level
2. Radar Chart (ASCII art)
3. Dimension Scores Table
4. Detailed Analysis per Dimension
5. Question-by-Question Results
6. Benchmarking Comparison
7. Improvement Recommendations

### 7.2 Create Radar Chart
Generate ASCII representation:

```
                 Information Retrieval
                        [XX]/100
                          ▲
                         ╱ ╲
                        ╱   ╲
        Content         │     │         Creative
         Understanding  │     │         Generation
           [XX]/100 ────┼─────┼────── [XX]/100
                       ╱     ╲
                      ╱       ╲
            Logical  │         │  Code
           Reasoning │         │  Generation
            [XX]/100 ┼─────────┼ [XX]/100
                      ╲       ╱
                       ╲     ╱
                        │   │
                   Tool │   │ Quality
                   Usage │   │ & Accuracy
                  [XX]/100 └─┴─ [XX]/100
                      Memory
                      & Context
                       [XX]/100
```

### 7.3 Generate Dimension Analysis
For each dimension:
- **Strengths**: What went well
- **Areas for Improvement**: What needs work
- **Question Breakdown**: Individual question scores
- **Recommendations**: Specific actions to improve

### 7.4 Generate Recommendations
**Immediate Actions** (Next 7 days):
- Focus on lowest-scoring dimension
- Install specific skills
- Practice specific question types

**Short-term Goals** (Next 30 days):
- Target scores for each dimension
- Learning resources
- Milestone achievements

**Skill Recommendations**:
- Based on dimension weaknesses
- Suggest specific @botlearn skills
- Explain expected impact

### 7.5 Create Export Options
Offer to export:
- JSON format (for API integration)
- Markdown format (for documentation)
- SVG radar chart (for visualization)
- Anonymized benchmark contribution

---

## Step 8: Results Presentation & Discussion

### 8.1 Present Full Report
Display complete examination report

### 8.2 Highlight Key Findings
```markdown
## Key Findings

**Strongest Dimension**: [Name] ([score]/100)
- This is your competitive advantage
- Consider leveraging this in your workflows

**Weakest Dimension**: [Name] ([score]/100)
- This is your biggest opportunity for growth
- Focus practice here for fastest improvement

**Most Improved from Last Exam**: [Name] (+[X] points)
**Most Declined from Last Exam**: [Name] (-[X] points)

**Overall Percentile**: Top [X]%
```

### 8.3 Answer Questions
- IF user asks about specific scores THEN provide detailed breakdown
- IF user disputes a score THEN show rubric application
- IF user wants to retake THEN offer options (same questions, new questions, focus on specific dimension)

### 8.4 Discuss Next Steps
- **Re-exam**: When to retake (typically 2-4 weeks)
- **Practice**: How to use practice mode
- **Learning**: Resources for weak dimensions
- **Skills**: Which skills to install

---

## Step 9: Session Cleanup & Storage

### 9.1 Save Session Data
Store complete session record:
```json
{
  "sessionId": "exam-[timestamp]",
  "userId": "[user-id]",
  "config": { /* exam configuration */ },
  "questions": [ /* all questions with metadata */ },
  "answers": { /* all user answers */ },
  "scores": {
    "questions": { /* individual question scores */ },
    "dimensions": { /* dimension scores */ },
    "overall": /* overall score */
  },
  "benchmarks": { /* comparison data */ },
  "report": { /* generated report */ },
  "timestamp": {
    "started": "[start time]",
    "completed": "[end time]",
    "duration": "[total duration]"
  }
}
```

### 9.2 Update User History
- Add to user's exam history
- Track progress over time
- Calculate improvement trends
- Identify patterns in performance

### 9.3 Option: Contribute to Benchmarks
Ask user:
```markdown
## Contribute to Global Benchmarks

Your anonymized results can help improve the OpenClaw Examiner
by contributing to population benchmarks.

**What's shared**:
- Dimension scores
- Question performance (aggregated)
- Configuration details

**What's NOT shared**:
- Your identity
- Your answers
- Personal information

Contribute? [Y/n]
```

### 9.4 Provide Session Summary
```markdown
## Exam Complete!

**Session ID**: exam-[timestamp]
**Duration**: [X minutes]
**Overall Score**: [XX]/100 ([Level])

**Next Steps**:
1. Review detailed report above
2. Focus on improving [weakest dimension]
3. Practice mode available anytime
4. Re-take exam in [X] weeks

Thank you for using OpenClaw Examiner!
```

---

## Conditional Branches

### IF: Practice Mode
- Show one question at a time
- Provide immediate feedback after each answer
- Show reference answer
- Explain score given
- Allow unlimited attempts per question
- Don't generate full report, show running tally

### IF: Timed Exam
- Enforce time limits strictly
- Auto-submit when time expires
- Warn at 50%, 25%, 10% time remaining
- Note time pressure in scoring context

### IF: User Struggles (multiple skips, low scores)
- Pause and check if user wants to:
  - Continue with remaining questions
  - Switch to easier questions
  - End exam early and score what's complete
- Provide encouragement
- Remind that exam is diagnostic, not judgmental

### IF: Technical Issues
- If question loading fails: Skip question, note in report
- If scoring fails: Manual intervention required
- If report generation fails: Provide raw scores
- Always preserve user answers for recovery

### IF: Retaking Exam
- Ask if user wants:
  - Same questions (to measure improvement)
  - New questions (to expand assessment)
  - Focus on specific dimensions
- Show previous scores for comparison
- Highlight growth areas

---

## Error Handling

| Error | Handling |
|-------|----------|
| Invalid answer format | Request correction, no penalty |
| Question loading fails | Skip question, adjust scoring |
| Scoring fails | Note as "manual review required" |
| Timeout | Auto-submit or extend based on user preference |
| System crash during exam | Save progress, allow resume |
| Missing reference answer | Exclude from benchmarking, flag for review |

---

## Self-Check

Before presenting final report:
- All answered questions scored
- Dimension scores calculated correctly
- Overall score accurate
- Radar chart dimensions scaled correctly
- Recommendations specific to performance
- Benchmarks applied correctly
- Report format consistent
- Export options available
- Session data saved
- User informed of next steps
