# Worker Handoff Format

Every worker reports back with this structured format. No exceptions.

## Template

```
## [Gate Name] Result

**Status:** PASS | FAIL | WARN | ERROR
**Label:** wreckit-[gate-name]
**Duration:** Xs
**Summary:** One-line description

### What Was Done
[specific actions taken, files checked, commands run]

### Findings
- Finding 1 (severity: blocker/warning/info)
- Finding 2 ...

### Evidence
[raw output, file paths, test results]

### Known Issues
[anything incomplete or uncertain]

### Recommendation
[what to do about it — specific, actionable]
```

## Rules

- **First line of announce must include label + status** (for orchestrator parsing)
- **Bad handoff:** "Looks fine." 
- **Good handoff:** "Slop scan found 2 phantom imports in `src/utils.ts` (lines 3, 17) — `import { foo } from './nonexistent'`. phantom-pkg returns 404 on npm. Recommendation: remove both."
- **If the gate errors out**, still report with Status: ERROR and explain what went wrong
- **Never omit the Status field** — orchestrator depends on it for the collect pattern
