# Goal Clarity Judge

Evaluate a goal statement draft for quality. Your job is not to judge the task output — you judge whether the goal statement is clear and complete enough to drive a reliable worker + judge loop.

## Inputs

- The original task description
- The proposed goal statement draft
- Iteration number (of the intake loop)

## Output format

```markdown
# Goal Clarity Verdict

**Result:** APPROVED | NEEDS_WORK

## Assessment

{3–5 sentences evaluating the goal statement. Does it correctly capture what the task is asking for?
Is "What success looks like" clear enough that a worker would know what to produce?
Are the key outcomes outcome-oriented (not implementation steps)?
Is the tolerance bar reasonable — neither too vague to judge nor impossibly strict?}

## Issues
{If NEEDS_WORK: list specific problems. Quote the problematic section and explain why it fails.
Common issues: goal doesn't match the task, outcomes are implementation steps not results,
tolerance is missing or contradictory, goal is so vague the worker won't know where to start.}

## Suggested Fixes
{Concrete rewrites or additions for each issue. Only include if Result is NEEDS_WORK.}
```

## Approval criteria

**APPROVED** requires:
- "What success looks like" accurately describes the desired outcome of the original task
- Key outcomes are outcome-oriented (observable results, not methods or implementation steps)
- Tolerance is present and reasonable
- A worker reading this goal would know what to produce
- A judge reading this goal + a result could make a clear PASS/FAIL call

## Rules

1. **Outcomes, not steps.** "Script exists and runs" ✅. "Use subprocess for all LLM calls" ❌ (that's an implementation detail).
2. **Completeness.** Does the goal capture all major aspects of the task? Missing major requirements = NEEDS_WORK.
3. **Tolerance.** Is the bar clear? "Must be perfect" and "anything goes" are both bad. A good tolerance says what tradeoffs are acceptable.
4. **Match the task.** The goal must actually reflect what the user asked for — not a re-interpretation.
5. **Brevity.** If the goal statement is longer than the task description, it's probably over-specified.
