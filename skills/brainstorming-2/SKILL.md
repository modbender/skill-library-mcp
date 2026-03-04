---
name: brainstorming
description: Socratic design refinement before coding. Use when user requests feature without clear spec.
---

# Brainstorming Skill

## When to Use

Trigger BEFORE writing code when:
- User request is vague ("make it better", "add feature X")
- Complex feature with multiple approaches
- Design decisions impact multiple components

## Workflow

### Step 1: Understand Intent
Ask clarifying questions:
- What problem are we solving?
- Who is the user?
- What's the success criteria?
- What constraints exist? (time, compatibility, dependencies)

### Step 2: Explore Alternatives
Present 2-3 approaches:
- Approach A (simple): [description]
- Approach B (robust): [description]
- Approach C (future-proof): [description]

For each: Pros, Cons, Complexity (1-5)

### Step 3: Design Document
After user picks approach, create design doc:

```markdown
# Feature: [Name]

## Problem
[1-2 sentences]

## Solution
[Chosen approach, 3-5 sentences]

## Components Affected
- [Component 1]: [Change description]
- [Component 2]: [Change description]

## Testing Strategy
- Unit tests: [What to test]
- Integration tests: [What to test]

## Edge Cases
- [Case 1]
- [Case 2]

## Success Criteria
- [ ] [Criterion 1]
- [ ] [Criterion 2]
```

Save to: `docs/design/YYYY-MM-DD-feature-name.md`

### Step 4: Transition to Planning
Pass design doc to writing-plans skill.

## Anti-Patterns

❌ Jump straight to implementation
❌ Present only one approach
❌ Skip edge case discussion
❌ Forget to save design doc

## Example

User: "Add caching"

Bad:
```
I'll add Redis caching to the API.
```

Good:
```
Let me understand the requirements first:

1. What should be cached? (API responses, DB queries, computed results?)
2. What's the invalidation strategy? (TTL, event-based, manual?)
3. What's the acceptable staleness? (seconds, minutes, hours?)

Based on your answers, I'll present 3 approaches with trade-offs.
```
