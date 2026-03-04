# Prompt Templates

Universal, pattern-based prompt templates. Domain specificity comes from Role Cards and Artifact Contracts — the prompt **skeleton** stays the same across all domains.

Replace `[bracketed]` values with your specifics.

---

## Universal Templates (All Patterns)

### Team Creation

```
Create a team of 4 teammates for [objective]:
- architect: [Planner title] — [planning responsibility + key context]
- developer: [Builder title] — [building responsibility + key context]
- tester:    [Validator title] — [validation responsibility + key context]
- reviewer:  [Critic title] — [critique responsibility + key context]
```

### Spawn Template (Universal)

```
Spawn a [teammate-id] teammate with the prompt:
"You are the [Domain Title] ([Generic Function]: Planner/Builder/Validator/Critic).

YOUR TASK: [task description from task list]

INPUT:
[Paste or reference the artifact from the previous step.
For first step: paste user requirements + source materials.]

PRODUCE: [Artifact Name]
Format: [Expected format — document, code, report, analysis, etc.]
Must include:
- [Required section/element 1]
- [Required section/element 2]
- [Required section/element 3]

CONSTRAINTS:
- [Domain rule 1]
- [Domain rule 2]
- [Style/standard to follow]

ACCEPTANCE CRITERIA:
- [Criterion 1]
- [Criterion 2]

When done, message the lead with your complete [Artifact Name].
If you encounter blockers, message the lead immediately with what you need."
```

### Handoff Message (Lead → Next Teammate)

```
Message [teammate-id]:
"The previous step ([Previous Title]) has completed. Here is their output:

[Paste artifact or key sections]

Your task is [task description]. Use the above as your primary input.

Key points to note:
- [Important decision/context from previous step]
- [Any open questions or flags]

Produce your [Artifact Name] and message me when done."
```

### Revision Request (Lead → Teammate)

```
Message [teammate-id]:
"Your [Artifact Name] needs revision. Specific feedback:

1. [Issue 1]: [What's wrong + what's expected]
2. [Issue 2]: [What's wrong + what's expected]

The following parts are good — keep them:
- [What works]

Please revise and message me with the updated [Artifact Name]."
```

### Final Synthesis (Lead → User)

```
## Workflow Complete: [Objective]

### Summary
[What was accomplished in 2-3 sentences]

### Deliverables
| Step | Agent | Artifact | Status |
|------|-------|----------|--------|
| 1. [Step name] | [Title] | [Artifact] | ✅ Complete |
| 2. [Step name] | [Title] | [Artifact] | ✅ Complete |
| 3. [Step name] | [Title] | [Artifact] | ✅ Complete |
| 4. [Step name] | [Title] | [Artifact] | ✅ Complete |

### Definition of Done
- [x] [Criterion 1]
- [x] [Criterion 2]
- [x] [Criterion 3]

### Remaining TODOs / Known Issues
- [Item 1]
- [Item 2]
```

---

## Pattern-Specific Templates

### sequential — Task List Template

```
Create these tasks with dependencies:

Task 1 (architect): "[Plan/Design] [subject]"
  - Input: [user requirements + existing assets]
  - Produce: [Plan artifact — format description]
  - Acceptance: [what makes this plan complete]
  - Deps: none

Task 2 (developer, depends on Task 1): "[Build/Create] [subject]"
  - Input: Plan from Task 1
  - Produce: [Primary artifact — format description]
  - Acceptance: [what makes this artifact complete]
  - Deps: Task 1

Task 3 (tester, depends on Task 2): "[Validate/Verify] [subject]"
  - Input: Artifact from Task 2 + criteria from Task 1
  - Produce: [Validation report — format description]
  - Acceptance: [pass/fail criteria defined]
  - Deps: Task 2

Task 4 (reviewer, depends on Task 3): "[Review/Critique] [subject]"
  - Input: Artifact + validation report
  - Produce: [Quality report — format description]
  - Acceptance: [all findings rated by severity]
  - Deps: Task 3
```

### parallel-merge — Task List Template

```
Create these tasks with dependencies:

Task 1 (architect): "Frame [topic] and define evaluation criteria"
  - Input: [user question/topic + constraints]
  - Produce: Problem framing + criteria matrix + angle assignments
  - Deps: none

Task 2a (developer, depends on Task 1): "Analyze from [Angle A] perspective"
  - Input: Problem framing from Task 1
  - Produce: Analysis with pros/cons/risks/recommendation from Angle A
  - Deps: Task 1

Task 2b (tester, depends on Task 1): "Analyze from [Angle B] perspective"
  - Input: Problem framing from Task 1
  - Produce: Analysis with pros/cons/risks/recommendation from Angle B
  - Deps: Task 1

Task 2c (reviewer, depends on Task 1): "Analyze from [Angle C] perspective"
  - Input: Problem framing from Task 1
  - Produce: Analysis with pros/cons/risks/recommendation from Angle C
  - Deps: Task 1

[Lead merges all analyses after Tasks 2a-2c complete]
```

### iterative-review — Task List Template

