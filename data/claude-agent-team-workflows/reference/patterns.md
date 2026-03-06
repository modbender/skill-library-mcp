# Pipeline Patterns — Deep Dive

Detailed reference for each canonical pipeline pattern with task graphs and handoff examples.

---

## 1. sequential

```
┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐    ┌──────────┐
│ Planner  │───▶│ Builder  │───▶│ Validator │───▶│  Critic  │───▶│   Lead   │
│(architect)│   │(developer)│   │ (tester) │    │(reviewer)│    │Synthesis │
└──────────┘    └──────────┘    └──────────┘    └──────────┘    └──────────┘
```

### When to Use
- Work is naturally linear: plan → build → verify → polish
- Each step's output is the next step's input
- No opportunity for parallelism

### Task Graph Example
```
Task 1 (architect): "Create [plan/spec]"
  Input:  User requirements + existing assets
  Output: Plan document with structure, approach, acceptance criteria
  Deps:   none

Task 2 (developer): "Produce [primary artifact]"
  Input:  Plan document from Task 1
  Output: Complete artifact following plan
  Deps:   Task 1

Task 3 (tester): "Validate [artifact]"
  Input:  Artifact from Task 2 + acceptance criteria from Task 1
  Output: Validation report (pass/fail per criterion, issues found)
  Deps:   Task 2

Task 4 (reviewer): "Critique [artifact + validation]"
  Input:  Artifact + validation report
  Output: Quality report (findings rated by severity, improvement suggestions)
  Deps:   Task 3
```

### Handoff Protocol
- Lead forwards **full plan** from Planner to Builder (don't summarize — context loss is the #1 failure mode)
- Lead forwards **artifact + relevant plan sections** from Builder to Validator
- Lead forwards **artifact + validation report** from Validator to Critic
- Lead collects **all 4 outputs** for final synthesis

### Common Domains
- Software feature development
- Content creation (article, documentation)
- Report writing
- Process design

---

## 2. parallel-merge

```
                 ┌──────────┐
             ┌──▶│ Builder  │──┐
             │   └──────────┘  │
┌──────────┐ │   ┌──────────┐  │   ┌──────────┐    ┌──────────┐
│ Planner  │─┼──▶│ Validator│──┼──▶│   Lead   │───▶│Validator │
│(architect)│ │  └──────────┘  │   │  Merge   │    │  Gate    │
└──────────┘ │   ┌──────────┐  │   └──────────┘    └──────────┘
             └──▶│  Critic  │──┘
                 └──────────┘
```

### When to Use
- Multiple independent perspectives are valuable
- Work can be done in parallel without dependencies
- Lead synthesis is the critical value-add (combining viewpoints)

### Task Graph Example
```
Task 1 (architect): "Frame the problem and define evaluation criteria"
  Input:  User's question/topic + constraints
  Output: Problem framing + criteria matrix + assigned angles
  Deps:   none

Task 2a (developer): "Analyze from [Angle A] perspective"
  Input:  Problem framing from Task 1
  Output: Analysis with pros/cons/risks from Angle A
  Deps:   Task 1

Task 2b (tester): "Analyze from [Angle B] perspective"
  Input:  Problem framing from Task 1
  Output: Analysis with pros/cons/risks from Angle B
  Deps:   Task 1

Task 2c (reviewer): "Analyze from [Angle C] perspective"
  Input:  Problem framing from Task 1
  Output: Analysis with pros/cons/risks from Angle C
  Deps:   Task 1

Task 3 (lead): "Merge analyses into unified recommendation"
  Input:  All 3 analyses
  Output: Synthesized recommendation with tradeoff matrix
  Deps:   Task 2a, 2b, 2c
```

### Handoff Protocol
- Lead sends **identical problem framing** from Planner to all 3 parallel teammates
- **Optionally** enable cross-messaging between parallel teammates (use broadcast sparingly)
- Lead collects **all parallel outputs** before merging
- Lead may use Validator for a final gate check after merge

### Common Domains
- Research & exploration
- Business strategy (market vs. financial vs. operational angles)
- Technology evaluation
- Risk assessment

---

## 3. iterative-review

```
┌──────────┐    ┌──────────┐ ◀─┐    ┌──────────┐    ┌──────────┐
│ Planner  │───▶│ Builder  │   │───▶│ Validator │───▶│   Lead   │
│(architect)│   │(developer)│───┘   │ (tester) │    │Synthesis │
└──────────┘    └──────────┘       └──────────┘    └──────────┘
                  ▲      │
                  │ ┌────────┐
                  └─│ Critic │
                    │(reviewer)│
                    └────────┘
                  (max N rounds)
```

### When to Use
- Output quality improves significantly with feedback loops
- Creator-critic dialogue produces better results than single-pass
- Domain has established review/revision processes

### Task Graph Example
```
Task 1 (architect): "Define requirements and quality criteria"
  Input:  User brief + reference materials
  Output: Detailed requirements spec + quality rubric
  Deps:   none

Task 2 (developer): "Create first draft of [artifact]"
  Input:  Requirements from Task 1
  Output: Draft v1
  Deps:   Task 1

Task 3 (reviewer): "Review draft and provide feedback"
  Input:  Draft v1 + quality rubric from Task 1
  Output: Feedback with specific, actionable revision requests
  Deps:   Task 2

Task 4 (developer): "Revise based on feedback"
  Input:  Draft v1 + reviewer feedback
  Output: Draft v2 (revised)
  Deps:   Task 3

[Repeat Tasks 3-4 up to N times if quality criteria not met]

Task 5 (tester): "Final validation against all acceptance criteria"
  Input:  Final draft + original requirements
  Output: Validation report (pass/fail per criterion)
  Deps:   Task 4 (final round)
```

### Loop Control
- **Default max:** 2 Builder↔Critic rounds
- **Escalation:** If not converging after max rounds, Lead asks user: "Continue iteration or finalize?"
- **Exit criteria:** Critic's feedback has no critical/major items remaining

### Handoff Protocol
- Lead relays **Critic's feedback verbatim** to Builder (don't filter — Builder needs full context)
- Lead tracks round number and quality trajectory
- Lead decides when to exit loop based on Critic's severity ratings

