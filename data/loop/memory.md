# Memory Between Iterations

## What to Persist

Stored in ~/loop/history/{loop-id}.json:
- **learnings** — Append-only log: what tried, what happened, what to try next
- **progress** — Structured state for complex multi-step tasks
- **iteration_count** — Current iteration number

## What NOT to Persist

- Full conversation history (context bloat)
- Failed code attempts (noise)
- Intermediate debugging output

## Storage Location

All loop data stored in ~/loop/:
- active.json — Currently running loops
- history/{id}.json — Completed loop logs
- learnings.md — Cross-loop patterns (optional)

## Cost Awareness

Loops multiply cost. Before starting:
- Estimate tokens per iteration
- Confirm with user if >10 iterations likely
- Consider if approach should change rather than iterate

## Safety Note

This skill does NOT:
- Make Git commits automatically
- Persist data outside ~/loop/
- Modify files without explicit task approval
