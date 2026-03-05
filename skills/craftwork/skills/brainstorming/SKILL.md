---
name: brainstorming
description: Design features before coding — explore codebase, propose 2-3 approaches with trade-offs, get approval before implementation
---

# Brainstorming — Design Before Code

## When to Use

Use BEFORE starting any non-trivial implementation. If you're about to write code for a new feature, architecture change, or multi-file modification, STOP and brainstorm first.

## Hard Gate

Do NOT write implementation code until you have:
1. Explored the codebase to understand current state
2. Proposed 2-3 approaches with trade-offs
3. Received approval on the chosen approach

## Process

### Step 1: Explore Context

Before proposing anything:

- Read recent commits to understand recent direction
- Search the codebase for related code and patterns
- Check existing documentation for prior decisions
- Understand what exists before proposing changes

### Step 2: Propose Approaches

Present 2-3 approaches with trade-offs and your recommendation:

```
DESIGN: [Feature Name]

Approach 1 (Recommended): [description]
- Pro: [benefit]
- Con: [cost]

Approach 2: [description]
- Pro: [benefit]
- Con: [cost]

Approach 3: [description]
- Pro: [benefit]
- Con: [cost]

My recommendation: Approach 1 because [reason].

Waiting for approval before proceeding.
```

### Step 3: Wait for Approval

Do NOT proceed until the decision-maker responds. If no response within the current session, note the pending design and move on to other work.

### Step 4: Transition to Planning

Once approved, create a detailed implementation plan before writing code. Use `craftwork:writing-plans` to structure the plan.

## Anti-Patterns

- **"This is too simple to need a design"** — Simple tasks cause the most wasted work from unexamined assumptions.
- **"I'll just figure it out as I go"** — Implementation without direction leads to rework.
- **"We already know how to do this"** — Search for prior decisions first. Don't repeat past mistakes.

## Key Principles

- YAGNI ruthlessly — remove unnecessary features from all designs
- Lead with your recommendation — don't present options without opinion
- Scale to complexity — a few sentences for simple tasks, detailed analysis for complex ones
- One question at a time — don't overwhelm with multiple questions