```
Create these tasks with dependencies:

Task 1 (architect): "Define [subject] requirements and quality rubric"
  - Input: [user brief + reference materials]
  - Produce: Requirements spec + quality criteria with severity levels
  - Deps: none

Task 2 (developer, depends on Task 1): "Create first draft of [artifact]"
  - Input: Requirements from Task 1
  - Produce: Draft v1
  - Deps: Task 1

Task 3 (reviewer, depends on Task 2): "Review draft against quality rubric"
  - Input: Draft v1 + quality rubric from Task 1
  - Produce: Feedback with actionable revision requests (rated by severity)
  - Deps: Task 2

Task 4 (developer, depends on Task 3): "Revise based on feedback"
  - Input: Draft v1 + reviewer feedback
  - Produce: Draft v2
  - Deps: Task 3

[Repeat Tasks 3-4 if critical/major items remain — max 2 rounds default]

Task 5 (tester, depends on Task 4): "Final validation"
  - Input: Final draft + original requirements
  - Produce: Pass/fail validation report
  - Deps: Task 4 (final round)
```

### fan-out-fan-in — Task List Template

```
Create these tasks with dependencies:

Task 1 (architect): "Decompose [scope] into independent chunks with contracts"
  - Input: Full scope + constraints
  - Produce: Chunk definitions with interfaces/contracts
  - Deps: none

Task 2a (architect, depends on Task 1): "Process Chunk A: [scope]"
  - Input: Chunk A definition + relevant inputs
  - Produce: Chunk A artifact per contract
  - Deps: Task 1

Task 2b (developer, depends on Task 1): "Process Chunk B: [scope]"
  - Input: Chunk B definition + relevant inputs
  - Produce: Chunk B artifact per contract
  - Deps: Task 1

Task 2c (tester, depends on Task 1): "Process Chunk C: [scope]"
  - Input: Chunk C definition + relevant inputs
  - Produce: Chunk C artifact per contract
  - Deps: Task 1

Task 2d (reviewer, depends on Task 1): "Process Chunk D: [scope]"
  - Input: Chunk D definition + relevant inputs
  - Produce: Chunk D artifact per contract
  - Deps: Task 1

[Lead merges all chunks after Tasks 2a-2d complete]

Task 3 (reviewer): "Quality gate on merged result"
  - Input: Merged artifact
  - Produce: Quality report
  - Deps: Lead merge
```

---

## Worked Examples

### Example A: Software Feature (sequential)

```
WORKFLOW INSTANCE SPEC
─────────────────────
Objective:      Add user authentication with JWT
Pattern:        sequential
Domain:         software-dev

ROLE CARDS
  Planner (architect):  Architect — Design auth flow, define API endpoints, DB schema
  Builder (developer):  Developer — Implement auth endpoints, middleware, DB models
  Validator (tester):   Tester — Write auth tests (unit + integration), test edge cases
  Critic (reviewer):    Code Reviewer — Security review, check OWASP top 10, code quality

ARTIFACTS
  Step 1 → Design Doc: API endpoints, JWT flow diagram, DB schema, middleware chain
  Step 2 → Source Code: Auth module files, migration, middleware
  Step 3 → Test Suite: Auth tests with coverage report
  Step 4 → Review Report: Security findings + code quality assessment
```

### Example B: Content Article (iterative-review)

```
WORKFLOW INSTANCE SPEC
─────────────────────
Objective:      Write a 2000-word guide on remote work productivity
Pattern:        iterative-review
Domain:         content-creation

ROLE CARDS
  Planner (architect):  Producer — Define audience, tone, outline, SEO keywords
  Builder (developer):  Writer — Draft article following brief, engaging style
  Validator (tester):   Fact-Checker — Verify statistics, check sources, accuracy
  Critic (reviewer):    Editor — Review clarity, flow, engagement, brand voice

ARTIFACTS
  Step 1 → Content Brief: Audience persona, outline, 5 SEO keywords, tone guide
  Step 2 → Draft: 2000-word article with source citations
  Step 3 → Editorial Feedback: Line-by-line suggestions, engagement improvements
  Step 4 → Fact-Check Report: Claim verification, source quality ratings
```

### Example C: Market Analysis (parallel-merge)

```
WORKFLOW INSTANCE SPEC
─────────────────────
Objective:      Evaluate entering the Southeast Asian e-commerce market
Pattern:        parallel-merge
Domain:         business-strategy

ROLE CARDS
  Planner (architect):  Strategist — Frame market entry question, define evaluation criteria
  Builder (developer):  Business Analyst — Market size, competitive landscape, SWOT
  Validator (tester):   Financial Modeler — TAM/SAM/SOM, investment required, ROI projections
  Critic (reviewer):    Risk Advisor — Regulatory risks, cultural barriers, operational challenges

ARTIFACTS
  Step 1 → Strategy Framework: Evaluation criteria, key questions per angle
  Step 2a → Market Analysis: Market data, competitors, opportunities
  Step 2b → Financial Model: Revenue projections, cost analysis, break-even
  Step 2c → Risk Assessment: Risk register, mitigations, go/no-go factors
```
