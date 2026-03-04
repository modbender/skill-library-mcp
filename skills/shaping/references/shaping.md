# Shaping Reference

Complete methodology for collaboratively defining problems and exploring solution options.

## Table of Contents

1. Multi-Level Consistency
2. Starting a Session
3. Requirements (R)
4. Shapes (S)
5. Fit Check
6. Shape Parts
7. Spikes
8. Documents
9. Big Picture

## Multi-Level Consistency

Shaping produces documents at different levels of abstraction. Truth must stay consistent across all levels.

### Document Hierarchy (high to low)

1. **Big Picture** — highest level, quick context acquisition
2. **Shaping doc** — ground truth for R's, shapes, parts, fit checks
3. **Slices doc** — ground truth for slice definitions, breadboards
4. **Individual slice plans** (V1-plan, etc.) — ground truth for implementation details

Each level summarizes levels below it. Changes ripple in both directions. Never let documents drift out of sync.

## Starting a Session

Offer both entry points:
- **Start from R** — Describe problem, pain points, constraints
- **Start from S** — Sketch a solution, extract requirements as you go

When shaping doc already has a selected shape: display fit check for selected shape only, summarize what is unsolved.

## Requirements (R)

Numbered set defining the problem space: R0, R1, R2...

- Negotiated collaboratively, not filled in automatically
- Track status: Core goal, Undecided, Leaning yes/no, Must-have, Nice-to-have, Out
- Requirements extracted from fit checks should be standalone (not shape-dependent)
- R states what's needed, not what's satisfied — satisfaction shown in fit check

## Shapes (S)

Letters represent mutually exclusive solution approaches.

- **A, B, C...** = top-level options (pick one)
- **C1, C2, C3...** = components/parts of Shape C (combine)
- **C3-A, C3-B...** = alternatives for component C3 (pick one)

### Shape Titles

Give shapes short descriptive titles:
- ✅ "E: Modify CUR in place to follow S-CUR"
- ❌ "E: The solution" (too vague)

### Notation Persistence

Keep notation as audit trail. Compose new options by referencing prior components (e.g., "Shape E = C1 + C2 + C3-A").

## Fit Check (Decision Matrix)

THE single table comparing all shapes against all requirements.

### Format

```markdown
| Req | Requirement | Status | A | B | C |
|-----|-------------|--------|---|---|---|
| R0 | Make items searchable | Core goal | ✅ | ✅ | ✅ |
| R1 | State survives refresh | Must-have | ✅ | ❌ | ✅ |

**Notes:**
- B fails R1: [brief explanation]
```

### Rules

- **Always show full requirement text** — never abbreviate
- **Binary only**: ✅ or ❌. No ⚠️, no other symbols
- **Shape columns contain only ✅ or ❌** — explanations in Notes
- If a shape passes all checks but feels wrong → missing requirement. Add new R.

## Shape Parts

Parts describe what we BUILD or CHANGE — mechanisms, not intentions.

### Parts Table

```markdown
| Part | Mechanism | Flag |
|------|-----------|:----:|
| F1 | Create widget (component, def, register) | |
| F2 | Magic authentication handler | ⚠️ |
```

- Empty flag = mechanism understood
- ⚠️ = flagged unknown — WHAT described but HOW unknown
- Flagged unknowns FAIL fit checks (⚠️ → ❌)

### Rules

- Parts must be mechanisms, not intentions or constraints
- Avoid tautologies between R and S — shape should add specificity about *how*
- Parts should be vertical slices, not horizontal layers
- Extract shared logic as standalone parts others reference
- Use hierarchical notation (E1.1, E1.2) only when needed for clarity

## Spikes

Investigation tasks to learn how existing system works and what steps are needed.

### Structure

```markdown
## [Component] Spike: [Title]

### Context
Why we need this investigation.

### Goal
What we're trying to learn.

### Questions
| # | Question |
|---|----------|
| X1-Q1 | Specific question about mechanics |

### Acceptance
Spike complete when all questions answered and we can describe [understanding].
```

- Always create in own file (e.g., `spike-[topic].md`)
- Acceptance = information/understanding, not conclusions
- Questions ask about mechanics, not effort

## Documents

| Document | Contains | Purpose |
|----------|----------|---------|
| Big Picture | Frame + Shape + Slices summary | Quick context |
| Frame | Source, Problem, Outcome | The "why" |
| Shaping doc | R, Shapes, Affordances, Breadboard, Fit Check | Working document |
| Slices doc | Slice details, per-slice affordances, wiring | Implementation plan |

### Frame

Contains:
- **Source** — Original requests, quotes (verbatim)
- **Problem** — What's broken, what pain exists
- **Outcome** — What success looks like

Always capture source material verbatim.

### Lifecycle

```
Frame → Shaping → Slices → Big Picture (summarizes all)
```

## Big Picture

One-page summary: Frame + Shape (fit check, parts, breadboard) + Slices (sliced breadboard + grid).

### Structure

```markdown
# [Feature] — Big Picture

**Selected shape:** [Letter] ([Description])

## Frame
### Problem
- [bullet list]
### Outcome  
- [bullet list]

## Shape
### Fit Check (R × [Selected Shape])
### Parts
### Breadboard

## Slices
[Sliced breadboard + Grid]
```

### Slices Grid Format

```markdown
|  |  |  |
|:--|:--|:--|
| **[V1: NAME](./v1-plan.md)**<br>⏳ PENDING<br><br>• Item 1<br>• Item 2<br><br>*Demo: description* | ... | ... |
```

Slice colors: V1 green, V2 blue, V3 orange, V4 purple, V5 yellow, V6 pink.

## Possible Actions (Any Order)

- Populate R, Sketch shape, Detail (components), Detail (affordances)
- Explore alternatives, Check fit, Extract Rs
- Breadboard, Spike, Decide, Create Big Picture, Slice

## Communication

Always show full tables — every row, every requirement, every part. Never summarize or abbreviate. The full table is the artifact.
