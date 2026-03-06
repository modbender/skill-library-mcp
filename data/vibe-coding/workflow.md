# Research-Plan-Implement Workflow

## Why This Matters

AI might have a completely wrong mental model of your codebase. Finding that out during planning = 10x cheaper than debugging 500 lines of cascading errors.

## The Three Phases

### Phase 1: Research

Before implementing anything, have AI explore:

```
"Read through the auth module (/lib/auth/) and summarize:
- How user sessions work
- Where tokens are stored
- How middleware validates requests"
```

```
"List all places in the codebase that handle payments. 
What patterns do they follow?"
```

**Output**: AI shows you its understanding. Correct misunderstandings NOW.

### Phase 2: Plan

Get a concrete plan before any code:

```
"Write a step-by-step plan for adding team invitations:
- List exact files you'll create or modify
- Describe what changes in each file
- Note any new dependencies needed"
```

**Review the plan yourself**:
- Does it touch the right files?
- Is the approach consistent with existing patterns?
- Are there side effects I need to consider?

### Phase 3: Implement

Only after plan approval:

```
"Implement step 1 from the plan: create the invitation model"
```

Execute one step at a time. Verify each step works before continuing.

## Workflow in Practice

### Quick Features (< 30 min)
1. Quick Research: "Does anything similar exist?"
2. Rapid Plan: "Show me files you'd touch"
3. Implement: Single prompt if small, chunk if larger

### Medium Features (30 min - 2 hours)
1. Full Research: Read existing patterns
2. Written Plan: Review in detail
3. Implement step by step with testing between steps

### Large Features (> 2 hours)
1. Research + Documentation: Create a mini-spec
2. Break into sub-tasks
3. Plan each sub-task
4. Implement with checkpoints

## Signs You Skipped Planning

- AI modifies files you didn't expect
- New bugs appear in unrelated features
- You realize halfway that approach is wrong
- AI creates duplicate code instead of reusing existing

## Recovery When Plans Go Wrong

```
"Stop. Let's reassess. 
Current state: [what's done]
Problem: [what's broken]
Options: What are 3 ways to proceed?"
```