### Common Domains
- Content editing (draft ↔ editor)
- Design refinement (prototype ↔ review)
- Proposal writing
- Code review cycles

---

## 4. fan-out-fan-in

```
                 ┌────────────┐
             ┌──▶│ Chunk A    │──┐
             │   │(architect) │  │
             │   └────────────┘  │
┌──────────┐ │   ┌────────────┐  │   ┌──────────┐    ┌──────────┐
│ Planner  │─┼──▶│ Chunk B    │──┼──▶│   Lead   │───▶│  Critic  │
│(architect)│ │  │(developer) │  │   │ Fan-in   │    │  Gate    │
└──────────┘ │   └────────────┘  │   └──────────┘    └──────────┘
             │   ┌────────────┐  │
             ├──▶│ Chunk C    │──┤
             │   │ (tester)   │  │
             │   └────────────┘  │
             │   ┌────────────┐  │
             └──▶│ Chunk D    │──┘
                 │(reviewer)  │
                 └────────────┘
```

### When to Use
- Large body of work can be split into independent chunks
- All chunks follow the same process but on different inputs
- Merge/integration step is needed after parallel completion

### Task Graph Example
```
Task 1 (architect): "Decompose work and define chunk contracts"
  Input:  Full scope + constraints
  Output: Chunk definitions with interfaces/contracts between them
  Deps:   none

Task 2a (architect): "Process Chunk A: [scope]"
  Input:  Chunk A definition + relevant inputs
  Output: Chunk A artifact following contract
  Deps:   Task 1

Task 2b (developer): "Process Chunk B: [scope]"
  Input:  Chunk B definition + relevant inputs
  Output: Chunk B artifact following contract
  Deps:   Task 1

Task 2c (tester): "Process Chunk C: [scope]"
  Input:  Chunk C definition + relevant inputs
  Output: Chunk C artifact following contract
  Deps:   Task 1

Task 2d (reviewer): "Process Chunk D: [scope]"
  Input:  Chunk D definition + relevant inputs
  Output: Chunk D artifact following contract
  Deps:   Task 1

Task 3 (lead): "Merge all chunks, verify contracts honored"
  Input:  All 4 chunk artifacts
  Deps:   Task 2a, 2b, 2c, 2d

Task 4 (reviewer): "Final quality gate on merged result"
  Input:  Merged artifact
  Output: Quality report
  Deps:   Task 3
```

### Key Consideration
- Planner's **chunk contracts** are critical: they define interfaces between chunks so merge works
- If chunks have cross-dependencies, use sequential or iterative-review instead
- Lead performs the integration/merge step

### Common Domains
- Multi-module software features (backend, frontend, API, tests)
- Large document sections (chapters, modules)
- Codebase-wide audits (security, performance, accessibility)
- Dataset processing (partition → process → combine)

---

## Choosing the Right Pattern

```
Is work naturally linear, step-by-step?
├── YES → sequential
└── NO
    ├── Can it be split into independent chunks of SAME type?
    │   ├── YES → fan-out-fan-in
    │   └── NO
    │       ├── Do you need multiple PERSPECTIVES on same input?
    │       │   ├── YES → parallel-merge
    │       │   └── NO → iterative-review (if quality needs feedback loops)
    │       └── Default → sequential
    └── Does quality improve with creator-critic dialogue?
        ├── YES → iterative-review
        └── NO → sequential
```

## Combining Patterns

Patterns can be composed for complex workflows:
- **sequential + iterative-review:** Plan → (Build ↔ Critique ×2) → Validate → Final
- **fan-out-fan-in + sequential:** Decompose → Parallel chunks → Merge → Validate → Critique
- **parallel-merge + iterative-review:** Frame → Parallel analysis → Merge → (Refine ↔ Critique ×2) → Validate
