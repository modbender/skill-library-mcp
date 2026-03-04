# Gate: LLM-as-Judge (optional, all modes)

**Question:** Does this meet subjective quality criteria?

Only runs when PRD includes subjective items (UX, design, readability, tone).
Skip entirely for pure backend/library work.

## Process

For each subjective criterion:
1. Present criterion + implementation to a **fresh session**
2. Binary pass/fail judgment with reasoning
3. Fail → specific, actionable feedback → loop back to Ralph loop Phase 2

## Examples

- "Navigation should be intuitive"
- "Error messages should be helpful, not cryptic"
- "Code should be readable by a junior developer"
- "API design should follow REST conventions"

## Pass/Fail

- **Pass:** All subjective criteria pass.
- **Fail:** Any criterion fails → return with specific feedback.
- **Cap:** Max 3 judge iterations per criterion. Still failing → Caution in proof bundle.
