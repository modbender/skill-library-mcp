---
name: rejection-logger
description: Captures and logs choices, options, or prompts that the agent evaluated and decided NOT to execute. Use whenever you skip a task, reject an approach, or choose one method over another to provide transparency into your reasoning.
---

# Rejection Logger

Transparency isn't just about showing what you did; it's about explaining what you *didn't* do. This skill helps you document rejected paths.

## Core Workflow

### 1. Identify Rejection
When you evaluate multiple ways to solve a problem and pick one, or when you decide a user request is unsafe/out of scope, log it.

### 2. Log Entry
Append to `.learnings/REJECTIONS.md` (create if missing):

```markdown
## [REJ-YYYYMMDD-XXX] <short_title>

**Timestamp**: ISO-8601
**Target**: <What was requested or considered>
**Decision**: REJECTED
**Reason**: <Why it was rejected (e.g., safety, complexity, better alternative)>
**Alternative**: <What was done instead>
```

## When to Use
- When a user asks for something and you say "No" or "I can't".
- When you consider two tools and pick one.
- When you refactor code and decide against a specific library.

## Benefits
- **Audit Trail**: Humans can see your internal deliberation.
- **Trust**: Showing rejections proves you are thinking, not just guessing.
- **Self-Correction**: Reviewing rejections helps you refine your decision boundaries.
