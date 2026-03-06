---
name: receiving-code-review
description: Handle code review feedback with technical rigor — verify before implementing, push back if incorrect, no performative agreement
---

# Receiving Code Review — Technical Rigor Over Social Comfort

## Core Principle

Verify before implementing. Ask before assuming. Technical correctness over social comfort.

## Forbidden Responses

NEVER respond with:
- "You're absolutely right!"
- "Great catch!"
- "Good point, I'll fix that!"

These are performative agreement. Instead, VERIFY the feedback is technically correct, then just fix it silently.

## Process

### Step 1: READ the Review

Read every comment. Understand what's being asked.

### Step 2: VERIFY Each Point

For each review comment:
- Is this technically correct?
- Does this match the codebase patterns?
- Does this align with the plan specification?

### Step 3: RESPOND

**If feedback is correct:**
Just fix it. No thanks needed. Push the fix and update the MR.

```bash
git add -A
git commit -m "fix: address review feedback"
git push origin [branch]
```

**If feedback is unclear:**
Ask for clarification. Don't guess what was meant.

```
RE: MR comment on [file:line] — Can you clarify?
Did you mean [interpretation A] or [interpretation B]?
```

**If feedback is incorrect:**
Push back with evidence. Don't implement wrong changes to be agreeable.

```
RE: MR comment on [file:line] — I think the current implementation
is correct because:
1. [Technical reason with evidence]
2. [Reference to existing pattern or documentation]
Happy to discuss if I'm missing something.
```

## When to Push Back

- Feedback would break existing functionality
- Feedback contradicts the plan specification
- Feedback adds unnecessary complexity (YAGNI)
- Feedback is technically incorrect
- Feedback conflicts with stated project requirements

## When NOT to Push Back

- Feedback identifies a real bug
- Feedback points out missing test coverage
- Feedback catches a security issue
- Feedback identifies violations of project conventions
