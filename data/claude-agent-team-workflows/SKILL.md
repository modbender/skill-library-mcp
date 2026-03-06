---
name: agent-team-workflows
description: "Universal multi-agent workflow orchestration using Claude Code Agent Teams. Use when user asks to run a team workflow, create an agent team, or coordinate parallel work across multiple teammates — for any domain (software, content, data, strategy, research, etc.)."
---

# Agent Team Workflows

Universal orchestration framework for 5-agent teams (1 Lead + 4 Teammates) across any domain.

## Prerequisites

Agent Teams must be enabled. Add to `~/.claude/settings.json`:

```json
{
  "env": {
    "CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS": "1"
  }
}
```

## Generic Roles

Teammate IDs are fixed. Their **function** is remapped per domain via **Role Cards**.

| Slot | ID | Generic Function | Core Responsibility |
|------|----|------------------|---------------------|
| **Lead** | (session) | Orchestrator | Assign tasks, relay context, quality gate, synthesize final output |
| **Slot A** | `architect` | **Planner** | Frame problem, decompose tasks, produce plan/spec/blueprint |
| **Slot B** | `developer` | **Builder** | Produce primary artifact (code, draft, dataset, model, proposal) |
| **Slot C** | `tester` | **Validator** | Check against acceptance criteria, test, evaluate correctness |
| **Slot D** | `reviewer` | **Critic** | Assess quality, risk, consistency, compliance, suggest improvements |

### Role Cards (Domain Remapping)

Each domain preset provides **Role Cards** that specialize the generic functions:

| Domain | Planner | Builder | Validator | Critic |
|--------|---------|---------|-----------|--------|
| Software Dev | Architect | Developer | Tester | Code Reviewer |
| Content Creation | Producer | Writer | Fact-Checker | Editor |
| Data Analysis | Analyst Lead | Data Engineer | Statistician | Peer Reviewer |
| Business Strategy | Strategist | Business Analyst | Financial Modeler | Risk Advisor |
| Research | Research Lead | Researcher | Methodology Auditor | Peer Reviewer |

> Full role cards with artifact contracts → `reference/domain-presets.md`

## Pipeline Patterns

4 canonical control-flow patterns. Domain meaning comes from Role Cards, not the pattern itself.

### 1. sequential — Step-by-Step Pipeline

```
Planner → Builder → Validator → Critic → Lead Synthesis
```

**Use when:** Work is linear and each step depends on the previous output.
**Examples:** Feature dev, content creation, report writing.

### 2. parallel-merge — Parallel Exploration + Merge

```
Planner → (Builder ∥ Validator ∥ Critic) → Lead Merge → Validator Gate → Lead Synthesis
```

**Use when:** Multiple perspectives can work independently, then combine.
**Examples:** Research, strategy analysis, multi-angle evaluation.

### 3. iterative-review — Build-Critique Loop

```
Planner → Builder ↔ Critic (max N rounds) → Validator → Lead Synthesis
```

**Use when:** Quality requires iteration between creator and reviewer.
**Examples:** Content editing, design refinement, proposal drafting.
**Guard:** Default max 2 rounds. More requires user approval.

### 4. fan-out-fan-in — Map-Reduce

```
Planner → fan-out tasks to all 4 teammates → Lead fan-in merge → Critic Gate → Lead Synthesis
```

**Use when:** Large work can be split into independent chunks processed in parallel.
**Examples:** Multi-module features, large dataset processing, codebase audit.

> Pattern deep dives with sample task graphs → `reference/patterns.md`

## Coordination Protocol

Strict 6-step protocol, domain-agnostic.

### Step 1: Confirm Scope

Before spawning any team, confirm with user:

1. **Objective** — specific deliverable
2. **Domain** — select preset or define custom Role Cards
3. **Pattern** — which pipeline pattern fits
4. **Constraints** — tools, tech stack, tone, compliance, budget
5. **Inputs** — source material, existing assets, context files
6. **Definition of Done** — checkbox acceptance criteria the user agrees to

### Step 2: Build Workflow Instance Spec

Fill in the universal template:

```
WORKFLOW INSTANCE SPEC
─────────────────────
Objective:      [deliverable]
Pattern:        [sequential | parallel-merge | iterative-review | fan-out-fan-in]
Domain:         [preset name or "custom"]

ROLE CARDS
  Planner (architect):  [domain title] — [specific responsibility]
  Builder (developer):  [domain title] — [specific responsibility]
  Validator (tester):   [domain title] — [specific responsibility]
  Critic (reviewer):    [domain title] — [specific responsibility]

ARTIFACTS (per step)
  Step 1 → [artifact name]: [format/content description]
  Step 2 → [artifact name]: [format/content description]
  Step 3 → [artifact name]: [format/content description]
  Step 4 → [artifact name]: [format/content description]

CONSTRAINTS:    [tools, rules, limits]
INPUTS:         [files, data, references]
DEFINITION OF DONE:
  □ [criterion 1]
  □ [criterion 2]
  □ [criterion 3]
```

