---
name: plans-methodology
description: Structured work tracking methodology using Plans. Use when creating, managing, reviewing, or delegating plans for significant work. Covers plan lifecycle (draft, approved, in_progress, completed, archived), folder structure, approval authority, cross-agent delegation, and task tracking. Use when a user asks to create a plan, track work, delegate tasks to sub-agents, or review plan status.
---

# Plans Methodology

Structured work tracking for individuals or multi-agent teams. Each agent maintains `plans/` in their workspace.

## Directory Structure

```
plans/
  README.md
  draft/          # Being defined, not yet approved
  approved/       # Ready for execution
  in_progress/    # Currently executing
  completed/      # Done
  archived/       # Historical reference
```

Each plan is a folder: `YYYY-MM-DD-plan-name/`

## Plan Contents

```
YYYY-MM-DD-plan-name/
  specs/              # Problem statements, requirements
  proposal.md         # Why: justification, impact, risks
  design.md           # How: architecture, flows, decisions
  tasks.md            # What: checkboxes, owners, phases
```

### proposal.md

```markdown
# Proposal: [Plan Name]

## Status
Draft | Submitted | Approved | Rejected

## Parent Plan
[agent]/plans/[state]/[plan-name] (if child plan)

## Problem
What problem are we solving?

## Proposed Solution
High-level approach.

## Impact
What changes? What improves?

## Cost / Effort
Time, resources, dependencies.

## Risks
What could go wrong?

## Decision
Approved by [name] on [date] | Rejected because [reason]
```

### design.md

```markdown
# Design: [Plan Name]

## Overview
What are we building/doing?

## Architecture / Approach
How does it work? Diagrams, flows, decisions.

## Dependencies
What do we need? Other plans, external services, other agents.

## Constraints
Limitations, rules, non-negotiables.

## Open Questions
Things still to be decided.
```

### tasks.md

```markdown
# Tasks: [Plan Name]

## Summary
Brief overview.

## Tasks

### Phase 1: [Name]
- [x] Task description -> Owner
  Completed YYYY-MM-DD. Notes.
- [ ] Task description -> Owner
  Details, acceptance criteria.
- [ ] Delegate to [Agent]: [what] -> [Agent]
  Child plan: [agent]/plans/[state]/[plan-name]
```

## Lifecycle

1. **Draft** - Specs written, proposal drafted
2. **Approved** - Proposal approved, design and tasks written
3. **In Progress** - Execution started
4. **Completed** - All tasks done
5. **Archived** - Kept for reference

Move the plan folder between state directories to change state.

## When to Create a Plan

Create when: multi-agent coordination needed, significant effort, multiple phases, needs approval, or progress tracking desired.

Skip for: quick tasks, simple lookups, routine operations.

## Approval Authority

Define your own hierarchy. Typical pattern:

- **Owner/CEO** approves strategic plans
- **Lead agent** can approve plans aligned with established vision
- **Sub-agents** submit proposals to their lead for approval

Document your approval chain in your workspace's `plans/README.md`.

## Delegation

When delegating work to another agent:

1. Parent plan's `tasks.md` references the child plan path
2. Child plan's `proposal.md` references the parent plan path

Example in parent `tasks.md`:
```markdown
- [ ] Delegate to [Agent]: implement feature X
  Child plan: [agent]/plans/in_progress/2026-02-20-feature-x
```

Example in child `proposal.md`:
```markdown
## Parent Plan
[lead-agent]/plans/in_progress/2026-02-20-parent-plan
```

## On Session Start

1. Check `plans/in_progress/` for active plans
2. Check `plans/draft/` for plans awaiting action
3. Continue where you left off

## Granularity Tips

- Not everything needs a plan. Use for significant, multi-step work.
- A single agent working on a quick fix does not need a plan.
- Plans shine when coordination, tracking, or approval is involved.
- Keep plan documents concise. Verbose plans get ignored.