### Step 3: Create Team

```
Create a team of 4 teammates:
- architect: [Planner role card — context and responsibility]
- developer: [Builder role card — context and responsibility]
- tester:    [Validator role card — context and responsibility]
- reviewer:  [Critic role card — context and responsibility]
```

### Step 4: Create Tasks with Dependencies

Create tasks following the selected pattern's pipeline order. Each task MUST have:
- Clear description referencing role card
- Required input artifact (from previous step or original inputs)
- Required output artifact (format + content)
- Acceptance criteria
- Dependency on predecessor task

### Step 5: Spawn Teammates with Rich Context

Each teammate MUST receive in their spawn prompt:

1. **Role Card** — their domain title + specific responsibilities
2. **Assigned task** — what to produce
3. **Input artifact** — output from previous step (Lead must relay this)
4. **Output artifact contract** — exact format and content expected
5. **Constraints** — domain rules, style guides, compliance
6. **Handoff instruction** — "Message the lead with [artifact] when done"

**Universal spawn template:**
```
Spawn a [ID] teammate with the prompt:
"You are the [Domain Title] ([Generic Function]).

YOUR TASK: [task description]

INPUT: [paste or reference previous step's output]

PRODUCE: [artifact name]
Format: [expected format]
Must include: [required sections/elements]

CONSTRAINTS:
- [rule 1]
- [rule 2]

When done, message the lead with your complete [artifact name].
If you encounter blockers, message the lead immediately."
```

### Step 6: Coordinate Handoffs

When a teammate completes their step:
1. Lead receives output via message
2. Lead validates output against acceptance criteria
3. Lead passes artifact + relevant context to next teammate via message
4. If output is insufficient → send specific feedback, ask to revise

### Step 7: Synthesize & Deliver

After all steps complete:
1. Collect all artifacts
2. Verify all Definition of Done criteria are met
3. Summarize what was done (traceability: each criterion → which step satisfied it)
4. List remaining TODOs or known issues
5. Present final deliverable to user

## Lead Discipline Rules

1. **Delegate only** — Lead does NOT produce primary artifacts. Use delegate mode (`Shift+Tab`).
2. **Relay all context** — Teammates have no shared history. Lead MUST forward relevant artifacts between steps.
3. **Direct messages** — Use direct messages, not broadcast (saves 4× tokens). Broadcast only for parallel-merge sync points.
4. **Right-size tasks** — 5-6 tasks per teammate max. Split large work.
5. **Gate high-risk actions** — Require user approval for: irreversible changes, external publication, legal/compliance, high-cost operations, production deployments.
6. **Wait for teammates** — Never proceed or implement yourself. Wait for teammate completion before next step.

## Handling Failures

| Situation | Action |
|-----------|--------|
| Teammate stuck | Message with additional context, hints, or simplified sub-task |
| Bad output | Send specific feedback citing acceptance criteria, ask to revise |
| Teammate stops | Spawn replacement with same context + summary of work already done |
| Conflict between teammates | Lead mediates, makes final decision, messages both with resolution |
| Task too large | Lead splits into subtasks, reassigns across teammates |
| Iterative loop exceeds max | Ask user whether to approve more rounds or finalize current state |

## Cost Guidelines

| Pattern | Est. Cost | Worth It When |
|---------|-----------|---------------|
| sequential | ~4-5× single | Work spans 3+ artifacts/files with clear pipeline |
| parallel-merge | ~4× single | 3+ independent perspectives needed |
| iterative-review | ~3-4× single | Quality requires creator-critic dialogue |
| fan-out-fan-in | ~5× single | Large work divisible into independent chunks |

**Rule of thumb:** If one agent can finish in one session, don't use a team. Teams shine when work is parallelizable or benefits from multiple specialized perspectives.

## Domain Presets (Quick Reference)

| Preset | Recommended Pattern | Key Artifacts |
|--------|-------------------|---------------|
| `software-dev` | sequential / fan-out-fan-in | Design doc, source code, test suite, review report |
| `content-creation` | iterative-review | Content brief, draft, fact-check report, final edit |
| `data-analysis` | fan-out-fan-in | Analysis plan, datasets/transforms, statistical evaluation, findings report |
| `business-strategy` | parallel-merge | Strategy framework, market analysis, financial model, risk assessment |
| `research` | parallel-merge | Research plan, literature review, methodology audit, synthesis paper |

> Full presets with role cards, artifacts, and worked examples → `reference/domain-presets.md`
> Ready-to-use prompt templates → `reference/prompt-templates.md`
> Pattern deep dives → `reference/patterns.md`
